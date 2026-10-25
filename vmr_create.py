"""
MTL -> VMR auto generator
Put this file inside the MTL folder and double-click it.
It reads every aircraft.cfg in its own folder, builds one rule per livery
and writes mtl_auto.vmr next to the script.
"""
import os
import re
import sys
from collections import OrderedDict

# ============== SETTINGS ==============
# Folder this script lives in (put the script inside the MTL folder)
MTL_PATH = os.path.dirname(os.path.abspath(sys.argv[0]))

# Leave empty to write ALL types found: []
# To write only specific types: ["B752"] or ["B752", "B753"]
ONLY_TYPES = []

# Types to skip, e.g. ["A320"]
EXCLUDE_TYPES = []

# True: also write a rule with only the type code (no airline), using all
# liveries of that type, for airlines that have no matching livery
FALLBACK_RULE = True

OUTPUT_NAME = "mtl_auto.vmr"
# =====================================


def parse_cfg(path):
    """aircraft.cfg -> (icao_type, [ {title, variation} ... ])"""
    try:
        with open(path, "r", encoding="utf-8-sig", errors="ignore") as f:
            lines = f.read().splitlines()
    except OSError:
        return None, []

    icao_type = None
    section = None
    entries = []
    current = None

    for raw in lines:
        line = raw.split(";")[0].strip()
        if not line:
            continue
        m = re.match(r"^\[(.+)\]$", line)
        if m:
            section = m.group(1).strip().lower()
            if section.startswith("fltsim."):
                current = {"title": "", "variation": ""}
                entries.append(current)
            else:
                current = None
            continue
        if "=" not in line:
            continue
        key, val = line.split("=", 1)
        key = key.strip().lower()
        val = val.strip().strip('"').strip()

        if section == "general" and key == "icao_type_designator":
            icao_type = val.upper()
        elif current is not None:
            if key == "title":
                current["title"] = val
            elif key == "ui_variation":
                current["variation"] = val

    return icao_type, [e for e in entries if e["title"]]


def get_airline(title, variation, icao_type):
    """Find the airline code: first from (XXX) in ui_variation, else from the title."""
    m = re.search(r"\(([A-Za-z0-9@]{2,4})\)", variation or "")
    if m:
        return m.group(1).upper()

    rest = title.upper().replace(" ", "")
    if icao_type and rest.startswith(icao_type):
        rest = rest[len(icao_type):]
    if rest.startswith("@"):
        return rest[:3]
    return rest[:3] if len(rest) >= 3 else None


def main():
    path = MTL_PATH
    if not os.path.isdir(path):
        print(f"Folder not found: {path}")
        path = input("Paste the MTL folder path: ").strip().strip('"')
        if not os.path.isdir(path):
            print("Invalid path.")
            return

    simobjects = os.path.join(path, "SimObjects")
    root = simobjects if os.path.isdir(simobjects) else path

    rules = OrderedDict()    # (airline, type) -> [titles]
    by_type = OrderedDict()  # type -> [titles]
    skipped = 0

    for dirpath, _, files in os.walk(root):
        for fn in files:
            if fn.lower() != "aircraft.cfg":
                continue
            icao_type, entries = parse_cfg(os.path.join(dirpath, fn))
            if not icao_type or not entries:
                skipped += 1
                continue
            if ONLY_TYPES and icao_type not in [t.upper() for t in ONLY_TYPES]:
                continue
            if icao_type in [t.upper() for t in EXCLUDE_TYPES]:
                continue

            for e in entries:
                title = e["title"]
                by_type.setdefault(icao_type, [])
                if title not in by_type[icao_type]:
                    by_type[icao_type].append(title)

                airline = get_airline(title, e["variation"], icao_type)
                if not airline:
                    continue
                key = (airline, icao_type)
                rules.setdefault(key, [])
                if title not in rules[key]:
                    rules[key].append(title)

    out = ['<?xml version="1.0" encoding="utf-8"?>', "<ModelMatchRuleSet>"]
    for (airline, t), titles in sorted(rules.items(), key=lambda x: (x[0][1], x[0][0])):
        out.append(f'<ModelMatchRule CallsignPrefix="{airline}" TypeCode="{t}" ModelName="{"//".join(sorted(titles))}" />')
    if FALLBACK_RULE:
        for t, titles in sorted(by_type.items()):
            out.append(f'<ModelMatchRule TypeCode="{t}" ModelName="{"//".join(sorted(titles))}" />')
    out.append("</ModelMatchRuleSet>")

    out_path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), OUTPUT_NAME)
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        f.write("\r\n".join(out) + "\r\n")

    print(f"Done! {len(rules)} airline rules, {len(by_type)} types.")
    print("Types:", ", ".join(by_type.keys()) or "-")
    if skipped:
        print(f"Skipped aircraft.cfg files: {skipped}")
    print(f"File: {out_path}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Error:", e)
    input("\nPress Enter to close...")