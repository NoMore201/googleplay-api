from setuptools import setup
from setuptools.command.build_py import build_py as _build


import os.path
import subprocess

PROTOC_BIN = "/usr/bin/protoc"

CURRENT_DIR = os.path.abspath( os.path.dirname( __file__ ) )

class ProtobufBuilder(_build):

    def run(self):
        # check if protobuf is installed
        if not os.path.isfile(PROTOC_BIN):
            raise Exception("You should install protobuf compiler")

        print("Building protobuf file")
        subprocess.run([PROTOC_BIN,
            "--proto_path=" + CURRENT_DIR,
            "--python_out=" + CURRENT_DIR + "/gpapi/",
            "googleplay.proto"])
        super().run()

setup(name='gpapi',
      version='0.4.3',
      description='Unofficial python api for google play',
      url='https://github.com/NoMore201/googleplay-api',
      author='NoMore201',
      author_email='domenico.iezzi.201@gmail.com',
      license='GPL3',
      packages=['gpapi'],
      package_data={
          'gpapi': [
              'config.py'
              'device.properties',
              'googleplay_pb2.py',
              'googleplay.py',
              'utils.py'
          ]},
      include_package_data=True,
      cmdclass={'build_py': ProtobufBuilder},
      install_requires=['cryptography>=2.2',
                        'protobuf>=3.5.2',
                        'requests'])
