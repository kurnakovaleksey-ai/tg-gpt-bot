import os, asyncio, aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

if not BOT_TOKEN or not OPENAI_API_KEY:
    raise SystemExit("Set BOT_TOKEN and OPENAI_API_KEY")

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

async def ask_openai(text: str) -> str:
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": OPENAI_MODEL,
        "messages": [
            {"role": "system", "content": "Отвечай кратко и по делу."},
            {"role": "user", "content": text}
        ],
        "temperature": 0.3
    }
    async with aiohttp.ClientSession() as s:
        async with s.post(url, headers=headers, json=payload, timeout=120) as r:
            data = await r.json()
            if r.status != 200:
                return f"OpenAI error {r.status}: {data}"
            return data["choices"][0]["message"]["content"].strip()

@dp.message(CommandStart())
async def start(m: types.Message):
    await m.answer("Готов. Напишите вопрос.")

@dp.message()
async def handle(m: types.Message):
    try:
        text = m.text or ""
        reply = await ask_openai(text)
        for chunk in (reply[i:i+3500] for i in range(0, len(reply), 3500)):
            await m.answer(chunk)
    except Exception as e:
        await m.answer(f"Ошибка: {e}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
