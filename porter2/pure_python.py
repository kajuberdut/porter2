from collections import defaultdict
from typing import List

from porter2.utlity import has_vowel, is_short_syllable, is_short_word, is_vowel

DEBUG = True

ListStr = List[str]


def stem(word: str) -> str:
    if len(word) <= 2:
        if DEBUG:
            print("exit early, word len <= 2")
        return word

    # using a list of characters to match the abilities of Go rune slice
    rs = list(word.lower())

    if DEBUG:
        print(f"{rs=}")

    rs, ex = exception1(rs)

    if ex:
        if DEBUG:
            print(f"Early exit from exception1 result:{rs=}")
        return "".join(rs)

    rs = preclude(rs)

    r1, r2 = markR1R2(rs)

    rs = step1a(step0(rs))

    if exception2(rs):
        return "".join(rs)

    return "".join(
        postlude(
            step5(step4(step3(step2(step1c(step1b(rs, r1)), r1), r1, r2), r2), r1, r2)
        )
    )


def preclude(rs: ListStr) -> ListStr:
    """Remove initial ', if present. Then set initial y, or y after a vowel, to Y."""
    if DEBUG:
        print(f"preclude called")
    if rs[0] == "'":
        rs = rs[1:]

    if rs[0] == "y":
        rs[0] = "Y"

    for i, r in enumerate(rs[:-1]):
        if is_vowel(r) and rs[i + 1] == "y":
            rs[i + 1] = "Y"

    return rs


def markR1R2(rs: ListStr) -> tuple[int, int]:
    """
    http:#snowball.tartarus.org/texts/r1r2.html

    R1 is the region after the first non-vowel following a vowel, or is the
    null region at the end of the word if there is no such non-vowel.

    R2 is the region after the first non-vowel following a vowel in R1, or is the
    null region at the end of the word if there is no such non-vowel.

    If the words begins gener, commun or arsen, set R1 to be the remainder of the word.
    """
    if DEBUG:
        print(f"markR1R2 called")
    r1 = -1

    if rs[0] == "g" and len(rs) >= 5 and rs[1:5] == "ener":
        r1 = 5
    elif rs[0] == "c" and len(rs) >= 6 and rs[1:6] == "ommun":
        r1 = 6
    elif rs[0] == "a" and len(rs) >= 5 and rs[1:5] == "rsen":
        r1 = 5

    if r1 == -1:
        r1 = mark_region(rs)

    return r1, r1 + mark_region(rs[r1:])


def mark_region(rs: ListStr) -> int:
    if DEBUG:
        print(f"mark_region called")
    if len(rs) == 0:
        return 0

    for i in range(len(rs) - 1):
        if is_vowel(rs[i]) and not is_vowel(rs[i + 1]):
            return i + 2

    return len(rs)


def step0(rs: ListStr) -> ListStr:
    """Search for the longest among the suffixes, and remove if found.
    '
    's
    's'
    """
    if DEBUG:
        print(f"step0 called")

    l = len(rs)
    m = None
    s = 0
    f = None

    for i in range(l):
        r = rs[l - i - 1]

        if s == 0:
            if r == "'":
                s = 1
                m = 1
                f = 1
            elif r == "s":
                s = 2
            else:
                break

        elif s == 1:
            if r == "s":
                s = 4
            else:
                break

        elif s == 2:
            if r == "'":
                s = 3
                m = 2
                f = 3
            else:
                break

        elif s == 4:
            if r == "'":
                s = 5
                m = 3
                f = 5
            else:
                break
        else:
            break

    if f in [1, 3, 5]:
        rs = rs[: l - m]

    return rs


