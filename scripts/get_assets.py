import requests

# Define the GitHub repository URL
repo_url = "https://github.com/Pixel-Fondue/modo-kit-central"

# Extract the owner and repo name from the URL
owner_repo = repo_url.split("github.com/")[1]

# Define the GitHub API URL for the latest release
api_url = f"https://api.github.com/repos/{owner_repo}/releases/latest"
api_path = "https://api.github.com/repos/Pixel-Fondue/modo-kit-central/releases/latest"
# Send a GET request to the GitHub API URL
response = requests.get(api_url)

# Check if the request was successful
if response.status_code == 200:
    # Parse the JSON response
    release_data = response.json()

    # Get the assets of the latest release
    assets = release_data.get("assets", [])

    # Print the assets' download URLs
    for asset in assets:
        print(asset["browser_download_url"])
else:
    print(f"Failed to fetch the latest release: {response.status_code}")
