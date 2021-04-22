import yaml

from parsers.serializer import object_serializer


class yaml_serializer(object_serializer):

    def dump(self, obj, file_path):
        data = super().obj_dic(obj)
        with open(file_path, "w") as file:
            yaml.dump(data, file)

    def dumps(self, obj):
        return yaml.dump(super().obj_dic(obj))

    def loads(self, s):
        return super().dic_type(yaml.load(s, Loader=yaml.FullLoader))

    def load(self, file_path):
        with open(file_path, "r") as file:
            data = yaml.load(file, Loader=yaml.FullLoader)
        return super().dic_type(data)
