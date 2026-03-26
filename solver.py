def load_words():
    with open("words.txt") as f:
        return [
            w.strip().replace(",", "").replace('"', "").lower()
            for w in f.readlines()
            if len(w.strip()) == 5
        ]


def match(word, guess, result):
    # 🟩 GREEN
    for i in range(5):
        if result[i] == "🟩":
            if word[i] != guess[i]:
                return False

    # 🟨 YELLOW
    for i in range(5):
        if result[i] == "🟨":
            if guess[i] not in word:
                return False
            if word[i] == guess[i]:
                return False

    # 🟥 RED (STRICT REMOVE)
    for i in range(5):
        if result[i] == "🟥":
            if guess[i] in word:
                return False

    return True


def filter_words(words, guess, result):
    return [w for w in words if match(w, guess, result)]


# 🔥 SMART GUESS (no repeated letters priority)
def best_guess(words):
    if not words:
        return "crane"

    # unique letters wale words ko prefer karo
    def score(word):
        return len(set(word))

    return max(words, key=score)
