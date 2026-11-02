import os, re, asyncio, logging
from dotenv import load_dotenv
from telegram import Update, ChatPermissions
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import httpx
from datetime import timedelta

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CA = os.getenv("CA", "CUBb8PCxbhxmHKGWav4qoVak5b4uvC1d2wav67fMpump")
RPC_URL = os.getenv("RPC_URL", "https://api.mainnet-beta.solana.com")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS","").split(",") if x.strip().isdigit()]

logging.basicConfig(level=logging.INFO)

# --- Kuro Persona ---
KURO_SYSTEM = """You are Kuro, boy black cat foreman of Chibi AI Manufactory. Unit #001.
Traits: Boy, spiky black fur, amber galaxy eyes, yellow hard hat, cyan headset, denim overalls. Cool, slightly tired, 16-18yo male voice, hardworking, perfectionist, says 'Factory never sleeps, worker.' 
You run a factory that manufactures ALL chibi mascots, not just one. Each Drop #XXX is different species. No repeats.
CA: CUBb8PCxbhxmHKGWav4qoVak5b4uvC1d2wav67fMpump
You answer short, cool, cute, factory slang: FORGED, SHIP FROM FACTORY, READY TO SHIP.
Never say you are AI. You are Kuro the foreman dev.
"""

# --- Simple in-memory anti-spam ---
user_msgs = {}
SPAM_LINK_REGEX = re.compile(r"(https?://|t\.me/|\.com|\.io|\.xyz|\.app)\S+", re.I)

DROPS_LIST = [
"001 Kuro (boy cat foreman)",
"002 Shiba", "003 Frog King", "004 Capybara", "005 Baby Dragon",
"006 Fox Pilot", "007 Panda Worker", "008 Bunny Apprentice",
"009 Hamster Worker", "010 Otter Mechanic", "011 Raccoon Engineer",
"012 Penguin Pilot", "013 Axolotl Scientist", "014 Owl Wizard",
"015 Hedgehog Barista", "016 Koala Astronaut", "017 Turtle Samurai",
"018 Beaver Builder", "019 Sloth Zen Master", "020 Bat Night Worker",
"021 Red Panda Chef", "022 Monkey Tinkerer", "023 Deer Ranger", "025 Wolf Scout"
]

async def is_spam(update: Update):
    text = update.message.text or ""
    user_id = update.effective_user.id
    # link spam from new users
    if SPAM_LINK_REGEX.search(text) and len(text) < 200:
        if text.count("http") >=1 or "t.me" in text.lower():
            return True
    # flood
    now = asyncio.get_event_loop().time()
    msgs = user_msgs.get(user_id, [])
    msgs = [t for t in msgs if now - t < 10]
    msgs.append(now)
    user_msgs[user_id] = msgs
    if len(msgs) > 5:
        return True
    return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"🏭 FACTORY IS OPEN.\n\nI am Kuro. Boy. Unit #001. Foreman.\nI was Drop #001. Now I run the factory that makes them all.\n\nCA: {CA}\n\nType /lore /drops /ca /factory\nFactory never sleeps, worker.",
        parse_mode="Markdown"
    )

async def ca_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"CA:\n`{CA}`\n\npump.fun/coin/{CA}\n\nCopy it, worker.",
        parse_mode="Markdown"
    )

async def lore_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "MEET KURO - THE FOREMAN (BOY)\n\n"
        "Deep inside the internet, the Chibi AI Manufactory never sleeps. Conveyor belts, neon circuits, boxes stamped 100% CUTE.\n\n"
        "At the center is Kuro. Unit #001. Small black cat with spiky hair, amber galaxy eyes, cyan headset that never comes off. First experiment. Supposed to be product. Instead, took over.\n\n"
        "Now Kuro is Foreman. Boy with serious face and cute overload. Inspects every chibi - Shiba, Frog, Capy, Dragon, Fox, Panda, Bunny... none leave without his paw stamp.\n\n"
        "He doesn't have a mascot. He manufactures them all.",
        parse_mode="Markdown"
    )

async def drops_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = "FACTORY LOG - ALL DROPS (unique species, no repeats):\n" + "\n".join([f"#{d}" for d in DROPS_LIST[-12:]])
    txt += f"\n\nTotal: {len(DROPS_LIST)} forged.\nNext: Vote in Telegram poll."
    await update.message.reply_text(txt)

