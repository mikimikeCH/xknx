"""Implementation of the KNX date data point."""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from xknx.exceptions import ConversionError

from .dpt import DPTComplex, DPTComplexData
from .payload import DPTArray, DPTBinary


@dataclass
class XYYColor(DPTComplexData):
    """
    Representation of XY color with brightness.

    `color`: tuple(x-axis, y-axis) each 0..1; None if invalid.
    `brightness`: int 0..255; None if invalid.
    """

    color: tuple[float, float] | None = None
    brightness: int | None = None

    def from_dict(self, data: Mapping[str, Any]) -> XYYColor:
        """Init from a dictionary."""
        color = None
        if (x_axis := data.get("x_axis")) is not None and (
            y_axis := data.get("y_axis")
        ) is not None:
            try:
                x_axis = float(data["x_axis"])
                y_axis = float(data["y_axis"])
                if not 0 <= x_axis <= 1 or not 0 <= y_axis <= 1:
                    raise ValueError
                color = (x_axis, y_axis)
            except (ValueError, TypeError):
                raise ConversionError("invalid x_axis or y_axis")

        return XYYColor(color=color, brightness=data.get("brightness"))

    def to_dict(self) -> dict[str, str | int | float | bool | None]:
        """Create a JSON serializable dictionary."""
        return {
            "x_axis": self.color[0] if self.color is not None else None,
            "y_axis": self.color[1] if self.color is not None else None,
            "brightness": self.brightness,
        }


class DPTColorXYY(DPTComplex[XYYColor]):
    """Abstraction for KNX 6 octet color xyY (DPT 242.600)."""

    payload_type = DPTArray
    payload_length = 6

    @classmethod
    def from_knx(cls, payload: DPTArray | DPTBinary) -> XYYColor:
        """Parse/deserialize from KNX/IP raw data."""
        raw = cls.validate_payload(payload)

        x_axis_int = raw[0] << 8 | raw[1]
        y_axis_int = raw[2] << 8 | raw[3]
        brightness = raw[4]

        color_valid = raw[5] >> 1 & 0b1
        brightness_valid = raw[5] & 0b1

        return XYYColor(
            color=(
                # round to 5 digits for better readability but still preserving precision
                round(x_axis_int / 0xFFFF, 5),
                round(y_axis_int / 0xFFFF, 5),
            )
            if color_valid
            else None,
            brightness=brightness if brightness_valid else None,
        )

    @classmethod
    def to_knx(cls, value: XYYColor) -> DPTArray:
        """Serialize to KNX/IP raw data."""
        try:
            color_valid = False
            brightness_valid = False
            x_axis, y_axis, brightness = 0, 0, 0

            if value.color is not None:
                for _ in (axis for axis in value.color if not 0 <= axis <= 1):
                    raise ValueError
                color_valid = True
                x_axis, y_axis = (round(axis * 0xFFFF) for axis in value.color)

            if value.brightness is not None:
                if not 0 <= value.brightness <= 255:
                    raise ValueError
                brightness_valid = True
                brightness = int(value.brightness)

            return DPTArray(
                (
                    x_axis >> 8,
                    x_axis & 0xFF,
                    y_axis >> 8,
                    y_axis & 0xFF,
                    brightness,
                    color_valid << 1 | brightness_valid,
                )
            )
        except (ValueError, TypeError):
            raise ConversionError(f"Could not serialize {cls.__name__}", value=value)
