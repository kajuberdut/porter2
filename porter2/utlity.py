
def is_vowel(r: str) -> bool:
    return r in ["a", "e", "i", "o", "u", "y"]


def has_vowel(rs: list[str]) -> bool:
    return any(is_vowel(r) for r in rs)


# A word is called short if it ends in a short syllable, and if R1 is null.
#
# Define a short syllable in a word as either
#  (a) a vowel followed by a non-vowel other than w, x or Y and preceded by a non-vowel, or
#  (b) a vowel at the beginning of the word followed by a non-vowel.
def is_short_syllable(rs: list[str]) -> bool:
    l = len(rs)

    if l in [0, 1]:
        return False
    elif l == 2:
        # (b) a vowel at the beginning of the word followed by a non-vowel.
        return is_vowel(rs[0]) and not is_vowel(rs[1])
    else:
        r, rr, rrr = rs[-1], rs[-2], rs[-3]

        # (a) a vowel followed by a non-vowel other than w, x or Y and preceded by a non-vowel
        # N v N
        return (
            not is_vowel(rrr)
            and is_vowel(rr)
            and (not is_vowel(r) and r != "w" and r != "x" and r != "Y")
        )

# A word is called short if it ends in a short syllable, and if R1 is null.
#
# Define a short syllable in a word as either
#  (a) a vowel followed by a non-vowel other than w, x or Y and preceded by a non-vowel, or
#  (b) a vowel at the beginning of the word followed by a non-vowel.
def is_short_word(rs: list[str], r1: int) -> bool:
	if r1 < len(rs):
		return False

	return is_short_syllable(rs)
