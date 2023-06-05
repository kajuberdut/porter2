# porter2
A pure python implimentation of the finite state machine found in surgebase's porter2 implimentation. 

For more information see [Credits](#credits-and-info)

## Usage
```python
from porter2 import stem

print(stem("running"))
# "run"
```

## What does the python library do?
This library impliments the same finite state machine logic as surgebase's porter2 implimentation only in pure Python instead of Go. The result is a word stemmer with zero dependencies and (reletively) easy to read/hack code but which still provides excellent performance. Benchmarks will be provided in the future.

## Alternatives for Porter2
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
