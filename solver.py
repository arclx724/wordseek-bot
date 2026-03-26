from collections import Counter

def load_words():
    with open("words.txt") as f:
        return [
            w.strip().replace(",", "").replace('"', "").lower()
            for w in f.readlines()
            if len(w.strip()) == 5
        ]


def match(word, guess, result):
    word_count = Counter(word)

    # 🟩 GREEN
    for i in range(5):
        if result[i] == "🟩":
            if word[i] != guess[i]:
                return False
            word_count[guess[i]] -= 1

    # 🟨 YELLOW
    for i in range(5):
        if result[i] == "🟨":
            if guess[i] not in word:
                return False
            if word[i] == guess[i]:
                return False
            if word_count[guess[i]] <= 0:
                return False
            word_count[guess[i]] -= 1

    # 🟥 RED (duplicate safe)
    for i in range(5):
        if result[i] == "🟥":
            if word_count[guess[i]] > 0:
                return False

    return True


def filter_words(words, guess, result):
    return [w for w in words if match(w, guess, result)]


def best_guess(words):
    if not words:
        return "crane"

    freq = Counter("".join(words))

    def score(word):
        return sum(freq[c] for c in set(word))

    return max(words, key=score)
