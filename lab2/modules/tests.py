import unittest
import os
from modules.parsers.jsonSerializer import json_serializer
from modules.parsers.pickleSerializer import pickle_serializer
from modules.parsers.tomlSerializer import toml_serializer
from modules.parsers.yamlSerializer import yaml_serializer


t = 10


class Surname:
    surname = "Takunov"


class Name:
    name = "Pavel"

    def s(self):
        return self.name


def Sum(a, b):
    return a + t + b


name = Name()
clas = Name
func = Sum
test = Surname()
def lm(x, y): return x*y


yaml_s = yaml_serializer()
toml_s = toml_serializer()
json_s = json_serializer()
pickle_s = pickle_serializer()
path = os.getcwd()
y_path = f"{path}/config.yaml"
j_path = f"{path}/config.json"
t_path = f"{path}/config.toml"
p_path = f"{path}/config.pickle"
j_dump_str = json_s.dumps(clas)
p_dumps_str = pickle_s.dumps(clas)


class TestSerializers(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None

    def test_yaml_load(self):
        yaml_s.dump(name, y_path)
        self.assertEqual(yaml_s.load(
            f"{path}/config.yaml").__class__, name.__class__)

    def test_json_load(self):
        json_s.dump(name, j_path)
        self.assertEqual(json_s.load(
            f"{path}/config.json").__class__, name.__class__)

    def test_pickle_load(self):
        pickle_s.dump(name, p_path)
        self.assertEqual(pickle_s.load(
            f"{path}/config.pickle").__class__, name.__class__)

    def test_toml_load(self):
        toml_s.dump(name, t_path)
        self.assertEqual(toml_s.load(
            f"{path}/config.toml").__class__, name.__class__)

    def test_pickle_loads(self):
        self.assertEqual(pickle_s.loads(
            pickle_s.dumps(name)).__class__, name.__class__)

    def test_json_loads(self):
        self.assertEqual(json_s.loads(
            json_s.dumps(name)).__class__, name.__class__)

    def test_toml_loads(self):
        self.assertEqual(toml_s.loads(
            toml_s.dumps(name)).__class__, name.__class__)

    def test_yaml_loads(self):
        self.assertEqual(yaml_s.loads(
            yaml_s.dumps(name)).__class__, name.__class__)

    def test_pickle_load_function(self):
        pickle_s.dump(func, p_path)
        self.assertEqual(pickle_s.load(p_path)(2, -2), 10)

    def test_json_load_function(self):
        json_s.dump(func, j_path)
        self.assertEqual(json_s.load(j_path)(-2, 3), 11)

    def test_toml_load_function(self):
        toml_s.dump(func, t_path)
        self.assertEqual(toml_s.load(t_path)(-10, -10), -10)

    def test_yaml_load_function(self):
        yaml_s.dump(name, y_path)
        self.assertEqual(yaml_s.load(y_path).s(2, 2), 4)

    def test_pickle_loads_class(self):
        t_str = pickle_s.dumps(test)
        self.assertEqual(pickle_s.loads(t_str).surname, "Takunov")

    def test_yaml_loads_class(self):
        t_str = yaml_s.dumps(test)
        self.assertEqual(yaml_s.loads(t_str).surname, "Takunov")

    def test_toml_loads_class(self):
        t_str = toml_s.dumps(test)
        self.assertEqual(toml_s.loads(t_str).surname, "Takunov")

    def test_jtest_son_loads_class(self):
        t_str = json_s.dumps(test)
        self.assertEqual(json_s.loads(t_str).surname, "Takunov")

    def test_lamda_load(self):
        self.assertEqual(json_s.load(j_path)(5, 10), 50)

    def test_dumps_lamda(self):
        lam = json_s.load(j_path)
        self.assertEqual(lam.__class__, lm.__class__)

    def test_json_dumps(self):
        self.assertEqual(json_s.dumps(clas), j_dump_str)

    def test_pickle_dump(self):
        self.assertEqual(pickle_s.dumps(clas), p_dumps_str)
