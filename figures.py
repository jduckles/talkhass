"""The talk's figures in the baleen style (https://github.com/jduckles/visual).

    python3 figures.py              # every figure into assets/baleen/
    python3 figures.py solar mesh   # just those

Diagrams are redrawn from the hand-made SVGs that were in assets/. The solar,
mesh and washer data in data/ is digitised from the dashboard screenshots used
in the first version of the talk, so the values are approximate.
"""
import csv
import sys
from pathlib import Path

import baleen.mpl as bm
from baleen.svg import Sheet

HERE = Path(__file__).parent
OUT = HERE / "assets" / "baleen"


def read(name):
    with open(HERE / "data" / name) as f:
        return [{k: float(v) for k, v in r.items()} for r in csv.DictReader(f)]


# ------------------------------------------------------------ diagrams

def architecture(mode="light"):
    s = Sheet(1200, 675, mode=mode,
              title="Devices produce states; the core keeps them",
              subtitle="Dashboards, apps and automations are all clients of that one state",
              source="talkhass architecture slide, redrawn",
              alt="Devices and services feed integrations and add-ons, which feed Home "
                  "Assistant Core. The core holds the event bus, the state machine, the "
                  "automation engine, the service registry and the recorder, which writes "
                  "to SQLite. Clients reach the core over its API.")
    W, H = s.body_w, s.body_h
    cw, gap = 200, 74
    top, hh = 8, 300
    dev = s.region(0, top, cw, hh, "context", "Devices & services",
                   ["lights, locks", "sensors, cameras", "calendars, media", "weather, phones"],
                   icon="devices", label="devices")
    integ = s.region(cw + gap, top, cw, hh, "tide", "Integrations",
                     ["Zigbee, Z-Wave", "Matter, MQTT", "ESPHome, Frigate", "vendor clouds"],
                     icon="plug", label="extensions")
    cx = 2 * (cw + gap)
    corew = 300
    core = s.region(cx, top, corew, hh + 40, "tide", dark=True, head="Home Assistant Core",
                    label="one asyncio process", icon="home")
    # the parts of the core; the state machine is the one that matters
    rows = [("Event bus", "every change is an event", None),
            ("State machine", "one live truth for each entity", "krill"),
            ("Automation engine", None, None),
            ("Service registry", None, None)]
    ry = top + 112
    for head, sub, hue in rows:
        rh = 46 if sub else 32
        if hue:
            s.rect(cx + 16, ry, corew - 32, rh, fill=s.m.wash[hue], stroke=hue, sw=1.4, r=6)
            tc, mc = s.m.ink, s.m.muted
        else:
            s.rect(cx + 16, ry, corew - 32, rh, fill="none", stroke=s.m.muted, sw=0.8, r=6)
            tc, mc = s.m.paper if mode == "light" else s.m.ink, s.m.context
        s.text(cx + 30, ry + 21, head, "head", 16, color=tc)
        if sub:
            s.text(cx + 30, ry + 39, sub, "text", 13, color=mc)
        ry += rh + 8
    rec = s.region(cx + 16, ry, corew - 32, 44, "tide", None)
    s.text(cx + 30, ry + 27, "Recorder", "head", 16)
    s.text(cx + corew - 30, ry + 27, "batched writes", "text", 13, color="muted", anchor="end")
    db = s.region(cx, top + hh + 70, corew, 78, "tide", "SQLite database",
                  ["states, events, statistics"])
    s.connect(rec, db, "bottom", "top", label="write", x=cx + corew / 2)
    clx = cx + corew + gap
    clw = W - clx
    ch = (hh - 2 * 14) / 3
    clients = [("Web interface", "dashboards, history", "device-desktop"),
               ("iOS app", "control, notify", "device-mobile"),
               ("Android app", "control, notify", "device-mobile")]
    for i, (head, sub, icon) in enumerate(clients):
        y = top + i * (ch + 14)
        b = s.region(clx, y, clw, ch, "context", None)
        s.icon(icon, clx + 14, y + ch / 2 - 13, 26, color="muted")
        s.text(clx + 50, y + ch / 2 - 2, head, "head", 16)
        s.text(clx + 50, y + ch / 2 + 17, sub, "text", 12.5, color="muted")
        s.connect(core, b, label="API" if i == 0 else None, y=y + ch / 2)
    s.connect(dev, integ, label="reports")
    s.connect(integ, core, label="entities", y=top + 132)
    return s.save(OUT / "architecture")


