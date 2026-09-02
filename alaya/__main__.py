"""``python -m alaya`` — start the stream with a console attached.

    python -m alaya                       offline: no API key, echo provider
    python -m alaya --provider deepseek   a real sixth consciousness (DEEPSEEK_API_KEY)
    python -m alaya --provider ollama     a local one — no key, nothing leaves the machine
    python -m alaya --no-eye --no-ear     injection only, no hardware
    python -m alaya --say                 speak aloud through macOS `say`
    python -m alaya --listen              transcribe the microphone (needs OpenAI key)
"""
from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path

from alaya.common import Commons
from alaya.console import Console
from alaya.directive import Directive
from alaya.identity import Identity
from alaya.manas import Manas
from alaya.mano import Mano
from alaya.providers import build
from alaya.seeds import SeedStore
from alaya.senses import DormantFaculty, Ear, Eye, Sense, SenseField
from alaya.trisvabhava import RopeSnake

ROOT = Path(__file__).resolve().parent.parent


def whisper_transcriber():
    """Speech-to-text via OpenAI. Remember: a transcript is 比量, never 現量."""
    import io
    import wave

    from openai import OpenAI

    client = OpenAI()

    def transcribe(samples, samplerate):
        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(samplerate)
            wav.writeframes((samples * 32767).astype("int16").tobytes())
        buffer.name = "audio.wav"
        buffer.seek(0)
        return client.audio.transcriptions.create(model="whisper-1", file=buffer).text

    return transcribe


def _load_env(path: Path) -> None:
    """Read KEY=value lines into the environment. Existing values win.

    Deliberately not python-dotenv: this is six lines, and a credential loader
    is a poor place to acquire a dependency.
    """
    if not path.exists():
        raise SystemExit(f"no such env file: {path}")
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip().strip("\"'")
        if value and key not in os.environ:
            os.environ[key] = value


def main() -> None:
    ap = argparse.ArgumentParser(prog="alaya", description="八識 — one stream, eight functions")
    ap.add_argument("--provider", default="echo",
                    choices=["echo", "claude", "openai", "deepseek", "ollama"])
    ap.add_argument("--model", default=None, help="override the provider's default model")
    ap.add_argument("--base-url", default=None,
                    help="any OpenAI-compatible endpoint (vLLM, Together, a proxy)")
    ap.add_argument("--env", default=None,
                    help="load API keys from this .env file before starting")
    ap.add_argument("--store", default=str(ROOT / "data" / "seeds.jsonl"))
    ap.add_argument("--identity", default=str(ROOT / "config" / "identity.yaml"))
    ap.add_argument("--no-eye", action="store_true", help="no camera")
    ap.add_argument("--no-ear", action="store_true", help="no microphone")
    ap.add_argument("--listen", action="store_true", help="transcribe speech (OpenAI)")
    ap.add_argument("--say", action="store_true", help="speak aloud via macOS `say`")
    ap.add_argument("--commons", default=None,
                    help="共業 — path to a shared world file two or more agents point at")
    ap.add_argument("--name", default="alaya", help="this agent's name in the shared world")
    ap.add_argument("--strict", action="store_true",
                    help="绳蛇检验 refuses outward acts that rest on nothing that arose")
    args = ap.parse_args()

    if args.env:
        _load_env(Path(args.env).expanduser())

    store = SeedStore(args.store)
    manas = Manas(store, path=Path(args.store).parent / "manas.md")

    faculties = {}
    faculties[Sense.EYE] = DormantFaculty(Sense.EYE) if args.no_eye else Eye()
    if args.no_ear:
        faculties[Sense.EAR] = DormantFaculty(Sense.EAR)
    else:
        faculties[Sense.EAR] = Ear(transcriber=whisper_transcriber() if args.listen else None)
    senses = SenseField(faculties=faculties)

    def say(text: str) -> None:
        print(f"  \033[1m🗣  {text}\033[0m")
        if args.say:
            subprocess.Popen(["say", text])

    mano = Mano(
        store=store,
        provider=build(args.provider, args.model, args.base_url),
        senses=senses,
        manas=manas,
        identity=Identity.load(args.identity),
        speaker=say,
        gate=RopeSnake(strict=args.strict),
        directive=Directive(Path(args.store).parent / "directive.md"),
    )
    commons = Commons(args.commons) if args.commons else None
    Console(mano, store, manas, senses, commons=commons, agent=args.name).run()


if __name__ == "__main__":
    main()
