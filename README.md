python3 -m venv venv

source venv/bin/activate

pip install requirements.txt

python manage.py migrate

daphne Live_Chat.asgi:application