def step1a(rs):
    """
    Search for the longest suffix among the suffixes, and perform the action indicated.
    sses: replace by ss
    ied : replace by i if preceded by more than one letter, otherwise by ie (so ties -> tie, cries -> cri)
    ies : replace by i if preceded by more than one letter, otherwise by ie (so ties -> tie, cries -> cri)
    s   : delete if the preceding word part contains a vowel not immediately before the s (so gas and this retain the s, gaps and kiwis lose it)
    us  : do nothing
    ss  : do nothing
    """
    if DEBUG:
        print(f"step1a called")

    l = len(rs)
    m = None
    s = None
    f = None

    for i in range(l):
        r = rs[l - i - 1]

        if s == 0:
            if r == "s":
                s = 1
                m = 1
                f = 1
            elif r == "d":
                s = 5
            else:
                break

        elif s == 1:
            if r == "e":
                s = 2
            elif r == "u":
                s = 9
                m = 2
                f = 9
            elif r == "s":
                s = 10
                m = 2
                f = 10
            else:
                break

        elif s == 2:
            if r == "s":
                s = 3
            elif r == "i":
                s = 8
                m = 3
                f = 8
            else:
                break

        elif s == 3:
            if r == "s":
                s = 4
                m = 4
                f = 4
            else:
                break

        elif s == 5:
            if r == "e":
                s = 6
            else:
                break

        elif s == 6:
            if r == "i":
                s = 7
                m = 3
                f = 7
            else:
                break

        else:
            break

    if f == 1:
        if l > 2 and has_vowel(rs[: l - 2]):
            rs = rs[: l - 1]

    elif f == 4:
        rs = rs[: l - 2]

    elif f in [7, 8]:
        rs = rs[: l - m]
        if l >= 5:
            rs.append("i")
        else:
            rs.extend(["i", "e"])

    elif f in [9, 10]:
        pass

    return rs


def step1b(rs, r1):
    """
    Search for the longest suffix among the suffixes, and perform the action indicated.
    1. ingly -> see note below
    2. eedly -> replace by ee if in R1
    3.  edly -> see note below
    4.   ing -> see note below
    5.   eed -> replace by ee if in R1
    6.    ed -> see note below

    Note: delete if the preceding word part contains a vowel, and after the deletion:
        if the word ends at, bl or iz add e (so luxuriat -> luxuriate), or
        if the word ends with a double remove the last letter (so hopp -> hop), or
        if the word is short, add e (so hop -> hope)
    """
    if DEBUG:
        print(f"step1b called")

    l = len(rs)
    m = None
    s = None
    f = None

    for i in range(l):
        r = rs[l - i - 1]

        if s == 0:
            if r == "y":
                s = 1
            elif r == "g":
                s = 9
            elif r == "d":
                s = 12
            else:
                break

        elif s == 1:
            if r == "l":
                s = 2
            else:
                break

        elif s == 2:
            if r == "g":
                s = 3
            elif r == "d":
                s = 6
            else:
                break

        elif s == 3:
            if r == "n":
                s = 4
            else:
                break

        elif s == 4:
            if r == "i":
                s = 5
                m = 5
                f = 5
            else:
                break

        elif s == 6:
            if r == "e":
                s = 7
                m = 4
                f = 7
            else:
                break

        elif s == 7:
            if r == "e":
                s = 8
                m = 5
                f = 8
            else:
                break

        elif s == 9:
            if r == "n":
                s = 10
            else:
                break

        elif s == 10:
            if r == "i":
                s = 11
                m = 3
                f = 11
            else:
                break

        elif s == 12:
            if r == "e":
                s = 13
                m = 2
                f = 13
            else:
                break

        elif s == 13:
            if r == "e":
                s = 14
                m = 3
                f = 14
            else:
                break

        else:
            break

    if f in [5, 7, 11, 13]:
        if not has_vowel(rs[: l - m]):
            return rs

        rs = rs[: l - m]

        if len(rs) > 2:
            r, rr = rs[-1], rs[-2]

            if (
                (rr == "a" and r == "t")
                or (rr == "b" and r == "l")
                or (rr == "i" and r == "z")
            ):
                rs.append("e")

            if r == rr and r in ["b", "d", "f", "g", "m", "n", "p", "r", "t"]:
                rs = rs[:-1]

        if is_short_word(rs, r1):
            rs.append("e")

    elif f == 8:
        if m >= r1:
            rs = rs[:-3]

    elif f == 14:
        if l - r1 >= m:
            rs = rs[:-1]

    return rs


