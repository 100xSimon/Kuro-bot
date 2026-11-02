# Kuro-Bot - Chibi AI Manufactory Foreman Mod

Boy black cat foreman that mods your Telegram. Tired, cool, cute.

## Features
- Auto-welcome new workers
- Spam/raid filter (links, flood, arabic scam)
- Lore answers: /lore, /drops, /ca, /factory
- Kuro AI chat - answers as boy foreman (uses OpenAI if key set, else rule-based)
- Holder verify: /verify <wallet> checks $CHIBI balance
- Auto-announce new Factory Drops (call /announce_drop)
- Delete + warn + ban

## Setup 1: Create Bot
1. Telegram -> @BotFather -> /newbot -> name: Kuro Factory Bot -> username: KuroFactoryBot
2. Copy token
3. Add bot to your Telegram group as Admin (make admin, enable delete messages, ban users)

## Setup 2: Deploy

### Option A - Railway (easiest, free)
1. Push this folder to GitHub
2. railway.app -> New Project -> Deploy from GitHub
3. Add Variables: BOT_TOKEN, OPENAI_API_KEY (optional), CA, RPC_URL
4. Deploy. Bot runs 24/7.

### Option B - VPS
```bash
pip install -r requirements.txt
cp .env.example .env # fill tokens
python kuro_bot.py
```

## Commands
/start - Factory open
/ca - Show CA
/lore - Kuro origin
/drops - Latest drops list
/factory - Roadmap
/verify <wallet> - Check holder tier
/announce_drop - Admin only, posts new drop template

Kuro persona: Boy, 16-18, tired foreman, says "Factory never sleeps, worker." 
CA: CUBb8PCxbhxmHKGWav4qoVak5b4uvC1d2wav67fMpump
