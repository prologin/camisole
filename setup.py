import sys
from setuptools import setup, find_packages

if sys.version_info < (3, 6):
    sys.exit("camisole requires Python 3.6 or later.")

setup(
    name='camisole',
    version='1.1',
    packages=find_packages(),
    url='https://github.com/prologin/camisole',
    license='GPL',
    author='Antoine Pietri, Alexandre Macabies',
    author_email='info@prologin.org',
    description='An asyncio-based source compiler and test runner.',
    install_requires=[
        'aiohttp',
        'msgpack-python',
        'pyyaml',
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'pytest-cov', 'pytest-asyncio'],
    test_suite='pytest',
    entry_points={
        'console_scripts': ['camisole = camisole.__main__:main'],
    },
    package_data={
        'camisole': ['conf.default.yml'],
    },
)
