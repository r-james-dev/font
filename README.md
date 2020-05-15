# font [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
Utilities for converting between different font formats.
# Install
### From Source:
Download this project from GitHub or by running:
```
$ git clone https://github.com/shark-whale/font
```
To install the project run:
```
$ python setup.py install
```
# Usage
## Converting font types
Convert a woff file to an otf file:
```
>>> import font
>>> with open("/path/to/woff_font.woff", "rb") as file:
        woff_file = font.WOFF.from_file(file)

>>> otf_file = woff_file.to_otf()
>>> with open("/path/to/otf_font.otf", "wb+") as file:
        file.write(otf_file.to_bytes())
```
... and vice versa ...
```
>>> with open("/path/to/otf_font.otf", "rb") as file:
        otf_file = font.OTF.from_file(file)

>>> woff_file = otf_file.to_woff()
>>> with open("/path/tp/woff_font.woff", "wb+") as file:
        file.write(woff_file.to_bytes())
```
## Collections
Collections store multiple font files which can be accessed by the `fonts` property:
```
>>> font_collection.fonts
[<font.otf.File object at ...>, ...]
```
### Add fonts to collections:
```
>>> my_collection.fonts.append(my_font)
```
### Extracting collections to WOFF:
```
>>> my_collection.to_woff()
[<font.woff.File object at ...>, ...]
```
There is not function to convert to otf as the files are already stored in this form in `TTC.fonts`

TrueType Collections also support the `to_bytes()` method.
