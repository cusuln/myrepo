"""Simple wave-height calculations using linear wave superposition."""

from dataclasses import dataclass
from math import sin
from typing import Iterable


@dataclass(frozen=True)
class WaveComponent:
    """Parameters for one sinusoidal wave component."""

    amplitude: float
    wave_number: float
    angular_frequency: float
    phase: float = 0.0


def calculate_wave_height(
    x: float,
    time: float,
    waves: Iterable[WaveComponent],
) -> float:
    """Calculate wave height at position ``x`` and time ``time``.

    Each component contributes ``amplitude * sin(wave_number * x
    - angular_frequency * time + phase)``.
    """
    return sum(
        wave.amplitude
        * sin(wave.wave_number * x - wave.angular_frequency * time + wave.phase)
        for wave in waves
    )
