import os
import sys
import jinja2
import aiohttp
import aiohttp.web
import asyncio
import aiohttp_jinja2
import logs
import stats
import time
import shutil
import traceback
import aiohttp_cors


loop = asyncio.get_event_loop()
app = aiohttp.web.Application(loop = loop)
cors = aiohttp_cors.setup(app)
app.router.add_static('/static', './static')
app.router.add_get('/favicon.ico',
    lambda r : aiohttp.web.HTTPSeeOther('./static/favicon.png')
)
aiohttp_jinja2.setup(app,
    loader = jinja2.FileSystemLoader('./templates/'))


def static_template(filepath):
    @aiohttp_jinja2.template(filepath)
    async def internal(request):
        return {}
    return internal


app.router.add_get('/', static_template('index.html'))
app.router.add_get('/pricing', static_template('pricing.html'))
app.router.add_get('/docs', static_template('docs.html'))
app.router.add_get('/contact', static_template('contact.html'))

@aiohttp_jinja2.template('stats.html')
async def page_stats(request):
    suc = stats.get_column('success')
    fal = stats.get_column('failure')
    return {
        'max_usage': max(s + f for s, f in zip(suc, fal)),
        'stats': [
            {
                'day': d + 1,
                'usage': s + f,
                'success': s
            }
            for d, s, f in zip(range(100), suc, fal)
        ]
    }
app.router.add_get('/stats', page_stats)


async def delete_old_files():
    try:
        await asyncio.sleep(3)
        while True:
            for i in os.listdir('./temp/'):
                p = './temp/' + i
                if not os.path.isfile(p):
                    age = time.time() - os.stat(p).st_mtime
                    if age > 60 * 60 * 2: # 2 hours
                        logs.info('Removing {}'.format(i))
                        shutil.rmtree(p)
                await asyncio.sleep(1)
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        pass


@app.on_startup.append
async def start_background_tasks(app):
    app['background_tasks'] = list(map(app.loop.create_task, [
        delete_old_files()
    ]))


@app.on_cleanup.append
async def cleanup_background_tasks(app):
    for i in app['background_tasks']:
        i.cancel()
    for i in app['background_tasks']:
        await i


import api2

allow_from_all_origins = {
    '*': aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers='*',
            allow_headers='*',
        )
}

cors.add(app.router.add_get('/api/v2/{filename}', api2.get), allow_from_all_origins)
cors.add(app.router.add_post('/api/v2', api2.post), allow_from_all_origins)


if __name__ == '__main__':
    logs.info('Starting server...')
    if len(sys.argv) >= 2:
        port = int(sys.argv[1])
    else:
        port = int(os.getenv('PORT', '5000'))
    aiohttp.web.run_app(app, host = '0.0.0.0', port = port)
