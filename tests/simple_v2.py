import requests
import shutil
import json
import sys

def download_file(url, dest):
	response = requests.get(url, stream = True)
	response.raise_for_status()
	with open(dest, 'wb') as out_file:
		shutil.copyfileobj(response.raw, out_file)

def render_latex(output_format, latex, dest_filename, host = 'http://63.142.251.124:80'):
	payload = {'code': latex, 'format': output_format}
	response = requests.post(host + '/api/v2', data = payload)
	response.raise_for_status()
	jdata = response.json()
	# Don't print the log since it's massive.
	print(jdata.get('log'))
	if 'log' in jdata:
		jdata['log'] = '...'
	print(json.dumps(jdata, indent = 4))
	if jdata['status'] == 'success':
		url = host + '/api/v2/' + jdata['filename']
		download_file(url, dest_filename)

latex = r'''
\documentclass{article}
\begin{document}
\pagenumbering{gobble}
\section{Hello, World!}
This is \LaTeX!
\end{document}
'''

if len(sys.argv) == 2:
	latex = open(sys.argv[1], encoding = 'utf-8').read()

render_latex('pdf', latex, './out.pdf', host = 'http://localhost:5000')

# render_latex('pdf', latex, './out.pdf')
