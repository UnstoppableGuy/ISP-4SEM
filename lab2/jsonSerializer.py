import json

from serializer import object_serializer


class json_serializer(object_serializer):

    def dump(self, obj, file_path):
        data = super().obj_dic(obj)
        with open(file_path, "w") as file:
            file.write(save_object_to_json(data))

    def dumps(self, obj):
        return save_object_to_json(super().obj_dic(obj))

    def loads(self, obj):
        return super().dic_type(json.loads(obj))

    def load(self, file_path):
        with open(file_path, "r") as file:
            dic = json.load(file)
        return super().dic_type(dic)


def save_object_to_json(dic):
    object = "{"
    for key in dic:
        if isinstance(dic[key], dict):
            temp = save_object_to_json(dic[key])
            object += "\"" + key + "\"" + ": " + temp + ", "
            continue
        elif isinstance(dic[key], list):
            object += "\"" + key + "\"" + ": ["
            for i in range(len(dic[key])):
                if isinstance(dic[key][i], str):
                    object += "\"" + dic[key][i] + "\", "
            if object.endswith(", "):
                object = object[:len(object) - 2] + "], "
            else:
                object += "] ,"
        else:
            if isinstance(dic[key], str):
                object += "\"" + key + "\"" + ": " + \
                    "\"" + dic[key] + "\"" + ", "
    if object.endswith(", "):
        object = object[:(len(object) - 2)] + "}"
    else:
        object += "}"
    return object



