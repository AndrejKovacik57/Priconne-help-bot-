import bot.client
import discord
from discord import app_commands
from discord.ext import commands
import bot.commands
import json
import os

# if os.path.exists(os.path.abspath(os.path.join(os.path.dirname( __file__ ), 'config.json'))):
#     with open("./config.json") as f:
#         configData = json.load(f)
# else:
#     configTemplate = {"TOKEN": "", "Prefix": "!"}
#     with open(os.path.abspath(os.path.join(os.path.dirname( __file__ ), 'config.json')), "w+") as f:
#         json.dump(configTemplate, f)


# TOKEN = configData["TOKEN"]
# prefix = configData["Prefix"]

# bot = commands.Bot(command_prefix="!", intents= discord.Intents.all())

# @bot.event
# async def on_ready():
#     print(f'{bot.user} is now running!')
#     await bot.change_presence(activity=discord.Game(name="/help"))
#     bot.commands.marin_commands()
    # try:
    #     # Don't do this. Should move elsewhere after testing is done
    #     synced = await client.tree.sync()
    #     print(f"Synced {len(synced)} command(s)")
    # except Exception as e:
    #     print(e)

# try:
#     bot.run(TOKEN)
# except Exception as err:
#     print(f"Error: {err}")


if __name__ == '__main__':
    #run the bot
    bot.client.run_discord_bot()