def step1c(rs):
    """
    Replace suffix y or Y by i if preceded by a non-vowel which is not the first letter
    of the word (so cry -> cri, by -> by, say -> say)
    """
    if DEBUG:
        print(f"step1b called")

    if len(rs) > 2:
        # Check if the last element in the rune array is "y" or "Y"
        if rs[-1] == "y" or rs[-1] == "Y":
            # If the second-last element is not a vowel, replace it with an "i"
            if not is_vowel(rs[-2]):
                rs[-1] = "i"
        return rs


def step2(rs, r1):
    """
    Search for the longest among the following suffixes, and, if found and in R1,
    perform the action indicated.

    1.  tional -> replace by tion
    2.    enci -> replace by ence
    3.    anci -> replace by ance
    4.    abli -> replace by able
    5.   entli -> replace by ent
    6.    izer -> replace by ize
    7. ization -> replace by ize
    8. ational -> replace by ate
    9.   ation -> replace by ate
    10.    ator -> replace by ate
    11.   alism -> replace by al
    12.   aliti -> replace by al
    13.    alli -> replace by al
    14. fulness -> replace by ful
    15.   ousli -> replace by ous
    16. ousness -> replace by ous
    17. iveness -> replace by ive
    18.   iviti -> replace by ive
    19.  biliti -> replace by ble
    20.     bli -> replace by ble
    21.     ogi -> replace by og if preceded by l
    22.   fulli -> replace by ful
    23.  lessli -> replace by less
    24.      li -> delete if preceded by a valid li-ending
    """

    if DEBUG:
        print(f"step2 called")

    l = len(rs)
    m = 0
    s = 0
    f = 0
    r = ""

    i = 0
    while i < l:
        r = rs[l - i - 1]

        if s == 0:
            if r == "s":
                s = 1
            elif r == "l":
                s = 14
            elif r == "n":
                s = 21
            elif r == "i":
                s = 28
            elif r == "m":
                s = 46
            elif r == "r":
                s = 61
            else:
                break
        elif s == 1:
            if r == "s":
                s = 2
            else:
                break
        elif s == 2:
            if r == "e":
                s = 3
            else:
                break
        elif s == 3:
            if r == "n":
                s = 4
            else:
                break
        elif s == 4:
            if r == "l":
                s = 5
            elif r == "s":
                s = 8
            elif r == "e":
                s = 11
            else:
                break
        elif s == 5:
            if r == "u":
                s = 6
            else:
                break
        elif s == 6:
            if r == "f":
                s = 7
                m = 7
                f = 7
                # fulness - final
            else:
                break
        elif s == 8:
            if r == "u":
                s = 9
            else:
                break
        elif s == 9:
            if r == "o":
                s = 10
                m = 7
                f = 10
                # ousness - final
            else:
                break
        elif s == 11:
            if r == "v":
                s = 12
            else:
                break
        elif s == 12:
            if r == "i":
                s = 13
                m = 7
                f = 13
                # iveness - final
            else:
                break
        elif s == 14:
            if r == "a":
                s = 15
            else:
                break
        elif s == 15:
            if r == "n":
                s = 16
            else:
                break

        elif s == 16:
            if r == "o":
                s = 17
            else:
                break

        elif s == 17:
            if r == "i":
                s = 18
            else:
                break

        elif s == 18:
            if r == "t":
                s = 19
                m = 6
                f = 19
                # tional - final
            else:
                break

        elif s == 19:
            if r == "a":
                s = 20
                m = 7
                f = 20
                # ational - final
            else:
                break

        elif s == 21:
            if r == "o":
                s = 22
            else:
                break

        elif s == 22:
            if r == "i":
                s = 23
            else:
                break

        elif s == 23:
            if r == "t":
                s = 24
            else:
                break

        elif s == 24:
            if r == "a":
                s = 25
                m = 5
                f = 25
                # ation - final
            else:
                break

        elif s == 25:
            if r == "z":
                s = 26
            else:
                break

        elif s == 26:
            if r == "i":
                s = 27
                m = 7
                f = 27
                # ization - final
            else:
                break

        elif s == 28:
            if r == "t":
                s = 29
            elif r == "l":
                s = 34
                m = 2
                f = 34
                # li - final
            elif r == "c":
                s = 55
            elif r == "g":
                s = 69
            else:
                break

        elif s == 29:
            if r == "i":
                s = 30
            else:
                break

        elif s == 30:
            if r == "l":
                s = 31
            elif r == "v":
                s = 44
            else:
                break

        elif s == 31:
            if r == "i":
                s = 32
            elif r == "a":
                s = 54
                m = 5
                f = 54
                # aliti - final
            else:
                break

        elif s == 32:
            if r == "b":
                s = 33
                m = 6
                f = 33
                # biliti - final
            else:
                break

        elif s == 34:
            if r == "s":
                s = 35
            elif r == "l":
                s = 39
            elif r == "t":
                s = 51
            elif r == "b":
                s = 59
                m = 3
                f = 59
                # bli - final
            else:
                break

        elif s == 35:
            if r == "s":
                s = 36
            elif r == "u":
                s = 42
            else:
                break

        elif s == 36:
            if r == "e":
                s = 37
            else:
                break

        elif s == 37:
            if r == "l":
                s = 38
                m = 6
                f = 38
                # lessli - final
            else:
                break

        elif s == 39:
            if r == "u":
                s = 40
            elif r == "a":
                s = 68
                m = 4
                f = 68
                # alli - final
            else:
                break

        elif s == 40:
            if r == "f":
                s = 41
                m = 5
                f = 41
                # fulli - final
            else:
                break

        elif s == 42:
            if r == "o":
                s = 43
                m = 5
                f = 43
                # ousli - final
            else:
                break

        elif s == 44:
            if r == "i":
                s = 45
                m = 5
                f = 45
                # iviti - final
            else:
                break

        elif s == 46:
            if r == "s":
                s = 47
            else:
                break

        elif s == 47:
            if r == "i":
                s = 48
            else:
                break

        elif s == 48:
            if r == "l":
                s = 49
            else:
                break

        elif s == 49:
            if r == "a":
                s = 50
                m = 5
                f = 50
                # alism - final
            else:
                break

        elif s == 51:
            if r == "n":
                s = 52
            else:
                break

        elif s == 52:
            if r == "e":
                s = 53
                m = 5
                f = 53
                # entli - final
            else:
                break

        elif s == 55:
            if r == "n":
                s = 56
            else:
                break

        elif s == 56:
            if r == "e":
                s = 57
                m = 4
                f = 57
                # enci - final
            elif r == "a":
                s = 58
                m = 4
                f = 58
                # anci - final
            else:
                break

        elif s == 59:
            if r == "a":
                s = 60
                m = 4
                f = 60
                # abli - final
            else:
                break

        elif s == 61:
            if r == "e":
                s = 62
            elif r == "o":
                s = 65
            else:
                break

        elif s == 62:
            if r == "z":
                s = 63
            else:
                break

        elif s == 63:
            if r == "i":
                s = 64
                m = 4
                f = 64
                # izer - final
            else:
                break

        elif s == 65:
            if r == "t":
                s = 66
            else:
                break

        elif s == 66:
            if r == "a":
                s = 67
                m = 4
                f = 67
                # ator - final
            else:
                break

        elif s == 69:
            if r == "o":
                s = 70
                m = 3
                f = 70
                # ogi - final
            else:
                break
        elif s == 69:
            if r == "o":
                s = 70
                m = 3
                f = 70
            else:
                break
        else:
            break

        i += 1

    if l - r1 < m:
        return rs

    # Modify rs based on f
    if f in {7, 10, 13}:
        # fulness - final
        # ousness - final
        # iveness - final
        rs = rs[: l - 4]

    if f in {7, 10, 13}:
        # fulness - final
        # ousness - final
        # iveness - final
        rs = rs[: l - 4]

    elif f in {19, 38, 41, 43, 53, 68}:
        # tional - final
        # lessli - final
        # fulli - final
        # ousli - final
        # entli - final
        # alli - final
        rs = rs[: l - 2]
    elif f in {20, 27}:
        # ational - final
        # ization - final
        rs[l - 5] = "e"
        rs = rs[: l - 4]
    elif f in {25, 45}:
        # ation - final
        # iviti - final
        rs[l - 3] = "e"
        rs = rs[: l - 2]
    elif f == 33:
        # biliti - final
        rs[l - 5] = "l"
        rs[l - 4] = "e"
        rs = rs[: l - 3]
    elif f == 34:
        # li - final
        if l > 2 and rs[l - 3] in {"c", "d", "e", "g", "h", "k", "m", "n", "r", "t"}:
            rs = rs[: l - 2]
    elif f in {50, 54}:
        # alism - final
        # aliti - final
        rs = rs[: l - 3]
    elif f in {57, 58, 59, 60}:
        # enci - final
        # anci - final
        # abli - final
        # bli - final
        rs[l - 1] = "e"
    elif f == 64:
        # izer - final
        rs = rs[: l - 1]
    elif f == 67:
        # ator - final
        rs[l - 2] = "e"
        rs = rs[: l - 1]
    elif f == 70:
        # ogi - final
        if l > 3 and rs[l - 4] == "l":
            rs = rs[: l - 1]

    return rs


