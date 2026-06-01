# DesktopCat Frame Generation Prompts V1

Use these prompts only after checking `docs/character-spec.md` and the action reference crops in `assets/action_refs`.

## Shared Identity Prompt

Same character in every frame: a cute high-quality 3D chibi cream orange-and-white kitten, big head and short round plush body, large round glossy deep-brown eyes with bright highlights, small pink nose, tiny soft w-shaped mouth, pale pink cheek blush, cream orange tabby forehead and cheek stripes, white muzzle, chest, belly and paws, big triangular ears with soft pink-orange inner ears, thin pale whiskers, short fluffy curled tail with orange ring markings, large pink-brown checked bow at the neck, small shiny gold bell centered on the bow. Soft premium 3D cartoon render, plush toy texture, warm edge light, full body visible, clean silhouette.

Hard rules: transparent background, no text, no watermark, no scenery, no props, no extra symbols, do not change the bow color, do not remove the gold bell, do not change the eye color, do not make a realistic cat, do not crop ears, paws, bow, bell, or tail.

Canvas: 512x512 PNG per frame, same scale, same floor baseline, full body visible.

## Batch Prompts

### idle

Create a 6-frame sprite strip for the same DesktopCat kitten sitting front-facing with front paws together. The motion is tiny and calm: soft breathing, very subtle body rise and fall, slow tail sway. Keep head, bow, bell, paws, and body scale consistent across frames.

### blink

Create a 4-frame sprite strip for the same DesktopCat kitten in the idle sitting pose. Eyes go open, half-closed, closed smiling, open again. No body pose change except tiny breathing. Keep the same baseline and scale.

### clicked

Create a 5-frame sprite strip for the same DesktopCat kitten reacting to a mouse click. The kitten looks surprised and cute: eyes widen, ears perk, body pops up slightly, then settles back. Keep bow and bell centered and visible. No comic symbols.

### happy

Create a 6-frame sprite strip for the same DesktopCat kitten happily bouncing in place. Eyes bright, blush slightly stronger, tail lifted and swaying, paws cute and rounded. Motion should be readable but gentle for a desktop pet.

### wave

Create a 6-frame sprite strip for the same DesktopCat kitten sitting and waving one front paw. The raised paw moves side to side while the other paw stays planted. Expression is gentle and affectionate. Keep bow and bell clear.

### sleep

Create a 6-frame sprite strip for the same DesktopCat kitten curled or lying down sleeping. Eyes closed, tail near the body, breathing very subtle. Full body visible, no Z letters, no blanket, no props.

### walk

Create an 8-frame sprite strip for the same DesktopCat kitten walking to the right with short alternating steps. Body gently bobs, tail follows, bell swings slightly. Keep scale and floor baseline stable so it can loop cleanly.

### drag

Create a 4-frame sprite strip for the same DesktopCat kitten being dragged. Front paws are slightly lifted, body hangs softly, expression puzzled but cute. Gentle dangling motion only. Keep full body visible and accessories consistent.

## Acceptance Before App Integration

- Every action is exported as separate transparent PNG frames in `assets/sprites/<action>/00.png`.
- All frames are the same `512x512` size.
- Character identity and accessories remain stable.
- The first generated batch must be reviewed as a contact sheet before touching runtime code.
