from json import JSONEncoder

from block import Block


class BlockEncoder(JSONEncoder):

    def default(self, o):
        if isinstance(o, Block):
            return

