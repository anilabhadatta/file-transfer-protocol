# FILE-TRANSFER-APP

## System Requirements:

> - Python 3.9+
> - Flask
> - Gunicorn

## Usage:

> 1. Clone the repository
> 2. Create Virtual Environment
> 3. Install the requirements.txt using pip
> 4. Run the Flask webapp using\
>    (Linux) gunicorn --workers=2 -b 127.0.0.1:5022 'app:app' --timeout 120000

>    (Windows) waitress-serve --listen=127.0.0.1:5022 --channel-timeout=120000 "app:app"
