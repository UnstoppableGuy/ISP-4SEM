from formatserializer.serializers.serializer_factory.factory import ObjectSerializeFactory

factory = ObjectSerializeFactory()
serialize_format = 'json'
serialize = factory.create_serializer(serialize_format)

file_from_convert = 'test.json'
test_func = serialize.load(file_from_convert)

print(test_func(15, 5))