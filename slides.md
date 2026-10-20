---
marp: true
theme: hass
size: 16:9
paginate: true
footer: 'Home Assistant · a state engine for your house'
highlight: github-dark
---

<!-- _class: lead -->
<!-- _footer: '' -->
<!-- _paginate: false -->

# Home Assistant

## A state engine for your house

Everything you can know about your home — and everything you can do about it.

Slides available at: https://jduckles.github.io/talkhass/



## Jonah Duckles - ZL4EKA

Presented at ZL4AA Wednesday - October 21, 2026

---

# The one-sentence version

> Home Assistant keeps a live model of your house as **states**, and lets you react when those states change.

<br>

**Know → decide → act.** Every integration, dashboard, and automation is one of those three.

<!--
If people remember one slide, this is it. States are the nouns, events are the verbs.
-->

---

# Two jobs, one product

<div class="columns">
<div>

### A state engine

- One place for every observation
- Timestamped and queryable
- Event-driven, not polled by you
- Rebuilt at startup from integrations
- History you can graph and audit

</div>
<div>

### An abstraction layer

- The same vocabulary for every vendor
- `light`, `lock`, `cover`, `climate`, `sensor`
- Swap the hardware, keep the automation
- Integrations do the translation

</div>
</div>

<div class="callout">

The abstraction is why your automations outlive your hardware.

</div>

<!--
Two jobs. The state engine is the interesting one for this talk;
the abstraction layer is why it survives a trip to the hardware store.
-->

---

<!-- _class: diagram -->

# The whole system in one picture

![w:840](assets/architecture.svg)

<div class="callout quiet">

Devices produce states; the core keeps them. Dashboards, apps, and automations are all clients of that one state.

</div>

---

# A short history

![w:940](assets/timeline.svg)

<div class="callout quiet">

One person's Python script became an appliance, a company, and a non-profit — in that order.

</div>

<!--
2013: Paulus Schoutsen releases 0.1 on 17 September.
2017: release 0.37 re-licenses the code under Apache 2.0; Hass.io (now HAOS) arrives the same year.
2018: Nabu Casa is founded to run Home Assistant Cloud and pay contributors.
2024: the Open Home Foundation takes ownership of the code and the brand.
-->

---

# Open source, with a real license

<div class="columns">
<div>

### Apache 2.0, since 0.37

- Permissive: use it, modify it, ship it commercially
- An explicit patent grant
- No copyleft, no per-seat fee, no rug-pull
- The code and brand are owned by the **Open Home Foundation**, a non-profit

</div>
<div>

<div class="stats">
  <div class="stat"><span>1,500+</span><small>integrations</small></div>
  <div class="stat"><span>21,000+</span><small>contributors — most of any GitHub project</small></div>
  <div class="stat"><span>2.7M+</span><small>households</small></div>
  <div class="stat"><span>12</span><small>releases a year</small></div>
</div>

</div>
</div>

<div class="callout">

Native **iOS and Android** apps are part of the product — free, local-first, and no cloud account required.

</div>

<!--
The license matters more than the star count: Apache 2.0 means no one can take the code away,
and the foundation means no one can sell the project out from under its users.
-->

---

# Every entity answers three questions

<span class="pill">What is it?</span>
<span class="pill">What is its state?</span>
<span class="pill">When did it change?</span>

<br>

1. **Identity** — `entity_id`, written as `domain.object_id`
   `light.kitchen_ceiling`, `binary_sensor.driveway_person`
2. **State** — one string, plus a bag of attributes
   `on`, `21.5`, `home`, `unavailable`
3. **Time** — `last_changed` and `last_updated`

<div class="callout quiet">

Everything else in Home Assistant — dashboards, automations, history, voice — is built on those three answers.

</div>

---

# The anatomy of a state

```json
{
  "entity_id": "light.kitchen_ceiling",
  "state": "on",
  "attributes": {
    "friendly_name": "Kitchen Ceiling",
    "brightness": 178,
    "color_temp_kelvin": 2700,
    "supported_color_modes": ["color_temp", "brightness"]
  },
  "last_changed": "2026-10-19T08:12:41.220Z",
  "last_updated": "2026-10-19T08:12:41.220Z",
  "context": { "user_id": null, "parent_id": null }
}
```

<div class="callout quiet">

`state` is always a string. Numbers, timestamps, and lists live in `attributes`.
`last_changed` moves when the **state** changes; `last_updated` moves on any attribute change.

