def word_count(text):
    return len(text.split())


def average_word_length(text):
    words = text.split()
    return sum(len(w) for w in words) / len(words)
