import requests

def gh_headers(token):
    return {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json"
    }

def create_repo(token, name):
    r = requests.post(
        "https://api.github.com/user/repos",
        headers=gh_headers(token),
        json={"name": name}
    )
    return r.status_code == 201, r.text

def list_repos(token):
    r = requests.get(
        "https://api.github.com/user/repos",
        headers={"Authorization": f"token {token}"}
    )
    data = r.json()
    return [{"name": repo["name"], "url": repo["html_url"]} for repo in data]
