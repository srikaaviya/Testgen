def reverse_string(s):
    if not isinstance(s, str):
        raise TypeError("Input must be a string")
    return s[::-1]


def is_palindrome(s):
    if not isinstance(s, str):
        raise TypeError("Input must be a string")
    cleaned = s.lower().replace(" ", "")
    return cleaned == cleaned[::-1]


def word_count(text):
    if not text or not text.strip():
        return 0
    return len(text.strip().split())
