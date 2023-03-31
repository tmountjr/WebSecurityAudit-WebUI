from os.path import isfile
from flask_cors import CORS
from flask import Flask, request
from urllib.parse import urlparse
from subprocess import Popen, PIPE, STDOUT
import os
import re

app = Flask(__name__)
CORS(app)

def execute(cmdstring, _stdout=PIPE, _stderr=PIPE):
    process = Popen(cmdstring, stdout=_stdout, stderr=_stderr, shell=True)
    resStdout, resStderr = process.communicate()
    if resStderr:
        return {"error": resStderr.decode('utf-8')}, 500
    else:
        return True
    
def serialize(location_string):
    serialized = re.sub(
        pattern=' \[(.*)\]\n$',
        string=location_string,
        repl=',\\1')
    (fromUrl, toUrl) = tuple(serialized.split(','))
    return {'from': fromUrl, 'to': toUrl}

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
        return {"error": "Domain parameter is missing"}, 400
    
    cmd1 = f'echo "{domain}" | subfinder -silent > "{domain}"-list.txt'
    cmd1_result = execute(cmd1)
    if type(cmd1_result) != bool:
        return cmd1_result
    
    # Find out which domains return 200
    active_filename = f"{domain}-list-active.txt"
    cmd2 = f'httpx -l "{domain}"-list.txt -silent -mc=200 > "{active_filename}"'
    cmd2_result = execute(cmd2)
    if type(cmd2_result) != bool:
        return cmd2_result

    # Need to do some postprocessing with the redirects to make sure that we
    # include any that redirect to the same domain, eg '' => '/' or '' => '/foo.html'
    cmd3 = f'httpx -l "{domain}"-list.txt -silent -mc=301,302 -location -nc'
    with Popen(['/bin/sh', '-c', cmd3], stdout=PIPE, stderr=STDOUT, universal_newlines=True) as p:
        redirects = [ serialize(x) for x in p.stdout.readlines() ]
        redirect_from_domains = [ urlparse(x['from']).netloc for x in redirects ]

        # Now we need to parse each entry in redirects.
        #   1. If the 'to' entry starts with a '/', then add 'from' to the list of active domains.
        #   2. If the 'to' entry starts with 'https?://', parse it, get the netloc value, and see if it matches something in the redirect list. If so, add it.

        to_write = set()

        for redirect in redirects:
            if redirect['to'].startswith('/'):
                to_write.add(redirect['from'])
            elif re.search('^https?://', redirect['to']):
                parsed_to = urlparse(redirect['to'])
                if parsed_to.netloc in redirect_from_domains:
                    to_write.add(redirect['from'])
            # Don't care if it wasn't in the redirect list - if it's already in the active list, great; if not, then it
            # may be redirecting somewhere completely different.

        # Push the extra domains into the active list.
        live_domains_file = open(active_filename, 'a')
        for x in to_write:
            live_domains_file.write(x + '\n')

        live_domains_file.close()

    cmd4 = f'wafw00f -i "{active_filename}" -o "{domain}"-audit.json'
    cmd4_result = execute(cmdstring=cmd4, _stderr=STDOUT)
    # We don't necessarily want to return errors here. if we've gotten this far we should wrap up the errors and return the json.
    if type(cmd4_result) != bool:
        if not isfile(f"{domain}-audit.json"):
            return cmd4_result
    
    # Read and return the audit file
    to_return = open(f"{domain}-audit.json", 'r').read()

    # For now don't clean up any files. May add this later.
    return to_return

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
