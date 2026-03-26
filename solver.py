def load_words():
    with open("words.txt") as f:
        return [w.strip().upper() for w in f.readlines()]


def match(word, guess, result):
    for i in range(5):
        if result[i] == "🟩" and word[i] != guess[i]:
            return False
        if result[i] == "🟨":
            if guess[i] not in word or word[i] == guess[i]:
                return False
        if result[i] == "🟥":
            if guess[i] in word:
                return False
    return True


def filter_words(words, guess, result):
    return [w for w in words if match(w, guess, result)]


def best_guess(words):
    if not words:
        return "CRANE"
    return words[0]
