from setuptools import setup

setup(name='gpapi',
      version='0.4.3',
      description='Unofficial python api for google play',
      url='https://github.com/NoMore201/googleplay-api',
      author='NoMore201',
      author_email='domenico.iezzi.201@gmail.com',
      license='GPL3',
      packages=['gpapi'],
      package_data={'gpapi': ['device.properties']},
      install_requires=['cryptography>=2.2',
                        'protobuf>=3.5.2',
                        'requests'])
