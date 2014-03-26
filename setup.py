from setuptools import setup

setup(
    name = "open511_api_tests",
    version = "0.1",
    url='',
    license = "",
    packages = [
        'open511_api_tests',
    ],
    install_requires = [
        'lxml>=2.3',
        'requests>=1.2.0',
        'open511>=0.2'
    ]
)
