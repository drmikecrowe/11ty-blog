---
layout: post
title: "Fun with Home Assistant - Part 2: Auto-Switching My Fire TV's HDMI Input from a USB Switch"
description: "How I wired a physical USB A/B switch to Home Assistant so flipping between my work and home laptops automatically wakes my Fire TV and changes its HDMI input — via ADB, a webhook, and a couple of nasty udev bugs."
date: 2026-06-19T11:00:00.000Z
permalink: /posts/2026/2026-06-19-fun-with-home-assistant-part-2-hdmi-switching/
draft: false
categories:
    - tech
tags:
    - home-assistant
    - fire-tv
    - adb
    - udev
    - home-automation
    - linux
    - webhook
author: Mike Crowe
seo:
    title: "Fun with Home Assistant - Part 2: Fire TV HDMI Switching via USB Switch"
    description: "Flipping a USB A/B switch between two laptops now wakes my Fire TV and changes its HDMI input automatically — using ADB keycodes, a Home Assistant webhook, and udev rules that fought me hard."
    image: images/featured.png
featured_image: images/featured.png
excerpt: "I use a 43-inch Fire TV as my monitor and a USB switch to share my keyboard between my work and home laptops. Now flipping that switch also flips the TV to the right HDMI input — automatically. Here's the ADB, webhook, and udev rabbit hole that made it work."
---

_This post was written with AI assistance (Claude) for structure and formatting. The debugging, the dead ends, and the opinions are entirely my own._

---

**Part 2 of 2: Fun with Home Assistant**

**Series Overview:**
- **Part 1:** [Pulling My Weather Station into Home Assistant with a $40 USB Radio](/posts/2026/2026-06-19-fun-with-home-assistant-part-1-weather-station/) - Capturing 433MHz sensors with an RTL-SDR
- **Part 2:** Auto-Switching My Fire TV's HDMI Input from a USB Switch *(you are here)*

---

Let me set expectations up front:

> **I thought this one would take an afternoon. It ate a weekend.**

In [Part 1](/posts/2026/2026-06-19-fun-with-home-assistant-part-1-weather-station/), the hard part was the *radio*, and the software mostly cooperated. This time it's the reverse: the idea is dead simple, and the software fought me at every single layer.

## Here's the scenario

I run a slightly cursed but genuinely great desk setup. My "monitor" is a 43-inch Insignia 4K Fire TV (model `AFTDCT31`, FireOS 7 / Android 9). It's enormous, it was cheap, and it's a perfectly good display. I love being able to place four screens in quadrants. No more dual monitors for me.

I have two laptops sharing that desk: my home laptop and my work laptop. To switch my keyboard and mouse between them, I use a physical USB A/B switch. Flip it one way and the peripherals talk to the home laptop; flip it the other way and they go to work.

The two laptops are plugged into the TV on **HDMI 1** (home) and **HDMI 2** (work).

So the daily friction is obvious: I flip the USB switch to change keyboards, and then I *also* have to grab the Fire TV remote, hit the input button, and pick the right HDMI. Every. Single. Time. And if the TV happened to be asleep, that's a whole separate wake-it-up dance first.

The goal: flipping the USB switch should be the *only* thing I do. The TV should follow on its own. Wake up if it's off, switch to HDMI 1 when I'm on the home laptop, HDMI 2 when I'm on the work laptop. Zero remotes.

To get there, I enabled ADB debugging on the Fire TV (Settings → Device → Developer Options → ADB Debugging) and added it to Home Assistant via the `androidtv` integration. That gives HA a pipe to send commands to the TV. Easy part done. Now the fun begins.

## Hurdle 1: The "correct" way to switch inputs locks the screen

My first instinct was to do this the *proper* Android way. Android TV has a Television Input Framework (TIF), and each HDMI port is exposed as an input service you can launch with an intent. So I tried:

```bash
am start -a android.intent.action.VIEW \
  -d content://android.media.tv/passthrough/com.mediatek.tvinput%2F.hdmi.HDMIInputService%2FHW4
```

