"""Smart home hub launcher. Run this (or its Home Screen icon) instead of panel.py.
It downloads the newest hub files from your own GitHub repository first, so updates arrive by themselves.

Privacy: the repository only holds the hub's code and layout. Anything personal goes in private.json,
which lives only on this iPad. It is never downloaded, uploaded or overwritten."""
import os
import runpy
from urllib.request import Request, urlopen

REPO = "SpeedyArt/smart-home-hub"   # your GitHub repository the hub is published to
BRANCH = "main"
FILES = ["Home.py", "panel.py", "panel.html", "hub.json"]  # always replaced with the newest version

HERE = os.path.dirname(os.path.abspath(__file__))


def latest_version():
    """The id of the newest commit. Downloading by id skips GitHub's few-minute cache of the branch."""
    req = Request(f"https://api.github.com/repos/{REPO}/commits/{BRANCH}",
                  headers={"Accept": "application/vnd.github.sha"})
    with urlopen(req, timeout=10) as r:
        sha = r.read().decode().strip()
    if len(sha) != 40:
        raise ValueError("unexpected answer from GitHub")
    return sha


def fetch(version, name):
    with urlopen(f"https://raw.githubusercontent.com/{REPO}/{version}/{name}", timeout=10) as r:
        return r.read()


def update():
    try:
        version = latest_version()
    except Exception:
        version = BRANCH  # GitHub's API is busy: the branch works too, it may just be a few minutes behind
    # Download everything first, and only swap files in once all of them arrived,
    # so a Wi-Fi drop can never leave a mix of old and new files.
    try:
        new = {name: fetch(version, name) for name in FILES}
    except Exception as e:  # offline: keep using the copy we already have
        print(f"Couldn't update ({e}), using the saved copy.")
        return
    for name, data in new.items():
        path = os.path.join(HERE, name)
        old = open(path, "rb").read() if os.path.exists(path) else None
        if data != old:
            with open(path + ".new", "wb") as f:
                f.write(data)
            os.replace(path + ".new", path)  # all at once, never half written
            print(f"Updated {name}")


update()
runpy.run_path(os.path.join(HERE, "panel.py"), run_name="__main__")
