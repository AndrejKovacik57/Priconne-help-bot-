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

# class MyGroup(app_commands.Group):
#     ...

# playerGroup = MyGroup(name="player", description="Player commands")

TOKEN = configData["TOKEN"]
prefix = configData["Prefix"]
service = Service("priconne_database")
client = commands.Bot(command_prefix="!", intents=discord.Intents.all())

def run_discord_bot():
    @client.event
    async def on_ready():
        print(f'{client.user} is now running!')
        await client.change_presence(activity=discord.Game(name="/help"))
        await client.load_extension("bot.clan-commands")
        await client.load_extension("bot.create-commands")
        await client.load_extension("bot.player-commands")
        # try:
        #     # Don't do this. Should move elsewhere after testing is done
        #     synced = await client.tree.sync()
        #     print(f"Synced {len(synced)} command(s)")
        # except Exception as e:
        #     print(e)


    ### TESTING / MISC COMMANDS ###

    @client.tree.command(name="hello")
    async def hello(interaction: discord.Interaction):
        await interaction.response.send_message(f"Hi fellow cosplayer {interaction.user.mention}! I'm Marin", ephemeral=False)

    
    @client.tree.command(name="help")
    async def help(interaction: discord.Interaction):
        await interaction.response.send_message(f"Hi fellow cosplayer {interaction.user.mention}! I'm Marin! Below are the list of commands\n**__Create__**\n**create clan `clan`**: Create clan called `clan`\n**create player `player`**: Create player called `player`\n\n**__Clan__**\n**clan check**: Check info regarding own clan\n**clan list**: Get list of clans\n**clan updatename `clan` `newname`**: Change name of `clan` to `newname`\n**clan playerlist**: Check list of players in clan\n**clan addplayer `player` `clan`**: Add `player` to `clan`\n**clan removeplayer `player` `clan`**: Remove `player` from `clan`\n\n**__Player__**\n**player delete `player`**: Delete `player`\n**player selfcheck**: Check info regarding self\n**player check `player`**: Check info regarding `player`", ephemeral=True)


    ### ADMIN COMMANDS ###


    ### LEAD ONLY Commands ###

    
    @client.tree.command(name="startclanbattle", description="Start clan battle on given date")
    @app_commands.describe(date = "Start date of CB")
    async def startclanbattle(interaction: discord.Interaction, date: str):
        """ Start clan battle on given date """
        try:
            # service.create_clan_battle() Re-do parameters
            await interaction.response.send_message(f"Starting clan battle on {date}")
        except:
            return ""
    

    ### GENERAL COMMANDS ###
    

    @client.tree.command(name="bossavailability", description="Displays hit bookings on all bosses")
    async def bossavailability(interaction: discord.Interaction):
        """ Check info regarding boss availability """
        try:
            await interaction.response.send_message(f"__**Overflow Count: \_\_\_**__\nBoss 1: \_\_ hits booked\nBoss 2: \_\_ hits booked\nBoss 3: \_\_ hits booked\nBoss 4: \_\_ hits booked\nBoss 5: \_\_ hits booked")
        except:
            return ""


    @client.tree.command(name="ovf", description="Overflows currently in clan")
    async def ovf(interaction: discord.Interaction):
        """ Check info regarding overflows existing in clan """
        try:
            await interaction.response.send_message(f"__**Overflow Count: \_\_\_**__\nPlayer: \_\_\_\_\nBoss: \_\_\_\nTime: \_\_:\_\_\nEstimated Damage: \_\_\_\_")
        except:
            return ""
    

    @client.tree.command(name="bookhit", description="Book a hit on this boss")
    @app_commands.describe(boss = "Boss", expecteddamage = "Expected damage")
    async def bookhit(interaction: discord.Interaction, boss: str, expecteddamage: str):
        """ Book a hit on boss """
        try:
            await interaction.response.send_message(f"Booked hit on boss: {boss}\nWith expected damage: {expecteddamage}")
        except:
            return ""
        
    
    @client.tree.command(name="hit", description="Register hit")
    @app_commands.describe(boss = "Boss", ovftime = "Overflow time, if any")
    async def hit(interaction: discord.Interaction, boss: str, ovftime: str):
        """ Record hit on boss """
        try:
            await interaction.response.send_message(f"Logged hit onto boss: {boss}\nYou have {ovftime} overflow time\nYou have \_\_\_ hits remaining")
        except:
            return ""


    client.run(TOKEN)