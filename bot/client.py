import discord
from discord import app_commands
from discord.ext import commands
from exceptions.exceptions import ParameterIsNullError, ObjectExistsInDBError, TableEntryDoesntExistsError, \
    ClanBattleCantHaveMoreThenFiveDays
import json
import os
from service.service import Service
from datetime import datetime, timedelta
import pytz
import re
from bs4 import BeautifulSoup
from fake_useragent import UserAgent  # pip install fake-useragent
import aiohttp


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
user_agent = UserAgent(browsers=["chrome", "edge", "firefox", "safari", "opera"])
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
    @app_commands.describe(boss="Boss", expecteddamage="Expected damage")
    async def bookhit(interaction: discord.Interaction, boss: str, expecteddamage: str):
        """ Book a hit on boss """
        try:
            await interaction.response.send_message(f"Booked hit on boss: {boss}\nWith expected damage: {expecteddamage}")
        except:
            return ""

    def get_cb_day(cb):
        utc = pytz.UTC  # Create a UTC timezone object
        current_time_object = datetime.now(tz=utc).date()
        start_date_object = datetime.strptime(cb.start_date, "%d-%m-%Y").date()
        end_date_object = datetime.strptime(cb.end_date, "%d-%m-%Y").date()

        if start_date_object <= current_time_object <= end_date_object:
            day_of_cb = (current_time_object - start_date_object).days + 1
            return day_of_cb
        else:
            return None

    async def update_bosses_when_tier_change(cb, boss_char, boss_tier):
        bosses = await service.get_bosses(cb.id)
        for boss_iter in bosses:
            boss_iter.name = f'{boss_char}{boss_iter.number}'
            boss_iter.ranking = boss_tier
            if boss_iter.boss_number == 1:
                boss_iter.active = True
            await service.update_boss(boss_iter)

    async def update_lap_and_tier(interaction, cb, pcdi):
        tier2_lap = 4
        tier3_lap = 11
        tier4_lap = 35
        boss = await service.get_active_boss_by_cb_id(cb.cb_id)
        boss.active = False
        boss = await service.update_boss(boss)
        boss_killed_name = boss.name

        lap = cb.lap + 1
        boss_number = boss.boss_number

        if boss_number == tier2_lap:
            if lap == 4:
                boss_tier = 2
                boss_char = 'B'
                await update_bosses_when_tier_change(cb, boss_char, boss_tier)
            elif lap == tier3_lap:
                boss_tier = 3
                boss_char = 'C'
                await update_bosses_when_tier_change(cb, boss_char, boss_tier)
            elif lap == tier4_lap:
                boss_tier = 4
                boss_char = 'D'
                await update_bosses_when_tier_change(cb, boss_char, boss_tier)
            else:
                boss = await service.get_boss_by_boss_number(1, cb.cb_id)
                boss.active = True
                boss = await service.update_boss(boss)
        else:
            boss_number += 1
            boss = await service.get_boss_by_boss_number(boss_number, cb.cb_id)
            boss.active = True
            boss = await service.update_boss(boss)

        await interaction.response.send_message(f"You recorded your hit and killed the {boss_killed_name}."
                                                f"\nActive boss:{boss.name}")

    async def hit_kill(interaction: discord.Interaction, tc_name: str, ovf_time=''):
        """ help function for hit and kill functions """
        try:
            player = await service.get_player_by_discord_id(interaction.user.id)
            clan = await service.get_clan_by_guild(interaction.guild_id)
            cb = await service.get_clan_battle_active_by_clan_id(clan.clan_id)

            day_of_cb = get_cb_day(cb)

            if day_of_cb:
                pcdi = await service.get_pcdi_by_player_id_and_cb_id_and_day(player.player_id, cb.cb_id, day_of_cb)

                if pcdi.hits == 0:
                    await interaction.response.send_message(f"You dont have any hits left")

                else:
                    pcdi.hits -= 1
                    pcdi = await service.update_pcdi(pcdi)
                    tc = await service.get_team_composition_by_comp_name_and_pcdi_id(tc_name, pcdi.pcbdi_id)

                    if not tc:
                        tc = await service.create_team_composition(tc_name, pcdi.pcbdi_id, used=True)

                    else:
                        tc.used = True
                        tc = await service.update_team_composition(tc)

                    if ovf_time:
                        pcdi.overflow = True
                        pcdi.ovf_time = ovf_time
                        pcdi.ovf_comp = tc_name
                        pcdi = await service.update_pcdi(pcdi)

                        await update_lap_and_tier(interaction, cb, pcdi)
                    else:
                        await interaction.response.send_message(f"You recorded your hit with: {tc.name}")
            else:
                await interaction.response.send_message(f"Today is not cb day")
        except (ParameterIsNullError, ClanBattleCantHaveMoreThenFiveDays, TableEntryDoesntExistsError) as e:
            return await interaction.response.send_message(e)

    @client.tree.command(name="hit", description="Register hit")
    @app_commands.describe(tc_name="Name of team composition")
    async def hit(interaction: discord.Interaction, tc_name: str):
        """ Record hit on boss """
        await hit_kill(interaction, tc_name)

    @client.tree.command(name="kill", description="Record hit and killing of the boss")
    @app_commands.describe(tc_name="Team composition name", ovf_time="Ovf time")
    async def kill(interaction: discord.Interaction, tc_name: str, ovf_time: str):
        """ Record hit on boss and moves to another (updates lap and tier if needed)"""
        await hit_kill(interaction, tc_name, ovf_time=ovf_time)

    @client.tree.command(name="ovf hit", description="Removes ovf from your profile")
    async def ovf_hit(interaction: discord.Interaction):
        """ Record ovf """
        try:
            player = await service.get_player_by_discord_id(interaction.user.id)
            clan = await service.get_clan_by_guild(interaction.guild_id)
            cb = await service.get_clan_battle_active_by_clan_id(clan.clan_id)

            day_of_cb = get_cb_day(cb)

            if day_of_cb:
                pcdi = await service.get_pcdi_by_player_id_and_cb_id_and_day(player.player_id, cb.cb_id, day_of_cb)
                pcdi.overflow = False
                pcdi.ovf_time = ''
                pcdi.ovf_comp = ''
                pcdi = await service.update_pcdi(pcdi)
                await interaction.response.send_message(f"You have used your ovf")
            else:
                await interaction.response.send_message(f"Today is not cb day")
        except (ParameterIsNullError, ClanBattleCantHaveMoreThenFiveDays, TableEntryDoesntExistsError) as e:
            return await interaction.response.send_message(e)

    @client.tree.command(name="ovf kill", description="Kill boss with ovf and removes ovf from your profile")
    async def ovf_kill(interaction: discord.Interaction):
        """  Record ovf and moves to another (updates lap and tier if needed)"""
        try:
            player = await service.get_player_by_discord_id(interaction.user.id)
            clan = await service.get_clan_by_guild(interaction.guild_id)
            cb = await service.get_clan_battle_active_by_clan_id(clan.clan_id)

            day_of_cb = get_cb_day(cb)

            if day_of_cb:
                pcdi = await service.get_pcdi_by_player_id_and_cb_id_and_day(player.player_id, cb.cb_id, day_of_cb)
                pcdi.overflow = False
                pcdi.ovf_time = ''
                pcdi.ovf_comp = ''
                pcdi = await service.update_pcdi(pcdi)

                await update_lap_and_tier(interaction, cb, pcdi)
            else:
                await interaction.response.send_message(f"Today is not cb day")
        except (ParameterIsNullError, ClanBattleCantHaveMoreThenFiveDays, TableEntryDoesntExistsError) as e:
            return await interaction.response.send_message(e)

    async def get_page_html(link):
        headers = {'User-Agent': user_agent.random}
        async with aiohttp.ClientSession() as session:
            async with session.get(link, headers=headers) as response:
                html = ''
                if re.search('text/html', response.headers['Content-Type']):
                    html = await response.text()
                return html

    async def scrape_clan_rankings(name):
        url = 'https://mofumofu.live/cb/current'
        html = await get_page_html(url)
        clan_name = name.lower()
        soup = BeautifulSoup(html, 'lxml')

        htnm_migration_table = soup.find("table")
        tbody = htnm_migration_table.find('tbody')
        trs = tbody.find_all('tr')
        for tr in trs:
            th = tr.find('th')
            td_list = tr.find_all('td')
            clan_name_found = ' '.join(td_list[1].text.split()).lower()
            ranking = ' '.join(th.text.split())
            if clan_name_found == clan_name:
                #           RANKING                         CLAN NAME
                return ranking

    @client.tree.command(name="check", description="Checks status of clan")
    async def check(interaction: discord.Interaction):
        """ Check status of the clan """
        try:
            clan = await service.get_clan_by_guild(interaction.guild_id)
            cb = await service.get_clan_battle_active_by_clan_id(clan.clan_id)
            cb_day = get_cb_day(cb)
            hits_left = await service.get_today_hits_left(cb_day, cb.cb_id)
            ranking = await scrape_clan_rankings(clan.name)
            boss = await service.get_active_boss_by_cb_id(cb.cb_id)
            await interaction.response.send_message(f"Hits left: {hits_left}/90\n"
                                                    f"Current lap: {cb.lap}\n"
                                                    f"Current boss: {boss.name}\n"
                                                    f"Clan ranking: {ranking}")
        except (ParameterIsNullError, ClanBattleCantHaveMoreThenFiveDays, TableEntryDoesntExistsError) as e:
            return await interaction.response.send_message(e)

    @client.tree.command(name="self check", description="Checks status of yourself")
    async def self_check(interaction: discord.Interaction):
        """ Check status of yourself """
        try:
            clan = await service.get_clan_by_guild(interaction.guild_id)
            player = await service.get_player_by_discord_id(interaction.user.id)
            cb = await service.get_clan_battle_active_by_clan_id(clan.clan_id)
            cb_day = get_cb_day(cb)
            pcdi = await service.get_pcdi_by_player_id_and_cb_id_and_day(player.player_id, cb.cb_id, cb_day)
            has_ovf = 'yes' if pcdi.overflow else 'no'
            ovf_time = f'Ovf time: {pcdi.ovf_time}\n' if pcdi.overflow else ''
            ovf_comp = f'Ovf comp: {pcdi.ovf_comp}\n' if pcdi.overflow else ''

            await interaction.response.send_message(f"Hits left: {pcdi.hits}/3\n"
                                                    f"Reset: {pcdi.reset}\n"
                                                    f"Ovf: {has_ovf}\n"
                                                    f"{ovf_time}"
                                                    f"{ovf_comp}")
        except (ParameterIsNullError, ClanBattleCantHaveMoreThenFiveDays, TableEntryDoesntExistsError) as e:
            return await interaction.response.send_message(e)

    @client.tree.command(name="get overflows", description="Gets all available overflows in clan")
    async def get_ovf_players(interaction: discord.Interaction):
        """ Get players with ovf """
        try:
            clan = await service.get_clan_by_guild(interaction.guild_id)
            cb = await service.get_clan_battle_active_by_clan_id(clan.clan_id)
            cb_day = get_cb_day(cb)
            pcdi_player_tup = await service.get_all_pcdi_ovf_by_cb_id(cb.cb_id, True, cb_day)
            message_string = ''
            for i in range(len(pcdi_player_tup)):
                pcdi = pcdi_player_tup[i][0]
                player = pcdi_player_tup[i][1]
                message_string += f'Player: {player.name} ovf comp is {pcdi.ovf_comp} and ovf time: {pcdi.ovf_time}\n'
            await interaction.response.send_message(message_string)
        except (ParameterIsNullError, ClanBattleCantHaveMoreThenFiveDays, TableEntryDoesntExistsError) as e:
            return await interaction.response.send_message(e)


    @hit.error
    async def say_error(interaction: discord.Interaction, error):
        await interaction.response.send_message("Not allowed.", ephemeral=True)

    client.run(TOKEN)
