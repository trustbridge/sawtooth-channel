from setuptools import setup, find_packages

setup(
    name='sawtooth_channel_dgm_tp',
    version='0.0.1',
    url='https://github.com/trustbridge/sawtooth-channel-dgm-tp',
    author='Chris Gough',
    author_email='chris.gough@omg.management',
    description='Sawtooth Transacton Processor for a G2G Channel implementing the Discrete Generic Message protocol',
    packages=find_packages(),
    install_requires=[
        'py-cid == 0.2.1',
        'multihash == 0.1.1',
        'pycountry'
    ],
)
