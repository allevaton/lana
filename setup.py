from setuptools import find_packages, setup

setup(
    name='lana',
    version='2.0',
    packages=find_packages(),
    url='http://www.github.com/allevaton/lana',
    license='GNU GPLv2',
    author='Nick Allevato',
    author_email='nicholas.allevato@gmail.com',
    description='',
    install_requires=['requests>=2.7', 'beautifulsoup4>=4.3']
)
