import tuincord
from tuincord import Status, OptionType, ChannelsType

from dotenv import dotenv_values

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

@bot.command(description="Upload a file to the CDN")
@bot.option("file", "The file to be uploaded", OptionType.ATTACHMENT, required=True)
async def upload(ctx, file):
	pass

bot.run(TOKEN)

# TODO:  @require_role("Moderator")
