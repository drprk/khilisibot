"""
KhilisiBot-style Telegram Troll Bot - IPL/CSK/Thala edition
"""

import logging
import random
import re
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

import os
BOT_TOKEN = os.environ.get("BOT_TOKEN")

TROLL_EVERY_N = [100]  # Every 7th message

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

message_counts: dict[int, int] = defaultdict(int)

MISPRONUNCIATIONS = [
    (r"\bthe\b",        "da"),
    (r"\bthis\b",       "dis"),
    (r"\bthat\b",       "dat"),
    (r"\bthey\b",       "dey"),
    (r"\bthose\b",      "doze"),
    (r"\bwith\b",       "wit"),
    (r"\byour\b",       "ur"),
    (r"\bare\b",        "iz"),
    (r"\bis\b",         "iz"),
    (r"\bwhat\b",       "wot"),
    (r"\bwhere\b",      "wia"),
    (r"\bhere\b",       "hia"),
    (r"\bthere\b",      "dere"),
    (r"\bbecause\b",    "coz"),
    (r"\bpeople\b",     "pipul"),
    (r"\bvery\b",       "veddy"),
    (r"\bfor\b",        "4"),
    (r"\byou\b",        "u"),
    (r"\bto\b",         "2"),
    (r"\btoo\b",        "2"),
    (r"\bgreat\b",      "gweat"),
    (r"\bright\b",      "wight"),
    (r"\bring\b",       "wing"),
    (r"\breal\b",       "weal"),
    (r"\brun\b",        "wun"),
    (r"\bthink\b",      "tink"),
    (r"\bthree\b",      "tree"),
    (r"\bthrough\b",    "tru"),
    (r"\bknow\b",       "kno"),
    (r"\bsomething\b",  "sumtin"),
    (r"\beverything\b", "evryting"),
    (r"\bnothing\b",    "nutin"),
    (r"\bbrother\b",    "anna"),
    (r"\bman\b",        "machan"),
]

