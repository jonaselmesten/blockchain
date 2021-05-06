import json


class JsonSerializable(object):

    def serialize(self):
        return json.dumps(self.__dict__, indent=4)

    def __repr__(self):
        return self.serialize()

    @staticmethod
    def dumper(obj):
        if "serialize" in dir(obj):
            return obj.serialize()

        return obj.__dict__