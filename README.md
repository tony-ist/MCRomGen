# About

This is a python script to generate ROM data for Minecraft CPUs. 

It assumes:
* You already have a working ROM. 
* Have WorldEdit enabled.
* You encode either true or false values with redstone blocks.
* You have only 8 bits vertically.
* Vertical spacing between values is 1 block.

# Usage

* Put your offsets pattern in `schems/offsets.txt`
  * First row is offsets of bytes in one direction
  * Second row is offsets of rows of bytes in the orthogonal direction

  ```
  0 2 4 6
  0 3 6 9 12
  ```

* Put your binary data to `schems/data.bin`
* Run the script

    ```bash
    python3 main.py schems/data.bin schems/offsets.txt schems/result.schem
    ```

* The resulting data schematic is placed in `schems/result.schem`
* Paste it into your ROM with WorldEdit command `//paste -a` 

# TODO

* Support staggering.
* Support encoding with barrels and other containers.
* Support diagonal ROM