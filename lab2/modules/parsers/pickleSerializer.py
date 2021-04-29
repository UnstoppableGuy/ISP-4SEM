import pickle

from modules.parsers.serializer import object_serializer


class pickle_serializer(object_serializer):

    def dump(self, obj, file_path):
        data = super().obj_dic(obj)
        with open(file_path, "wb") as file:
            pickle.dump(data, file)

    def dumps(self, obj):
        return pickle.dumps(super().obj_dic(obj))

    def loads(self, s):
        return super().dic_type(pickle.loads(s))

    def load(self, file_path):
        with open(file_path, "rb") as file:
            data = pickle.load(file)
        return super().dic_type(data)