def recorder(mode="light"):
    s = Sheet(1200, 675, mode=mode,
              title="The recorder is just another listener on the bus",
              subtitle="It writes in batches to one SQLite file, so a slow disk never stops the lights",
              source="talkhass recorder slide, redrawn",
              alt="The event bus feeds two paths. The control path runs to automations and "
                  "services. The recorder path writes batches through SQLAlchemy to one "
                  "SQLite file, which feeds history, the API and long-term statistics.")
    W, H = s.body_w, s.body_h
    bw = 180
    bus = s.region(0, 20, bw, H - 70, "tide", dark=True, head="Event bus",
                   label="the spine", icon="bolt",
                   body_text="Every update fires state_changed. Anyone can listen.")
    x1 = bw + 150
    cw = (W - x1 - 2 * 50) / 3
    ytop, ybot, rh = 20, 200, 190
    ctl = [("Automations", "trigger, condition, action"),
           ("Services", "light.turn_on, notify"),
           ("Your house", "lights, locks, heat")]
    prev = None
    for i, (head, sub) in enumerate(ctl):
        b = s.region(x1 + i * (cw + 50), ytop, cw, 120, "context", head, [sub],
                     label="control path" if i == 0 else None)
        s.connect(prev or bus, b, label=None, y=ytop + 60)
        prev = b
    rec = s.region(x1, ybot, cw, rh, "krill", "Recorder",
                   ["batched writes", "commit_interval", "SQLAlchemy"],
                   icon="database", label="history path")
    db = s.region(x1 + cw + 50, ybot, cw, rh, "tide", "home-assistant_v2.db",
                  ["one SQLite file", "states, events, statistics", "WAL, ACID, no server"],
                  icon="file-certificate", size=16)
    use = s.region(x1 + 2 * (cw + 50), ybot, cw, rh, "tide", "History",
                   ["graphs and cards", "the API", "long-term statistics"], icon="chart-line")
    s.connect(bus, rec, label="state_changed", y=ybot + rh / 2)
    s.connect(rec, db, y=ybot + rh / 2)
    s.connect(db, use, y=ybot + rh / 2)
    s.para(x1, ybot + rh + 44,
           "purge_keep_days trims the raw states. Long-term statistics are kept forever.",
           W - x1, "text", 15, color="muted")
    return s.save(OUT / "recorder")


def loop(mode="light"):
    s = Sheet(1200, 675, mode=mode, title="Every automation has the same shape",
              subtitle="Something changed, is it my business, do something",
              source="talkhass state-loop slide, redrawn",
              alt="Five stages in a loop: devices, integrations, the state machine, "
                  "automations, and services back to devices.")
    W, H = s.body_w, s.body_h
    bw, bh, gap = 250, 140, 168
    c0, c1, c2 = 0, bw + gap, 2 * (bw + gap)
    y1, y2 = 10, H - bh - 10
    dev = s.region(c0, y1, bw, bh, "kelp", "Devices", ["lights, plugs, sensors"],
                   icon="devices", label="the world")
    integ = s.region(c1, y1, bw, bh, "tide", "Integrations", ["one per ecosystem"],
                     icon="plug", label="adapters")
    core = s.region(c2, y1, W - c2, y2 + bh - y1, "tide", dark=True, head="State machine",
                    label="the core", icon="database",
                    body_text="Every entity has one current state. Each change fires "
                              "state_changed on the event bus.")
    auto = s.region(c1, y2, bw, bh, "krill", "Automations", ["trigger, condition, action"],
                    icon="automation", label="the logic")
    svc = s.region(c0, y2, bw, bh, "urchin", "Services", ["light.turn_on, notify"],
                   icon="settings", label="the reach")
    s.connect(dev, integ, label="reports")
    s.connect(integ, core, label="sets state", y=integ.cy)
    s.connect(core, auto, "left", "right", label="state_changed", y=auto.cy, color="krill")
    s.connect(auto, svc, "left", "right", label="calls")
    s.connect(svc, dev, "top", "bottom", label="acts on", label_offset=(0, 4))
    return s.save(OUT / "state-loop")


