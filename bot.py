import tuincord
from tuincord import Status, OptionType

from dotenv import dotenv_values
from flask import Flask
from pages import pages
import threading
import random
import string
import json
import re
import os

TOKEN = dotenv_values(".env")["TOKEN"]

app = Flask(__name__)
app.register_blueprint(pages)

# intents = discord.Intents.default()
# intents.members = True
# intents.message_content = True

# command_prefix='?', description=description, intents=intents)
bot = tuincord.Bot(status=Status.idle)

MAP_FILENAME = "map.json"


@bot.event
async def on_ready():
    if not os.path.isfile(MAP_FILENAME):
        with open(MAP_FILENAME, "w") as f:
            f.write("[]")

    print(f'Logged in')
    print('------')


@bot.command(description="Shorten a URL")
@bot.option("url", "The URL to be shortened", OptionType.STRING, required=True)
async def shorten(interaction, data):
    URL = data["value"]

    match = re.search(
        r"^[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&\/\/=]*)",
        URL
    )

    if match:
        with open(MAP_FILENAME, "r") as f:
            shortened_urls = json.load(f)

        for item in shortened_urls:
            if item["url"] == URL:
                await interaction.respond(f"URL already exists with key: {item["shortcode"]}")
                return

        key = ''.join(random.choices(
            string.ascii_letters + string.digits, k=5))
        shortened_urls.append(
            {
                "url": URL,
                "shortcode": key,
                "owner": interaction.user_id
            }
        )
        with open(MAP_FILENAME, "w") as f:
            json.dump(shortened_urls, f)
        await interaction.respond(f"Shortened URL key: {key}")
    else:
        if URL.startswith(('http://', 'https://')):
            await interaction.respond("You can only submit URLs without protocol")
            return
        await interaction.respond("This is not an URL")

def run_flask():
    app.run(port=5000)

flask_thread = threading.Thread(target=app.run, daemon=True)
flask_thread.start()

bot.run(TOKEN)

# TODO:  @require_role("Moderator")
