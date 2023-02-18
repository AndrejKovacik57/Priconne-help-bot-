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


TOKEN = configData["TOKEN"]
prefix = configData["Prefix"]
service = Service("priconne_database")
client = commands.Bot(command_prefix="!", intents=discord.Intents.all())


# def is_owner(interaction: discord.Interaction):
#     if interaction.user.id == interaction.guild.role


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
        await interaction.response.send_message(f"Hi fellow cosplayer {interaction.user.mention}! Your Discord ID is {interaction.user.id}. I'm Marin", ephemeral=False)

    
    @client.tree.command(name="help")
    async def help(interaction: discord.Interaction):
        embed = discord.Embed(title="Marin Bot Commands", color=0x3083e3,
            description="""
                Hi fellow **Cosplayer**! I'm a CB bot, designed to make your CB life easier!

                **help**: Shows list of commands.
                **invite**: Bot invite link *(WIP)*.
            """)
        # embed.set_author(name="MangaUpdates", icon_url=self.bot.user.avatar.url)
        # embed.set_author(name="Marin")
        embed.add_field(name="__Create__", 
            value="""
                **create clan `clan`**: Create clan called `clan`.
                **create player `player`**: Create player called `player`.
            """, inline=False)
        embed.add_field(name="__Clan__",
            value="""
                **clan check**: Check info regarding own clan.
                **clan list**:  Get list of clans.
                **clan updatename `clan` `newname`**: Change name of `clan` to `newname`.
                **clan playerlist**: Check list of players in clan.
                **clan addplayer `player` `clan`**: Add `player` to `clan`.
                **clan removeplayer `player` `clan`**: Remove `player` from `clan`.
            """, inline=False)
        embed.add_field(name="__Player__",
            value="""
                **player delete `player`**: Delete `player`.
                **player selfcheck**: Check info regarding self.
                **player check `player`**: Check info regarding `player`.
            """, inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)


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


    @hit.error
    async def say_error(interaction: discord.Interaction, error):
        await interaction.response.send_message("Not allowed.", ephemeral=True)


    client.run(TOKEN)