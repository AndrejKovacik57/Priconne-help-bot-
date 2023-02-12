import discord
from discord import app_commands
from discord.ext import commands
from exceptions.exceptions import ParameterIsNullError, ObjectExistsInDBError, TableEntryDoesntExistsError
import json
import os
from service.service import Service


# Open config.json file
# If doesn't exist, create with empty TOKEN field
if os.path.exists(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'config.json'))):
    with open("./config.json") as f:
        configData = json.load(f)
else:
    configTemplate = {"TOKEN": "", "Prefix": "!"}
    with open(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'config.json')), "w+") as f:
        json.dump(configTemplate, f)


# dbfile = f"{os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'config.json'))}"



TOKEN = configData["TOKEN"]
prefix = configData["Prefix"]
service = Service("priconne_database")
client = commands.Bot(command_prefix="!", intents=discord.Intents.all())

def run_discord_bot():
    @client.event
    async def on_ready():
        print(f'{client.user} is now running!')
        await client.change_presence(activity=discord.Game(name="/help"))
        # try:
        #     # Don't do this. Should move elsewhere after testing is done
        #     synced = await client.tree.sync()
        #     print(f"Synced {len(synced)} command(s)")
        # except Exception as e:
        #     print(e)


    ### TESTING / MISC COMMANDS ###

    @client.tree.command(name="hello")
    async def hello(interaction: discord.Interaction):
        await interaction.response.send_message(f"Hi fellow cosplayer {interaction.user.mention} with id: {interaction.user.id}! I'm Marin", ephemeral=False)


    ### ADMIN COMMANDS ###


    ### LEAD ONLY Commands ###


    # Create a clan
    # WIP - Need to connect to service for proper functionality
    @client.tree.command(name="createclan", description="Create clan")
    @app_commands.describe(clan = "Clan to create")
    async def createclan(interaction: discord.Interaction, clan: str):
        try:
            service.create_clan(clan)
            await interaction.response.send_message(f"{interaction.user.name} said to create the clan: '{clan}'")
        except ObjectExistsInDBError as e:
            await interaction.response.send_message(f"Clan: {clan} already exists!")
            # print(f"Caught error: {e}")

    
    # Add player to an existing clan
    # WIP - Need to connect to service for proper functionality
    # WIP - Need to make it so player is a DROPDOWN LIST / autocomplete for EXISTING CLANS
    # WIP - Make it so clan is a DROPDOWN LIST / autocomplete for EXISTING CLANS
    @client.tree.command(name="addplayer", description="Add a player to a clan")
    @app_commands.describe(player = "Player to add", clan="Clan to add player to")
    async def addplayer(interaction: discord.Interaction, player: str, clan: str):
        try:
            await interaction.response.send_message(f"Adding {player} to clan: {clan}.")
        except ObjectExistsInDBError as e:
            await interaction.response.send_message(f"Clan: {clan} already exists!")

    
    # Start clan battle
    # WIP - Need to connect to service for proper functionality
    # WIP - Need date conversion
    @client.tree.command(name="startclanbattle", description="Start clan battle on given date")
    @app_commands.describe(date = "Start date of CB")
    async def startclanbattle(interaction: discord.Interaction, date: str):
        try:
            # service.create_clan_battle() Re-do parameters
            await interaction.response.send_message(f"Starting clan battle on {date}")
        except:
            return ""


    # Check info about player
    # WIP - Need to connect to service for proper functionality
    @client.tree.command(name="playercheck", description="Hits left, bosses booked, reset used?")
    async def playercheck(interaction: discord.Interaction):
        try:
            
            await interaction.response.send_message(f"""
__**Info for player:**__ \_\_\_
Hits Remaining: \_\_
Bosses Booked: \_\_
Reset available? (YES/NO)""")
        except:
            return ""
    

    ### GENERAL COMMANDS ###


    # Create player
    # WIP - Need to connect to service for proper functionality
    @client.tree.command(name="createplayer", description="Create player")
    @app_commands.describe(player = "Player to create")
    async def createplayer(interaction: discord.Interaction, player: str):
        try:
            service.create_player(player, interaction.user.id)
            await interaction.response.send_message(f"Created {player}.")
        except ObjectExistsInDBError as e:
            await interaction.response.send_message(f"Player: {player} already exists!")

    
    # Check info about clan
    # WIP - Need to connect to service for proper functionality
    @client.tree.command(name="clancheck", description="Clan position, lap, tier, current boss (booked hits???), hits remaining")
    async def clancheck(interaction: discord.Interaction):
        try:
            service.get_clan_battles_in_clan("Automatically fetched clan_id / clan_name")
            await interaction.response.send_message(f"""
__**Info for clan: \_\_\_**__
Position: \_\_\_
Lap: \_\_\_
Tier: (A/B/C/D)
Boss: \_\_\_
Hits Remaining: \_\_\_""")
        except:
            return ""
    

    # Check info about self
    # WIP - Need to connect to service for proper functionality
    @client.tree.command(name="selfcheck", description="Hits left, reset used?")
    async def selfcheck(interaction: discord.Interaction):
        try:
            service.get_player_by_id(interaction.user.id)
            await interaction.response.send_message(f"""
__**Info for player:**__ \_\_\_
Hits Remaining: \_\_
Reset available? (YES/NO)""")
        except None as e:
            await interaction.response.send_message("You're not registered! Please register using **/createplayer**")
    

    # Check info boss availability
    # WIP - Need to connect to service for proper functionality
    @client.tree.command(name="bossavailability", description="Displays hit bookings on all bosses")
    async def bossavailability(interaction: discord.Interaction):
        try:
            await interaction.response.send_message(f"""
__**Overflow Count: \_\_\_**__
Boss 1: \_\_ hits booked
Boss 2: \_\_ hits booked
Boss 3: \_\_ hits booked
Boss 4: \_\_ hits booked
Boss 5: \_\_ hits booked""")
        except:
            return ""


    # Check info regarding overflows
    # WIP - Need to connect to service for proper functionality
    @client.tree.command(name="ovf", description="Overflows currently in clan")
    async def ovf(interaction: discord.Interaction):
        try:
            await interaction.response.send_message(f"""
__**Overflow Count: \_\_\_**__
Player: \_\_\_\_
Boss: \_\_\_
Time: \_\_:\_\_
Estimated Damage: \_\_\_\_""")
        except:
            return ""
    

    # Book hit on boss
    # WIP - Need to connect to service for proper functionality
    @client.tree.command(name="bookhit", description="Book a hit on this boss")
    @app_commands.describe(boss = "Boss", expecteddamage = "Expected damage")
    async def bookhit(interaction: discord.Interaction, boss: str, expecteddamage: str):
        try:
            await interaction.response.send_message(f"""
Booked hit on boss: {boss}
With expected damage: {expecteddamage}""")
        except:
            return ""
        
    
    # Hit boss
    # WIP - Need to connect to service for proper functionality
    @client.tree.command(name="hit", description="Register hit")
    @app_commands.describe(boss = "Boss", ovftime = "Overflow time, if any")
    async def hit(interaction: discord.Interaction, boss: str, ovftime: str):
        try:
            await interaction.response.send_message(f"""
Logged hit onto boss: {boss}
You have {ovftime} overflow time
You have \_\_\_ hits remaining""")
        except:
            return ""


    client.run(TOKEN)