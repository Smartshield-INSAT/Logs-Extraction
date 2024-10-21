import logging
from flask import Flask, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

logging.basicConfig(filename='/var/log/myapp/server.log', level=logging.INFO, format='%(asctime)s %(message)s')

@app.route('/')
def home():
    app.logger.info('Home page accessed')
    return "Welcome to the Flask server!"

@app.route('/process', methods=['POST'])
def process():
    data = request.json
    app.logger.info(f'Processing request: {data}')
    return "Request processed"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
