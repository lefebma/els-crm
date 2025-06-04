from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>ELS CRM - Azure Test</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 800px; margin: 0 auto; }
            .status { background: #d4edda; padding: 20px; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎉 ELS CRM Application</h1>
            <div class="status">
                <h2>✅ Application Successfully Deployed to Azure!</h2>
                <p>Your CRM application is now running on Azure App Service.</p>
                <p><strong>Status:</strong> Healthy and Running</p>
                <p><strong>Environment:</strong> Azure App Service</p>
                <p><strong>Python Version:</strong> 3.11</p>
            </div>
            <h3>Next Steps:</h3>
            <ul>
                <li>Access the full CRM functionality at <code>/login</code></li>
                <li>API endpoints available at <code>/api/</code></li>
                <li>Database will be initialized on first use</li>
            </ul>
        </div>
    </body>
    </html>
    '''

@app.route('/health')
def health():
    return {'status': 'healthy', 'app': 'ELS CRM', 'version': '1.0.0'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)
