from setuptools import setup

setup(name='rwgpapi',
      version='0.1',
      description='A fork of https://github.com/NoMore201/googleplay-api with some enhancements.',
      url='https://github.com/rehmatworks/googleplay-api',
      author='Rehmat',
      author_email='contact@rehmat.works',
      license='GPL3',
      packages=['gpapi'],
      package_data={'gpapi': ['device.properties']},
      install_requires=['pycryptodome',
                        'protobuf>=3.5.2',
                        'requests'])
