import os
import requests
import pandas as pd
from dotenv import load_dotenv

# Load the GitHub token from .env file
load_dotenv()
github_token = os.getenv("GITHUB_TOKEN")
headers = {
    "Authorization": f"token {github_token}"
}

# Fetch users function
def fetch_users(location="Seattle", followers=">200"):
    users = []
    page = 1
    while True:
        url = "https://api.github.com/search/users"
        params = {
            "q": f"location:{location} followers:{followers}",
            "per_page": 30,
            "page": page
        }
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        
        # Debugging print to see if users are fetched
        print("Fetched users:", data)  # Optional

        if "items" not in data or not data["items"]:
            break

        users.extend(data["items"])
        page += 1
    return users

# Fetch repositories function
def fetch_repositories(username):
    repos = []
    page = 1
    while page <= 5:  # Limit to 500 repositories
        url = f"https://api.github.com/users/{username}/repos"
        params = {"sort": "pushed", "direction": "desc", "per_page": 100, "page": page}
        response = requests.get(url, headers=headers, params=params)
        repo_data = response.json()
        
        if not repo_data:
            break
        
        repos.extend(repo_data)
        page += 1
    return repos

# Helper function to clean up the company name
def clean_company_name(company):
    if company:
        return company.strip().lstrip("@").upper()
    return ""

# Function to save users to CSV
def save_users_to_csv(users):
    user_data = []
    for user in users:
        user_data.append({
            "login": user.get("login"),
            "name": user.get("name", ""),
            "company": clean_company_name(user.get("company", "")),
            "location": user.get("location", ""),
            "email": user.get("email", ""),
            "hireable": user.get("hireable", ""),
            "bio": user.get("bio", ""),
            "public_repos": user.get("public_repos", 0),
            "followers": user.get("followers", 0),
            "following": user.get("following", 0),
            "created_at": user.get("created_at", "")
        })
    df = pd.DataFrame(user_data)
    df.to_csv("users.csv", index=False)

# Function to save repositories to CSV
def save_repositories_to_csv(repositories):
    repo_data = []
    for repo in repositories:
        repo_data.append({
            "login": repo["owner"]["login"],
            "full_name": repo["full_name"],
            "created_at": repo["created_at"],
            "stargazers_count": repo["stargazers_count"],
            "watchers_count": repo["watchers_count"],
            "language": repo["language"] if repo["language"] else "",
            "has_projects": repo["has_projects"],
            "has_wiki": repo["has_wiki"],
            "license_name": repo["license"]["key"] if repo["license"] else ""
        })
    df = pd.DataFrame(repo_data)
    df.to_csv("repositories.csv", index=False)

# Main script execution
if __name__ == "__main__":
    # Fetch users from Seattle with over 200 followers
    users = fetch_users()
    print(f"Number of users fetched: {len(users)}")  # Optional for debugging

    save_users_to_csv(users)

    # Fetch repositories for each user and save to CSV
    all_repositories = []
    for user in users:
        repos = fetch_repositories(user['login'])
        all_repositories.extend(repos)

    save_repositories_to_csv(all_repositories)
