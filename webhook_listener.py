from flask import Flask, request
import subprocess
import os

app = Flask(__name__)

@app.route('/github-webhook', methods=['POST'])
def github_webhook():
    # Only respond to push events
    if request.headers.get('X-GitHub-Event') == 'push':
        repo_path = os.path.dirname(os.path.abspath(__file__))
        subprocess.run(['git', 'pull'], cwd=repo_path)
        return 'Pulled latest changes!', 200
    return 'Ignored', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
