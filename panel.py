"""Smart home hub for iPad (Pythonista). Everything on screen comes from hub.json:
edit that file to add rooms, devices, buttons, icons and colours, then run this again."""
import json
import os
import threading
import time
import webbrowser
from urllib.parse import quote
from urllib.request import urlopen

import console
import editor
import ui

HERE = os.path.dirname(os.path.abspath(__file__))
HUB_FILE = os.path.join(HERE, "hub.json")


PRIVATE_FILE = os.path.join(HERE, "private.json")  # personal settings: stays on this iPad only


def merge(base, extra):
    """Lay private.json's settings over hub.json's (nested sections are merged, not replaced)."""
    for key, value in extra.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            merge(base[key], value)
        else:
            base[key] = value
    return base


def load_hub():
    with open(HUB_FILE, encoding="utf-8") as f:
        hub = json.load(f)
    if os.path.exists(PRIVATE_FILE):
        with open(PRIVATE_FILE, encoding="utf-8") as f:
            merge(hub, json.load(f))
    return hub


def run_button(button):
    """Do what a hub.json button asks. Returns (ok, message)."""
    if "shortcut" in button:  # an Apple Shortcut, e.g. one that controls HomeKit devices
        webbrowser.open("shortcuts://x-callback-url/run-shortcut?name=" + quote(button["shortcut"])
                        + "&x-success=" + quote("pythonista3://"))
        return True, ""
    if "url" in button:  # open any app or link
        webbrowser.open(button["url"])
        return True, ""
    if button.get("edit"):  # open hub.json for editing
        hub_view.close()
        editor.open_file(HUB_FILE)
        return True, ""
    return False, "This button has no shortcut, url or edit set in hub.json"


_day_brightness = None


def set_night_brightness(on):
    """Dim the iPad screen at night (hub.json night.brightness) and restore it in the morning."""
    global _day_brightness
    level = (HUB.get("night") or {}).get("brightness")
    if level is None:
        return
    try:
        from objc_util import ObjCClass, on_main_thread
        screen = ObjCClass("UIScreen").mainScreen()

        @on_main_thread
        def apply():
            global _day_brightness
            if on:
                _day_brightness = screen.brightness()
                screen.setBrightness_(float(level))
            elif _day_brightness is not None:
                screen.setBrightness_(_day_brightness)
        apply()
    except Exception:
        pass  # dimming is a nice-to-have


class Bridge:
    def webview_should_start_load(self, webview, url, nav_type):
        if not url.startswith("panel://"):
            return True
        self.run(webview, url[len("panel://"):].strip("/"))
        return False

    @ui.in_background
    def run(self, webview, button_id):
        if button_id.startswith("night-"):
            set_night_brightness(button_id.endswith("1"))
            return
        try:
            r, d, b = (int(x) for x in button_id.split("-"))
            ok, msg = run_button(HUB["rooms"][r]["devices"][d]["buttons"][b])
        except Exception as e:
            ok, msg = False, str(e) or type(e).__name__
        webview.eval_js(f"done({json.dumps(button_id)}, {json.dumps(ok)}, {json.dumps(msg)})")


try:
    HUB = load_hub()
except ValueError as e:  # a typo in hub.json
    console.alert("hub.json has a mistake", str(e), "Edit hub.json", hide_cancel_button=True)
    editor.open_file(HUB_FILE)
    raise SystemExit

with open(os.path.join(HERE, "panel.html"), encoding="utf-8") as f:
    html = f.read().replace("<script>", f"<script>window.HUB = {json.dumps(HUB)};\n", 1)

class Hub(ui.View):
    """Full-screen holder for the web page. Puts the iPad back to normal when the hub closes."""
    def will_close(self):
        set_night_brightness(False)
        console.set_idle_timer_disabled(False)


console.set_idle_timer_disabled(True)  # keep the screen on while the hub is open
theme = HUB.get("theme", {})
bg = (theme.get("background") or ["#3a1d0e" if theme.get("style") == "ginger-cat" else "#0b1020"])[0]
hub_view = Hub(name="Home", background_color=bg)
view = ui.WebView(frame=hub_view.bounds, flex="WH", background_color=bg)
view.delegate = Bridge()
view.load_html(html)
hub_view.add_subview(view)
hub_view.present("fullscreen", hide_title_bar=True)


def stop_bounce():
    """Turn off the web view's rubber-band scrolling so the page stays put."""
    try:
        from objc_util import ObjCClass, ObjCInstance, on_main_thread
        scroll_view = ObjCClass("UIScrollView")

        @on_main_thread
        def walk(v):
            if v.isKindOfClass_(scroll_view):
                v.setBounces_(False)
                v.setAlwaysBounceVertical_(False)
                v.setAlwaysBounceHorizontal_(False)
                v.setScrollEnabled_(False)  # the page scrolls itself when it needs to
                v.setMinimumZoomScale_(1.0)
                v.setMaximumZoomScale_(1.0)
            for sub in v.subviews():
                walk(sub)
        walk(ObjCInstance(view))
    except Exception:
        pass


stop_bounce()


# ---------- Weather (Open-Meteo, free, no account) ----------
def weather_place(w):
    """Work out where to get the weather for: hub.json coordinates, then the iPad's location, then the town name."""
    if w.get("latitude") is not None and w.get("longitude") is not None:
        return w["latitude"], w["longitude"], w.get("place", "")
    try:
        import location
        location.start_updates()
        loc = None
        for _ in range(20):  # wait up to 5 seconds for a fix
            loc = location.get_location()
            if loc:
                break
            time.sleep(0.25)
        location.stop_updates()
        if loc:
            w["latitude"], w["longitude"] = round(loc["latitude"], 3), round(loc["longitude"], 3)
            if not w.get("place"):
                found = location.reverse_geocode(loc) or [{}]
                w["place"] = found[0].get("City", "")
            return w["latitude"], w["longitude"], w["place"]
    except Exception:
        pass
    if w.get("place"):
        url = "https://geocoding-api.open-meteo.com/v1/search?count=1&name=" + quote(w["place"])
        results = json.load(urlopen(url, timeout=15)).get("results") or []
        if results:
            w["latitude"], w["longitude"] = results[0]["latitude"], results[0]["longitude"]
            return w["latitude"], w["longitude"], w["place"]
        raise ValueError(f"Couldn't find '{w['place']}'. Check the place name in hub.json")
    raise ValueError("Allow location for Pythonista, or set your town as \"place\" in hub.json")


def js(code):
    try:
        return view.eval_js(code)
    except Exception:
        return None


def weather_loop():
    w = HUB.get("weather") or {}
    if w.get("show") is False:
        return
    for _ in range(40):  # wait for the page to be ready
        if js("typeof setWeather") == "function":
            break
        time.sleep(0.25)
    while hub_view.on_screen:
        try:
            lat, lon, place = weather_place(w)
            url = (f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
                   "&current=temperature_2m,weather_code,precipitation"
                   "&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max"
                   "&minutely_15=precipitation"
                   "&hourly=precipitation_probability,temperature_2m,wind_gusts_10m"
                   "&timezone=auto&forecast_days=2")
            data = json.load(urlopen(url, timeout=15))
            js(f"setWeather({json.dumps(data)}, {json.dumps(place)})")
            wait = 10 * 60  # often enough for rain heads-ups
        except Exception as e:
            js(f"weatherMsg({json.dumps('Weather: ' + str(e))})")
            wait = 2 * 60  # try again soon
        for _ in range(wait):
            if not hub_view.on_screen:
                return
            time.sleep(1)


# Its own thread, so it never holds up the buttons.
threading.Thread(target=weather_loop, daemon=True).start()
