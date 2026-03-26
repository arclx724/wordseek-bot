import asyncio
import random
from telethon import TelegramClient, events

from solver import load_words, filter_words, best_guess
from config import *

client = TelegramClient(SESSION, API_ID, API_HASH)

# 🔒 STATE CONTROL
words = load_words()
possible = words.copy()
last_guess = None
game_active = False


def reset_game():
    global possible, last_guess, game_active
    possible = words.copy()
    last_guess = None
    game_active = True
    print("🔄 New game started")


def stop_game():
    global game_active
    game_active = False
    print("🛑 Game stopped")


async def safe_send(event, text):
    await asyncio.sleep(random.uniform(DELAY_MIN, DELAY_MAX))
    await event.reply(text)


@client.on(events.NewMessage)
async def handler(event):
    global possible, last_guess, game_active

    text = event.raw_text.lower()

    # =========================
    # 🏁 GAME END DETECT (STOP)
    # =========================
    if "congrats! you guessed it correctly" in text or "correct word:" in text:
        stop_game()
        return

    if "guessed it correctly" in text or "winner" in text:
        stop_game()
        return

    # =========================
    # 🎮 NEW GAME DETECT
    # =========================
    if "/new" in text or "start with /new" in text:
        reset_game()

        # first guess
        first_word = "CRANE"
        last_guess = first_word
        await safe_send(event, first_word)
        return

    # =========================
    # ❌ IGNORE IF GAME NOT ACTIVE
    # =========================
    if not game_active:
        return

    # =========================
    # 🧠 PROCESS RESULT
    # =========================
    if "🟩" in text or "🟨" in text or "🟥" in text:
        try:
            result = text.strip().split()[-1]

            if not last_guess:
                return

            possible = filter_words(possible, last_guess, result)

            guess = best_guess(possible)
            last_guess = guess

            await safe_send(event, guess)

        except Exception as e:
            print("Error:", e)


async def main():
    await client.start()
    print("🤖 Bot running...")
    await client.run_until_disconnected()


asyncio.run(main())
