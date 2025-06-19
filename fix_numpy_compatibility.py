import subprocess
import sys

def run_command(command):
    print(f"Running: {command}")
    process = subprocess.run(command, shell=True, check=False)
    if process.returncode != 0:
        print(f"Command failed with return code {process.returncode}")
    return process.returncode == 0

# Uninstall packages that might be causing conflicts
packages_to_uninstall = [
    "numpy",
    "pandas",
    "scikit-learn",
    "tensorflow-cpu",
    "smartapi-python"
]

for package in packages_to_uninstall:
    run_command(f"{sys.executable} -m pip uninstall -y {package}")

# Install packages in the correct order
run_command(f"{sys.executable} -m pip install numpy==1.22.4")  # Using an older version that's more compatible
run_command(f"{sys.executable} -m pip install pandas==1.3.3")
run_command(f"{sys.executable} -m pip install scikit-learn==1.0.2")  # Using an older version that's more compatible
run_command(f"{sys.executable} -m pip install tensorflow-cpu==2.9.0")  # Using an older version that's more compatible
run_command(f"{sys.executable} -m pip install smartapi-python==1.5.5")

# Try to install TA-Lib from the wheel file
run_command(f"{sys.executable} -m pip install ta_lib-0.6.3-cp39-cp39-win_amd64.whl")

print("\nPackages reinstalled. Please try running your application again.")