from __future__ import annotations

import math
from dataclasses import dataclass

from .model import RigModel


@dataclass(frozen=True)
class PartPose:
    offset: tuple[float, float] = (0.0, 0.0)
    rotation: float = 0.0
    scale: float | tuple[float, float] = 1.0
    opacity: float = 1.0


@dataclass(frozen=True)
class RigPose:
    parts: dict[str, PartPose]


class RigAnimation:
    def __init__(self, model: RigModel) -> None:
        self.model = model

    def pose(self, action: str, phase: float) -> RigPose:
        phase = phase % 1.0
        if action == "blink":
            return self._blink(phase)
        if action == "wave":
            return self._wave(phase)
        if action == "clicked":
            return self._clicked(phase)
        if action == "happy":
            return self._happy(phase)
        if action == "sleep":
            return self._full_pose("pose_sleep", phase, sway=0.6, breathe=1.5)
        if action == "drag":
            return self._full_pose("pose_drag", phase, sway=2.2, breathe=0.8)
        return self._idle(phase)

    def _base(self) -> dict[str, PartPose]:
        parts = {name: PartPose() for name in self.model.parts}
        for hidden in [
            "ear_left",
            "ear_right",
            "paw_wave_right",
            "mouth_open",
            "pose_wave",
            "pose_clicked",
            "pose_happy",
            "pose_sleep",
            "pose_drag",
        ]:
            if hidden in parts:
                parts[hidden] = PartPose(opacity=0.0)
        return parts

    def _idle(self, phase: float) -> RigPose:
        wave = math.sin(phase * math.tau)
        slow_wave = math.sin((phase * math.tau) - 0.7)
        parts = self._base()
        parts.update(
            {
                "body": PartPose(offset=(0.0, 2.0 * wave), scale=1.0 + 0.008 * wave),
                "head": PartPose(offset=(0.0, -1.5 * wave), rotation=1.2 * slow_wave),
                "eye_left": PartPose(offset=(0.0, -1.5 * wave), rotation=0.5 * slow_wave),
                "eye_right": PartPose(offset=(0.0, -1.5 * wave), rotation=0.5 * slow_wave),
                "eyelid_left": PartPose(opacity=0.0),
                "eyelid_right": PartPose(opacity=0.0),
                "tail_01": PartPose(rotation=2.0 * slow_wave),
                "tail_02": PartPose(rotation=4.0 * slow_wave),
                "tail_03": PartPose(rotation=5.0 * slow_wave),
                "bell": PartPose(offset=(0.4 * slow_wave, 1.0 * abs(wave)), rotation=2.0 * slow_wave),
            }
        )
        return RigPose(parts)

    def _blink(self, phase: float) -> RigPose:
        idle = self._idle(phase).parts
        if phase < 0.25:
            close = phase / 0.25
        elif phase < 0.62:
            close = 1.0
        elif phase < 0.9:
            close = 1.0 - ((phase - 0.62) / 0.28)
        else:
            close = 0.0

        parts = dict(idle)
        eye_scale = (1.0, max(0.08, 1.0 - close * 0.92))
        parts["eye_left"] = PartPose(offset=(0.0, -1.0 + close * 11.0), scale=eye_scale, opacity=1.0 - close)
        parts["eye_right"] = PartPose(offset=(0.0, -1.0 + close * 11.0), scale=eye_scale, opacity=1.0 - close)
        parts["eyelid_left"] = PartPose(offset=(0.0, -1.0), opacity=close)
        parts["eyelid_right"] = PartPose(offset=(0.0, -1.0), opacity=close)
        return RigPose(parts)

    def _clicked(self, phase: float) -> RigPose:
        if "pose_clicked" in self.model.parts:
            parts = {name: PartPose(opacity=0.0) for name in self.model.parts}
            pop = math.sin(min(1.0, phase / 0.65) * math.pi)
            settle = 1.0 - self._smoothstep(max(0.0, phase - 0.55) / 0.45)
            energy = max(0.15, pop * settle)
            parts["pose_clicked"] = PartPose(
                offset=(0.0, -8.0 * energy),
                scale=1.0 + 0.035 * energy,
                rotation=-1.5 * math.sin(phase * math.tau) * energy,
                opacity=1.0,
            )
            if "mouth_open" in parts:
                parts["mouth_open"] = PartPose(opacity=1.0)
            return RigPose(parts)

        parts = dict(self._idle(phase).parts)
        pop = math.sin(min(1.0, phase / 0.7) * math.pi)
        settle = 1.0 - self._smoothstep(max(0.0, phase - 0.55) / 0.45)
        energy = max(0.0, pop * settle)
        parts["body"] = PartPose(offset=(0.0, -7.0 * energy), scale=1.0 + 0.04 * energy)
        parts["head"] = PartPose(offset=(0.0, -11.0 * energy), scale=1.0 + 0.025 * energy, rotation=-1.5 * energy)
        parts["ear_left"] = PartPose(offset=(-1.5 * energy, -13.0 * energy), rotation=-5.0 * energy)
        parts["ear_right"] = PartPose(offset=(1.5 * energy, -13.0 * energy), rotation=5.0 * energy)
        parts["eye_left"] = PartPose(offset=(-1.0 * energy, -10.0 * energy), scale=1.0 + 0.08 * energy)
        parts["eye_right"] = PartPose(offset=(1.0 * energy, -10.0 * energy), scale=1.0 + 0.08 * energy)
        if "mouth_open" in parts:
            parts["mouth_open"] = PartPose(offset=(0.0, -8.0 * energy), scale=0.7 + 0.35 * energy, opacity=energy)
        parts["paw_front_left"] = PartPose(offset=(-11.0 * energy, -45.0 * energy), rotation=-18.0 * energy)
        parts["paw_front_right"] = PartPose(offset=(11.0 * energy, -45.0 * energy), rotation=18.0 * energy)
        parts["bell"] = PartPose(offset=(2.0 * energy, -2.0 * energy), rotation=16.0 * math.sin(phase * math.tau * 2.0) * energy)
        return RigPose(parts)

    def _happy(self, phase: float) -> RigPose:
        if "pose_happy" in self.model.parts:
            parts = {name: PartPose(opacity=0.0) for name in self.model.parts}
            bounce = abs(math.sin(phase * math.tau))
            wag = math.sin(phase * math.tau * 3.0)
            parts["pose_happy"] = PartPose(
                offset=(0.0, -10.0 * bounce),
                scale=1.0 + 0.025 * bounce,
                rotation=1.2 * wag,
                opacity=1.0,
            )
            if "paw_wave_right" in parts:
                parts["paw_wave_right"] = PartPose(opacity=1.0)
            return RigPose(parts)

        parts = dict(self._wave(phase).parts)
        bounce = abs(math.sin(phase * math.tau))
        wag = math.sin(phase * math.tau * 4.0)
        parts["body"] = PartPose(offset=(0.0, -8.0 * bounce), scale=1.0 + 0.025 * bounce)
        parts["head"] = PartPose(offset=(0.0, -11.0 * bounce), rotation=2.0 * math.sin(phase * math.tau))
        parts["eye_left"] = PartPose(offset=(0.0, -10.0 * bounce), scale=(1.04, 1.08))
        parts["eye_right"] = PartPose(offset=(0.0, -10.0 * bounce), scale=(1.04, 1.08))
        if "mouth_open" in parts:
            parts["mouth_open"] = PartPose(offset=(0.0, -9.0 * bounce), scale=0.8 + 0.25 * bounce, opacity=0.85)
        if "paw_wave_right" in parts:
            parts["paw_wave_right"] = PartPose(offset=(-3.0, -8.0 - 10.0 * bounce), rotation=-10.0 + 13.0 * wag, opacity=1.0)
        parts["paw_front_left"] = PartPose(offset=(-8.0, -32.0 - 10.0 * bounce), rotation=-12.0)
        parts["tail_01"] = PartPose(rotation=8.0 + 7.0 * wag)
        parts["tail_02"] = PartPose(rotation=12.0 + 10.0 * wag)
        parts["tail_03"] = PartPose(rotation=16.0 + 12.0 * wag)
        parts["bell"] = PartPose(offset=(2.5 * wag, -3.0 * bounce), rotation=18.0 * wag)
        return RigPose(parts)

    def _full_pose(self, pose_part: str, phase: float, sway: float, breathe: float) -> RigPose:
        parts = {name: PartPose(opacity=0.0) for name in self.model.parts}
        wave = math.sin(phase * math.tau)
        if pose_part in parts:
            parts[pose_part] = PartPose(
                offset=(0.0, breathe * wave),
                rotation=sway * math.sin(phase * math.tau - 0.5),
                scale=1.0 + 0.006 * wave,
                opacity=1.0,
            )
        return RigPose(parts)

    def _wave(self, phase: float) -> RigPose:
        if "pose_wave" in self.model.parts:
            parts = {name: PartPose(opacity=0.0) for name in self.model.parts}
            lift = self._smoothstep(min(1.0, phase / 0.28)) if phase < 0.5 else self._smoothstep(max(0.0, (1.0 - phase) / 0.32))
            wiggle = math.sin(phase * math.tau * 3.0)
            parts["pose_wave"] = PartPose(
                offset=(0.0, -4.0 * lift),
                scale=1.0 + 0.012 * lift,
                rotation=0.8 * wiggle * lift,
                opacity=1.0,
            )
            return RigPose(parts)

        parts = dict(self._idle(phase).parts)
        lift = self._smoothstep(min(1.0, phase / 0.28)) if phase < 0.5 else self._smoothstep(max(0.0, (1.0 - phase) / 0.32))
        wiggle = math.sin(phase * math.tau * 3.0)

        parts["body"] = PartPose(offset=(0.0, -2.0 * lift), scale=1.0 + 0.01 * lift)
        parts["head"] = PartPose(offset=(0.0, -4.0 * lift), rotation=-1.0 * lift)
        parts["ear_left"] = PartPose(offset=(0.0, -4.0 * lift), rotation=-1.0 * lift)
        parts["ear_right"] = PartPose(offset=(0.0, -4.0 * lift), rotation=-1.0 * lift)
        parts["eye_left"] = PartPose(offset=(0.0, -4.0 * lift))
        parts["eye_right"] = PartPose(offset=(0.0, -4.0 * lift))
        parts["paw_front_right"] = PartPose(
            offset=(-18.0 * lift, -74.0 * lift),
            rotation=-22.0 * lift + 13.0 * wiggle * lift,
            opacity=1.0 - lift,
        )
        if "paw_wave_right" in parts:
            parts["paw_wave_right"] = PartPose(
                offset=(-3.0 * lift, -4.0 * lift),
                rotation=-5.0 * lift + 10.0 * wiggle * lift,
                opacity=lift,
            )
        parts["paw_front_left"] = PartPose(offset=(1.0 * lift, -3.0 * lift), rotation=3.0 * lift)
        parts["bow_right"] = PartPose(offset=(-1.5 * lift, -2.0 * lift), rotation=-3.0 * lift)
        parts["bow_center"] = PartPose(offset=(0.0, -2.0 * lift), rotation=2.0 * wiggle * lift)
        parts["bell"] = PartPose(offset=(2.0 * wiggle * lift, -1.5 * lift), rotation=8.0 * wiggle * lift)
        parts["tail_01"] = PartPose(rotation=4.0 * lift + 4.0 * wiggle * lift)
        parts["tail_02"] = PartPose(rotation=6.0 * lift + 6.0 * wiggle * lift)
        parts["tail_03"] = PartPose(rotation=8.0 * lift + 8.0 * wiggle * lift)
        return RigPose(parts)

    @staticmethod
    def _smoothstep(value: float) -> float:
        value = max(0.0, min(1.0, value))
        return value * value * (3.0 - 2.0 * value)
