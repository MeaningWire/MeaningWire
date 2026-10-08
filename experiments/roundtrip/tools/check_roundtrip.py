#!/usr/bin/env python3
"""CASE-001 semantic normalization/round-trip invariant checker."""

from __future__ import annotations
import json
import sys
from pathlib import Path
import xml.etree.ElementTree as ET

NS = {"m": "http://www.musicxml.org/ns/musicxml"}

def parse(path: str) -> dict:
    root = ET.parse(path).getroot()
    result = {"version": root.attrib.get("version"), "parts": [], "notes": []}
    part_names = {}
    pl = root.find("part-list")
    if pl is not None:
        for sp in pl.findall("score-part"):
            part_names[sp.attrib["id"]] = sp.findtext("part-name")

    for part in root.findall("part"):
        pid = part.attrib["id"]
        name = part_names.get(pid)
        abs_pos = 0
        part_record = {"id": pid, "name": name, "measures": []}
        for measure in part.findall("measure"):
            mnum = measure.attrib.get("number")
            measure_start = abs_pos
            local_pos = 0
            event_index = 0
            for note in measure.findall("note"):
                duration = int(note.findtext("duration", "0"))
                pitch = note.find("pitch")
                rest = note.find("rest")
                is_chord = note.find("chord") is not None
                if is_chord:
                    start = measure_start + local_pos - (prev_duration if event_index else 0)
                else:
                    start = measure_start + local_pos
                if rest is not None:
                    pitch_value = "REST"
                elif pitch is not None:
                    pitch_value = pitch.findtext("step") + pitch.findtext("octave")
                else:
                    pitch_value = "UNPITCHED"
                result["notes"].append({
                    "part": pid,
                    "part_name": name,
                    "measure": mnum,
                    "event_index": event_index,
                    "start": start,
                    "duration": duration,
                    "pitch": pitch_value,
                    "chord": is_chord,
                })
                if not is_chord:
                    local_pos += duration
                prev_duration = duration
                event_index += 1
            abs_pos = measure_start + 4
            part_record["measures"].append({"number": mnum, "start": measure_start})
        result["parts"].append(part_record)
    return result

def invariants(d: dict) -> dict:
    notes = d["notes"]
    simultaneous = {}
    for n in notes:
        simultaneous.setdefault((n["part"], n["measure"], n["start"]), []).append(n["pitch"])
    return {
        "version": d["version"],
        "part_count": len(d["parts"]),
        "note_count": len(notes),
        "parts": [(p["id"], p["name"]) for p in d["parts"]],
        "note_events": [(n["part"], n["measure"], n["start"], n["duration"], n["pitch"]) for n in notes],
        "simultaneous_groups": sorted(
            [(p, m, s, sorted(ps)) for (p, m, s), ps in simultaneous.items() if len(ps) > 1]
        ),
    }

def main() -> int:
    if len(sys.argv) != 3:
        print("usage: check_roundtrip.py SOURCE.xml RECONSTRUCTED.xml", file=sys.stderr)
        return 2
    a = invariants(parse(sys.argv[1]))
    b = invariants(parse(sys.argv[2]))
    print(json.dumps({"pass": a == b, "source": a, "reconstructed": b}, indent=2, sort_keys=True))
    return 0 if a == b else 1

if __name__ == "__main__":
    raise SystemExit(main())
