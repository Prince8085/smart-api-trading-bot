import os
import sys
import subprocess
import time

def run_command(command):
    """Run a command and print output"""
    print(f"Running: {command}")
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        shell=True
    )
    
    # Print output in real-time
    for line in process.stdout:
        print(line.strip())
    
    process.wait()
    
    if process.returncode != 0:
        print(f"Command failed with return code {process.returncode}")
        for line in process.stderr:
            print(line.strip())
        return False
    
    return True

def main():
    """Setup and run the trading bot"""
    print("=" * 50)
    print("TRADING BOT SETUP AND RUN")
    print("=" * 50)
    
    # Step 1: Install required packages
    print("\nStep 1: Installing required packages...")
    packages = [
        "flask",
        "pandas",
        "numpy",
        "requests",
        "python-dotenv",
        "smartapi-python",
        "pyotp",
        "schedule"
    ]
    
    for package in packages:
        run_command(f"pip install {package}")
    
    # Step 2: Get TOTP from user
    print("\nStep 2: Setting up TOTP for Angel One...")
    print("Angel One now requires a Time-based One-Time Password (TOTP) for authentication.")
    print("You can get this from your Angel One authenticator app.")
    
    totp = input("Enter your current TOTP from authenticator app: ")
    
    # Update .env file with TOTP
    with open('.env', 'r') as f:
        env_lines = f.readlines()
    
    # Update TOTP line
    for i, line in enumerate(env_lines):
        if line.startswith('TOTP='):
            env_lines[i] = f"TOTP={totp}\n"
            break
    
    # Write updated .env file
    with open('.env', 'w') as f:
        f.writelines(env_lines)
    
    print(f"Updated .env file with TOTP: {totp}")
    
    # Step 3: Test API connection
    print("\nStep 3: Testing connection to Angel One API...")
    
    # Update SmartAPIWrapper to use TOTP
    smart_api_wrapper_path = "app/api/smart_api_wrapper.py"
    
    # Check if file exists
    if os.path.exists(smart_api_wrapper_path):
        with open(smart_api_wrapper_path, 'r') as f:
            content = f.read()
        
        # Check if file already has TOTP support
        if "def login(self, totp=None):" not in content:
            print("Updating SmartAPIWrapper to support TOTP...")
            
            # Add import os if not present
            if "import os" not in content:
                content = content.replace(
                    "import time",
                    "import time\nimport os"
                )
            
            # Update login method
            content = content.replace(
                "def login(self):",
                "def login(self, totp=None):"
            )
            
            # Update login implementation
            content = content.replace(
                "try:\n            data = self.smart_api.generateSession(self.client_code, self.secret_key)",
                "try:\n            # Check if TOTP is provided\n            if not totp:\n                # Try to get TOTP from environment variable\n                totp = os.getenv(\"TOTP\")\n                if not totp:\n                    logger.error(\"TOTP is required for login but not provided\")\n                    return False\n            \n            # Generate session with TOTP\n            data = self.smart_api.generateSession(self.client_code, self.secret_key, totp)"
            )
            
            # Update constructor
            content = content.replace(
                "def __init__(self, api_key, secret_key, client_code):",
                "def __init__(self, api_key, secret_key, client_code, totp=None):"
            )
            
            # Update constructor implementation
            content = content.replace(
                "self.login()",
                "self.totp = totp\n        self.login(totp)"
            )
            
            # Write updated file
            with open(smart_api_wrapper_path, 'w') as f:
                f.write(content)
            
            print("SmartAPIWrapper updated successfully")
    
    # Update app.py to use TOTP
    app_py_path = "app.py"
    
    if os.path.exists(app_py_path):
        with open(app_py_path, 'r') as f:
            content = f.read()
        
        # Check if app.py already has TOTP support
        if "totp=os.getenv(\"TOTP\")" not in content:
            print("Updating app.py to use TOTP...")
            
            # Update API wrapper initialization
            content = content.replace(
                "api_wrapper = SmartAPIWrapper(\n    api_key=os.getenv(\"API_KEY\", \"9gagZWXo\"),\n    secret_key=os.getenv(\"SECRET_KEY\", \"9314923c-1ccd-4ed1-9c20-1adc1566ed35\"),\n    client_code=os.getenv(\"CLIENT_CODE\", \"angleone\")",
                "api_wrapper = SmartAPIWrapper(\n    api_key=os.getenv(\"API_KEY\", \"9gagZWXo\"),\n    secret_key=os.getenv(\"SECRET_KEY\", \"9314923c-1ccd-4ed1-9c20-1adc1566ed35\"),\n    client_code=os.getenv(\"CLIENT_CODE\", \"angleone\"),\n    totp=os.getenv(\"TOTP\")"
            )
            
            # Write updated file
            with open(app_py_path, 'w') as f:
                f.write(content)
            
            print("app.py updated successfully")
    
    # Step 4: Run the bot
    print("\nStep 4: Running the trading bot...")
    print("The bot will start in 3 seconds...")
    time.sleep(3)
    
    run_command("python app.py")

if __name__ == "__main__":
    main()