TROLL_TEMPLATES = [

    # ── Classic roasts ────────────────────────────────────────────────────────
    "👆 {name} sed: \"{msg}\"\n\nMy analysis: absolute nonsense 💀",
    "❗️{name} u mean \"{garbled}\"?? iz dat wat u sed??",
    "Ekskuse me {name}... did u jus say \"{garbled}\"?? 💀💀",
    "{name}: \"{garbled}\"\n\nDa group after reading dis: 😐",
    "Bro {name} typed dis wit full confidence 😭\n\"{garbled}\"",
    "We hereby nominate {name} 4 da 'Most Confusing Message' award 🏆\n\"{garbled}\"",
    "{name} said \"{garbled}\" and expected us 2 understand 💀",
    "Sir/Ma'am {name}, wot iz \"{garbled}\" supposed 2 mean exactly? 🤔",
    "Da bot haz spoken: {name}'s \"{garbled}\" haz been flagged 4 crimes against grammar 🚔",
    "Translating {name}'s message... Error 404: Meaning not found 🤖\nOriginal: \"{garbled}\"",
    "Nobody:\nAbsolutely nobody:\n{name}: \"{garbled}\" 💀",
    "{name} woke up, chose chaos, and typed \"{garbled}\" 😤",
    "Da confidence wit which {name} delivered \"{garbled}\" is both impressive and terrifying 😨",
    "{name} typed \"{garbled}\" and logged off like nothing happened. Da villain origin story 😈",
    "I read {name}'s \"{garbled}\" 3 times. Still makes less sense each time 🔄💀",
    "Da universe iz 13.8 billion years old and somehow produced {name} typing \"{garbled}\". Wild 🌌",
    "Da prophecy spoke of a chosen one who wud send \"{garbled}\". {name} iz dat chosen one 🌟",
    "{name}'s \"{garbled}\" iz da reason people go on social media detox 📵",
    "Future generations will study {name}'s \"{garbled}\" as a cautionary tale 📚",
    "Da last words of {name}'s reputation: \"{garbled}\" 🪦",
    "{name} cooked \"{garbled}\" and served it 2 da group. We r all food poisoned now 🤢",
    "Even da dumbest animal in da savanna haz more 2 say than {name}'s \"{garbled}\" 🦁",
    "I put {name}'s \"{garbled}\" in2 Google Translate. It said: pls help dis person 🌍",
    "Da simulation glitched and allowed {name} 2 send \"{garbled}\". We r looking in2 it 🖥️",
    "{name}'s \"{garbled}\" iz giving main character energy in all da wrong ways 🎭",
    "Breaking: {name}'s \"{garbled}\" haz been classified as a natural disaster in 12 countries 🌍🚨",

    # ── Game of Thrones ───────────────────────────────────────────────────────
    "Daenerys Targaryen wud burn \"{garbled}\" by {name} wit dragonfire and she wud b right 🐉🔥",
    "Da Night King raised da dead and even dey refused 2 acknowledge {name}'s \"{garbled}\" ❄️💀",
    "Tyrion Lannister drinks and knows tings. After reading {name}'s \"{garbled}\" he jus drinks 🍷",
    "Jon Snow knows nutting. But even he knows {name}'s \"{garbled}\" iz pure madness 🗡️",
    "Cersei said: wen u play da game of group chats, u win or u die. {name} typed \"{garbled}\" and died 👑💀",
    "Hodor cud only say one word but it made more sense than {name}'s \"{garbled}\" 🚪",
    "Even da Three-Eyed Raven refused 2 see {name}'s \"{garbled}\" coming. Dat's how bad it iz 🐦",
    "Arya Stark haz a list. {name}'s \"{garbled}\" jus got added 2 it 🗡️📋",
    "Winter is coming. And so iz da secondhand embarrassment from {name}'s \"{garbled}\" ❄️😬",
    "Khaleesi haz reviewed \"{garbled}\" by {name}. Her verdict: Dracarys 🔥👑",
    "A Lannister always pays their debts. {name} always delivers nonsense like \"{garbled}\" 💰",
    "House {name} words: \"{garbled}\" — dat's y dey hav no house anymore 🏰💀",
    "Ghost da direwolf growled at {name}'s \"{garbled}\". Good boy. Smart boy 🐺",
    "Melisandre looked into da flames and saw \"{garbled}\" by {name}. Dat's y she left Westeros 🔥👁️",
    "Samwell Tarly read every book in da Citadel. Found no explanation 4 {name}'s \"{garbled}\" 📚",
    "Varys' little birds brought him news of {name}'s \"{garbled}\". He wept 4 da realm 🕊️",
    "Da Dothraki hav no word 4 \"{garbled}\" in their language. Lucky dem 🐎",
    "Ned Stark lost his head 4 honor. {name} losing credibility 4 \"{garbled}\" iz less honorable 🗡️",
    "Fire cannot kill a dragon. But {name}'s \"{garbled}\" almost killed da vibe in dis chat 🐉💀",
    "Da maesters of da Citadel hav studied {name}'s \"{garbled}\" and declared it a new form of madness 🔬",
    "Joffrey woz da worst king. But even he wudnt hav decreed dat \"{garbled}\" iz acceptable 👑",
    "Theon Greyjoy, after ALL he went thru, managed 2 say more sensible tings than {name}'s \"{garbled}\" 🏴‍☠️",
    "Stannis Baratheon: da one true king. {name}'s \"{garbled}\": da one true disaster 🔥",
    "Oberyn Martell died 4 justice. He wud die again reading {name}'s \"{garbled}\" 🐍",
    "Ygritte said u know nutting Jon Snow. She had never met {name} 👀",

    # ── IPL / Cricket ─────────────────────────────────────────────────────────
    "{name}'s \"{garbled}\" iz da dropped catch of dis conversation. Dhoni wud b disappointed 🏏💀",
    "Da DRS review iz in: {name}'s \"{garbled}\" iz OUT. Stumped by common sense 🏏",
    "Commentator voice: AND {name} haz delivered \"{garbled}\"... dat's a wide. Very wide. 🎙️",
    "{name} swung 4 a six wit \"{garbled}\" and got bowled out by basic logic 🏏💨",
    "IPL auction update: {name}'s \"{garbled}\" haz been UNSOLD. Even at base price of ₹20 lakhs 💸",
    "Da pitch report says: conditions r perfect 4 batting. {name} still managed 2 send \"{garbled}\" tho 📊",
    "Rohit Sharma wud retire from dis conversation if he saw {name}'s \"{garbled}\" 🏏",
    "Virat Kohli has played 500+ matches. He haz never been as lost as {name} with \"{garbled}\" 🏏😤",
    "{name}'s \"{garbled}\" iz like a dot ball every single time. No runs. No sense. 🏏",
    "Even Jasprit Bumrah's unplayable yorker iz more understandable than {name}'s \"{garbled}\" 🎯",
    "Da IPL trophy haz more value than da point {name} woz trying 2 make in \"{garbled}\" 🏆",
    "Nasser Hussain on commentary: I've seen bad cricket. I've never seen anyting like {name}'s \"{garbled}\" 🎙️",
    "Da Super Over cannot save {name} from da damage done by \"{garbled}\" ⚡",
    "RCB haz won zero IPL titles. {name}'s \"{garbled}\" haz won zero braincells. Both r consistent 💙❌",
    "Even a beamer doesn't hurt as much as reading {name}'s \"{garbled}\" 😬🏏",
    "{name}'s \"{garbled}\" iz da cricketing equivalent of a 5-ball over. How did dis even happen 😭",
    "Hardik Pandya switched teams and still got more support than {name}'s \"{garbled}\" 🏏",
    "Da Duckworth-Lewis method cannot calculate how wrong {name}'s \"{garbled}\" iz 📐",
    "Strategic timeout called 2 recover from {name}'s \"{garbled}\" 🛑",
    "Da umpire raised both fingers. {name}'s \"{garbled}\" iz OUT. Double wicket 🏏🖕",

    # ── Thala / CSK / MS Dhoni ────────────────────────────────────────────────
    "Thala 7 iz a reason. {name}'s \"{garbled}\" iz NOT a reason for anything 💛🦁",
    "MS Dhoni finishes games wit calmness and class. {name} finishes sentences wit \"{garbled}\" 💛😔",
    "Dhoni: keeps cool under pressure\n{name}: sends \"{garbled}\" under zero pressure 💛💀",
    "Whistle Podu for CSK 🎺 Silence Podu for {name}'s \"{garbled}\" 🤫",
    "Thala 7 - because every great team needs a number 7\n{name}'s message iz reason number 0 💛",
    "Even da Chennai Super Kings' losing seasons made more sense than {name}'s \"{garbled}\" 💛",
    "CSK fans survived 2 years of suspension. Dey cannot survive {name}'s \"{garbled}\" tho 💛😭",
    "Dhoni's helicopter shot iz iconic. {name}'s \"{garbled}\" iz just a crash landing 🚁💥",
    "Thala would never. {name} always does. Proof: \"{garbled}\" 💛🦁",
    "Da Yellow Army stands strong. Dey sat down after reading {name}'s \"{garbled}\" 💛🪑",
    "MS Dhoni haz da best finishing record in cricket. {name} couldn't even finish a sensible thought: \"{garbled}\" 💛",
    "CSK: 5 time champions 🏆\n{name}'s \"{garbled}\": 0 time sensible 💀",
    "Dhoni's last ball six in 2011 World Cup > Everything. {name}'s \"{garbled}\" < Everything 💛🏆",
    "Yellove iz real. {name}'s \"{garbled}\" iz not real in any sense 💛❤️",
    "Da Chepauk crowd haz seen better days and better messages than {name}'s \"{garbled}\" 🏟️💛",
    "Thala 7 - because 7 iz perfect. {name}'s \"{garbled}\" - because some tings r perfectly wrong 💛😂",
    "Even da most painful CSK loss hurt less than reading {name}'s \"{garbled}\" 💛💔",
    "Dhoni: cool, calm, calculated\n{name}'s \"{garbled}\": chaotic, confusing, certified nonsense 💛💀",
    "CSK won trophies in their comeback season. {name} sent \"{garbled}\" in their comeback message. Different results 💛",
    "Ravindra Jadeja and Dhoni hav da best partnership in IPL history. {name} and common sense do not 💛🗡️",
    "Suresh Raina - Mr. IPL himself - wud read {name}'s \"{garbled}\" and say: nahi yaar 💛🙈",
    "Da iconic Dhoni stump out iz faster than {name}'s brain when typing \"{garbled}\" ⚡💛",
    "Thala for a reason: Dhoni always delivers. {name} always disappoints. Proof: \"{garbled}\" 💛",
    "CSK jersey number 7 iz sacred 🙏 {name}'s message \"{garbled}\" iz... da opposite of sacred 💛💀",
    "Doni keeps da team calm. Nobody can stay calm after {name}'s \"{garbled}\" 💛😤",
    "Da yellow helmet iz fearless. Da person who sent \"{garbled}\" iz {name}. Very different energy 💛🪖",

    # ── Tamil / South India culture ───────────────────────────────────────────
    "Rajinikanth wud flip a cigarette, catch it in his mouth and still make more sense than {name}'s \"{garbled}\" 🕶️",
    "Vijay anna wud dance in da rain 4 dis group but not 4 {name}'s \"{garbled}\" 💃🌧️",
    "Kamal Haasan haz acted in 200+ films in 10 languages. None of dem iz as confusing as {name}'s \"{garbled}\" 🎬",
    "Even Managaram traffic iz less confusing than {name}'s \"{garbled}\" 🚗😵",
    "Saravana Stores haz everything. A solution 4 {name}'s \"{garbled}\"? Illa 🛒❌",
    "Idly, sambar, filter kaapi ☕ — tings dat make sense. {name}'s \"{garbled}\" — does not make dis list",
    "Vadivelu comedy iz intentional. {name}'s \"{garbled}\" iz accidental comedy 😂",
    "Auto driver logic > {name}'s \"{garbled}\" logic. And dat's sayin sumtin 🛺",
    "Neenga romba over ah irukeenga {name}. Proof: \"{garbled}\" 🙄",
    "Enna da ithu {name}... \"{garbled}\" nu enna type pannitu iruka 🤦",

    # ── Bollywood ─────────────────────────────────────────────────────────────
    "{name} typed \"{garbled}\" like dis iz a SRK monologue. It iz not 🎬",
    "Ek dum bakwaas. {name} typed \"{garbled}\" and thought it woz profound 🤦",
    "Even Amitabh Bachchan's baritone cud not make \"{garbled}\" by {name} sound good 🎤",
    "Da item number nobody asked 4: {name} presenting \"{garbled}\" 💃",
    "Bhai (Salman Khan) wud forgive many tings. Not \"{garbled}\" by {name} tho 💪",
    "Kuch kuch hota hai, {name}. Dis? \"{garbled}\"? Nahi hota 💔",

    # ── Movies / Pop culture ──────────────────────────────────────────────────
    "Thanos snapped and wiped out half da universe. He kept {name}'s \"{garbled}\" 2 torture da survivors 💜",
    "Gandalf said: u shall not pass. He woz talking about {name}'s \"{garbled}\" entering da realm of sense 🧙‍♂️",
    "Even Voldemort wud not claim \"{garbled}\" by {name} 🧙",
    "Spider-Man: with great power comes great responsibility.\n{name}: \"{garbled}\" 🕷️",
    "Even Shrek, in his swamp, talking 2 a donkey, made more sense than {name}'s \"{garbled}\" 🧅",
    "Tony Stark built a suit in a cave. {name} typed \"{garbled}\" in perfect comfort. Disappointing 🦾",
    "Da force iz not strong wit {name}'s \"{garbled}\" ⚔️✨",

    # ── Philosophy ────────────────────────────────────────────────────────────
    "Socrates said da unexamined life iz not worth living. {name}'s \"{garbled}\" iz not worth reading 📜",
    "Einstein said imagination iz more important than knowledge. {name}'s \"{garbled}\" haz neither 🧠❌",
    "Shakespeare wrote 37 plays. None r as dramatic as {name} sending \"{garbled}\" 🎭",
    "Sun Tzu wrote da Art of War. {name} wrote \"{garbled}\". Very different legacies 📖⚔️",
    "Confucius say: man who types \"{garbled}\" haz much 2 learn. Luking at u {name} 🏮",

    # ── Tech ──────────────────────────────────────────────────────────────────
    "404: Brain not found. Source: {name}'s \"{garbled}\" 💻❌",
    "GitHub rejected {name}'s pull request titled \"{garbled}\" wit da comment: pls no 💻",
    "Google returned 0 results 4 \"{garbled}\" by {name}. First time in history 🔍",
    "Loading {name}'s meaning from \"{garbled}\"... ████░░░░ ERROR: null returned 🖥️",
    "{name}'s \"{garbled}\" crashed my mental RAM. I need 2 restart 🧠💥",

    # ── Extra chaotic ──────────────────────────────────────────────────────────
    "{name}: hold my chai\n*types \"{garbled}\"*\nDa chai: even I don't want 2 b associated wit dis ☕",
    "Da government should tax {name} extra 4 \"{garbled}\". Stupidity levy 📋💸",
    "Monkeys typing randomly cud eventually produce Shakespeare. Dey already produced {name}'s \"{garbled}\" 🐒",
    "I called mi grandmother and read her {name}'s \"{garbled}\". She hung up. She NEVER hangs up 👵📞",
    "Medical science cannot explain {name}'s \"{garbled}\". Neither can any other science 🔬",
    "Da brain scan came back. {name}'s \"{garbled}\" haz been traced 2 a very specific region: wrong 🧠❌",
    "Doctors hav identified a new condition: \"{garbled}\" syndrome, named after {name} 🏥",
    "Hurricane {name} haz made landfall. Category: \"{garbled}\". Evacuate ur brain cells 🌀",
    "A broken clock iz right twice a day. {name}'s \"{garbled}\" iz wrong all day every day ⏰",
    "If stupidity woz currency, {name}'s \"{garbled}\" wud make dem a billionaire 💰",
]


