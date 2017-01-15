from setuptools import setup, find_packages

setup(
    name='camisole',
    version='0.3',
    packages=find_packages(),
    url='https://bitbucket.com/prologin/camisole',
    license='GPL',
    author='serialk, zopieux',
    description='An asyncio-based source compiler and test runner.',
    install_requires=['aiohttp'],
    entry_points={
        'console_scripts': ['camisole = camisole.__main__:main'],
    },
)
