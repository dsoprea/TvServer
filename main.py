import web

from config import urls, mapping

if __name__ == "__main__":
    app = web.application(urls, mapping)
    app.run()

