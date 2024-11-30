import json
import sys
import os

def update_proxies():
    # Print synopsis and description
    print(f"Synopsis:")
    print(f"    Replaces or adds proxies in accounts.json from a proxies.txt file\n")
    print(f"Description:")
    print(f"    - Reads accounts from accounts.json")
    print(f"    - Reads proxies from proxies.txt")
    print(f"    - Replaces existing proxies or adds new ones")
    print(f"    - Writes the updated accounts back to accounts.json")
    print(f"    - Expects proxies to be in the format IP:PORT:USERNAME:PASSWORD or IP:PORT or a mix and on separate lines")
    print(f"    - This script needs to be in the same folder as accounts.json and proxies.txt")
    print(f"    - Or you can run this script with a batch/bash script and define ACCOUNTS_PATH and PROXIES_PATH as variables\n")

    # Ask for user confirmation
    while True:
        user_input = input("Do you want to run this script? (Yes/Y or No/N): ").strip().lower()
        
        if user_input in ['yes', 'y']:
            break
        elif user_input in ['no', 'n']:
            print(f"Script execution cancelled.")
            sys.exit(0)
        else:
            print(f"Invalid input. Please enter Yes/Y or No/N.")

    try:
        # Use os.path to handle file paths flexibly
        script_dir = os.path.dirname(os.path.abspath(__file__))
        accounts_path = os.getenv('ACCOUNTS_PATH', os.path.join(script_dir, 'accounts.json'))
        proxies_path = os.getenv('PROXIES_PATH', os.path.join(script_dir, 'proxies.txt'))

        # Read the accounts JSON
        with open(accounts_path, 'r') as f:
            accounts_json = json.load(f)

        # Read the proxies from the text file
        with open(proxies_path, 'r') as f:
            proxies = f.read().splitlines()

        # Check if we have enough proxies
        if len(proxies) < len(accounts_json):
            raise ValueError(f"Not enough proxies in proxies.txt. Need at least {len(accounts_json)} proxies.")

        # Iterate through accounts and update/add proxies
        for i in range(len(accounts_json)):
            # Split the proxy line into components
            proxy_parts = proxies[i].strip().split(':')
            
            # Validate proxy format
            if len(proxy_parts) < 2:
                raise ValueError(f"Invalid proxy format at line {i + 1}: {proxies[i]}. Expected at least IP:PORT")

            # Construct the proxy string based on the number of parts
            if len(proxy_parts) == 4:
                # If 4 parts, use IP:PORT:USERNAME:PASSWORD format
                proxy_string = f"socks5://{proxy_parts[2]}:{proxy_parts[3]}@{proxy_parts[0]}:{proxy_parts[1]}"
            else:
                # If 2 parts, use simple IP:PORT format
                proxy_string = f"socks5://{proxy_parts[0]}:{proxy_parts[1]}"
            
            # Update the proxy in the account
            accounts_json[i]['proxy'] = proxy_string

        # Convert back to JSON and save
        with open(accounts_path, 'w') as f:
            json.dump(accounts_json, f, indent=2)

        print(f"Proxies successfully updated in accounts.json")

    except FileNotFoundError as e:
        print(f"File not found: {e}")
        sys.exit(1)
    except PermissionError:
        print(f"Permission denied. Check file permissions.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        input("Press Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    update_proxies()
