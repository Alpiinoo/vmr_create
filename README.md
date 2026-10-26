# mtl-vmr-generator

Python script that makes a VMR file out of an MTL package. I use it with vPilot on VATSIM in MSFS 2024.

I normally fly with FSLTL, but it doesn't have a 757. So I grabbed an MTL package that has one and wrote this so I don't have to edit the VMR by hand every time I download a new livery.

## How to use

1. Put `vmr_create.py` in the MTL package folder (same place as manifest.json)
2. Run it (double click or `python vmr_create.py`)
3. It spits out `mtl_auto.vmr` in the same folder
4. Add that file in vPilot under Settings > Model Matching
