from setuptools import find_packages, setup


setup(
    name="LR2",
    version="2.4",
    packages=find_packages(include=['modules', 'modules.*']),
    entry_points={
        'console_scripts': [
            'parser=modules.main:main',
        ],
    },
    install_requires=[
        'coverage==5.5',
        'entrypoints==0.3',
        'py==1.10.0',
        'pytest==6.2.3',
        'pytest-cov==2.11.1',
        'PyYAML==5.4.1',
        'simplejson==3.16.0',
        'toml==0.10.2',
        'virtualenv==20.0.17',
    ]
)
