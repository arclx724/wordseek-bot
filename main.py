import asyncio
import random
import time
from telethon import TelegramClient, events

from solver import load_words, filter_words, best_guess
from config import *

client = TelegramClient(SESSION, API_ID, API_HASH)

words = load_words()

# 🔥 PER CHAT STATE
chat_states = {}

LAST_SENT = {}


def get_chat(chat_id):
    if chat_id not in chat_states:
        chat_states[chat_id] = {
            "enabled": False,
            "game_active": False,
            "possible": words.copy(),
            "used": set(),
            "last_guess": None
        }
    return chat_states[chat_id]


def reset_game(state):
    state["possible"] = words.copy()
    state["used"] = set()
    state["last_guess"] = None
    state["game_active"] = True
    print("🎮 Game Started")


def stop_game(state):
    state["game_active"] = False
    print("🛑 Game Stopped")


async def safe_send(event, text, chat_id):
    try:
        now = time.time()

        if chat_id not in LAST_SENT:
            LAST_SENT[chat_id] = 0

        if now - LAST_SENT[chat_id] < 3:
            await asyncio.sleep(random.randint(3, 5))

        await asyncio.sleep(random.uniform(2, 4))
        await event.reply(text.lower())

        LAST_SENT[chat_id] = time.time()

    except Exception as e:
        print("Send error:", e)


def extract_result(text):
    emojis = ["🟥", "🟩", "🟨"]
    return "".join([c for c in text if c in emojis])


@client.on(events.NewMessage)
async def handler(event):
    chat_id = event.chat_id
    state = get_chat(chat_id)

    try:
        text = event.raw_text.lower().strip()
    except:
        return

    print(f"[{chat_id}] 📩 {text}")

    # 🔥 ENABLE ONLY THIS CHAT
    if text == "arclx":
        state["enabled"] = True
        print(f"✅ Enabled in {chat_id}")
        return

    # 🛑 DISABLE ONLY THIS CHAT
    if text == "stop":
        state["enabled"] = False
        stop_game(state)
        print(f"❌ Disabled in {chat_id}")
        return

    # ❌ ignore other chats
    if not state["enabled"]:
        return

    # 🏁 WIN DETECT
    if "correct word:" in text or "guessed it correctly" in text:
        stop_game(state)
        return

    # 🎮 NEW GAME
    if "/new" in text:
        reset_game(state)

        first_word = "crane"
        state["last_guess"] = first_word
        state["used"].add(first_word)

        await safe_send(event, first_word, chat_id)
        return

    if not state["game_active"]:
        return

    # 🧠 PROCESS RESULT
    if "🟩" in text or "🟨" in text or "🟥" in text:
        try:
            result = extract_result(text)

            if len(result) != 5:
                return

            if not state["last_guess"]:
                return

            possible = filter_words(
                state["possible"],
                state["last_guess"],
                result
            )

            possible = [w for w in possible if w not in state["used"]]

            print(f"🧠 Possible: {len(possible)}")

            if not possible:
                possible = [w for w in words if w not in state["used"]]
                if not possible:
                    print("❌ Stuck")
                    return

            guess = best_guess(possible)

            state["last_guess"] = guess
            state["used"].add(guess)
            state["possible"] = possible

            await safe_send(event, guess, chat_id)

        except Exception as e:
            print("Error:", e)


async def main():
    await client.start()
    print("✅ Bot running...")
    await client.run_until_disconnected()


asyncio.run(main())
