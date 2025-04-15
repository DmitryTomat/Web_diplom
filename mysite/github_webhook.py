import os
from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/github-webhook/', methods=['POST'])
def webhook():
    if request.method == 'POST':
        # Обновляем код
        os.system('cd /home/вашusername/mysite/Web_diplom/mysite && git pull')

        # Перезагружаем приложение
        os.system('touch /var/www/вашusername_pythonanywhere_com_wsgi.py')
        return jsonify({'status': 'success'}), 200
    return jsonify({'status': 'bad request'}), 400