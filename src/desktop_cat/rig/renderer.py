from __future__ import annotations

from functools import cached_property

from PIL import Image

from .animation import RigPose
from .model import RigModel, RigPart


class RigRenderer:
    def __init__(self, model: RigModel) -> None:
        self.model = model

    @cached_property
    def _images(self) -> dict[str, Image.Image]:
        return {
            name: Image.open(part.file).convert("RGBA")
            for name, part in self.model.parts.items()
        }

    def render(self, pose: RigPose) -> Image.Image:
        canvas = Image.new("RGBA", self.model.canvas_size, (0, 0, 0, 0))
        for part in sorted(self.model.parts.values(), key=lambda item: item.z_index):
            part_pose = pose.parts.get(part.name)
            image, transformed_pivot = self._transformed_image(
                part,
                part_pose.scale,
                part_pose.rotation,
                part_pose.opacity,
            )
            x = int(round(part.position[0] + part_pose.offset[0] + part.pivot[0] - transformed_pivot[0]))
            y = int(round(part.position[1] + part_pose.offset[1] + part.pivot[1] - transformed_pivot[1]))
            canvas.alpha_composite(image, (x, y))
        return canvas

    def _transformed_image(
        self,
        part: RigPart,
        pose_scale: float | tuple[float, float],
        rotation: float,
        opacity: float,
    ) -> tuple[Image.Image, tuple[float, float]]:
        source = self._images[part.name]
        if isinstance(pose_scale, tuple):
            scale_x = part.scale * pose_scale[0]
            scale_y = part.scale * pose_scale[1]
        else:
            scale_x = part.scale * pose_scale
            scale_y = part.scale * pose_scale
        if scale_x != 1.0 or scale_y != 1.0:
            size = (max(1, int(source.width * scale_x)), max(1, int(source.height * scale_y)))
            source = source.resize(size, Image.Resampling.LANCZOS)
        pivot = (part.pivot[0] * scale_x, part.pivot[1] * scale_y)
        if rotation:
            pad = int(max(source.width, source.height) * 2)
            stage = Image.new("RGBA", (pad, pad), (0, 0, 0, 0))
            center = (pad / 2.0, pad / 2.0)
            stage.alpha_composite(source, (int(round(center[0] - pivot[0])), int(round(center[1] - pivot[1]))))
            rotated = stage.rotate(rotation, resample=Image.Resampling.BICUBIC, expand=False)
            bbox = rotated.getbbox()
            if bbox:
                source = rotated.crop(bbox)
                pivot = (center[0] - bbox[0], center[1] - bbox[1])
            else:
                source = rotated
                pivot = center
        if opacity < 1.0:
            source = source.copy()
            alpha = source.getchannel("A").point(lambda value: int(value * opacity))
            source.putalpha(alpha)
        return source, pivot
