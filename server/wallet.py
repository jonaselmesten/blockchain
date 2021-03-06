import json

from flask import request, Blueprint

from server.node import blockchain
from util.hash_util import apply_sha256
from util.serialize import JsonSerializable

wallet_api = Blueprint("wallet_api", __name__, template_folder="server")


@wallet_api.route('/wallet_balance', methods=['GET'])
def get_balance():
    total = 0
    public_key = apply_sha256(request.args.get("public_key"))
    utxo = []

    # Add all UTXO
    for tx_output in blockchain.unspent_tx:
        if tx_output.receiver == public_key:
            total += tx_output.amount
            utxo.append(tx_output)

    return json.dumps({"balance": total,
                       "utxo": utxo},
                      default=JsonSerializable.dumper,
                      indent=4)
