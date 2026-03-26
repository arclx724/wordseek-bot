def load_words():
    with open("words.txt") as f:
        return [
            w.strip().replace(",", "").replace('"', "").lower()
            for w in f.readlines()
            if len(w.strip()) >= 5
        ]


def match(word, guess, result):
    word = list(word)

    # 🟩 GREEN check
    for i in range(5):
        if result[i] == "🟩":
            if word[i] != guess[i]:
                return False

    # 🟨 YELLOW check
    for i in range(5):
        if result[i] == "🟨":
            if guess[i] not in word:
                return False
            if word[i] == guess[i]:
                return False

    # 🟥 RED check (SMART)
    for i in range(5):
        if result[i] == "🟥":
            # agar guess letter kisi aur jagah green/yellow hai toh ignore karo
            if guess[i] in guess[:i] or guess[i] in guess[i+1:]:
                continue
            if guess[i] in word:
                return False

    return True


def filter_words(words, guess, result):
    return [w for w in words if match(w, guess, result)]


# 🔥 SMART GUESS (frequency based)
def best_guess(words):
    if not words:
        return "crane"

    freq = {}

    # letter frequency count
    for w in words:
        for ch in set(w):
            freq[ch] = freq.get(ch, 0) + 1

    # score words
    def score(word):
        return sum(freq.get(c, 0) for c in set(word))

    # best word
    return max(words, key=score)
