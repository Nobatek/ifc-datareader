"""A toolbox."""

import string


def clean_str(str_in):
    """Clean a string by removing 'punctuation' characters.

    :param str str_in: The input string to clean.
    :return str: The cleaned input string.
    """
    if str_in is None:
        return None

    # forbidden chars: !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~
    for cur_char in string.punctuation:
        if cur_char in str_in:
            str_in = str_in.replace(cur_char, '')

    return str_in
