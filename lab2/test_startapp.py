from formatserializer.serializers.serializer_factory.factory import ObjectSerializeFactory

class MyClass:

    def __init__(self, test, lol, kek):
        self.test = test
        self.lol = lol
        self.kek = kek

    @staticmethod
    def my_class_func(a, b, c):
        return sum((a, b, c)) - (a * b * c)

    def my_class_func_2(self):
        return self.lol + self.kek


def my_func(a, b):
    return (a * b) ** 2


my_list = [i for i in range(10)]

my_set = {i for i in range(5)}

my_dict = {i: i ** 2 for i in range(7)}

my_var = 'Hello'


factory = ObjectSerializeFactory()
serialize_format = 'json'
serialize = factory.create_serializer(serialize_format)
obj = serialize.dumps(MyClass)




'''
serialize.dump(obj, 'class.json')


classA = 'class.json'
deserialized_lambda = serialize.load(classA)
'''

file_from_convert = 'test.json'
test_func = serialize.load(file_from_convert)

print(test_func(15, 5))