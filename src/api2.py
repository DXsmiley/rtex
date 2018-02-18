import os
import json
import string
import re
import aiohttp
import logs
import stats

import jobs
from random_string import random_string

async def post(request):
    # print(await request.text())
    req = (await request.post()) or (await request.json())
    code = req.get('code')
    output_format = req.get('format').lower()
    client_name = req.get('client_name', 'unnamed')
    if not isinstance(code, str) or not isinstance(output_format, str):
        raise aiohttp.web.json_response({'error': 'bad input formats'}) 
    if output_format not in ('pdf', 'png', 'jpg'):
        return aiohttp.web.json_response({'error': 'invalid output format'}) 
    job_id = random_string(64)
    logs.info('Job {} started'.format(job_id))
    reply = await jobs.render_latex(job_id, output_format, code)
    if reply['status'] == 'success':
        reply['filename'] = job_id + '.' + output_format
        logs.info('Job success : {}'.format(job_id))
        stats.track_event('api2', 'success', client=client_name)
    else:
        logs.info('Job failed : {}'.format(job_id))
        stats.track_event('api2', 'failure', client=client_name)
    return aiohttp.web.json_response(reply)

async def get(request):
    filename = request.match_info['filename']
    if not re.match(r'^[A-Za-z0-9]{64}\.(pdf|png|pdf)$', filename):
        logs.info('{} not found'.format(filename))
        raise aiohttp.web.HTTPBadRequest
    path = './temp/' + filename.replace('.', '/a.')
    if not os.path.isfile(path):
        raise aiohttp.web.HTTPNotFound
    return aiohttp.web.FileResponse(path)
