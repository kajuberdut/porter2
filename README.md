# porter2
A python wrapper around surgebase's porter2 implimentation. 

The surgebase library impliments a finate state machine and as such has very good performance.
For more information see [Credits](#credits-and-info)

## Usage
```python
from porter2 import stem

print(stem("running"))
# "run"
```

## What dose the python library do?
In order to make this wrapper library I took the porter2.go file from Surgebase, made a few small modifications including
making the stem function accept and return C strings and renaming the package to main.
I then compiled that file to C, and provided a [small wrapper](https://github.com/kajuberdut/porter2/porter2/stem.py) to call the c version.

Becuase the C version of porter2.go is 2.4 MB, I went ahead and compressed it using Python's built in bz2 and the zipper module to unzip it
on first use. The bz2 version is about 0.8 MB. As a result of the decompression step, the very first time porter2 is imported it will take a fraction
of a second longer than future imports.

## Alternatives for Porter2 in Python
* [pystemmer](https://github.com/snowballstem/pystemmer)
* [A Python version](https://github.com/evandempsey/porter2-stemmer)
* [Another Python version from Whoosh](https://github.com/mchaput/whoosh/blob/main/src/whoosh/lang/porter2.py)

## Credits and Info
I'm not clear on the relationship between surgebase and Jian Zhen but zhenjl appears to deserve authorship credit and surgebase is where I found the go implimentation.
* [Martin Porter](https://en.wikipedia.org/wiki/Martin_Porter)
* [SurgeBase for go source](https://github.com/surgebase/porter2)
* [Jian Zhen](https://github.com/zhenjl)

## Additional Info
* [Jian Zhen's blog post](https://zhen.org/blog/generating-porter2-fsm-for-fun-and-performance/)
* [Porter 2 Wikipedia Entry](https://en.wikipedia.org/wiki/Stemming)
* [History of the Porter Stemmer](https://tartarus.org/martin/PorterStemmer/)
