import discord
from discord.ext import commands
import asyncio
import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(command_prefix="!", intents=intents)

# For tracking sent items
sent_items = set()

# Load feeds
with open("feeds.json", "r") as f:
    feeds = json.load(f)


def search_vinted(feed):
    try:
        url = f"https://www.vinted.it/api/v2/catalog/items"
        params = {
            "search_text": feed["query"],
            "brand_id": feed.get("brand_id", ""),
            "price_to": feed.get("max_price", ""),
            "order": "newest_first"
        }

        res = requests.get(url, params=params, timeout=10)
        if res.status_code != 200:
            print(f"❌ Errore API: {feed['query']}")
            return []

        data = res.json()
        return data.get("items", [])

    except Exception as e:
        print("API ERROR:", e)
        return []


def format_message(item):
    title = item["title"]
    price = item["price"]["amount"]
    url = item["url"]
    photo = item["photos"][0]["url"] if item["photos"] else ""
    return f"💥 Nuovo trovato!\n📌 {title}\n💶 {price}€\n🔗 {url}\n🖼️ {photo}"


async def check_feeds():
    while True:
        for feed in feeds:
            channel_id = feed["channel_id"]
            channel = client.get_channel(channel_id)
            if not channel:
                print(f"⚠️ Canale non trovato: {channel_id}")
                continue

            items = search_vinted(feed)

            for item in items:
                item_id = item["id"]
                title = item["title"].lower()

                if feed["query"].lower() not in title:
                    continue

                if item_id in sent_items:
                    continue

                sent_items.add(item_id)

                msg = format_message(item)
                await channel.send(msg)

            await asyncio.sleep(2)

        await asyncio.sleep(30)


@client.event
async def on_ready():
    print(f"✅ Bot connesso come {client.user}")
    client.loop.create_task(check_feeds())


client.run(TOKEN)
