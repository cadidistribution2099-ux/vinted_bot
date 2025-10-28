import asyncio

async def check_feeds():
    while True:  # Loop continuo per controllare nuovi item
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

            await asyncio.sleep(1)

        await asyncio.sleep(30)  # tempo tra un controllo e l’altro

@client.event
async def on_ready():
    print(f"✅ Bot connesso come {client.user}")
    client.loop.create_task(check_feeds())

