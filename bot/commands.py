import sys
sys.path.append("..")
import discord
from discord import app_commands
from discord.ext import commands
# from main import client

import random
from service.service import Service

### DEPRECATED. CURRENTLY ALL COMMANDS EXIST IN client.py ###

# def marin_commands():

    # @client.event
    # async def on_ready():
    #     print(f'{client.user} is now running!')
    #     await client.change_presence(activity=discord.Game(name="!marin help"))
    #     try:
    #         # Don't do this. Should move elsewhere after testing is done
    #         synced = await client.tree.sync()
    #         print(f"Synced {len(synced)} command(s)")
    #     except Exception as e:
    #         print(e)

    # @client.tree.command(name="hello")
    # async def hello(interaction: discord.Integration):
    #     await interaction.response.send_message(f"Hi fellow cosplager {interaction.user.mention}! I'm Marin", ephemeral=False)


    # @client.tree.command(name="create", description="Create clan or player")
    # @app_commands.describe(clan = "Clan to create")
    # async def create(interaction: discord.Interaction, clan: str):
    #     await interaction.response.send_message(f"{interaction.user.name} said '{clan}'")
    # @app_commands.describe(player = "Player to create")
    # async def create(interaction: discord.Interaction, player: str):
    #     await interaction.response.send_message(f"{interaction.user.name} said '{player}'")
        

    # @client.tree.command(name="command_name", description="command_description")
    # async def command_name(interaction: discord.Interaction):
    #     #code here
    #     await interaction.response.send_message(f"Pong. You got me working")
    