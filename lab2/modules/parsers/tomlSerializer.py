import toml

from modules.parsers.serializer import object_serializer


class toml_serializer(object_serializer):

    def dump(self, obj, file_path):
        data = super().obj_dic(obj)
        with open(file_path, "w") as file:
            toml.dump(data, file)

    def dumps(self, obj):
        return toml.dumps(super().obj_dic(obj))

    def loads(self, s):
        return super().dic_type(toml.loads(s))

    def load(self, file_path):
        with open(file_path, "r") as file:
            data = toml.load(file)
        return super().dic_type(data)
