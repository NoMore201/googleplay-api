import site
import subprocess

build_dir = f"builds"
pyinstaller = ("venv\\Scripts\\pyinstaller.exe")

# Stores Google API resource to be bundled as PyInstaller doesn't hook it automatically
# NOTE: Update this if the API version changes
print("Storing Google API resource...")
site_packages = site.getsitepackages()
google_api = "google_api_python_client-1.12.3.dist-info"
google_api_path = f"{site_packages[1]}\\{google_api}"
print("Complete!")

# Calls the pyinstaller exe with the following arguments:
# dist, build, and spec are all saved to the build_dir
# Adds Google API as declared above and device properties
# Lastly tells which script to compile
subprocess.call(
[pyinstaller, 
"--distpath", f"{build_dir}/dist", 
"--workpath", f"{build_dir}/build", 
"--specpath", f"{build_dir}/build", 
"-F",
"--add-data", f"{google_api_path};{google_api}",
"--add-data", "../../login.json;.",
"--add-data", "../../gpapi/device.properties;gpapi",
"-n", f"Google API Test", 
"example.py"]
)