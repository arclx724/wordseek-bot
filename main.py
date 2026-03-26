import asyncio
import random
from telethon import TelegramClient, events

from solver import load_words, filter_words, best_guess
from config import *

client = TelegramClient(SESSION, API_ID, API_HASH)

# 🔒 STATE
words = load_words()
possible = words.copy()
last_guess = None
game_active = False
bot_enabled = False


def reset_game():
    global possible, last_guess, game_active
    possible = words.copy()
    last_guess = None
    game_active = True


def stop_game():
    global game_active
    game_active = False


# ✅ FIXED SEND FUNCTION
async def safe_send(event, text):
    try:
        await asyncio.sleep(random.uniform(DELAY_MIN, DELAY_MAX))

        # 🔥 always send to chat directly (no reply)
        await client.send_message(event.chat_id, text)

    except Exception as e:
        print("Send error:", e)


@client.on(events.NewMessage)
async def handler(event):
    global possible, last_guess, game_active, bot_enabled

    try:
        text = event.raw_text.lower().strip()
    except:
        return

    # =========================
    # 🔥 MANUAL START (silent)
    # =========================
    if text == "arclx":
        bot_enabled = True
        return

    # =========================
    # 🛑 MANUAL STOP (silent)
    # =========================
    if text == "stop":
        bot_enabled = False
        stop_game()
        return

    # =========================
    # ❌ IGNORE if bot OFF
    # =========================
    if not bot_enabled:
        return

    # =========================
    # 🏁 GAME END DETECT
    # =========================
    if "congrats! you guessed it correctly" in text or "correct word:" in text:
        stop_game()
        return

    if "winner" in text:
        stop_game()
        return

    # =========================
    # 🎮 NEW GAME DETECT
    # =========================
    if "/new" in text or "start with /new" in text:
        reset_game()

        first_word = "CRANE"
        last_guess = first_word

        await safe_send(event, first_word)
        return

    # =========================
    # ❌ IGNORE if game not active
    # =========================
    if not game_active:
        return

    # =========================
    # 🧠 PROCESS RESULT
    # =========================
    if "🟩" in text or "🟨" in text or "🟥" in text:
        try:
            result = text.strip().split()[-1]

            if len(result) != 5:
                return

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
    print("✅ Bot is running...")
    await client.run_until_disconnected()


asyncio.run(main())