def step3(rs, r1, r2):
    """
    Search for the longest among the following suffixes, and, if found and in R1,
    perform the action indicated.

    1.  tional -> replace by tion
    2. ational -> replace by ate
    3.   alize -> replace by al
    4.   icate -> replace by ic
    5.   iciti -> replace by ic
    6.    ical -> replace by ic
    7.     ful -> delete
    8.    ness -> delete
    9.   ative -> delete if in R2
    """

    if DEBUG:
        print(f"step2 called")

    l = len(rs)  # string length
    m = 0  # suffix length
    s = 0  # state
    f = 0  # end state of longest suffix
    r = ""  # current rune

    while True:
        for i in range(l):
            r = rs[l - i - 1]

            if s == 0:
                if r in ["l", "e", "i", "s"]:
                    s = {"l": 1, "e": 8, "i": 17, "s": 26}[r]
                else:
                    break

            elif s == 1:
                if r in ["a", "u"]:
                    s = {"a": 2, "u": 24}[r]
                else:
                    break

            elif s == 2:
                if r in ["n", "c"]:
                    s = {"n": 3, "c": 22}[r]
                else:
                    break

            elif s == 3 and r == "o":
                s = 4

            elif s == 4 and r == "i":
                s = 5

            elif s == 5 and r == "t":
                s = 6
                m = 6
                f = 6  # tional - final

            elif s == 6 and r == "a":
                s = 7
                m = 7
                f = 7  # ational - final

            elif s == 8:
                if r in ["z", "t", "v"]:
                    s = {"z": 9, "t": 13, "v": 30}[r]
                else:
                    break

            elif s == 9 and r == "i":
                s = 10

            elif s == 10 and r == "l":
                s = 11

            elif s == 11 and r == "a":
                s = 12
                m = 5
                f = 12  # alize - final

            elif s == 13 and r == "a":
                s = 14

            elif s == 14 and r == "c":
                s = 15

            elif s == 15 and r == "i":
                s = 16
                m = 5
                f = 16  # icate - final

            elif s == 17 and r == "t":
                s = 18

            elif s == 18 and r == "i":
                s = 19

            elif s == 19 and r == "c":
                s = 20

            elif s == 20 and r == "i":
                s = 21
                m = 5
                f = 21  # iciti - final

            elif s == 22 and r == "i":
                s = 23
                m = 4
                f = 23  # ical - final

            elif s == 24 and r == "f":
                s = 25
                m = 3
                f = 25  # ful - final

            elif s == 26 and r == "s":
                s = 27

            elif s == 27 and r == "e":
                s = 28

            elif s == 28 and r == "n":
                s = 29
                m = 4
                f = 29  # ness - final

            elif s == 30 and r == "i":
                s = 31

            elif s == 31 and r == "t":
                s = 32

            elif s == 32 and r == "a":
                s = 33
                m = 5
                f = 33  # ative - final

            else:
                break
        else:
            continue
        break

    # if not found and in R1, do nothing
    if l - r1 < m:
        return rs

    if f in [6, 23]:
        # tional - final
        # ical - final
        rs = rs[: l - 2]

    elif f == 7:
        # ational - final
        rs[l - 5] = "e"
        rs = rs[: l - 4]

    elif f in [12, 16, 21]:
        # alize - final
        # icate - final
        # iciti - final
        rs = rs[: l - 3]

    elif f in [25, 29]:
        # ful - final
        # ness - final
        rs = rs[: l - m]

    elif f == 33:
        # ative - final
        # delete if in R2
        if l - r2 >= m:
            rs = rs[: l - m]

    return rs


