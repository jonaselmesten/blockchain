from Block import Block
from Blockchain import Blockchain

blockchain = Blockchain()

def add_block():
    block = Block("fetto", blockchain.get_last_block().compute_hash())
    block.mine_block()
    blockchain.add_block(block)

add_block()
add_block()
add_block()
blockchain.is_chain_valid()