def timeline(mode="light"):
    s = Sheet(1200, 675, mode=mode, title="One person's script became a foundation",
              subtitle="Home Assistant, 2013 to 2024",
              source="home-assistant.io blog and Open Home Foundation announcement",
              alt="Timeline: 2013 first release, 2017 Apache 2.0 and Hass.io, 2018 Nabu "
                  "Casa, 2024 Open Home Foundation.")
    W, H = s.body_w, s.body_h
    events = [
        (2013, "tide", "First release", "Paulus Schoutsen publishes 0.1, a Python script for home lights", "rocket"),
        (2017, "kelp", "Apache 2.0, Hass.io", "Release 0.37 relicenses the code; Hass.io turns a Pi into a hub", "device-desktop"),
        (2018, "kowhai", "Nabu Casa", "A company that pays core developers, funded by Cloud subscriptions", "building"),
        (2024, "krill", "Open Home Foundation", "A non-profit takes ownership of the code and the brand", "users"),
    ]
    x0, x1 = 60, W - 60
    ty = H * 0.5
    yr = lambda y: x0 + (y - 2013) / (2024 - 2013) * (x1 - x0)
    s.line([(x0 - 30, ty), (x1 + 30, ty)], color="line", sw=2)
    for y in range(2013, 2025):
        s.line([(yr(y), ty - 5), (yr(y), ty + 5)], color="context", sw=1.2)
    cw = 232
    for i, (y, hue, head, text, icon) in enumerate(events):
        x = yr(y)
        up = i % 2 == 0
        s.badge(x, ty, icon, hue, r=24)
        s.text(x, ty + (-38 if up else 54), str(y), "number", 28, color=hue, anchor="middle")
        cx = min(max(x - cw / 2, -20), W - cw + 20)
        ch = 116
        top = ty - 72 - ch if up else ty + 84
        s.line([(x, ty + (-66 if up else 66)), (x, top + (ch if up else 0))], color=hue,
               sw=1.2, dash="2 4")
        s.rect(cx, top, cw, ch, fill=s.m.wash[hue], stroke=hue, sw=1.2)
        s.text(cx + 16, top + 34, head, "head", 20)
        s.para(cx + 16, top + 62, text, cw - 32, "text", 15, color="muted")
    return s.save(OUT / "timeline")


# ------------------------------------------------------------ plots

def washer(mode="light", context="paper"):
    bm.use(mode, context)
    d = read("washer_power.csv")
    x = [r["minute"] for r in d]
    y = [r["watts"] for r in d]
    fig, ax = bm.figure()
    bm.band(ax, 10, 74, "running", hue_name="tide", where="right")
    ax.plot(x, y, color=bm.hue("tide"))
    bm.rule(ax, 8, "threshold 8 W", color=bm.hue("krill"), side="right")
    ax.set_xlim(0, 100)
    ax.set_ylim(-60, 2500)
    ax.set_yticks([0, 500, 1000, 1500, 2000])
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:,.0f}")
    ax.set_xticks(range(0, 101, 20))
    ax.xaxis.set_major_formatter(lambda v, _: f"{v:.0f} min" if v == 100 else f"{v:.0f}")
    fig.canvas.draw()
    ax.get_xticklabels()[-1].set_ha("right")
    bm.unit(ax, "Watts drawn by the washing machine")
    bm.callout(ax, (10, 2000), "Heating element", "the 2 kW plateau", at=(21, 2130))
    bm.callout(ax, (74, 8), "Done", "under 8 W for 5 minutes", at=(77, 420),
               color=bm.hue("krill"))
    bm.callout(ax, (5, 120), "Start", "over 8 W for 2 minutes", at=(1, 2130), ha="left",
               color=bm.hue("krill"))
    bm.callout(ax, (60, 520), "Spin cycle", None, at=(62, 900), color=bm.hue("tide"))
    bm.title(fig, "Power alone tells you when the wash is done",
             "A smart plug's watts become two derived states: running and done")
    bm.brand(fig, source="talkhass power-cycle diagram, redrawn (illustrative)")
    return bm.save(fig, OUT / "power-cycle")