def step4(rs, r2):
    """
    Search for the longest among the following suffixes, and, if found and in R2,
    perform the action indicated.

    1.  able -> delete
    2.    al -> delete
    3.  ance -> delete
    4.   ant -> delete
    5.   ate -> delete
    6. ement -> delete
    7.  ence -> delete
    8.   ent -> delete
    9.    er -> delete
    10.  ible -> delete
    11.    ic -> delete
    12.   ism -> delete
    13.   iti -> delete
    14.   ive -> delete
    15.   ize -> delete
    16.  ment -> delete
    17.   ous -> delete
    18.   ion -> delete if preceded by s or t
    """

    if DEBUG:
        print("step4 called")

    l = len(rs)  # string length
    m = 0  # suffix length
    s = 0  # state
    f = 0  # end state of longest suffix
    r = ""  # current rune

    while s is not None:
        print(f"while loop. {s=}")
        for i in range(l):
            r = rs[l - i - 1]

            if s == 0:
                s = {"s": 1, "l": 14, "n": 21, "i": 28, "m": 46, "r": 61}.get(r)

            elif s == 1:
                s = {"s": 2}.get(r)

            elif s == 2:
                s = {"b": 3}.get(r)

            elif s == 3:
                s, m, f = defaultdict(
                    lambda: (None, m, f), {"a": (4, 4, 4), "i": (21, 4, 21)}
                ).get(r)
                # f4 = able - final
                # f21 = ible - final

            elif s == 4:
                s = {"l": 5, "s": 8, "e": 11}.get(r)

            elif s == 5 and r == "a":
                s = 6
                m = 2
                f = 6  # al - final

            elif s == 7 and r == "n":
                s = 8

            elif s == 8:
                if r == "a":
                    s = 9
                    m = 4
                    f = 9  # ance - final
                elif r == "e":
                    s = 18
                    m = 4
                    f = 18  # ence - final
                else:
                    break

            elif s == 10 and r == "n":
                s = 11

            elif s == 11:
                if r == "a":
                    s = 12
                    m = 3
                    f = 12  # ant - final
                elif r == "e":
                    s = 15
                    m = 3
                    f = 15  # ent - final
                else:
                    break

            elif s == 13 and r == "a":
                s = 14
                m = 3
                f = 14  # ate - final

            elif s == 15 and r == "m":
                s = 16
                m = 4
                f = 16  # ment - final

            elif s == 16 and r == "e":
                s = 17
                m = 5
                f = 17  # ement - final

            elif s == 19 and r == "e":
                s = 20
                m = 2
                f = 20  # er - final

            elif s == 22 and r == "i":
                s = 23
                m = 2
                f = 23  # ic - final

            elif s == 24 and r == "s":
                s = 25

            elif s == 25 and r == "i":
                s = 26
                m = 3
                f = 26  # ism - final

            elif s == 27 and r == "t":
                s = 28

            elif s == 28 and r == "i":
                s = 29
                m = 3
                f = 29  # iti - final

            elif s == 30 and r == "i":
                s = 31
                m = 3
                f = 31  # ive - final

            elif s == 32 and r == "i":
                s = 33
                m = 3
                f = 33  # ize - final

            elif s == 34 and r == "u":
                s = 35

            elif s == 35:
                if r == "s":
                    s = 36
                elif r == "u":
                    s = 42

            elif s == 36:
                if r == "e":
                    s = 37

            elif s == 37 and r == "o":
                s = 38
                m = 6
                f = 38
            # lessli - final

            elif s == 38 and r == "i":
                s = 39
                m = 3
                f = 39  # ion - final

            else:
                s = None
        else:
            s = None

    if l - r2 < m:
        return rs

    if f in [4, 6, 9, 12, 14, 15, 16, 17, 18, 20, 21, 23, 26, 29, 31, 33, 36]:
        rs = rs[: l - m]

    elif f == 39:
        if l >= 4 and rs[l - 4] in ["s", "t"]:
            rs = rs[: l - 3]

    return rs


