from flask import Flask, render_template, request, send_from_directory, make_response, redirect
from werkzeug.utils import secure_filename
import os
import sys
import natsort
import shutil
sys.stdout.flush()

app = Flask(__name__)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
try:
    os.mkdir("tmp")
except:
    pass
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'tmp')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def load_files():
    files = natsort.natsorted(os.listdir(app.config['UPLOAD_FOLDER']))
    size = []
    for i, file in enumerate(files):
        size.append(" -> " + "%.2fMB" % (
            float(os.stat(os.path.join(app.config['UPLOAD_FOLDER'], file)).st_size)/(1024*1024)))
    stats = zip(files, size)
    return stats


def get_storage():
    BytesPerGB = 1024 * 1024 * 1024
    (total, used, free) = shutil.disk_usage(os.getcwd())
    total = ("Total: %.2fGB" % (float(total)/BytesPerGB))
    used = ("Used:  %.2fGB" % (float(used)/BytesPerGB))
    free = ("Free:  %.2fGB" % (float(free)/BytesPerGB))
    return (total, used, free)


@app.route("/", methods=['GET'])
def search():
    return render_template("home.html", stats=load_files(), storage=get_storage())


@app.route("/gen_del", methods=['POST', 'GET'])
def gen_del():
    if request.method == "POST":
        filename = request.form.get('filename')
        if request.form.get("generate"):
            if filename:
                return render_template("home.html", storage=get_storage(), stats=load_files(), download_path=f"/tmp/{filename}")
            return render_template("404.html", message="Filename is empty")
        elif request.form.get("delete"):
            if filename:
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                return render_template("home.html", storage=get_storage(), stats=load_files())
            return render_template("404.html", message="Filename is empty")
    return redirect('/')


@app.route("/upload", methods=['POST', 'GET'])
def upload():
    if request.method == "POST":
        files = request.files['files']
        save_path = os.path.join(
            app.config['UPLOAD_FOLDER'], secure_filename(files.filename))
        current_chunk = int(request.form['dzchunkindex'])

        if os.path.exists(save_path) and current_chunk == 0:
            return make_response(('File already exists', 400))

        try:
            with open(save_path, 'ab') as f:
                f.seek(int(request.form['dzchunkbyteoffset']))
                f.write(files.stream.read())
        except OSError:
            return make_response(("Not sure why,"
                                  " but we couldn't write the file to disk", 500))

        total_chunks = int(request.form['dztotalchunkcount'])

        if current_chunk + 1 == total_chunks:
            if os.path.getsize(save_path) != int(request.form['dztotalfilesize']):
                return make_response(('Size mismatch', 500))
        return make_response(('Chunck upload success', 200))
    return redirect('/')


@app.route("/tmp/<filename>")
def file_download(filename):
    try:
        d = send_from_directory(
            app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
        return d
    except:
        return render_template("404.html", message="File does not exist")


if __name__ == "__main__":
    app.run(threaded=True)
