import tuincord
from tuincord import Status

from dotenv import dotenv_values

TOKEN = dotenv_values(".env")["TOKEN"]

# intents = discord.Intents.default()
# intents.members = True
# intents.message_content = True

bot = tuincord.Bot(status=Status.idle)#command_prefix='?', description=description, intents=intents)

@bot.event
async def ready():
    print(f'Logged in')
    print('------')

@bot.event
async def typing_start():
    print("Someone started typing")

@bot.command()
async def hello(ctx):
    await ctx.send("Hey")

bot.run(TOKEN)

# TODO: Rough command structure 

# @bot.command()
# @option("user", type=User, required=True)
# @option("reason", type=str, default=None)
# @require_role("Moderator")
# async def ban(ctx, user, reason):