</div>

---

# Domains: the nouns of the house

| Domain | What it models | Example |
| --- | --- | --- |
| `light` | on/off, brightness, colour | `light.kitchen_ceiling` |
| `switch` | on/off | `switch.coffee_maker` |
| `lock` | locked / unlocked / jammed | `lock.front_door` |
| `cover` | open/closed, position | `cover.garage_door` |
| `climate` | mode, target and current temp | `climate.hallway` |
| `sensor` | a number or a string | `sensor.washer_power` |
| `binary_sensor` | on / off | `binary_sensor.driveway_person` |
| `person` | home / not_home | `person.jonah` |
| `sun` | above / below horizon | `sun.sun` |
| `calendar` | on while an event is running | `calendar.work` |
| `weather` | condition + forecast | `weather.home` |

<!--
Domains are not decoration: they define which services apply and how the UI renders.
A binary_sensor is a yes/no; a sensor is a value. Get that right and everything downstream is easier.
-->

---

# State is not always a boolean

- **`on` / `off`** — the workhorses
- **Numbers** — `21.5`, `178`, `8.4`
- **Text** — `home`, `not_home`, `heating`, `cooling`
- **Timestamps** — `2026-10-19T08:12:41+00:00`
- **`unknown`** — the entity exists, but has never reported
- **`unavailable`** — it is gone: network, battery, reload, dead device

<div class="callout warn">

**`unavailable` is not `off`.** Treating them the same is how a dead sensor becomes a dark house — or an unlocked door.

</div>

<!--
This is the most common production bug in home automation.
Design automations to fail visibly, not silently.
-->

---

<!-- _class: compact -->

# What can you know about your house?

| Question | Entity | State |
| --- | --- | --- |
| Is the light on? How dim? | `light.kitchen_ceiling` | `on`, `brightness: 178` |
| Is the room occupied? | `binary_sensor.kitchen_occupancy` | `on` |
| Is anyone home? | `person.jonah` | `home` |
| What time of day is it? | `sensor.time_of_day` | `evening` |
| Where is the sun? | `sun.sun` | `below_horizon`, `elevation: -12.4` |
| Is it a public holiday? | `binary_sensor.workday` | `off` |
| Is a meeting happening now? | `calendar.work` | `on` |
| Is someone coming up the drive? | `binary_sensor.driveway_person` | `on` |
| Is the washer running? | `sensor.washer_power` | `412 W` |
| Is the dishwasher done? | `binary_sensor.dishwasher_done` | `on` |

<div class="callout quiet">

Ten questions, ten states, one vocabulary. Note how many of the right-hand answers are **inferred**, not measured.

</div>

---

<!-- _class: compact -->

# Occupancy

**Occupancy is not a sensor. It is a "derived state"**

<div class="columns">
<div>

- **PIR motion** — cheap, fast, blind to stillness
- **mmWave** — sees stillness, more false positives
- **Phone Wi-Fi / GPS** — great for "home", lags on exit
- **BLE beacons** — room-level, battery-dependent
- **Cameras** — precise, privacy trade-off
- **Doors, media, lights** — inference, not measurement

</div>
<div>

```yaml
template:
  - binary_sensor:
      - name: "Kitchen occupied"
        state: >
          {{ is_state('binary_sensor.kitchen_motion', 'on')
             or is_state('binary_sensor.kitchen_presence', 'on')
             or is_state('media_player.kitchen', 'playing') }}
        delay_off:
          minutes: 5
```

</div>
</div>

<div class="callout">

One sensor lies. Five sensors argue. Encode the argument once, in a template.

</div>

---

<!-- _class: compact -->

# Time, sun, calendars, holidays

<div class="columns">
<div>

### The sun

`sun.sun` is `above_horizon` or `below_horizon`, with attributes:

- `elevation`, `azimuth`
- `next_dawn`, `next_dusk`
- `next_rising`, `next_setting`

Triggers can offset it: sunset at **−00:45**.

### Time of day

- `sensor.time` — `18:42`
- the `tod` helper → `binary_sensor.evening`
- a template sensor → `night`, `morning`, `afternoon`

</div>
<div>

### Calendars

`calendar.work` is `on` **while an event is running**.

Trigger on `start` / `end`, with an offset.

### Holidays

`workday` knows countries and provinces:

```yaml
binary_sensor:
  - platform: workday
    country: NZ
    province: WGN
```

Now "is it a workday?" is just a state.

