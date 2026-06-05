# DesktopCat Companion Experience Roadmap

## Purpose

DesktopCat is a gift-like desktop companion for a long-distance relationship.
The goal is not to build a complex pet game. The goal is to give the user's
partner a gentle, cute kitten on her desktop that can quietly carry care,
miss-you moments, reminders, and emotional support while both people are busy
with school and living far apart.

The product direction remains:

```text
polished sprite pet first -> low-burden companion behaviors -> gift-quality packaging
```

Do not add heavy raising systems, shops, currencies, or complex daily chores
unless they directly support the feeling of companionship without adding
burden.

## Design Principles

- Keep the kitten cute, stable, and non-disruptive.
- Prefer offline companion value before networked features.
- Make every feature feel like care from the user, not generic app noise.
- Avoid asking the partner to configure technical settings.
- Preserve the full-transparent PNG animation pipeline and QA gates.
- Keep reminders gentle and dismissible.
- Let busy mode reduce interruption rather than add tasks.

## Priority 1: Offline Companion Message Pack

This is the highest-priority companion upgrade.

### Goal

Let the user prepare a private set of affectionate, encouraging, and practical
messages. DesktopCat then says them at appropriate times, so the partner feels
the user's presence even when no network or live messaging is available.

### Scope

- Add a dedicated offline companion message pack, for example:
  `assets/companion_messages/partner_default.json` or a user config file.
- Support message categories:
  - morning
  - lunch
  - afternoon
  - evening
  - bedtime
  - late_night
  - busy_support
  - miss_you
  - comfort
  - encouragement
- Reuse existing speech bubble behavior.
- Avoid repeating the same message too often.
- Allow each message to optionally define:
  - text
  - time window
  - weight or priority
  - cooldown days
  - optional action such as `wave`, `cute`, `happy`, or `sleep`

### Example Messages

```text
今天也要慢慢来，不要一醒来就把自己绷太紧。
小猫替我监督你吃饭啦，不许随便糊弄过去。
忙了一天辛苦啦，看到小猫就当我抱你一下。
如果还没睡，小猫要皱眉了。我也会心疼的。
今天也很想你，但我们都先把眼前的事做好。
```

### Acceptance

- The feature works fully offline.
- No message requires network setup.
- Messages do not spam the user.
- Time-based messages do not conflict with existing meal/sleep reminders.
- The partner can dismiss a message without disabling the whole pet.

## Priority 2: Busy Low-Distraction Mode

### Goal

Support the partner when she is busy with study or work. In this mode, the
kitten stays present but quiet.

### Scope

- Add a mode named `忙碌陪伴模式` or `低打扰模式`.
- Reduce random speech frequency.
- Prefer calm actions: `idle`, `blink`, `sleep`, and rare `wave`.
- Keep essential reminders:
  - meal reminders
  - hydration or short rest prompts
  - bedtime prompts
- Add optional focus blocks such as 45 or 60 minutes.
- After a focus block, the kitten gently suggests a break.

### Acceptance

- The mode can be toggled from the context menu or config.
- It does not introduce panels, timers, or controls that feel like another
  productivity app to manage.
- It reduces interruption compared with normal mode.
- It remains visually alive through subtle animation.

## Priority 3: Time-Aware Living Rhythm

### Goal

Make DesktopCat feel like it lives through the day with the partner rather
than randomly swapping animations.

### Scope

- Morning: more awake, gentle greetings.
- Afternoon: quiet companionship and occasional encouragement.
- Evening: warmer messages after a busy day.
- Late night: calmer visuals, sleepier behavior, stronger rest prompts.
- Deep night: avoid playful interruptions; focus on care and rest.

### Implementation Notes

- Extend the existing `time_reminders.py` direction rather than creating a
  separate scheduling system.
- Keep behavior deterministic enough to test with launcher preview flags.
- Add test times for each time window.

### Acceptance

- Time windows are explicit and testable.
- Messages and actions match the time of day.
- Late-night behavior feels caring, not scolding or noisy.

## Priority 4: Life-Like Animation Polish

### Goal

Improve the feeling that the kitten is a real desktop companion by making
motion transitions and idle behavior more natural.

### Scope