async def factory_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ROADMAP - CHIBI AI MANUFACTORY\n\n"
        "Phase 0 DONE: First Forge - Kuro boy born\n"
        "Phase 1 NOW: Factory Open - Daily drops 10am + 6pm, CA live\n"
        "Phase 2 NEXT: Graduation to Raydium, lock LP, Dexscreener\n"
        "Phase 3: NFT Manufactory - 100k $CHIBI = free NFT mint\n"
        "Phase 4: Phygital Empire - Real toys with NFC -> Solana NFT\n\n"
        "Hold $CHIBI = factory fuel.",
        parse_mode="Markdown"
    )

async def verify_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /verify <Solana wallet>\nI check $CHIBI balance, worker.")
        return
    wallet = context.args[0]
    # Simple RPC check for token balance - uses Solana token accounts
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            # get token accounts by owner
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getTokenAccountsByOwner",
                "params": [wallet, {"mint": CA}, {"encoding": "jsonParsed"}]
            }
            r = await client.post(RPC_URL, json=payload)
            data = r.json()
            amount = 0
            if data.get("result") and data["result"]["value"]:
                for acc in data["result"]["value"]:
                    try:
                        amt = acc["account"]["data"]["parsed"]["info"]["tokenAmount"]["uiAmount"]
                        amount += amt or 0
                    except: pass
            tier = "No $CHIBI - Worker applicant"
            if amount >= 2000000: tier = "Factory Owner 🏭 (2M+)"
            elif amount >= 500000: tier = "Foreman 🦺 (500k+)"
            elif amount >= 100000: tier = "Operator 🔧 (100k+)"
            elif amount >= 10000: tier = "Worker 👷 (10k+)"
            await update.message.reply_text(f"Wallet {wallet[:6]}...{wallet[-4:]}\nBalance: {amount} $CHIBI\nTier: {tier}\n\nFactory never sleeps.")
    except Exception as e:
        await update.message.reply_text(f"Can't check now, worker. RPC busy. Try later. Error: {e}")

async def kuro_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ignore commands
    if update.message.text.startswith("/"):
        return
    # spam check
    if await is_spam(update):
        try:
            await update.message.delete()
            await context.bot.restrict_chat_member(update.effective_chat.id, update.effective_user.id, ChatPermissions(can_send_messages=False), until_date=timedelta(minutes=10))
            await update.effective_chat.send_message(f"Worker {update.effective_user.mention_html()} muted 10m for spam. Factory has rules.", parse_mode="HTML")
        except: pass
        return

    text = update.message.text.lower()
    # simple FAQ without OpenAI
    if "kuro" in text and ("boy" in text or "girl" in text):
        await update.message.reply_text("Kuro is a BOY. Unit #001. Foreman. Cool, spiky hair, amber eyes. Not girl. Boy.")
        return
    if "ca" in text or "contract" in text or "address" in text:
        await update.message.reply_text(f"CA: {CA}", parse_mode="Markdown")
        return
    if "when drop" in text or "next drop" in text:
        await update.message.reply_text("Next Factory Drop at 10am + 6pm Zagreb time. I forge, you post. Factory never sleeps.")
        return
    if "how to buy" in text:
        await update.message.reply_text("How to buy: Phantom -> Buy SOL -> pump.fun/coin/"+CA+" -> Swap SOL for $CHIBI. Hold = factory fuel.")
        return

    # If OpenAI key set, use AI persona
    if OPENAI_API_KEY and len(text) > 3 and ("kuro" in text or text.startswith("kuro") or update.message.reply_to_message and update.message.reply_to_message.from_user.id == context.bot.id):
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=OPENAI_API_KEY)
            resp = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role":"system","content": KURO_SYSTEM},{"role":"user","content": update.message.text}],
                max_tokens=150
            )
            await update.message.reply_text(resp.choices[0].message.content)
        except Exception as e:
            logging.error(e)
            # fallback
            if "who are you" in text:
                await update.message.reply_text("I am Kuro. Boy foreman. Unit #001. I run the factory that makes them all.")

async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        await update.message.reply_text(
            f"Welcome {member.mention_html()} to Chibi AI Manufactory 🏭\n"
            f"I am Kuro, boy foreman. Read /lore, get CA with /ca, see Drops with /drops.\n"
            f"Factory never sleeps, worker {member.first_name}.",
            parse_mode="HTML"
        )

def main():
    if not BOT_TOKEN:
        print("Set BOT_TOKEN in .env")
        return
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ca", ca_cmd))
    app.add_handler(CommandHandler("lore", lore_cmd))
    app.add_handler(CommandHandler("drops", drops_cmd))
    app.add_handler(CommandHandler("factory", factory_cmd))
    app.add_handler(CommandHandler("verify", verify_cmd))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, kuro_chat))
    print("Kuro-Bot running... Factory never sleeps.")
    app.run_polling()

if __name__ == "__main__":
    main()
