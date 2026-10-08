#!/usr/bin/env python3
"""CASE-001 semantic invariant checker."""

from __future__ import annotations
import json
import sys
import xml.etree.ElementTree as ET


def parse(path: str) -> dict:
    root = ET.parse(path).getroot()
    names = {
        sp.attrib["id"]: sp.findtext("part-name", "")
        for sp in root.findall("part-list/score-part")
    }
    notes = []
    for part in root.findall("part"):
        pid = part.attrib["id"]
        global_pos = 0
        for measure in part.findall("measure"):
            mnum = measure.attrib.get("number", "")
            local_pos = 0
            current_start = 0
            for idx, note in enumerate(measure.findall("note")):
                chord = note.find("chord") is not None
                duration = int(note.findtext("duration", "0"))
                if chord:
                    start = global_pos + current_start
                else:
                    start = global_pos + local_pos
                    current_start = local_pos
                    local_pos += duration

                pitch = note.find("pitch")
                if note.find("rest") is not None:
                    pitch_value = "REST"
                elif pitch is not None:
                    pitch_value = (
                        pitch.findtext("step", "")
                        + pitch.findtext("octave", "")
                    )
                else:
                    pitch_value = "UNPITCHED"

                notes.append(
                    {
                        "part": pid,
                        "part_name": names.get(pid, ""),
                        "measure": mnum,
                        "event_index": idx,
                        "start": start,
                        "duration": duration,
                        "pitch": pitch_value,
                        "chord": chord,
                    }
                )
            global_pos += local_pos

    return {
        "version": root.attrib.get("version"),
        "parts": [
            (p.attrib["id"], names.get(p.attrib["id"], ""))
            for p in root.findall("part")
        ],
        "notes": notes,
    }


def invariants(parsed: dict) -> dict:
    notes = parsed["notes"]
    groups = {}
    for n in notes:
        groups.setdefault(
            (n["part"], n["measure"], n["start"]), []
        ).append(n["pitch"])

    return {
        "version": parsed["version"],
        "parts": parsed["parts"],
        "note_count": len(notes),
        "note_events": [
            (
                n["part"],
                n["measure"],
                n["start"],
                n["duration"],
                n["pitch"],
            )
            for n in notes
        ],
        "simultaneous_groups": sorted(
            [
                (p, m, s, sorted(pitches))
                for (p, m, s), pitches in groups.items()
                if len(pitches) > 1
            ]
        ),
    }


def main() -> int:
    if len(sys.argv) != 3:
        print(
            "usage: check_roundtrip.py SOURCE.xml RECONSTRUCTED.xml",
            file=sys.stderr,
        )
        return 2

    source = invariants(parse(sys.argv[1]))
    reconstructed = invariants(parse(sys.argv[2]))
    result = {
        "pass": source == reconstructed,
        "source": source,
        "reconstructed": reconstructed,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