</div>
</div>

<div class="callout quiet">

Anything that can craft a valid "state" object can create a state. States are the building blocks of "Automations" 

</div>

---

# Inference: we can derive states from data

In this case Watts from a power monitoring plug on a washing machine

![w:750](assets/power-cycle.svg)

<div class="callout">

`running` and `done` are states you **derive**. The measurable state is power, and a duration turns an instant into a fact.

</div>

---

# The loop

![w:900](assets/state-loop.svg)

<div class="callout quiet">

Something changed → is it my business? → do something. Every automation is that shape.

</div>

---

# Automation: trigger, condition, action

```yaml
triggers:
  - trigger: numeric_state
    entity_id: sensor.washer_power
    above: 8
    for: "00:02:00"

conditions:
  - condition: state
    entity_id: person.jonah
    state: home

actions:
  - action: notify.mobile_app_phone
    data:
      message: "Washer started"
```

<div class="columns">
<div>

- **Trigger** — a state change, a time, the sun, a calendar event, a webhook
- **Condition** — extra state checks; all must pass

</div>
<div>

- **Action** — call a service, wait, choose, repeat
- `for:` turns "right now" into "for two minutes"

</div>
</div>

---

# Automations in the web interface 

![width:600](assets/automation.png)

---

# The abstraction layer

**Same nouns, every product.**

| You want | You call | Underneath |
| --- | --- | --- |
| Turn on a light | `light.turn_on` | Hue, Zigbee, Z-Wave, Wi-Fi, Matter |
| Unlock a door | `lock.unlock` | August, Yale, Nuki, Aqara |
| Set a temperature | `climate.set_temperature` | Nest, Ecobee, TRVs |
| Play audio | `media_player.play_media` | Sonos, Chromecast, Apple TV |
| Read a sensor | entity state | MQTT, Modbus, BLE, cloud APIs |

<div class="callout">

If it can be observed, it can be an entity. If it can be acted on, it can be a service.

</div>

<!--
Protocols come and go. The vocabulary does not.
This is also the answer to "will this work with my weird thing?" — usually, via an integration.
-->

---

# Deployment 1: a VM in your cluster

**HAOS image on Proxmox, KVM, or ESXi.**

- Snapshots before every upgrade
- Backups to NAS, off the host
- 2 vCPU, 4 GB RAM, 32 GB disk covers most homes
- You still get Supervisor, add-ons, and HAOS updates
- You get the ability to run "add-ons" which are Docker containers that can add other functionality

<div class="callout warn">

**Zigbee Radios** USB passthrough for Zigbee/Z-Wave, or dedicated device.
Use a USB extension cable, a powered hub, or a network coordinator
(SLZB-06, Zigbee2MQTT, ser2net).

</div>

<div class="columns">
<div>

**Pros** — snapshots, consolidation, remote host access, easy restore.

</div>
<div>

**Cons** — passthrough pain, host maintenance is house downtime.

</div>
</div>

---

# Deployment 2: dedicated hardware

**An appliance for the house.**

- **Home Assistant Green**, or your own Pi / mini PC
- Raspberry Pi 4 or 5 — **boot from SSD, never an SD card**
- Any x86 mini PC; ARM and x86 both work
- HAOS gives you Supervisor, add-ons, and managed updates
- UPS on the HA box and the network gear

<div class="callout">

Keep the radio stick on a USB extension cable, away from USB 3 ports and the Pi itself. It is the cheapest reliability upgrade you can buy.

</div>

<div class="columns">
<div>

**Pros** — isolated, predictable, radios are physically local, no hypervisor.

</div>
<div>

**Cons** — another box and power brick; backups are your job.

</div>
</div>

---

#  Home Assistant Green 


![width:800](assets/hass_green_2.png)


---

# Deployment 3: a container

```yaml
services:
  homeassistant:
    image: ghcr.io/home-assistant/home-assistant:stable
    network_mode: host
    volumes:
      - ./config:/config
    restart: unless-stopped
```

<div class="columns">
<div>

- You get **Core only**
- No Supervisor → **no add-ons**
- No HAOS backups or one-click updates
- You own Python deps, reverse proxy, updates

</div>
<div>

- Fine for Kubernetes or "everything in one orchestrator"
- USB devices need explicit mapping
- Not the path of least resistance

</div>
</div>

<div class="callout warn">

I would not recommend it for a normal home. The appliance *is* the product — the container strips the parts that make it one.

