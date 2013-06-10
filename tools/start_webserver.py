import web

import log_config

from config.ui.url import urls, mapping

app = web.application(urls, mapping)
app.run()