def step5(rs, r1, r2):
    """
    Search for the the following suffixes, and, if found, perform the action indicated.

    e -> delete if in R2, or in R1 and not preceded by a short syllable
    l -> delete if in R2 and preceded by l
    """

    if DEBUG:
        print("step5 called")

    l = len(rs)
    if l < 1:
        return rs

    r = rs[-1]
    if r == "e":
        # in R2, delete
        if l - r2 > 0:
            return rs[:-1]

        # not in R1, quit
        if l - r1 < 1:
            return rs

        # in R1, test to see if preceded by a short syllable
        if not is_short_syllable(rs[:-1]):
            return rs[:-1]

    elif r == "l":
        if l > 1 and l - r2 > 0 and rs[-2] == "l":
            return rs[:-1]

    return rs


def postlude(rs: ListStr):
    if DEBUG:
        print("postlude called")

    for i, r in enumerate(rs):
        if r == "Y":
            rs[i] = "y"
    return rs


def exception1(rs: ListStr):
    """
    word exceptions list 1. Can't do a map since we have a []rune, and []rune cannot
    be a key to the map..argh..

    Returns true if word is an exception, false if not. The replacement word is
    returned if true. Otherwise the same word is returned if false.

    andes -> andes
    atlas -> atlas
    bias -> bias
    cosmos -> cosmos
    dying -> die
    early -> earli
    gently -> gentl
    howe -> howe
    idly -> idl
    lying -> lie
    news -> news
    only -> onli
    singly -> singl
    skies -> sky
    skis -> ski
    sky -> sky
    tying -> tie
    ugly -> ugli
    """

    if DEBUG:
        print("exception1 called")

    l = len(rs)
    if l > 6:
        return rs, False

    if rs[l - 1] not in ["s", "g", "y", "e"]:
        return rs, False

    if rs[0] == "a":
        if l != 5:
            return rs, False

        if rs[1] == "n" and rs[2] == "d" and rs[3] == "e" and rs[4] == "s":
            return rs, True
        elif rs[1] == "t" and rs[2] == "l" and rs[3] == "a" and rs[4] == "s":
            return rs, True

        return rs, False

    elif rs[0] == "b":
        if l == 4 and rs[1] == "i" and rs[2] == "a" and rs[3] == "s":
            return rs, True

        return rs, False

    elif rs[0] == "c":
        if (
            l == 6
            and rs[1] == "o"
            and rs[2] == "s"
            and rs[3] == "m"
            and rs[4] == "o"
            and rs[5] == "s"
        ):
            return rs, True

        return rs, False

    elif rs[0] in ["d", "l", "t"]:
        if l == 5 and rs[1] == "y" and rs[2] == "i" and rs[3] == "n" and rs[4] == "g":
            rs[1], rs[2] = "i", "e"
            return rs[:3], True

        return rs, False

    elif rs[0] == "e":
        if l == 5 and rs[1] == "a" and rs[2] == "r" and rs[3] == "l" and rs[4] == "y":
            rs[4] = "i"
            return rs, True

        return rs, False

    elif rs[0] == "g":
        if (
            l == 6
            and rs[1] == "e"
            and rs[2] == "n"
            and rs[3] == "t"
            and rs[4] == "l"
            and rs[5] == "y"
        ):
            return rs[:5], True

        return rs, False

    elif rs[0] == "h":
        if l == 4 and rs[1] == "o" and rs[2] == "w" and rs[3] == "e":
            return rs, True

        return rs, False

    elif rs[0] == "i":
        if l == 4 and rs[1] == "d" and rs[2] == "l" and rs[3] == "y":
            return rs[:3], True

        return rs, False

    elif rs[0] == "n":
        if l == 4 and rs[1] == "e" and rs[2] == "w" and rs[3] == "s":
            return rs, True

        return rs, False

    elif rs[0] == "o":
        if l == 4 and rs[1] == "n" and rs[2] == "l" and rs[3] == "y":
            rs[3] = "i"
            return rs, True

        return rs, False

    elif rs[0] == "s":
        if rs[1] == "i":
            if (
                l == 6
                and rs[2] == "n"
                and rs[3] == "g"
                and rs[4] == "l"
                and rs[5] == "y"
            ):
                return rs[:5], True

            return rs, False

        elif rs[1] == "k":
            if l == 3 and rs[2] == "y":
                return rs, True
            elif l == 4 and rs[2] == "i" and rs[3] == "s":
                rs = rs[:3]
                return rs, True
            elif l == 5 and rs[2] == "i" and rs[3] == "e" and rs[4] == "s":
                rs[2] = "y"
                return rs[:3], True

            return rs, False

    elif rs[0] == "u":
        if l == 4 and rs[1] == "g" and rs[2] == "l" and rs[3] == "y":
            rs[3] = "i"
            return rs, True

        return rs, False

    return rs, False