On a normal Android TV, that switches to HDMI 1. On a Fire OS Edition TV, here's where I ran afoul of Amazon's customizations: if you don't have over-the-air channels scanned (I don't; it's a monitor, not a TV), launching that input activity triggers an intent redirect loop straight into `LiveTvSettings`, which nags you to run a channel scan and *locks up the screen*. The TV becomes a brick until you back out manually.

So much for doing it the "right" way.

The fix: skip the framework entirely and send raw keystrokes. The physical input-select behavior is wired to low-level Android keycodes that talk straight to the MediaTek hardware input controller, with no Television Input Framework in the loop and nothing to lock up the screen:

- `243` = `KEYCODE_TV_INPUT_HDMI_1`
- `244` = `KEYCODE_TV_INPUT_HDMI_2`

```bash
# Switch to HDMI 1, instantly, no redirect loop:
input keyevent 243
```

That's it. These fire the same instant hardware switch the remote's input button does. Boring, low-level, and exactly what I wanted.

## Hurdle 2: Home Assistant can't tell me which input is active

The next thing I wanted was to *know* which HDMI input the TV is currently showing, so automations could be smart about it. The `androidtv` integration doesn't expose that. There's no `current_hdmi_input` attribute anywhere.

Here's the secret: the information is buried in the TV's own service dumps. The active hardware input service connection shows up under `dumpsys tv_input`:

```bash
dumpsys tv_input | grep "mInfo: TvInputInfo" | grep -E -o "HW[0-9]+"
```

That spits out `HW4` when HDMI 1 is active, `HW5` for HDMI 2, and **nothing** if the TV is asleep or sitting on the Home screen. I wired that one-liner into an ADB command from Home Assistant and stashed the result in the `adb_response` attribute of the `media_player.office_monitor` entity. Now HA can actually answer "what's on screen right now?"

## The Home Assistant side: a webhook that wakes, waits, and switches

With the two ADB tricks in hand, the HA half is a single automation triggered by a **local webhook**. The laptop hits the webhook, and the automation:

1. Checks if the TV is off/asleep, and if so wakes it (`media_player.turn_on`) and waits 3 seconds for ADB to reconnect.
2. Reads the requested input from the webhook's JSON body and fires the matching keycode.

```yaml
- id: 'office_tv_switch_hdmi_webhook'
  alias: "TV: Switch HDMI via Webhook"
  description: "Switch HDMI input on Office Monitor via local webhook"
  triggers:
    - trigger: webhook
      webhook_id: office_tv_switch_hdmi
      allowed_methods:
        - POST
      local_only: true
  conditions: []
  actions:
    # 1. Turn on the TV if it is currently off/standby/idle
    - if:
        - condition: not
          conditions:
            - condition: state
              entity_id: media_player.office_monitor
              state: "on"
            - condition: state
              entity_id: media_player.office_monitor
              state: "playing"
            - condition: state
              entity_id: media_player.office_monitor
              state: "paused"
            - condition: state
              entity_id: media_player.office_monitor
              state: "idle"
      then:
        - action: media_player.turn_on
          target:
            entity_id: media_player.office_monitor
        - delay: "00:00:03"

    # 2. Trigger the requested input
    - choose:
        # Switch to HDMI 1 (keyevent 243)
        - conditions:
            - condition: template
              value_template: "{{ trigger.json.input == 'hdmi1' }}"
          sequence:
            - action: androidtv.adb_command
              target:
                entity_id: media_player.office_monitor
              data:
                command: "input keyevent 243"
        # Switch to HDMI 2 (keyevent 244)
        - conditions:
            - condition: template
              value_template: "{{ trigger.json.input == 'hdmi2' }}"
          sequence:
            - action: androidtv.adb_command
              target:
                entity_id: media_player.office_monitor
              data:
                command: "input keyevent 244"
  mode: queued
```

Two details worth calling out:

- `local_only: true` — this webhook is only reachable from my LAN. 
- `mode: queued` — if I flip the switch twice quickly, the requests process in order instead of stomping on each other.

Now I just need the laptop to `POST` to that webhook the instant the USB switch changes. On Linux, that means **udev**. And this is where the weekend disappeared.

## Hurdle 3: udev says the rule ran. The webhook says it never arrived.

