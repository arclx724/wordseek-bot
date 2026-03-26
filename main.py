import asyncio
import random
from telethon import TelegramClient, events

from solver import load_words, filter_words, best_guess
from config import *

client = TelegramClient(SESSION, API_ID, API_HASH)

# 🔒 STATE
words = load_words()
possible = words.copy()
used_words = set()

last_guess = None
game_active = False
bot_enabled = False


def reset_game():
    global possible, last_guess, game_active, used_words
    possible = words.copy()
    used_words = set()
    last_guess = None
    game_active = True


def stop_game():
    global game_active
    game_active = False


async def safe_send(event, text):
    try:
        await asyncio.sleep(random.uniform(DELAY_MIN, DELAY_MAX))
        await client.send_message(event.chat_id, text)
    except Exception as e:
        print("Send error:", e)


@client.on(events.NewMessage)
async def handler(event):
    global possible, last_guess, game_active, bot_enabled, used_words

    try:
        text = event.raw_text.lower().strip()
    except:
        return

    # 🔥 START
    if text == "arclx":
        bot_enabled = True
        return

    # 🛑 STOP
    if text == "stop":
        bot_enabled = False
        stop_game()
        return

    if not bot_enabled:
        return

    # 🏁 GAME END
    if "correct word:" in text or "guessed it correctly" in text:
        stop_game()
        return

    # 🎮 NEW GAME
    if "/new" in text:
        reset_game()

        first_word = "crane"
        last_guess = first_word
        used_words.add(first_word)

        await safe_send(event, first_word)
        return

    if not game_active:
        return

    # 🧠 RESULT PROCESS
    if "🟩" in text or "🟨" in text or "🟥" in text:
        try:
            result = text.strip().split()[-1]

            if len(result) != 5:
                return

            if not last_guess:
                return

            possible = filter_words(possible, last_guess, result)

            # 🔥 REMOVE USED WORDS
            possible = [w for w in possible if w not in used_words]

            if not possible:
                return

            guess = best_guess(possible)
            last_guess = guess
            used_words.add(guess)

            await safe_send(event, guess)

        except Exception as e:
            print("Error:", e)


async def main():
    await client.start()
    print("✅ Bot running...")
    await client.run_until_disconnected()


asyncio.run(main())
