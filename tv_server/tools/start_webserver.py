import web

from tv_server import log_config
from tv_server.config.ui.url import urls, mapping

app = web.application(urls, mapping)
app.run()

