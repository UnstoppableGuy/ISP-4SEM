import setuptools

setuptools.setup(
    name='lab2',
    version='2.0',
    author='Pavel Takunov',
    author_email='pavel.takynov@gmail.com',
    description='Python Simple Serializer',
    packages=setuptools.find_packages(),
    python_requires=">=3.8",
    install_requires=[
        'PyYAML==5.4.1',
        'toml==0.10.0'
    ],
)
