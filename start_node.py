from flask import Flask

from server.wallet import call_api

app = Flask(__name__)
app.register_blueprint(call_api)

if __name__ == "__main__":
    app.run()


