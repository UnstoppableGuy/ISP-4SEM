from modules.parsers.jsonSerializer import json_serializer
from modules.parsers.pickleSerializer import pickle_serializer
from modules.parsers.tomlSerializer import toml_serializer
from modules.parsers.yamlSerializer import yaml_serializer
from modules.consoleApp import parser_build, read_from_config


def choose_serializer(input_format, output_format):
    if input_format.endswith(".json"):
        deserializer = json_serializer()
    elif input_format.endswith(".pickle"):
        deserializer = pickle_serializer()
    elif input_format.endswith(".toml"):
        deserializer = toml_serializer()
    elif input_format.endswith(".yaml"):
        deserializer = yaml_serializer()
    else:
        raise Exception("Invalid format!")

    if output_format == "json":
        serializer = json_serializer()
    elif output_format == "pickle":
        serializer = pickle_serializer()
    elif output_format == "toml":
        serializer = toml_serializer()
    elif output_format == "yaml":
        serializer = yaml_serializer()
    else:
        raise Exception("Invalid format!")
    return serializer, deserializer


"""
class Person:
    # конструктор
    def __init__(self, name):
        self.name = name  # устанавливаем имя
 
    def __del__(self):
        print(self.name,"удален из памяти")
    def display_info(self):
        print("Привет, меня зовут", self.name)
 """


def main():
    # json = json_serializer()
    # path = os.getcwd()
    # json.dump(Person("Tom"),f'{path}/file.json')
    parser = parser_build()
    my_namespace = parser.parse_args()
    if not my_namespace.config:
        serializer, deserializer = choose_serializer(my_namespace.input_file, my_namespace.output_format)
        obj = deserializer.load(my_namespace.input_file)
        serializer.dump(obj, my_namespace.output_file)
    else:
        config = read_from_config(my_namespace.config)
        serializer, deserializer = choose_serializer(config['input_file'], config['output_format'])
        obj = deserializer.load(config['input_file'])
        serializer.dump(obj, config['output_file'])


if __name__ == "__main__":
    main()
