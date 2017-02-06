from setuptools import setup, find_packages

setup(
    name='camisole',
    version='0.4',
    packages=find_packages(),
    url='https://bitbucket.com/prologin/camisole',
    license='GPL',
    author='serialk, zopieux',
    description='An asyncio-based source compiler and test runner.',
    install_requires=['aiohttp'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'pytest-cov'],
    test_suite='pytest',
    entry_points={
        'console_scripts': ['camisole = camisole.__main__:main'],
    },
)
