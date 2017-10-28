import os
import jinja2
import aiohttp
import aiohttp.web
import asyncio
import aiohttp_jinja2
import logs


loop = asyncio.get_event_loop()
app = aiohttp.web.Application(loop = loop)
app.router.add_static('/static', './static')
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
app.router.add_get('/docs/python', static_template('docs/python.html'))
app.router.add_get('/contact', static_template('contact.html'))


import api2
app.router.add_get('/api/v2/{filename}', api2.get)
app.router.add_post('/api/v2', api2.post)


if __name__ == '__main__':
    logs.info('Starting server...')
    port = int(os.getenv('PORT', '5000'))
    aiohttp.web.run_app(app, host = '0.0.0.0', port = port)