def mispronounce(text: str) -> str:
    result = text.lower()
    for pattern, replacement in MISPRONUNCIATIONS:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    return result


def pick_troll_reply(sender_name: str, original_msg: str) -> str:
    garbled = mispronounce(original_msg)
    template = random.choice(TROLL_TEMPLATES)
    return template.format(
        name=sender_name,
        msg=original_msg[:80] + ("…" if len(original_msg) > 80 else ""),
        garbled=garbled[:80] + ("…" if len(garbled) > 80 else ""),
        time=datetime.now().strftime("%H:%M"),
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Khaleesi haz arrived 🐉\nThala 7 iz a reason. Every 7th message gets roasted 💛🔥"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Every 7th message gets roasted 🔥\n"
        f"{len(TROLL_TEMPLATES)} troll templates: GOT 🐉 + IPL 🏏 + CSK/Thala 💛 + more\n"
        "/stats - see ur doom countdown"
    )


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    count = message_counts[chat_id]
    next_troll = 7 - (count % 7)
    await update.message.reply_text(
        f"📊 {count} messages counted.\n"
        f"Next roast in {next_troll} message(s) 😈\n"
        f"{len(TROLL_TEMPLATES)} troll templates loaded 💛🐉🏏"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message or update.edited_message
    if not message or not message.text:
        return
    if message.chat.type not in ("group", "supergroup"):
        return

    chat_id = message.chat_id
    message_counts[chat_id] += 1
    count = message_counts[chat_id]

    if not any(count % n == 0 for n in TROLL_EVERY_N):
        return

    sender = message.from_user
    name = sender.first_name if sender else "Anon"
    text = message.text.strip()
    if not text:
        return

    try:
        await message.reply_text(pick_troll_reply(name, text))
    except Exception as e:
        logger.warning("Could not send troll reply: %s", e)


def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("Bot is running with %d troll templates… Thala 7 for a reason 💛", len(TROLL_TEMPLATES))
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
