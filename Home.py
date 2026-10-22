"""Smart home hub launcher. Run this (or its Home Screen icon) instead of panel.py.
It downloads the newest hub files from your own GitHub repository first, so updates arrive by themselves.
Your hub.json is never overwritten, so your rooms and buttons stay as you set them."""
import os
import runpy
from urllib.request import urlopen

REPO = "SpeedyArt/smart-home-hub"   # your GitHub repository the hub is published to
BRANCH = "main"
FILES = ["panel.py", "panel.html"]  # always replaced with the newest version
FIRST_TIME_ONLY = ["hub.json"]      # only downloaded if you don't have one yet

HERE = os.path.dirname(os.path.abspath(__file__))


def fetch(name):
    url = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/{name}"
    with urlopen(url, timeout=10) as r:
        return r.read()


def update():
    missing = [f for f in FIRST_TIME_ONLY if not os.path.exists(os.path.join(HERE, f))]
    for name in FILES + missing:
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