- Keep the V2 animation contract:
  every non-idle action starts and ends idle-compatible.
- Improve transition selection:
  - `idle -> blink -> idle`
  - `idle -> wave -> idle`
  - `idle -> sleep_in -> sleep -> wake -> idle`
- Tune random action frequency so the kitten is noticeable but not distracting.
- Keep `sleep`, `wake`, `idle`, and `blink` especially polished because these
  are the most visible low-distraction states.

### Acceptance

- No action visually jumps at first or last frame.
- The kitten does not feel hyperactive.
- Busy mode and evening mode prefer calmer animations.
- Candidate changes pass visual QA before promotion.

## Priority 5: Gift-Quality Setup And Packaging

### Goal

Make the pet easy to give and easy to run on the partner's computer.

### Scope

- Package a stable `.exe`.
- Keep first launch simple:
  - create config automatically
  - start near the screen corner
  - show one gentle arrival message
- Keep essential tray/context menu controls:
  - show/hide
  - reset position
  - open config
  - toggle autostart
  - toggle low-distraction mode
  - quit
- Avoid requiring the partner to edit JSON for normal use.

### Acceptance

- Fresh launch works without developer tools.
- Reset position can recover from off-screen placement.
- Quit works cleanly with no lingering process.
- The packaged app is smoke-tested before delivery.

### Next Gift Polish Pass

The next optimization pass should make the current `DesktopCatGift` package
feel less like a developer artifact and more like a finished personal gift.
Adopt the following medium/high-priority improvements:

- Add a short partner-facing `README_先看我.txt` to the gift package with
  first-run, quit, and config-editing instructions.
- Check and fix Chinese UI/menu/config text so first launch, right-click menu,
  reminder buttons, and generated config README do not show mojibake.
- Improve the first-launch experience with one warmer, more personal arrival
  message and avoid immediate competing bubbles.
- Add two offline, low-burden couple-specific context-menu interactions:
  `我想他了` and `今天辛苦啦`.
- Reduce packaged zip size by including only the runtime assets needed by
  `DesktopCatGift`, especially the active candidate batch and companion message
  files, not raw experiments, QA artifacts, old batches, or references.
- Add a kitten app icon for the packaged executable.
- Restore the last valid on-screen position on restart, while falling back to
  the default corner if the saved position is off-screen.

Explicitly do **not** make low-distraction mode the default in this pass.

## Priority 6: Couple-Specific Touches

### Goal

Make the pet feel specifically made for this relationship, not like a generic
desktop pet.

### Candidate Features

- Meet-again countdown.
- Special day messages, such as birthdays, anniversaries, exams, deadlines,
  or planned visits.
- Custom nickname support.
- A menu item like `我想他了`, where the kitten says one of the user's prepared
  comforting replies.
- A `今天辛苦啦` interaction that gives a gentle affirmation.
- Optional seasonal or exam-week message packs.

### Acceptance

- Features remain offline-first.
- The partner does not need to manage a new system.
- Text feels personal and warm.
- Messages can be edited safely without changing code.

## Deferred: Networked Partner Messaging

The Supabase-based "send a live message to the partner's kitten" direction is
valuable but deferred.

### Reason

It requires setup on the partner's computer, Supabase configuration, accounts,
pairing data, and privacy-sensitive configuration. It should resume only when
both computers can be configured directly.

### Current Status

The prototype implementation has been saved outside the active working tree as
a Git stash:

```text
stash@{0}: On main: cat messaging mvp WIP
```

When ready to resume, restore and review it before continuing:

```powershell
git stash apply stash@{0}
```

Do not make network messaging part of the current active roadmap until the
offline companion experience and gift packaging are strong.

## Explicit Non-Goals For Now

- Feeding, hunger, coins, shops, or daily chores.
- AI chat as the main experience.
- Voice, image, or file messaging.
- Large settings panels.
- High-frequency notifications.
- Any feature that makes the partner feel she must maintain the pet.

## Recommended Next Implementation Order

1. Offline companion message pack.
2. Busy low-distraction mode.
3. Time-aware living rhythm polish.
4. Speech bubble and reminder visual polish.
5. Gift-quality packaging.
6. Couple-specific touches.
7. Resume networked messaging only when both computers can be configured.
