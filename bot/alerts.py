"""Alert sending functions."""

import httpx
import asyncio
from typing import Optional


async def send_discord_alert(webhook_url: Optional[str], message: str):
    if not webhook_url:
        return
    async with httpx.AsyncClient() as client:
        try:
            await client.post(webhook_url, json={"content": message}, timeout=10)
        except Exception as e:
            print(f"Discord alert failed: {e}")


async def send_telegram_alert(bot_token: Optional[str], chat_id: Optional[str], message: str):
    if not bot_token or not chat_id:
        return
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    async with httpx.AsyncClient() as client:
        try:
            await client.post(url, data={"chat_id": chat_id, "text": message})
        except Exception as e:
            print(f"Telegram alert failed: {e}")


def send_discord_sync(webhook_url: Optional[str], message: str):
    asyncio.run(send_discord_alert(webhook_url, message))


def send_telegram_sync(bot_token: Optional[str], chat_id: Optional[str], message: str):
    asyncio.run(send_telegram_alert(bot_token, chat_id, message))
