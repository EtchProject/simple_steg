# Simple Steg

This script can simply encode an image into another image using LSB steganography with some xor encryption based off of the password SHA-512 hash. The image being encoded must have smaller or equal dimensions to the one it is being hidden in.

## Encoding
```python3 steg.py encode -B base.png -H hidden.png password```

## Decoding
```python3 steg.py decode -S secret.png password```


### Extra options

You can also use the option -b to specify the number of bits you want per channel for the hidden image in the base image
