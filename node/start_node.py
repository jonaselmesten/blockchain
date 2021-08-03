from flask import Flask

from node.server.consensus import consensus_api
from node.server.peers import peers_api
from node.server.tx import tx_api
from node.server.wallet import wallet_api

app = Flask(__name__)
app.register_blueprint(tx_api)
app.register_blueprint(consensus_api)
app.register_blueprint(wallet_api)
app.register_blueprint(peers_api)

if __name__ == "__main__":
    app.run()


