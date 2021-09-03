import yaml

from unittest import TestCase
from parameterized import parameterized

from formatserializer.services.service_yaml.service import YamlService
from formatserializer.testing.services.service_abstract_base.service import (
    ExampleClass, example_function
)
from formatserializer.testing.services.service_json.service import (
    expected_dict_int, expected_dict_class, expected_dict_function
)


class YamlServiceTestCase(TestCase):
    def setUp(self) -> None:
        self.service = YamlService

    def test__serialize_data__success(self):
        actual_result = yaml.load(self.service.serialize_data(example_function),  Loader=yaml.Loader)
        expected_result = yaml.load(yaml.dump(expected_dict_function), Loader=yaml.Loader)

        self.assertEqual(actual_result.keys(), expected_result.keys())

        self.assertEqual(actual_result.get('base64'), expected_result.get('base64'))
        self.assertEqual(actual_result.get('name'), expected_result.get('name'))
        self.assertEqual(actual_result.get('type'), expected_result.get('type'))
        self.assertEqual(actual_result.get('serializable_by_default'), expected_result.get('serializable_by_default'))

        self.assertListEqual(actual_result.get('code'), expected_result.get('code'))

    @parameterized.expand([
        ("object_int_123", expected_dict_int, 123),
        ("object_int_class", expected_dict_class, ExampleClass),
        ("object_int_function", expected_dict_function, example_function),
    ])
    def test__deserialize_data__success(self, _, serialize_base64, expected_result):
        actual_result = self.service.deserialize_data(serialize_base64)

        self.assertEqual(actual_result, expected_result)
