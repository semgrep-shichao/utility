import requests
from datetime import datetime, timedelta

# === CONFIG ===
TOKEN = 'ATCTT3xFfGN0_xvupNK3VD-Glb4gaWCAUmMQt5y2dH2Xk4IJaot6Btz71aJy4N8Atp0v8lRxxvyUoayaJaE0GHXsLvepO-'
WORKSPACE = 'semgrep-ci'
BASE_URL = 'https://api.bitbucket.org/2.0'
DAYS = 30

HEADERS = {
    "Authorization": f"Bearer {TOKEN}"
}

# === LOGIC ===

def get_repos(workspace):
    repos = []
    url = f"{BASE_URL}/repositories/{workspace}"
    while url:
        res = requests.get(url, headers=HEADERS)
        res.raise_for_status()
        data = res.json()
        repos.extend([repo['slug'] for repo in data['values']])
        url = data.get('next')
    return repos

def get_committers(workspace, repo_slug, since_date):
    committers = set()
    url = f"{BASE_URL}/repositories/{workspace}/{repo_slug}/commits"
    while url:
        res = requests.get(url, headers=HEADERS)
        res.raise_for_status()
        data = res.json()
        for commit in data['values']:
            date_str = commit['date'] if 'date' in commit else commit['committer']['date']
            commit_date = datetime.strptime(date_str[:19], "%Y-%m-%dT%H:%M:%S")
            if commit_date < since_date:
                return committers
            author_raw = commit.get('author', {}).get('raw', '')
            if author_raw:
                committers.add(author_raw)
        url = data.get('next')
    return committers

def main():
    since_date = datetime.utcnow() - timedelta(days=DAYS)
    repos = get_repos(WORKSPACE)
    all_committers = set()

    for repo in repos:
        print(f"Checking repo: {repo}")
        committers = get_committers(WORKSPACE, repo, since_date)
        all_committers.update(committers)

    print(f"\nTotal unique committers in the last {DAYS} days: {len(all_committers)}")
    for committer in all_committers:
        print(f" - {committer}")

if __name__ == "__main__":
    main()