</div>

---

# Nabu Casa: the commercial half

<div class="columns">
<div>

### The company

- Founded in **2018** by the people behind Home Assistant
- **No investors, no VC** — funded by customers
- The majority of its profit goes to the **Open Home Foundation**
- Pays full-time maintainers of Home Assistant and ESPHome
- Designs and sells the official hardware

</div>
<div>

### What it ships

- **Home Assistant Cloud** — optional remote access, Alexa and Google, speech-to-text and text-to-speech
- **iOS and Android companion apps** — free, native, and they talk directly to your instance
- **Official hardware** — Green, Connect radios, Voice PE
- Not the owner of the project — the foundation is

</div>
</div>

<div class="callout">

Nabu Casa cannot sell the project, and the project cannot be bought. That is the point of the foundation.

</div>

<!--
The apps matter here: they are the daily interface for most households,
they connect locally when they can, and they need no Nabu Casa account.
-->

---

<!-- _class: compact -->

# The hardware Nabu Casa built

| Year | Product | What it is | Now |
| --- | --- | --- | --- |
| 2020 | Home Assistant Blue | First appliance: ODROID-N2+, custom case, HAOS preinstalled | Discontinued |
| 2021 | Home Assistant Yellow | Raspberry Pi CM4 carrier, optional Zigbee/Thread radio, M.2 NVMe, PoE variant | Discontinued |
| 2022 | Connect ZBT-1 | The first Zigbee/Thread USB radio, launched as SkyConnect | Discontinued |
| 2023 | Home Assistant Green | Entry appliance: 1.8 GHz ARM, 4 GB RAM, 32 GB eMMC, no radios | **Current** |
| 2024 | Voice Preview Edition | Local voice satellite: ESP32-S3, XMOS audio, physical mic mute | **Current** |
| 2025 | Connect ZBT-2 | Zigbee/Thread radio with an external, tuned antenna | **Current** |
| 2025 | Connect ZWA-2 | Z-Wave and Z-Wave Long Range, with a large tuned antenna | **Current** |

<div class="callout quiet">

Every current box runs the same Home Assistant OS you can install yourself.
The radios are standard USB devices — ZHA, Zigbee2MQTT, and Z-Wave JS all use them.

</div>

---

# Buy it for the convenience

<div class="columns">
<div>

### What you get

- Plug in power and Ethernet; onboarding does the rest
- **Green** for the hub, **Connect ZBT-2 / ZWA-2** for radios
- **Voice PE** for local voice, with a mute switch that cuts mic power
- Supervisor, add-ons, updates, and backups in one UI
- iOS and Android apps that point straight at your instance

</div>
<div>

### What you don't give up

- The same HAOS image as a DIY install
- The same backup format — restore onto a Pi, VM, or mini PC
- Standard radios, including Zigbee2MQTT and Z-Wave JS
- Local control: no cloud account required
- Your data stays a file on your disk

</div>
</div>

<div class="callout">

Buy it because you want the appliance, not because the software needs it. That distinction is the whole philosophy.

</div>

---

# Choosing

| If you want… | Pick |
| --- | --- |
| An appliance with the least maintenance | HAOS on Home Assistant Green (or your own box) |
| Snapshots and an existing cluster | HAOS VM on Proxmox / KVM |
| Everything inside one orchestrator | Container — Core only |
| Zigbee / Z-Wave radios | Dedicated box, or a VM with USB passthrough or a network coordinator |
| A lab you can break and restore | VM with snapshots |

<div class="callout quiet">

The state engine is the same in all three. Only the packaging changes.

</div>

---

# Under the hood

<div class="columns">
<div>

- **Python 3 + asyncio** — one event loop
- **Event bus** — every state change is an event
- **State machine** — in-memory, rebuilt at startup
- **Integrations** — one async library per ecosystem

</div>
<div>

- **Services** — registered actions with validated schemas
- **Recorder** — SQLAlchemy into SQLite (or Postgres)
- **Frontend** — web app over a WebSocket API
- **Automation engine** — triggers subscribe to the bus

</div>
</div>

<br>

![w:860](assets/recorder.svg)

<!--
The event bus is the spine. Recorder is just another subscriber —
it does not sit in the control path, which is why a slow disk does not stop the lights.
-->

---

# SQLite is amazing

<div class="columns">
<div>

