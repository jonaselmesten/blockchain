from flask import Flask

from server.consensus import consensus_api
from server.peers import peers_api
from server.tx import tx_api
from server.wallet import wallet_api

app = Flask(__name__)
app.register_blueprint(tx_api)
app.register_blueprint(consensus_api)
app.register_blueprint(wallet_api)
app.register_blueprint(peers_api)

if __name__ == "__main__":
    app.run()


