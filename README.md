# mtl-vmr-generator

Python script that makes a VMR file out of an MTL package. I use it with vPilot on VATSIM in MSFS 2024.

I normally fly with FSLTL, but it doesn't have a 757. So I grabbed an MTL package that has one and wrote this so I don't have to edit the VMR by hand every time I download a new livery.

## How to use

1. Put `vmr_create.py` in the MTL package folder (same place as manifest.json)
2. Run it (double click or `python vmr_create.py`)
3. It spits out `mtl_auto.vmr` in the same folder
4. Add that file in vPilot under Settings > Model Matching

Downloaded a new livery? Just run it again.

## What it does

It goes through all the `aircraft.cfg` files, reads the titles, and figures out the airline code from `ui_variation` (like "Delta (DAL)") or from the title if that's missing. If an airline has more than one livery for a type, they get put in one rule (`B752DAL//B752DAL3`) so vPilot picks one at random.

There's also a fallback rule for each type with no airline, so a callsign without its own livery still gets some model instead of nothing.

## Settings

Top of the script:

- `ONLY_TYPES` - only write these types, like `["B752"]`. Leave empty for everything
- `EXCLUDE_TYPES` - skip these types
- `FALLBACK_RULE` - set to `False` if you don't want the type-only rules
- `OUTPUT_NAME` - name of the output file

## Notes

- If you only need it for the types FSLTL is missing, set `ONLY_TYPES`, otherwise it will also cover stuff FSLTL already has
- Order of the rule files in vPilot matters, put this one before the FSLTL one
- Model names are taken straight from `aircraft.cfg`, so they should always match