- **Public domain**, one file, zero configuration
- The most widely deployed database engine on earth — phones, browsers, cars, aircraft
- **ACID**, with WAL: readers never block the writer
- The file format is portable across platforms and versions
- **Backup is a file copy** — or one command
- No server, no port, no auth surface to expose
- 281 TB theoretical limit; you will not reach it
- 25+ years of adversarial testing

</div>
<div>

```bash
# consistent backup while it runs
sqlite3 home-assistant_v2.db \
  ".backup '/backup/ha.db'"

# or a compacted copy
sqlite3 home-assistant_v2.db \
  "VACUUM INTO '/backup/ha.db'"

# is it healthy?
sqlite3 home-assistant_v2.db \
  "PRAGMA integrity_check;"
```

<div class="callout quiet">

The boring choice that outlives your hardware. That is a compliment.

</div>

</div>
</div>

---

# SQLite inside Home Assistant

<div class="columns">
<div>

- Database: `config/home-assistant_v2.db`
- Written by `recorder` in **batches**, not per event
- `purge_keep_days` trims raw history (default 10 days)
- **Long-term statistics** keep hourly aggregates forever
- `recorder:` include/exclude keeps the file small
- Default because it is genuinely enough for most homes

</div>
<div>

```yaml
recorder:
  purge_keep_days: 14
  commit_interval: 5
  exclude:
    domains:
      - media_player
    entity_globs:
      - sensor.*_signal_strength
```

</div>
</div>

<div class="callout">

A home is a low-write workload with occasional bursts. This is exactly the shape SQLite handles well.

</div>

---

<!-- _class: compact -->

# You can interrogate the database directly

```bash
sqlite3 -readonly config/home-assistant_v2.db
```

```sql
SELECT sm.entity_id, s.state, s.last_updated_ts
FROM states s
JOIN states_meta sm ON sm.metadata_id = s.metadata_id
WHERE sm.entity_id = 'sensor.washer_power'
ORDER BY s.last_updated_ts DESC
LIMIT 10;
```

<div class="columns">
<div>

- `states` + `states_meta` — the raw event log
- `statistics` — long-term aggregates
- `events` — non-state events
- Timestamps are Unix epoch floats

</div>
<div>

- Open **read-only** while HA is running
- `EXPLAIN QUERY PLAN` before you blame the disk
- The file is portable: copy it anywhere and query it
- Never put it on NFS or SMB

</div>
</div>

<div class="callout warn">

A live `cp` can capture a torn write. Use `.backup` or `VACUUM INTO`.

</div>

---

# When SQLite is not enough

Home Assistant does support Postgres

<div class="columns">
<div>

**Stay on SQLite if…**

- one Home Assistant instance
- tens of thousands of state changes per day
- history measured in weeks
- you value a single portable file

</div>
<div>

**Move to Postgres if…**

- very large installs with high event rates
- multiple writers or shared reporting
- long raw retention, external BI tools
- you already operate Postgres well

</div>
</div>

```yaml
recorder:
  db_url: postgresql://user:pass@host/homeassistant
```

<div class="callout quiet">

Move for a measured reason, not for fashion. In most homes SQLite is not the bottleneck — the radio is.

</div>

---

# Some screenshots 


---

<!-- _class: screenshot -->

# Temp / Humidity 

![alt text](assets/temp-humid.png)

---

<!-- _class: screenshot -->

## EV 

<div class="image-pair">

![h:245](assets/ev-controls.png)

![h:360](assets/ev-sensors.png)

</div>


---

<!-- _class: screenshot -->

# Mesh repeater 

![alt text](assets/mesh-repeater-battery.png)

---

<!-- _class: screenshot -->

# Mesh repeater 

![alt text](assets/mesh-node-count.png)

---

<!-- _class: screenshot -->

# Messages Per Minute - Maori Hill Repeater

![alt text](assets/mesh-msgpermin.png)


---

<!-- _class: screenshot -->

# Solar 

![alt text](assets/solar.png)

---

# Recap

<div class="big">

1. **Devices** report observations.
2. **Integrations** translate them into entities.
3. The **state machine** holds one live truth.
4. **Automations** watch for changes and decide.
5. **Services** act on the world — and the loop repeats.

</div>

<br>

<div class="callout">

Thing in your house can feed a state engine. Home Assistant ties it all together.

</div>

---

<!-- _class: lead -->
<!-- _footer: '' -->

# Questions?

## home-assistant.io · developers.home-assistant.io · sqlite.org

https://jduckles.github.io/talkhass
