import asyncio
import random
import time
from telethon import TelegramClient, events

from solver import load_words, filter_words, best_guess
from config import *

client = TelegramClient(SESSION, API_ID, API_HASH)

words = load_words()
possible = words.copy()
used_words = set()

last_guess = None
game_active = False
bot_enabled = False
LAST_SENT = 0


def reset_game():
    global possible, last_guess, game_active, used_words
    possible = words.copy()
    used_words = set()
    last_guess = None
    game_active = True
    print("🎮 Game Started")


def stop_game():
    global game_active
    game_active = False
    print("🛑 Game Stopped")


async def safe_send(event, text):
    global LAST_SENT

    try:
        now = time.time()

        if now - LAST_SENT < 3:
            await asyncio.sleep(random.randint(3, 5))

        await asyncio.sleep(random.uniform(2, 4))
        await event.reply(text.lower())

        LAST_SENT = time.time()
        print("➡️ Sent:", text)

    except Exception as e:
        print("Send error:", e)


def extract_result(text):
    emojis = ["🟥", "🟩", "🟨"]
    result = ""

    for ch in text:
        if ch in emojis:
            result += ch

    return result


@client.on(events.NewMessage)
async def handler(event):
    global possible, last_guess, game_active, bot_enabled, used_words

    try:
        text = event.raw_text.lower()
    except:
        return

    print("📩 MSG:", text)  # 🔥 DEBUG

    # 🔥 START BOT
    if text.strip() == "arclx":
        bot_enabled = True
        print("✅ Bot Enabled")
        return

    # 🛑 STOP BOT
    if text.strip() == "stop":
        bot_enabled = False
        stop_game()
        print("❌ Bot Disabled")
        return

    if not bot_enabled:
        return

    # 🏁 GAME WIN
    if "correct word:" in text or "guessed it correctly" in text:
        stop_game()
        return

    # 🎮 NEW GAME (FIXED)
    if "/new" in text:
        reset_game()

        first_word = "audio"
        last_guess = first_word
        used_words.add(first_word)

        await safe_send(event, first_word)
        return

    if not game_active:
        return

    # 🧠 PROCESS RESULT
    if "🟩" in text or "🟨" in text or "🟥" in text:
        try:
            result = extract_result(text)
            print("🎯 Result:", result)

            if len(result) != 5:
                return

            if not last_guess:
                return

            possible = filter_words(possible, last_guess, result)

            possible = [w for w in possible if w not in used_words]

            print("🧠 Possible:", len(possible))

            if not possible:
                print("⚠️ Resetting...")
                possible = [w for w in words if w not in used_words]

                if not possible:
                    print("❌ Stuck")
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
