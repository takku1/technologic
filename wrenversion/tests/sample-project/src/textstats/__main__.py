import sys

from .stats import average_word_length, word_count

text = " ".join(sys.argv[1:])
print(f"words: {word_count(text)}  average length: {average_word_length(text):.2f}")
