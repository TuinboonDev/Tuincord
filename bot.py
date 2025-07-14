import tuincord
from tuincord import Status, OptionType

from dotenv import dotenv_values
import re

TOKEN = dotenv_values(".env")["TOKEN"]

# intents = discord.Intents.default()
# intents.members = True
# intents.message_content = True

# command_prefix='?', description=description, intents=intents)
bot = tuincord.Bot(status=Status.idle)


@bot.event
async def on_ready():
    print(f'Logged in')
    print('------')


@bot.command(description="Shorten a URL")
@bot.option("url", "The URL to be shortened", OptionType.STRING, required=True)
async def shorten(interaction, url):
    match = re.search(
        r"[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&\/\/=]*)",
        url["value"]
    )

    if match:
        await interaction.respond(url["value"])
    else:
        await interaction.respond("This is not an URL")

bot.run(TOKEN)

# TODO:  @require_role("Moderator")
