# Smart Home Hub (iPad, Pythonista)

Your own smart home hub. It runs in Pythonista on the iPad, with no PC needed.
Everything you see comes from **hub.json**, so you can change it as much as you like.

## Setup (one time)
1. Put `panel.py`, `panel.html` and `hub.json` in one folder in Pythonista (replace old copies).
2. **Add the TV to Apple Home:** on the TV, go to Settings > Connection > AirPlay and HomeKit > HomeKit > Set Up.
   On the iPad, open the Home app, tap **+ > Add Accessory**, and scan the code. Check that the Home app can turn the TV on and off.
3. **Make two Shortcuts** in the Shortcuts app. Each one uses a **Control Home** action on Living Room TV:
   one called exactly **TV On** (turns it on) and one called **TV Off** (turns it off).
4. Open `panel.py` in Pythonista and tap ▶.

**TV switch:** the TV is one on/off switch; tap anywhere on its bubble. It glows while the TV is on.
The hub sees whether the TV is on by itself: it finds the TV on your Wi-Fi (the first time, allow Pythonista
to use the local network) and keeps its address in `private.json` on the iPad. Any device can be a switch:
`{ "name": "Lamp", "icon": "light", "toggle": { "on": {"shortcut": "Lamp On"}, "off": {"shortcut": "Lamp Off"} } }`

Home Screen icon: in Pythonista open `panel.py`, tap the wrench > **Shortcuts… > Home Screen**.
Keep it on: Settings > Display & Brightness > Auto-Lock > **Never**, and leave the iPad charging.

## Customising (hub.json)
Open `hub.json` in Pythonista (or add a button with `"edit": true` to open it from the hub). Save it and run `panel.py` again.

```
rooms -> devices -> buttons
```

**Room:** `{ "name": "Bedroom", "devices": [ ... ] }`

**Device:** `{ "name": "Lamp", "icon": "light", "buttons": [ ... ] }`

**Button:** a `label`, an optional `icon` and `color`, and one of these:
| key | what it does | example |
|---|---|---|
| `"shortcut"` | runs an Apple Shortcut by name (use this for anything in the Home app) | `"shortcut": "Lamp On"` |
| `"url"` | opens an app or link | `"url": "spotify://"` |
| `"edit": true` | opens hub.json for editing | |

**Icons:** tv, power, moon, light, plug, fan, speaker, music, lock, thermostat, blinds,
camera, home, star, play, bed, sun, edit

**Colours:** any colour code, e.g. `"#ffb547"`. Pick one from a site like htmlcolorcodes.com.

**Weather:** shown top right, refreshed every 15 minutes (free Open-Meteo service).
The hub uses the iPad's location, so tap **Allow** when Pythonista asks the first time.
If that doesn't work, type your town under `weather`, e.g. `"place": "Manchester"`, and it looks it up.
If the weather can't load, a short message there says why.
Heads-ups appear under the weather when they matter: "Rain in ~20 mins", "Rain easing off in ~30 mins",
"Rain likely around 6 PM", frost overnight, and strong gusts. Set `"show": false` to hide it.

**Night mode:** tap the cat to switch (it falls asleep), or let it switch by itself.

**Cat moods:** by day the cat now and then naps, stretches with a yawn, chases a fly, or watches a robin land in the window.
Under `night`: `"auto": true` uses the `"start"` / `"end"` times (24-hour, e.g. "22:00"), and `"brightness"`
(0 to 1) dims the iPad screen at night. Remove `brightness` to leave the screen alone.

**Hamster:** a ginger hamster lives at the left of the sill. By day he peeks out of his cardboard tube, sniffs and nibbles seeds. At night he runs on his wheel. Tap him for a squeak and a heart.

**Timer:** tap the Timer bubble. Drag around the ring (each full turn is an hour, up to 12 hours),
or tap a quick time. While it runs you can add time, pause or cancel. Set `"timer": {"show": false}` to hide it.
Keep the iPad's volume up to hear the chime.

**Layout:** a cosy room. The cat sits on the windowsill, and the window shows the live weather
(sun, clouds, rain, snow, storms, and the moon and stars at night). Controls are round bubbles on the left.

**Theme:** `"style": "ginger-cat"` gives the ginger cat theme. Remove it for the original purple look.
`theme.background` is the two background gradient colours, `theme.glow` is the two soft glows,
and `theme.text` is the text colour. Set `"show_clock": false` to replace the clock with the title.

### Example: add a bedroom lamp
1. Add the lamp to the Home app, then make Shortcuts called "Lamp On" and "Lamp Off".
2. Add this to `rooms` in hub.json (watch the commas between entries):
```json
{
  "name": "Bedroom",
  "devices": [
    { "name": "Lamp", "icon": "light", "buttons": [
      { "label": "On",  "icon": "sun",  "color": "#ffd166", "shortcut": "Lamp On" },
      { "label": "Off", "icon": "moon", "color": "#7c8cff", "shortcut": "Lamp Off" }
    ]}
  ]
}
```
A **scene** works the same way: one Shortcut that does several things (e.g. "Movie night": TV on, lights dim).

If hub.json has a typo, the hub tells you and opens the file so you can fix it.
