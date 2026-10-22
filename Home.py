"""Smart home hub launcher. Run this (or its Home Screen icon) instead of panel.py.
It downloads the newest hub files from your own GitHub repository first, so updates arrive by themselves.

Privacy: the repository only holds the hub's code and layout. Anything personal goes in private.json,
which lives only on this iPad. It is never downloaded, uploaded or overwritten."""
import os
import runpy
from urllib.request import urlopen

REPO = "SpeedyArt/smart-home-hub"   # your GitHub repository the hub is published to
BRANCH = "main"
FILES = ["Home.py", "panel.py", "panel.html", "hub.json"]  # always replaced with the newest version

HERE = os.path.dirname(os.path.abspath(__file__))


def fetch(name):
    url = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/{name}"
    with urlopen(url, timeout=10) as r:
        return r.read()


def update():
    for name in FILES:
        try:
            data = fetch(name)
        except Exception as e:  # offline: keep using the copy we already have
            print(f"Couldn't update {name} ({e}), using the saved copy.")
            continue
        path = os.path.join(HERE, name)
        old = open(path, "rb").read() if os.path.exists(path) else None
        if data != old:
            with open(path, "wb") as f:
                f.write(data)
            print(f"Updated {name}")


update()
runpy.run_path(os.path.join(HERE, "panel.py"), run_name="__main__")
