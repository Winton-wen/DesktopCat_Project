# DesktopCat

DesktopCat is a Windows desktop pet project. The current reset focuses on one thing first: making the kitten animation look polished before adding more systems.

## Current Visual Target

The active character is a cute 3D chibi cream orange-and-white kitten with:

- large glossy deep-brown eyes
- small pink nose and pale blush
- cream orange tabby markings
- white muzzle, chest, belly, and paws
- fluffy ringed tail
- large pink-brown checked bow
- centered shiny gold bell

The current approved direction image is:

```text
assets/concept/desktopcat_action_sheet_v1.png
```

Old generated sprite frames and old build output have been removed. Do not use the previous rough cutout/transform pipeline.

## V1 Scope

V1 should only ship after these animation assets pass visual QA:

- `idle`
- `blink`
- `clicked`
- `happy`
- `wave`
- `sleep`
- `walk`
- `drag`

Runtime features stay minimal:

- transparent desktop pet window
- mouse click reaction
- dragging
- speech bubbles
- tray quit/show controls if already available

Deferred: feeding, status panels, shops, mini-games, anger/eating/stretching systems, and complex settings.

## Asset Workflow

Prepare clean folders:

```powershell
.petvenv\Scripts\python.exe tools\prepare_sprite_workspace.py
```

Extract per-action reference crops from the approved concept sheet:

```powershell
.petvenv\Scripts\python.exe tools\extract_action_refs.py
```

The current generated source strips are stored in:

```text
assets/generated_strips/
```

Process them into transparent 512x512 runtime frames:

```powershell
.petvenv\Scripts\python.exe tools\process_generated_strips.py
```

Create QA contact sheets:

```powershell
.petvenv\Scripts\python.exe tools\make_action_preview.py
.petvenv\Scripts\python.exe tools\make_motion_contact.py
```

QA outputs:

```text
assets/qa/sprite_contact_sheet.png
assets/qa/motion_contact_sheet.png
```

## Development Run

Run the desktop pet locally:

```powershell
powershell -ExecutionPolicy Bypass -File .\run_dev.ps1
```

## Package

Package only after the new sprite assets pass QA:

```powershell
powershell -ExecutionPolicy Bypass -File .\build.ps1
```
