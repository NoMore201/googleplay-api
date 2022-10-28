from setuptools import setup
from setuptools.command.build_py import build_py as _build


import os.path
import subprocess
import shutil

PROTOC_EXEC = "protoc"

CURRENT_DIR = os.path.abspath( os.path.dirname( __file__ ) )

class ProtobufBuilder(_build):

    def run(self):
        # check if protobuf is installed
        exec_path = shutil.which(PROTOC_EXEC)
        if exec_path is None:
            raise Exception("You should install protobuf compiler")

        print("Building protobuf file")
        subprocess.run([exec_path,
            "--proto_path=" + CURRENT_DIR,
            "--python_out=" + CURRENT_DIR + "/gpapi/",
            CURRENT_DIR + "/googleplay.proto"])
        super().run()

setup(name='ak-gpapi',
      version='0.4.4-post2',
      description='Unofficial python api for google play',
      url='https://github.com/appknox/googleplay-api',
      author='appknox',
      author_email='engineering@appknox.com',
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
