import discord
from discord.ext import tasks
import requests
import json
import os
from dotenv import load_dotenv
import time

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
client = discord.Client(intents=intents)

# Carica la configurazione dei feed
with open("feeds.json", "r", encoding="utf-8") as f:
    feeds = json.load(f)

# Cache ID per non inviare due volte lo stesso annuncio
sent_items = set()

VINTED_URL = "https://www.vinted.it/api/v2/catalog/items"


def search_vinted(feed):
    params = {
        "search_text": feed["query"],
        "price_to": feed["max_price"],
        "status_ids": ",".join(map(str, feed["conditions"])),
        "catalog_ids": ",".join(map(str, feed["categories"])),
        "per_page": 10,
    }

    response = requests.get(VINTED_URL, params=params)
    if response.status_code != 200:
        print(f"Errore API: {feed['name']}")
        return []

    data = response.json()
    return data.get("items", [])


def format_message(item):
    title = item["title"]
    price = item["price"]["amount"]
    url = f"https://www.vinted.it/items/{item['id']}"
    return f"👜 Nuovo articolo trovato!\n**{title}** - {price}€\n{url}"


@tasks.loop(seconds=45)  # ⏱ ogni 45 secondi
async def check_feeds():
    for feed in feeds:
        channel_id = feed["channel_id"]
        channel = client.get_channel(channel_id)

        items = search_vinted(feed)

        for item in items:
            item_id = item["id"]
            title = item["title"].lower()

            # Filtro aggiuntivo → keyword nel titolo
            if feed["query"].lower() not in title:
                continue

            if item_id in sent_items:
                continue

            sent_items.add(item_id)
            msg = format_message(item)
            await channel.send(msg)

        time.sleep(1)


@client.event
async def on_ready():
    print(f"✅ Bot connesso come {client.user}")
    check_feeds.start()


client.run(TOKEN)