def exception2(rs: ListStr):
    """
    Following step 1a, leave the following invariant,

    inning
    outing
    canning
    herring
    earring
    proceed
    exceed
    succeed
    """

    if DEBUG:
        print("exception2 called")

    l = len(rs)
    if l != 6 and l != 7:
        return False

    if rs[l - 1] not in ["g", "d"]:
        return False

    if rs[0] == "i":
        # inning
        if (
            l != 6
            or rs[1] != "n"
            or rs[2] != "n"
            or rs[3] != "i"
            or rs[4] != "n"
            or rs[5] != "g"
        ):
            return False

    elif rs[0] == "o":
        # outing
        if (
            l != 6
            or rs[1] != "u"
            or rs[2] != "t"
            or rs[3] != "i"
            or rs[4] != "n"
            or rs[5] != "g"
        ):
            return False

    elif rs[0] == "c":
        # canning
        if (
            l != 7
            or rs[1] != "a"
            or rs[2] != "n"
            or rs[3] != "n"
            or rs[4] != "i"
            or rs[5] != "n"
            or rs[6] != "g"
        ):
            return False

    elif rs[0] == "h":
        # herring
        if (
            l != 7
            or rs[1] != "e"
            or rs[2] != "r"
            or rs[3] != "r"
            or rs[4] != "i"
            or rs[5] != "n"
            or rs[6] != "g"
        ):
            return False

    elif rs[0] == "e":
        if l == 7:
            # earring
            if (
                rs[1] != "a"
                or rs[2] != "r"
                or rs[3] != "r"
                or rs[4] != "i"
                or rs[5] != "n"
                or rs[6] != "g"
            ):
                return False
        elif l == 6:
            # exceed
            if (
                rs[1] != "x"
                or rs[2] != "c"
                or rs[3] != "e"
                or rs[4] != "e"
                or rs[5] != "d"
            ):
                return False

    elif rs[0] == "p":
        # proceed
        if (
            l != 7
            or rs[1] != "r"
            or rs[2] != "o"
            or rs[3] != "c"
            or rs[4] != "e"
            or rs[5] != "e"
            or rs[6] != "d"
        ):
            return False

    elif rs[0] == "s":
        # succeed
        if (
            l != 7
            or rs[1] != "u"
            or rs[2] != "c"
            or rs[3] != "c"
            or rs[4] != "e"
            or rs[5] != "e"
            or rs[6] != "d"
        ):
            return False

    else:
        return False

    return True


if __name__ == "__main__":
    print(stem("running"))
