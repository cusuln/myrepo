"""HTTP API and static page for the wave simulation demo."""

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from math import isfinite
from pathlib import Path

from wave_simulation import WaveComponent, calculate_wave_height


MAX_BODY_SIZE = 128_000
MAX_POSITIONS = 1_000
MAX_WAVES = 20
INDEX_PATH = Path(__file__).with_name("index.html")


def _finite_number(value: object, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a number")
    number = float(value)
    if not isfinite(number):
        raise ValueError(f"{name} must be finite")
    return number


class WaveRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path not in ("/", "/index.html"):
            self.send_error(404)
            return

        page = INDEX_PATH.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(page)))
        self.end_headers()
        self.wfile.write(page)

    def do_POST(self) -> None:
        if self.path != "/api/wave-height":
            self.send_error(404)
            return

        try:
            content_length = int(self.headers.get("Content-Length", ""))
        except ValueError:
            self._send_json(400, {"error": "A valid Content-Length header is required"})
            return

        if content_length < 0:
            self._send_json(400, {"error": "Content-Length must not be negative"})
            return
        if content_length > MAX_BODY_SIZE:
            self._send_json(413, {"error": "Request body is too large"})
            return

        try:
            payload = json.loads(self.rfile.read(content_length))
            samples = self._calculate_samples(payload)
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
            self._send_json(400, {"error": str(error)})
            return

        self._send_json(200, {"samples": samples})

    @staticmethod
    def _calculate_samples(payload: object) -> list[dict[str, float]]:
        if not isinstance(payload, dict):
            raise ValueError("Request body must be a JSON object")

        positions = payload.get("positions")
        raw_waves = payload.get("waves")
        if not isinstance(positions, list) or not positions:
            raise ValueError("positions must be a non-empty array")
        if len(positions) > MAX_POSITIONS:
            raise ValueError(f"positions must contain at most {MAX_POSITIONS} values")
        if not isinstance(raw_waves, list) or len(raw_waves) > MAX_WAVES:
            raise ValueError(f"waves must be an array with at most {MAX_WAVES} values")

        time = _finite_number(payload.get("time"), "time")
        waves = []
        for index, raw_wave in enumerate(raw_waves):
            if not isinstance(raw_wave, dict):
                raise ValueError(f"waves[{index}] must be an object")
            waves.append(
                WaveComponent(
                    amplitude=_finite_number(raw_wave.get("amplitude"), f"waves[{index}].amplitude"),
                    wave_number=_finite_number(raw_wave.get("wave_number"), f"waves[{index}].wave_number"),
                    angular_frequency=_finite_number(
                        raw_wave.get("angular_frequency"),
                        f"waves[{index}].angular_frequency",
                    ),
                    phase=_finite_number(raw_wave.get("phase", 0), f"waves[{index}].phase"),
                )
            )

        return [
            {
                "x": x,
                "height": calculate_wave_height(x, time, waves),
            }
            for x in (_finite_number(value, f"positions[{index}]") for index, value in enumerate(positions))
        ]

    def _send_json(self, status: int, payload: dict[str, object]) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the wave simulation demo server")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), WaveRequestHandler)
    print(f"Wave demo available at http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping wave demo server")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
