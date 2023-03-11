#!/usr/bin/env zsh
#
# Security Audit
# Discover sub-domains running an http server on the hosts
# Process these domains through WafW00f engine & output in JSON

from flask import Flask, request, jsonify
from subprocess import Popen, PIPE

app = Flask(__name__)

@app.route('/wsra', methods=['GET'])
def wsra():
    domain = request.args.get('domain', '')
    if not domain:
        return jsonify({'error': 'Domain parameter is missing'}), 400
    cmd = f'echo "{domain}" | subfinder -silent | httpx -silent | wafw00f -j -'
    process = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
    stdout, stderr = process.communicate()
    if stderr:
        return jsonify({'error': stderr.decode('utf-8')}), 500
    return stdout.decode('utf-8')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
