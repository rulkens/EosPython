from setuptools import setup, find_packages

setup(
    name = "EOS",
    version = "0.1",
    packages = find_packages(),

    author = "Alexander Rulkens",
    author_email = "alex@studioludens.com",
    description = "Python library for controlling the EOS light.",

    entry_points={
        'console_scripts': [
            'eos-httpd = eos.server.http:main',
            'eos-wsd = eos.server.ws:main',
         ],
    },
)