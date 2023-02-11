import discord
from discord import app_commands
from discord.ext import commands
import json
import os

from . import responses

if os.path.exists(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'config.json'))):
    with open("./config.json") as f:
        configData = json.load(f)
else:
    configTemplate = {"TOKEN": "", "Prefix": "!"}
    with open(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'config.json')), "w+") as f:
        json.dump(configTemplate, f)


TOKEN = configData["TOKEN"]
prefix = configData["Prefix"]


async def send_command(message, user_message, is_private):
    try:
        response = responses.handle_command(user_message)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)


client = commands.Bot(command_prefix="!", intents= discord.Intents.all())

def run_discord_bot():
    # client = discord.Client()
    # client = commands.Bot(command_prefix="!", intents= discord.Intents.all())


    @client.event
    async def on_ready():
        print(f'{client.user} is now running!')
        await client.change_presence(activity=discord.Game(name="!marin help"))
        try:
            # Don't do this. Should move elsewhere after testing is done
            synced = await client.tree.sync()
            print(f"Synced {len(synced)} command(s)")
        except Exception as e:
            print(e)


    @client.tree.command(name="hello")
    async def hello(interaction: discord.Integration):
        await interaction.response.send_message(f"Hi {interaction.user.mention}! The slash command worked :smile:", ephemeral=True)


    @client.tree.command(name="ping", description="Bot's ping in ms.")
    async def ping(interaction: discord.Interaction):
        bot_ping = round(client.latency * 1000)
        await interaction.response.send_message(f"Pong. {bot_ping} ms.")

    @client.tree.command(name="create")
    @app_commands.describe(create_clan = "Clan to create")
    async def create(interaction: discord.Interaction, create_clan: str):
        await interaction.response.send_message(f"{interaction.user.name} said '{create_clan}'")
        

    @client.tree.command(name="command_name", description="command_description")
    async def command_name(interaction: discord.Interaction):
        #code here
        await interaction.response.send_message(f"Pong. You got me working")



    @client.event
    async def on_message(message):
        # So bot doesn't take it's own output as input
        if message.author == client.user:
            return

        # For now, only work in #bot-testchannel
        if message.channel.name == 'bot-testchannel':

            # print(f"{message}")
            username = str(message.author)
            user_message = str(message.content)
            channel = str(message.channel)

            print(f"{username} said: '{user_message}' ({channel})")
            # print(f"{user_message[0:6]}")
            # print(f"{ user_message[7:]}")

            # If the user message contains '!marin' do something with bot
            if user_message[0:6] == '!marin':
                user_message = user_message[7:]  # [7:] Removes the '!marin '
                await send_command(message, user_message, is_private=False)


    client.run(TOKEN)