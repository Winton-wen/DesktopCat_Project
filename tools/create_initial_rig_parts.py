from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "sprites" / "idle" / "00.png"
BLINK_SOURCE = ROOT / "assets" / "sprites" / "blink" / "05.png"
WAVE_SOURCE = ROOT / "assets" / "sprites" / "wave" / "08.png"
CLICKED_SOURCE = ROOT / "assets" / "sprites" / "clicked" / "04.png"
HAPPY_SOURCE = ROOT / "assets" / "sprites" / "happy" / "13.png"
SLEEP_SOURCE = ROOT / "assets" / "sprites" / "sleep" / "05.png"
DRAG_SOURCE = ROOT / "assets" / "sprites" / "drag" / "04.png"
OUTPUT = ROOT / "assets" / "rig_parts" / "desktop_cat"


def masked_crop(source: Image.Image, box: tuple[int, int, int, int], shape: str) -> Image.Image:
    crop = source.crop(box)
    mask = Image.new("L", crop.size, 0)
    draw = ImageDraw.Draw(mask)
    w, h = crop.size
    if shape == "ellipse":
        draw.ellipse((0, 0, w - 1, h - 1), fill=255)
    elif shape == "upper_ellipse":
        draw.ellipse((0, 0, w - 1, int(h * 1.18)), fill=255)
    elif shape == "left_ear":
        draw.polygon([(0, h), (int(w * 0.58), 0), (w, h)], fill=255)
    elif shape == "right_ear":
        draw.polygon([(0, h), (int(w * 0.42), 0), (w, h)], fill=255)
    elif shape == "tail_segment":
        draw.rounded_rectangle((0, 0, w - 1, h - 1), radius=max(8, min(w, h) // 2), fill=255)
    elif shape == "soft_rect":
        draw.rounded_rectangle((0, 0, w - 1, h - 1), radius=max(10, min(w, h) // 3), fill=255)
    elif shape == "raised_paw":
        draw.polygon(
            [
                (int(w * 0.18), int(h * 0.02)),
                (int(w * 0.70), 0),
                (int(w * 0.94), int(h * 0.33)),
                (int(w * 0.84), int(h * 0.74)),
                (int(w * 0.58), h - 1),
                (int(w * 0.16), int(h * 0.94)),
                (0, int(h * 0.48)),
            ],
            fill=255,
        )
    elif shape == "source_alpha":
        mask = crop.getchannel("A")
    else:
        draw.rectangle((0, 0, w - 1, h - 1), fill=255)
    if shape != "source_alpha":
        mask = mask.filter(ImageFilter.GaussianBlur(1.2))
    crop.putalpha(Image.composite(crop.getchannel("A"), Image.new("L", crop.size, 0), mask))
    return crop


def eyelid(size: tuple[int, int], color: tuple[int, int, int, int]) -> Image.Image:
    image = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    mid_y = size[1] // 2
    draw.rounded_rectangle((2, mid_y - 8, size[0] - 3, mid_y + 8), radius=8, fill=color)
    draw.arc((2, mid_y - 15, size[0] - 3, mid_y + 18), 185, 355, fill=(88, 48, 34, 210), width=3)
    return image.filter(ImageFilter.GaussianBlur(0.3))


def remove_source_artifacts(image: Image.Image, global_box: tuple[int, int, int, int]) -> Image.Image:
    fixed = image.copy()
    pixels = fixed.load()
    left, top, _, _ = global_box
    for y in range(fixed.height):
        gy = top + y
        for x in range(fixed.width):
            gx = left + x
            r, g, b, a = pixels[x, y]
            if a == 0:
                continue
            pale_artifact = r > 210 and g > 210 and b > 210
            top_dash = 208 <= gx <= 305 and 82 <= gy <= 94 and a < 180 and pale_artifact
            right_guide = 370 <= gx <= 406 and 58 <= gy <= 166 and pale_artifact
            left_guide = 92 <= gx <= 116 and 240 <= gy <= 355 and pale_artifact
            if top_dash or right_guide or left_guide:
                pixels[x, y] = (r, g, b, 0)
    return fixed


def soften_head_eye_sockets(image: Image.Image) -> Image.Image:
    base = image.copy()
    soft = Image.new("RGBA", base.size, (0, 0, 0, 0))
    hard = Image.new("RGBA", base.size, (0, 0, 0, 0))
    soft_draw = ImageDraw.Draw(soft)
    hard_draw = ImageDraw.Draw(hard)
    fur = (239, 204, 174, 255)
    shadow = (215, 165, 128, 95)
    for box in [(45, 88, 115, 164), (148, 88, 218, 164)]:
        soft_draw.ellipse((box[0] - 4, box[1] - 4, box[2] + 4, box[3] + 4), fill=(239, 204, 174, 210))
        hard_draw.ellipse(box, fill=fur)
        hard_draw.arc((box[0] + 8, box[1] + 12, box[2] - 8, box[3] - 12), 188, 352, fill=shadow, width=2)
    soft = soft.filter(ImageFilter.GaussianBlur(4.0))
    return Image.alpha_composite(Image.alpha_composite(base, soft), hard)


def write_parts() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    source = Image.open(SOURCE).convert("RGBA")
    blink_source = Image.open(BLINK_SOURCE).convert("RGBA")
    wave_source = Image.open(WAVE_SOURCE).convert("RGBA")
    clicked_source = Image.open(CLICKED_SOURCE).convert("RGBA")
    happy_source = Image.open(HAPPY_SOURCE).convert("RGBA")
    sleep_source = Image.open(SLEEP_SOURCE).convert("RGBA")
    drag_source = Image.open(DRAG_SOURCE).convert("RGBA")
    specs = [
        ("tail_01", "tail_01.png", (354, 278, 420, 438), "tail_segment", None, (12, 140), (354, 278), 5, [-18, 18]),
        ("tail_02", "tail_02.png", (360, 278, 425, 385), "tail_segment", "tail_01", (18, 92), (360, 278), 6, [-20, 20]),
        ("tail_03", "tail_03.png", (358, 269, 416, 340), "tail_segment", "tail_02", (23, 62), (358, 269), 7, [-24, 24]),
        ("body", "body.png", (137, 226, 367, 494), "ellipse", None, (115, 238), (137, 226), 10, [-6, 6]),
        ("paw_back_left", "paw_back_left.png", (104, 376, 183, 489), "ellipse", "body", (42, 88), (104, 376), 16, [-12, 12]),
        ("paw_back_right", "paw_back_right.png", (285, 376, 364, 489), "ellipse", "body", (38, 88), (285, 376), 16, [-12, 12]),
        ("head", "head.png", (96, 56, 416, 303), "source_alpha", None, (160, 196), (96, 56), 30, [-4, 4]),
        ("ear_left", "ear_left.png", (105, 62, 190, 160), "left_ear", "head", (60, 83), (105, 62), 34, [-12, 12]),
        ("ear_right", "ear_right.png", (312, 62, 397, 160), "right_ear", "head", (25, 83), (312, 62), 34, [-12, 12]),
        ("eye_left", "eye_left.png", (156, 160, 205, 219), "ellipse", "head", (24, 30), (156, 160), 45, [-4, 4]),
        ("eye_right", "eye_right.png", (258, 160, 307, 219), "ellipse", "head", (24, 30), (258, 160), 45, [-4, 4]),
        ("eyelid_left", "eyelid_left.png", (120, 135, 232, 235), "blink_patch", "head", (58, 50), (120, 135), 48, [-4, 4]),
        ("eyelid_right", "eyelid_right.png", (230, 135, 342, 235), "blink_patch", "head", (58, 50), (230, 135), 48, [-4, 4]),
        ("mouth_open", "mouth_open.png", (218, 205, 273, 269), "clicked_patch", "head", (28, 35), (218, 205), 49, [-6, 6]),
        ("paw_front_left", "paw_front_left.png", (178, 324, 235, 492), "ellipse", "body", (28, 151), (178, 324), 38, [-16, 16]),
        ("paw_front_right", "paw_front_right.png", (235, 324, 292, 492), "ellipse", "body", (29, 151), (235, 324), 38, [-16, 16]),
        ("paw_wave_right", "paw_wave_right.png", (80, 168, 166, 326), "wave_patch", "body", (48, 126), (66, 168), 58, [-28, 28]),
        ("bow_left", "bow_left.png", (135, 257, 233, 354), "ellipse", "body", (88, 45), (135, 257), 50, [-12, 12]),
        ("bow_right", "bow_right.png", (234, 257, 333, 354), "ellipse", "body", (10, 45), (234, 257), 50, [-12, 12]),
        ("bow_center", "bow_center.png", (219, 268, 260, 321), "ellipse", "body", (21, 25), (219, 268), 52, [-8, 8]),
        ("bell", "bell.png", (225, 271, 253, 303), "ellipse", "bow_center", (14, 11), (225, 271), 54, [-20, 20]),
        ("pose_wave", "pose_wave.png", (0, 0, 512, 512), "wave_full", None, (256, 256), (0, 0), 90, [-6, 6]),
        ("pose_clicked", "pose_clicked.png", (0, 0, 512, 512), "clicked_full", None, (256, 256), (0, 0), 90, [-6, 6]),
        ("pose_happy", "pose_happy.png", (0, 0, 512, 512), "happy_full", None, (256, 256), (0, 0), 90, [-8, 8]),
        ("pose_sleep", "pose_sleep.png", (0, 0, 512, 512), "sleep_full", None, (256, 256), (0, 0), 90, [-4, 4]),
        ("pose_drag", "pose_drag.png", (0, 0, 512, 512), "drag_full", None, (256, 256), (0, 0), 90, [-8, 8]),
    ]
    parts = []
    for name, filename, box, shape, parent, pivot, position, z_index, limit in specs:
        if shape == "generated":
            color = (242, 183, 152, 238)
            image = eyelid((box[2] - box[0], box[3] - box[1]), color)
        elif shape == "blink_patch":
            image = masked_crop(blink_source.copy(), box, "soft_rect")
        elif shape == "wave_patch":
            image = masked_crop(wave_source.copy(), box, "raised_paw")
        elif shape == "clicked_patch":
            image = masked_crop(clicked_source.copy(), box, "soft_rect")
        elif shape == "wave_full":
            image = wave_source.copy()
        elif shape == "clicked_full":
            image = clicked_source.copy()
        elif shape == "happy_full":
            image = happy_source.copy()
        elif shape == "sleep_full":
            image = sleep_source.copy()
        elif shape == "drag_full":
            image = drag_source.copy()
        else:
            image = masked_crop(source.copy(), box, shape)
        image = remove_source_artifacts(image, box)
        image.save(OUTPUT / filename)
        parts.append(
            {
                "name": name,
                "file": filename,
                "parent": parent,
                "pivot": list(pivot),
                "position": list(position),
                "z_index": z_index,
                "scale": 1.0,
                "rotation_limit": limit,
            }
        )

    rig = {
        "name": "desktop_cat_pseudo_live2d_v1",
        "source_image": str(SOURCE.relative_to(ROOT)).replace("\\", "/"),
        "canvas_size": [512, 512],
        "notes": [
            "Initial source-derived layered rig for QA preview only.",
            "Current sprite runtime remains the production fallback.",
        ],
        "parts": parts,
    }
    (OUTPUT / "rig.json").write_text(json.dumps(rig, indent=2), encoding="utf-8")


if __name__ == "__main__":
    write_parts()
