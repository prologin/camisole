from setuptools import setup

setup(
    name='camisole',
    version='0.2',
    packages=['camisole'],
    url='https://bitbucket.com/prologin/camisole',
    license='GPL',
    author='serialk, zopieux',
    description='An asyncio-based source compiler and test runner.',
    install_requires=['aiohttp'],
)
