from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def hello():
    return '<h1>Minimal CRM Test</h1><p>Flask is working!</p>'

@app.route('/health')
def health():
    return {'status': 'ok', 'message': 'Minimal CRM app is running'}

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.getenv('PORT', 8000)))
