# About

This is a python script to generate ROM data for Minecraft CPUs. 

It assumes:
* You already have a working ROM. 
* Have WorldEdit enabled.
* You encode either true or false values with redstone blocks. 
* No redstone blocks exist in the ROM other than encoding true/false.
* There is the same amount of bits in each 3D direction (on x, y or z axis).
* Vertical spacing between values (redstone blocks) is 1 block.

# Usage

* Replace the bottom bit of first byte with `White Wool`
* Replace the bottom bit of second byte with `Green Wool`
* Replace the bottom bit of last byte with `Blue Wool`
* Copy the ROM template from `White Wool` to the topmost bit of last byte
* Put your template schematic in `schems/template.schem`
* Put your binary data to `schems/data.bin`
* Run the script

```bash
python3 main.py schems/data.bin schems/template.schem schems/result.schem
```

* The resulting data schematic is placed in `schems/result.schem`

# TODO

* Support staggering.
* Support encoding with barrels and other containers.