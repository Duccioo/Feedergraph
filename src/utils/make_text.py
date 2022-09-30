import random
from unicodedata import name as unicode_name
from itertools import accumulate
from bisect import bisect

# Set the unicode version.
# Your system may not support Unicode 7.0 charecters just yet! So hipster.
UNICODE_VERSION = 6

# Sauce: http://www.unicode.org/charts/PDF/U1F300.pdf
EMOJI_RANGES_UNICODE = {
    6: [
        ("\U0001F300", "\U0001F320"),
        ("\U0001F330", "\U0001F335"),
        ("\U0001F337", "\U0001F37C"),
        ("\U0001F380", "\U0001F393"),
        ("\U0001F3A0", "\U0001F3C4"),
        ("\U0001F3C6", "\U0001F3CA"),
        ("\U0001F3E0", "\U0001F3F0"),
        ("\U0001F400", "\U0001F43E"),
        ("\U0001F440",),
        ("\U0001F442", "\U0001F4F7"),
        ("\U0001F4F9", "\U0001F4FC"),
        ("\U0001F500", "\U0001F53C"),
        ("\U0001F540", "\U0001F543"),
        ("\U0001F550", "\U0001F567"),
        ("\U0001F5FB", "\U0001F5FF"),
    ],
    7: [
        ("\U0001F300", "\U0001F32C"),
        ("\U0001F330", "\U0001F37D"),
        ("\U0001F380", "\U0001F3CE"),
        ("\U0001F3D4", "\U0001F3F7"),
        ("\U0001F400", "\U0001F4FE"),
        ("\U0001F500", "\U0001F54A"),
        ("\U0001F550", "\U0001F579"),
        ("\U0001F57B", "\U0001F5A3"),
        ("\U0001F5A5", "\U0001F5FF"),
    ],
    8: [
        ("\U0001F300", "\U0001F579"),
        ("\U0001F57B", "\U0001F5A3"),
        ("\U0001F5A5", "\U0001F5FF"),
    ],
}

NO_NAME_ERROR = "(No name found for this codepoint)"


def random_emoji(unicode_version=6):
    if unicode_version in EMOJI_RANGES_UNICODE:
        emoji_ranges = EMOJI_RANGES_UNICODE[unicode_version]
    else:
        emoji_ranges = EMOJI_RANGES_UNICODE[-1]

    # Weighted distribution
    count = [ord(r[-1]) - ord(r[0]) + 1 for r in emoji_ranges]
    weight_distr = list(accumulate(count))

    # Get one point in the multiple ranges
    point = random.randrange(weight_distr[-1])

    # Select the correct range
    emoji_range_idx = bisect(weight_distr, point)
    emoji_range = emoji_ranges[emoji_range_idx]

    # Calculate the index in the selected range
    point_in_range = point
    if emoji_range_idx != 0:
        point_in_range = point - weight_distr[emoji_range_idx - 1]

    # Emoji 😄
    emoji = chr(ord(emoji_range[0]) + point_in_range)

    return emoji


def number_to_emoji(int):
    legenda = {
        "0": "0️⃣",
        "1": "1️⃣",
        "2": "2️⃣",
        "3": "3️⃣",
        "4": "4️⃣",
        "5": "5️⃣",
        "6": "6️⃣",
        "7": "7️⃣",
        "8": "8️⃣",
        "9": "9️⃣",
    }
    string_int = str(int)
    string_emoji = ""
    for cifra in string_int:
        string_emoji = string_emoji + str(legenda[str(cifra)])+" "
    return string_emoji


def bip_bop():

    rand = random.randrange(0, 5)
    if rand == 0:
        return " BIP BOP "
    elif rand == 1:
        return " BOP PIP "
    elif rand == 2:
        return " BUP BIP "
    elif rand == 3:
        return " BI BI BIP "
    elif rand == 4:
        return " PIP BUP "


if __name__ == "__main__":

    print(number_to_emoji(34215))