def solar(mode="light", context="paper"):
    bm.use(mode, context)
    d = read("solar_april.csv")
    day = [r["day"] for r in d]
    sol = [r["solar_kwh"] for r in d]
    grid = [r["grid_import_kwh"] for r in d]
    exp = [-r["export_kwh"] for r in d]
    fig, ax = bm.figure()
    w = 0.72
    ax.bar(day, sol, w, color=bm.hue("kowhai"))
    ax.bar(day, grid, w, bottom=sol, color=bm.hue("tide"))
    ax.bar(day, exp, w, color=bm.hue("urchin"))
    ax.axhline(0, color=bm.M().ink, lw=1, zorder=3)
    ax.set_xlim(0.4, 30.6)
    ax.set_ylim(-24, 86)
    ax.set_xticks([1, 5, 9, 13, 17, 21, 25, 29])
    ax.xaxis.set_major_formatter(lambda v, _: f"Apr {v:.0f}")
    ax.set_yticks([-20, 0, 20, 40, 60])
    ax.yaxis.set_major_formatter(lambda v, _: f"{abs(v):.0f}")
    bm.legend_row(ax, [("Solar used at home", "kowhai"), ("From the grid", "tide"),
                       ("Sent to the grid", "urchin")])
    tot_sol = sum(sol) + sum(-e for e in exp)
    share = sum(sol) / (sum(sol) + sum(grid))
    best = max(d, key=lambda r: r["solar_kwh"])
    bm.callout(ax, (best["day"], best["solar_kwh"] + best["grid_import_kwh"]),
               f"Apr {best['day']:.0f}: best solar day",
               f"{best['solar_kwh']:.0f} kWh used at home", at=(11, 56))
    peak = max(d, key=lambda r: r["grid_import_kwh"])
    bm.callout(ax, (peak["day"], peak["solar_kwh"] + peak["grid_import_kwh"]),
               f"Apr {peak['day']:.0f}: {peak['solar_kwh'] + peak['grid_import_kwh']:.0f} kWh",
               "mostly from the grid", at=(6.2, 70))
    ax.text(30.6, -21, "kWh sent out  ↓", ha="right", va="bottom", fontsize=bm.S()["note"],
            color=bm.M().muted)
    bm.unit(ax, "kWh per day", side="right")
    bm.title(fig, f"Solar covered about {share:.0%} of April's use",
             f"{tot_sol:,.0f} kWh generated; {-sum(exp):,.0f} kWh of it went back to the grid")
    bm.brand(fig, source="Home Assistant energy dashboard, digitised from a screenshot (approximate)")
    return bm.save(fig, OUT / "solar")


def mesh(mode="light", context="paper"):
    bm.use(mode, context)
    d = read("mesh_msgpermin.csv")
    x = [r["day_of_october"] for r in d]
    y = [r["messages_per_min"] for r in d]
    fig, ax = bm.figure()
    line, = ax.plot(x, y, drawstyle="steps-post", lw=1.4)
    bm.context(line)
    outs = [x[i] for i, v in enumerate(y) if v == 0 and (i == 0 or y[i - 1] > 0)]
    for k, t in enumerate(outs):
        bm.callout(ax, (t, 0), f"Oct {round(t)}", "repeater silent" if k == 0 else None,
                   dx=-14 if k == 2 else 12, dy=24)
    avg = sum(y) / len(y)
    bm.rule(ax, avg, f"average {avg:.1f} msg/min", side="left", color=bm.hue("tide"))
    ax.set_xlim(1, 19.6)
    ax.set_ylim(0, 2.05)
    ax.set_xticks(range(1, 20, 2))
    ax.xaxis.set_major_formatter(lambda v, _: f"Oct {v:.0f}")
    ax.set_yticks([0, 0.5, 1.0, 1.5, 2.0])
    bm.unit(ax, "Messages received per minute")
    bm.title(fig, f"The Maori Hill repeater went quiet {len(outs)} times in October",
             "MeshCore repeater message rate; everything else is normal chatter")
    bm.brand(fig, source="Home Assistant history, digitised from a screenshot (approximate)")
    return bm.save(fig, OUT / "mesh-msgpermin")


ALL = {f.__name__: f for f in (architecture, recorder, loop, timeline, washer, solar, mesh)}

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name in sys.argv[1:] or ALL:
        for p in ALL[name]():
            print(p)
