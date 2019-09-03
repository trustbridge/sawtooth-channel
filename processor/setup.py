from __future__ import print_function

import os
import subprocess

from setuptools import setup, find_packages

conf_dir = "/etc/sawtooth"

# FIXME: xo! can we delete this anyhow
data_files = [
    (conf_dir, ['packaging/xo.toml.example'])
]

if os.path.exists("/etc/default"):
    data_files.append(
        ('/etc/default', ['packaging/systemd/sawtooth-coo-tp-python']))

if os.path.exists("/lib/systemd/system"):
    data_files.append(('/lib/systemd/system',
                       ['packaging/systemd/sawtooth-coo-tp-python.service']))

# FIXME: bin/get_version is too gaflumpy.
# Something like this would be better:
# https://github.com/paparazzi/paparazzi/blob/master/paparazzi_version
setup(
    name='sawtooth-coo',
    version=subprocess.check_output(
        ['../bin/get_version']).decode('utf-8').strip(),
    description='Sawtooth Channel for G2G messaging, '
    'using a Discrete Generic Message protocol',
    author='Commonwealth Of Australia',
    url='https://github.com/trustbridge/sawtooth-channel-dgm-tp',
    packages=find_packages(),
    install_requires=[
        'aiohttp',
        'colorlog',
        'protobuf',
        'sawtooth-sdk',
        'sawtooth-signing',
        'PyYAML',
    ],
    data_files=data_files,
    entry_points={
        'console_scripts': [
            'coo-tp-python = sawtooth_coo.processor.main:main',
        ]
    })
