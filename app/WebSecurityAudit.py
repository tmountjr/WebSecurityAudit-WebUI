from flask import Flask, request
from subprocess import Popen, PIPE
import os

app = Flask(__name__)

@app.route('/wsra/healthcheck', methods=['GET'])
def healthcheck():
    domain = request.args.get('domain', '')
    if domain:
        return domain
    else:
        return 'OK'

@app.route('/wsra', methods=['GET'])
def wsra():
    domain = request.args.get('domain', '')
    if not domain:
        return {'error': 'Domain parameter is missing'}, 400
    cmd1 = f'echo "{domain}" | subfinder -silent | httpx -mc=200 -silent > "{domain}"-audit.txt'
    cmd2 = f'wafw00f -i "{domain}"-audit.txt -o "{domain}"-audit.json && rm "{domain}"-audit.txt'
    cmd3 = f'cat "{domain}"-audit.json && rm "{domain}"-audit.json'
    process1 = Popen(cmd1, stdout=PIPE, stderr=PIPE, shell=True)
    stdout1, stderr1 = process1.communicate()
    if stderr1:
        return {'error': stderr1.decode('utf-8')}, 500
    process2 = Popen(cmd2, stdout=PIPE, stderr=PIPE, shell=True)
    stdout2, stderr2 = process2.communicate()
    if stderr2:
        return {'error': stderr2.decode('utf-8')}, 500
    process3 = Popen(cmd3, stdout=PIPE, stderr=PIPE, shell=True)
    stdout3, stderr3 = process3.communicate()
    if stderr3:
        return {'error': stderr3.decode('utf-8')}, 500
    return stdout3.decode('utf-8')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