The plan: a udev rule that fires when the USB switch attaches (I'm on this laptop → HDMI 1) and another when it detaches (I switched away → HDMI 2), each calling a little script that curls the webhook.

My first script backgrounded the curl so the udev event could return quickly. Standard-looking stuff:

```bash
#!/bin/bash
INPUT=$1

# Call local webhook in background
curl -s -X POST -H "Content-Type: application/json" \
     -d "{\"input\":\"$INPUT\"}" \
     https://ha.drmikecrowe.net/api/webhook/office_tv_switch_hdmi &
```

The rule matched. `udevadm` confirmed the script "ran." And nothing happened. The TV never moved. No errors. Just... silence.

Here's the bug, and it's a good one: under modern `systemd-udevd`, `RUN+=` commands execute inside a transient cgroup that udev kills the instant the event handler returns. That `&` I added to be polite? It forks the curl into the background right as udev reaps the entire cgroup and takes my half-sent request with it. The script genuinely ran. The HTTP call never completed.

The fix: launch the work as a *detached* transient unit that outlives the udev event, using `systemd-run --no-block --collect`, and drop the `&`:

```bash
#!/bin/bash
INPUT=$1
CODE=$(curl -s --max-time 10 -o /dev/null -w "%{http_code}" \
     -X POST -H "Content-Type: application/json" \
     -d "{\"input\":\"$INPUT\"}" \
     https://ha.drmikecrowe.net/api/webhook/office_tv_switch_hdmi)
echo "tv-hdmi: input=$INPUT http=$CODE curl_exit=$?"
```

That `echo` logs the HTTP status to the journal so I can actually see whether HA received the call. Foreshadowing: I needed it.

## Hurdle 4: the "remove" rule that refused to fire

The attach rule worked first. The *detach* rule (the one that switches to HDMI 2 when I flip away) would not fire no matter what I did.

I'd read the classic guidance: udev rules matching `ACTION=="remove"` can't use hardware attributes like `ATTRS{idVendor}`, because once the device is unplugged its sysfs attributes are gone. The recommended fix is to match on the *cached environment* properties udev keeps, `ENV{ID_VENDOR_ID}` and `ENV{ID_MODEL_ID}`. So I did that. Still nothing.

Here's where I lost an hour: `udevadm test --action=remove` and `udevadm info` lied to me. Both read the still-cached udev database while the device is *present*, so they happily showed the `ID_VENDOR_ID`/`ID_MODEL_ID` properties, proving my rule "should" match. But those tools were describing a device that wasn't being removed.

So I captured a *real* unplug instead:

```bash
udevadm monitor --environment --udev
```

And the actual removal event for my switch looked like this:

```
ACTION=remove
DEVPATH=.../usb2/2-2
DEVTYPE=usb_device
PRODUCT=2109/817/9013     <-- idVendor/idProduct/bcdDevice (leading zeros stripped)
TYPE=9/0/3
                          <-- NO ID_VENDOR_ID, NO ID_MODEL_ID
```

There it is. The `ID_*` properties are synthesized by udev's `usb_id` builtin *only on `add`*. They are not replayed into the real `remove` uevent. The cached database has them; the live removal event does not. Matching on `ENV{ID_VENDOR_ID}` for a removal is matching on a property that simply isn't there.

The fix: match on `ENV{PRODUCT}`, which is the one identifier present in *both* add and remove events:

```udev
# Hub attached -> HDMI 1
ACTION=="add",    SUBSYSTEM=="usb", ENV{DEVTYPE}=="usb_device", ENV{PRODUCT}=="2109/817/*", RUN+="/usr/bin/systemd-run --no-block --collect /usr/local/bin/toggle_tv_hdmi.sh hdmi1"

# Hub detached -> HDMI 2
ACTION=="remove", SUBSYSTEM=="usb", ENV{DEVTYPE}=="usb_device", ENV{PRODUCT}=="2109/817/*", RUN+="/usr/bin/systemd-run --no-block --collect /usr/local/bin/toggle_tv_hdmi.sh hdmi2"
```

A couple of things baked into those two lines that took real debugging to land on:

- `ENV{PRODUCT}=="2109/817/*"` — note the glob on the last field. `PRODUCT` is `idVendor/idProduct/bcdDevice`, and I don't care about the firmware revision, so I wildcard it.
- `ENV{DEVTYPE}=="usb_device"` — without this, the rule fires once per child USB *interface* instead of once for the device. My switch is a VIA Labs USB3 hub that, annoyingly, enumerates as two devices on every connect: `2109:0817` (the USB 3.0 SuperSpeed hub) and `2109:2817` (a USB 2.0 hub). I match only the USB3 device (`0817`) and constrain to `usb_device`, so each flip fires exactly *once*, not two or four times.

## The debugging playbook (steal this)

This kind of multi-layer automation fails silently at every boundary, so I worked out an order to check things. Future-me will need this; maybe you will too:

1. Did the rule match? `udevadm test --action=add /sys/bus/usb/devices/<path>` and look for `RUN{program}`. (Trustworthy for `add`, misleading for `remove`; see above.)
2. Did the script run, and did curl reach HA? `journalctl -f | rg tv-hdmi`. `http=200` means HA received it; `http=000` means a network/DNS failure from the system context (a common gotcha: the root/udev environment resolves DNS differently than your shell).
3. HA returned 200 but the TV didn't move? It's HA-side. Webhooks return 200 on *receipt*, regardless of whether the automation succeeded. Check the automation Traces and the ADB connection to the TV.
4. The `remove` never fires? Capture a real unplug with `udevadm monitor --environment --udev` and confirm which properties the event *actually* carries.

That second step is why my final script logs the HTTP code. The difference between "the rule didn't match," "curl couldn't reach the network," and "HA got it but the TV ignored it" is three completely different rabbit holes, and you want to know which one you're in *before* you start digging.

## The bonus I didn't plan for

Here's the part that made the whole weekend worth it. Because the HA automation wakes the TV (`media_player.turn_on`) before switching inputs, plugging my laptop into the switch from a *cold, asleep TV* now does both jobs in one motion: the screen wakes up and lands on HDMI 1 automatically. I didn't design that; it just fell out of the "wake if off, then switch" sequence. Flip the switch, and a dark TV comes to life showing exactly the right laptop.

## Reflection: what I gave up

I'll be honest about the trade-offs, because this is held together with some genuinely hacky glue:

- It's brittle to hardware specifics. The keycodes (`243`/`244`), the `dumpsys tv_input` parsing, and the `HW4`/`HW5` mapping are all specific to *this* MediaTek-based Fire TV. A different TV means rediscovering all of it.
- ADB debugging stays on. The Fire TV has ADB enabled permanently for this to work. On a LAN I control I'm fine with that, but it's an attack surface, and you should weigh it.
- udev is unforgiving and lies under test. The biggest lesson here: `udevadm test` reflects the *cached* state, not the live event. For `remove` rules, only a real `udevadm monitor` capture tells the truth.
- Webhooks always return 200. A successful HTTP response proves HA *received* the request, not that the TV did anything. Don't trust the curl exit code as success.
- No status feedback to the laptop. The laptop fires and forgets. If the TV is unplugged or ADB has wandered off, the switch flips and nothing happens, silently. For a daily-driver convenience that's an acceptable failure mode; for anything important, it wouldn't be.

What I gained is exactly what I set out for: I flip one physical switch and my giant Fire-TV-monitor follows, waking from sleep and landing on the right laptop, no remote ever. For a setup I touch a dozen times a day, killing that little friction is worth every hour of the udev fight.

## Close

The whole thing is four small pieces: two ADB keycodes, one Home Assistant webhook automation, one udev rule pair, and a five-line shell script. The hard part was never the code. It was discovering *why* each layer was silently doing nothing.

If you're building something similar, the tools that did the work:

- [**Home Assistant `androidtv` integration**](https://www.home-assistant.io/integrations/androidtv/) — the ADB pipe to the TV
- [**Home Assistant webhook triggers**](https://www.home-assistant.io/docs/automation/trigger/#webhook-trigger) — the LAN-only entry point
- `systemd-run` and `udev` — the Linux glue (`man systemd.exec`, `man udev`)

_Have your own Fire TV / ADB / udev horror stories? Hit me up on [GitHub](https://github.com/drmikecrowe) or wherever you found this post._
