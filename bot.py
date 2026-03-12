"""
KhilisiBot - AI-powered contextual roasting using Claude
Roasts every 100th message based on actual chat history
"""

import logging
import os
import random
import re
import httpx
from collections import defaultdict
from datetime import datetime
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_KEY")

TROLL_EVERY_N = [100]

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Per-chat message counters and history
message_counts: dict[int, int] = defaultdict(int)
chat_history: dict[int, list] = defaultdict(list)
MAX_HISTORY = 15  # messages to keep for context

MISPRONUNCIATIONS = [
    (r"\bthe\b",        "da"),
    (r"\bthis\b",       "dis"),
    (r"\bthat\b",       "dat"),
    (r"\bthey\b",       "dey"),
    (r"\bwith\b",       "wit"),
    (r"\byour\b",       "ur"),
    (r"\bare\b",        "iz"),
    (r"\bis\b",         "iz"),
    (r"\bwhat\b",       "wot"),
    (r"\bbecause\b",    "coz"),
    (r"\bpeople\b",     "pipul"),
    (r"\bvery\b",       "veddy"),
    (r"\bfor\b",        "4"),
    (r"\byou\b",        "u"),
    (r"\bto\b",         "2"),
    (r"\bsomething\b",  "sumtin"),
    (r"\bbrother\b",    "anna"),
    (r"\bman\b",        "machan"),
]

# Fallback templates if AI fails
FALLBACK_TEMPLATES = [
    "👆 {name} sed: \"{msg}\"\n\nMy analysis: absolute nonsense 💀",
    "Translating {name}'s message... Error 404: Meaning not found 🤖\nOriginal: \"{msg}\"",
    "Khaleesi haz reviewed {name}'s message. Her verdict: Dracarys 🔥👑",
    "Thala wud never. {name} always does. Proof: \"{msg}\" 💛",
    "Da DRS review iz in: {name}'s message iz OUT. Stumped by common sense 🏏",
    "Even da Night King raised an eyebrow at {name}'s \"{msg}\" ❄️💀",
    "MS Dhoni keeps cool under pressure. {name} sends \"{msg}\" under zero pressure 💛😔",
    "Da bot haz spoken: {name} haz been flagged 4 crimes against grammar 🚔",
]


def mispronounce(text: str) -> str:
    result = text.lower()
    for pattern, replacement in MISPRONUNCIATIONS:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    return result


async def get_ai_roast(target_name: str, target_msg: str, history: list) -> str:
    """Call Claude API to generate a contextual roast."""
    if not ANTHROPIC_KEY:
        return None

    # Format chat history for context
    history_text = "\n".join(
        [f"{m['name']}: {m['text']}" for m in history[-MAX_HISTORY:]]
    )

    prompt = f"""You are KhilisiBot, a savage but funny Telegram group troll bot inspired by Game of Thrones' Khaleesi. 
You roast group members in a fun, playful way using broken English, desi slang, IPL/CSK references, and GOT lore.

Here is the recent chat history of the group:
{history_text}

The person you must roast RIGHT NOW is: {target_name}
Their most recent message was: "{target_msg}"

Write a single short roast (2-4 lines max) that:
- Is VERY specific to what {target_name} just said or the topic being discussed
- References something from the recent chat history if possible
- Uses broken English like "iz", "dat", "dis", "u", "2", "4", "wit", "coz"
- Can include GOT references, IPL/CSK/Thala references, desi/Tamil references
- Is funny and savage but not mean-spirited
- Ends with a relevant emoji
- Does NOT start with "{target_name} said" — be creative

Just write the roast. Nothing else."""

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": ANTHROPIC_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": "claude-haiku-4-5-20251001",
                    "max_tokens": 200,
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
            data = response.json()
            return data["content"][0]["text"].strip()
    except Exception as e:
        logger.warning("AI roast failed: %s", e)
        return None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Khaleesi haz arrived 🐉\nI now use AI 2 roast ur friends wit full context 😈\nEvery 100th message gets it 💛🔥"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Every 100th message gets an AI-powered contextual roast 🤖🔥\n"
        "I read da last 15 messages 4 context b4 roasting\n"
        "/stats - see ur doom countdown"
    )


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    count = message_counts[chat_id]
    next_troll = 100 - (count % 100)
    await update.message.reply_text(
        f"📊 {count} messages counted.\n"
        f"Next AI roast in {next_troll} message(s) 😈🤖"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message or update.edited_message
    if not message or not message.text:
        return
    if message.chat.type not in ("group", "supergroup"):
        return

    chat_id = message.chat_id
    sender = message.from_user
    name = sender.first_name if sender else "Anon"
    text = message.text.strip()

    # Store in history
    chat_history[chat_id].append({"name": name, "text": text})
    if len(chat_history[chat_id]) > MAX_HISTORY * 2:
        chat_history[chat_id] = chat_history[chat_id][-MAX_HISTORY:]

    message_counts[chat_id] += 1
    count = message_counts[chat_id]

    if not any(count % n == 0 for n in TROLL_EVERY_N):
        return

    if not text:
        return

    # Try AI roast first
    history_snapshot = list(chat_history[chat_id][:-1])  # exclude current msg
    roast = await get_ai_roast(name, text, history_snapshot)

    # Fall back to template if AI fails
    if not roast:
        template = random.choice(FALLBACK_TEMPLATES)
        roast = template.format(name=name, msg=text[:80])

    try:
        await message.reply_text(roast)
    except Exception as e:
        logger.warning("Could not send roast: %s", e)


def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("KhilisiBot running with AI-powered contextual roasting 🐉🤖")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
