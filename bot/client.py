import discord
from discord import app_commands
from discord.ext import commands
from exceptions.exceptions import ParameterIsNullError, ObjectExistsInDBError, TableEntryDoesntExistsError, \
    ClanBattleCantHaveMoreThenFiveDaysError, DesiredBossIsDeadError, PlayerNotInClanError, ObjectDoesntExistsInDBError
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
from typing import List


def run_discord_bot():
    @client.event
    async def on_ready():
        print(f'{client.user} is now running!')
        await client.change_presence(activity=discord.Game(name="/help"))
        await client.load_extension("bot.clan-commands")
        await client.load_extension("bot.create-commands")
        await client.load_extension("bot.player-commands")
        await client.load_extension("bot.server-commands")
        # try:
        #     # Don't do this. Should move elsewhere after testing is done
        #     synced = await client.tree.sync()
        #     print(f"Synced {len(synced)} command(s)")
        # except Exception as e:
        #     print(e)

    ### HELPER FUNCTIONS ###

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
        bosses = await service.get_bosses(cb.cb_id)
        for boss_iter in bosses:
            boss_iter.name = f'{boss_char}{boss_iter.boss_number}'
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
        boss_number = boss.boss_number

        if boss_number == 5:
            cb.lap = cb.lap + 1
            cb = await service.update_clan_batte(cb)
            if cb.lap == tier2_lap:
                boss_tier = 2
                boss_char = 'B'
                await update_bosses_when_tier_change(cb, boss_char, boss_tier)
            elif cb.lap == tier3_lap:
                boss_tier = 3
                boss_char = 'C'
                await update_bosses_when_tier_change(cb, boss_char, boss_tier)
            elif cb.lap == tier4_lap:
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

        return await interaction.response.send_message(
            f"You recorded your hit with ovf time {pcdi.ovf_time} and killed the {boss_killed_name}."
            f"\nActive boss:{boss.name}")

    async def hit_kill(interaction: discord.Interaction, player_discord_id: int, tc_name: str, ovf_time=''):
        """ help function for hit and kill functions """
        try:
            players = await service.get_player_by_discord_id(player_discord_id)
            clan = await service.get_clan_by_guild(interaction.guild_id)
            cb = await service.get_clan_battle_active_by_clan_id(clan.clan_id)
            day_of_cb = get_cb_day(cb)
            if len(players) == 1:
                player = players[0]
                if day_of_cb:
                    pcdi = await service.get_pcdi_by_player_id_and_cb_id_and_day(player.player_id, cb.cb_id, day_of_cb)
                    if pcdi.overflow:
                        return await interaction.response.send_message(f"You have oveflow active, you cant use hit "
                                                                       f"command")
                    if pcdi.hits == 0:
                        return await interaction.response.send_message(f"You dont have any hits left")

                    else:
                        tc = await service.get_team_composition_by_comp_name_and_pcdi_id(tc_name, pcdi.pcbdi_id)
                        if not tc:
                            tc = await service.create_team_composition(tc_name, pcdi.pcbdi_id)

                        if tc.used and not ovf_time:
                            return await interaction.response.send_message(f"You already used team composition: "
                                                                           f"{tc.name}")

                        pcdi.hits -= 1
                        tc.used = True
                        tc = await service.update_team_composition(tc)

                        if ovf_time:
                            pcdi.overflow = True
                            pcdi.ovf_time = ovf_time
                            pcdi.ovf_comp = tc_name

                            pcdi = await service.update_pcdi(pcdi)

                            return await update_lap_and_tier(interaction, cb, pcdi)
                        else:
                            await service.update_pcdi(pcdi)
                            return await interaction.response.send_message(f"You recorded your hit with: {tc.name}")
            else:
                await interaction.response.send_message(f"Today is not cb day")
        except (ParameterIsNullError, ClanBattleCantHaveMoreThenFiveDaysError, TableEntryDoesntExistsError) as e:
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
                return ranking
        return 'Clan is not top 100'

    def boss_char_by_lap(lap):
        tier2_lap = 4
        tier3_lap = 11
        tier4_lap = 35
        if tier2_lap <= lap < tier3_lap:
            boss_char = 'B'
        elif tier3_lap <= lap < tier4_lap:
            boss_char = 'C'
        elif lap >= tier4_lap:
            boss_char = 'D'
        else:
            boss_char = 'A'
        return boss_char

    async def book_boss_help(interaction, ovf_time, lap, boss_num, comp_name):
        try:
            lap_int = int(lap)
            boss_num_int = int(boss_num)
            players = await service.get_player_by_discord_id(interaction.user.id)
            clan = await service.get_clan_by_guild(interaction.guild_id)
            cb = await service.get_clan_battle_active_by_clan_id(clan.clan_id)
            boss = await service.get_boss_by_boss_number(boss_num_int, cb.cb_id)
            boss_char = boss_char_by_lap(lap_int)
            boss_name = f'{boss_char}{boss.name[1:]}'
            if len(players) == 1:
                player = players[0]
                if ovf_time:
                    booking = await service.create_boss_booking(lap_int, cb.lap, True, comp_name, boss.boss_id,
                                                                player.player_id, cb.cb_id, ovf_time=ovf_time)
                    return await interaction.response.send_message(
                        f'You booked comp: {booking.comp_name} with ovf time: {ovf_time}, for boss: {boss_name}'
                        f' in lap: {lap}'
                    )
                else:
                    booking = await service.create_boss_booking(lap_int, cb.lap, False, comp_name, boss.boss_id,
                                                                player.player_id, cb.cb_id)
                    return await interaction.response.send_message(
                        f'You booked comp: {booking.comp_name}, for boss: {boss_name} in lap: {lap}'
                    )

        except (ObjectDoesntExistsInDBError, ParameterIsNullError, ClanBattleCantHaveMoreThenFiveDaysError,
                ValueError) as e:
            await interaction.response.send_message(e)

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
        embed.add_field(name="__Server__",
            value="""
                **server setup**: Register server in bot. **MUST** run or else bot will not operate.
                **server addadminrole `role_id`**: Add role *(role ID)* as **admin role** in bot.
                **server addleadrole `role_id`**: Add role *(role ID)* as **lead role** in bot.
            """, inline=False)
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


    ### LEAD ONLY Commands ###


    @client.tree.command(name="startclanbattle", description="Start clan battle on given date")
    @app_commands.describe(date = "Start date of CB")
    async def startclanbattle(interaction: discord.Interaction, date: str):
        """ Start clan battle on given date """
        try:
            guild = await service.get_guild_by_id(interaction.guild.id)
            if not guild:
                raise TableEntryDoesntExistsError("Server doesn't exist! Please run **/server setup**")

            await interaction.response.send_message(f"Starting clan battle on {date}")
        except:
            return ""


    ### GENERAL COMMANDS ###


    # @client.tree.command(name="bossavailability", description="Displays hit bookings on all bosses")
    # async def bossavailability(interaction: discord.Interaction):
    #     """ Check info regarding boss availability """
    #     try:
    #         guild = await service.get_guild_by_id(interaction.guild.id)
    #         if not guild:
    #             raise TableEntryDoesntExistsError("Server doesn't exist! Please run **/server setup**")
    #         await interaction.response.send_message(
    #             f"__**Overflow Count: \_\_\_**__"
    #             f"\nBoss 1: \_\_ hits booked"
    #             f"\nBoss 2: \_\_ hits booked"
    #             f"\nBoss 3: \_\_ hits booked"
    #             f"\nBoss 4: \_\_ hits booked"
    #             f"\nBoss 5: \_\_ hits booked")
    #     except:
    #         return ""


    @client.tree.command(name="ovf", description="Overflows currently in clan")
    async def ovf(interaction: discord.Interaction):
        """ Check info regarding overflows existing in clan """
        try:
            guild = await service.get_guild_by_id(interaction.guild.id)
            if not guild:
                raise TableEntryDoesntExistsError("Server doesn't exist! Please run **/server setup**")
            await interaction.response.send_message(
                f"__**Overflow Count:**__ \_\_\_"
                f"\nPlayer: \_\_\_\_"
                f"\nBoss: \_\_\_"
                f"\nTime: \_\_:\_\_"
                f"\nEstimated Damage: \_\_\_\_")
        except:
            return ""

    # @client.tree.command(name="bookhit", description="Book a hit on this boss")
    # @app_commands.describe(boss="Boss", expecteddamage="Expected damage")
    # async def bookhit(interaction: discord.Interaction, boss: str, expected_damage: str):
    #     """ Book a hit on boss """
    #     try:
    #         guild = await service.get_guild_by_id(interaction.guild.id)
    #         if not guild:
    #             raise TableEntryDoesntExistsError("Server doesn't exist! Please run **/server setup**")
    #         await interaction.response.send_message(
    #             f"Booked hit on boss: {boss}"
    #             f"\nWith expected damage: {expected_damage}")
    #     except TableEntryDoesntExistsError as e:
    #         await interaction.response.send_message(e)

    @client.tree.command(name="hit", description="Register hit")
    @app_commands.describe(tc_name="Name of team composition")
    async def hit(interaction: discord.Interaction, tc_name: str):
        """ Record hit on boss """
        try:
            await service.get_guild_by_id(interaction.guild.id)
            await hit_kill(interaction, interaction.user.id, tc_name)
        except TableEntryDoesntExistsError as e:
            await interaction.response.send_message(e)

    @client.tree.command(name="pilothit", description="Pilot and register hit")
    @app_commands.describe(tc_name="Name of team composition", piloted_player_name='Name of the player that was piloted')
    async def pilot_hit(interaction: discord.Interaction, tc_name: str, piloted_player_name: str):
        """ Record hit on boss """
        try:
            guild = await service.get_guild_by_id(interaction.guild.id)
            if not guild:
                raise TableEntryDoesntExistsError("Server doesn't exist! Please run **/server setup**")

            player = await service.get_player_by_name(piloted_player_name)
            clan_player_tuple = await service.get_clan_player(player.player_id)
            clan = await service.get_clan_battle_by_id(guild.guild_id)
            if not clan_player_tuple:
                raise TableEntryDoesntExistsError(f'Player {piloted_player_name} is not in clan.')
            clan_player_clan = clan_player_tuple[1]
            if clan_player_clan.clan_id != clan.clan_id:
                raise TableEntryDoesntExistsError(f'Player {piloted_player_name} is not in clan.')

            await hit_kill(interaction, player.discord_id, tc_name)
        except (TableEntryDoesntExistsError, PlayerNotInClanError, ValueError) as e:
            await interaction.response.send_message(e)

    @client.tree.command(name="kill", description="Record hit and killing of the boss")
    @app_commands.describe(tc_name="Team composition name", ovf_time="Ovf time")
    async def kill(interaction: discord.Interaction, tc_name: str, ovf_time: str):
        """ Record hit on boss and moves to another (updates lap and tier if needed)"""
        try:
            await service.get_guild_by_id(interaction.guild.id)
            await hit_kill(interaction, interaction.user.id, tc_name, ovf_time=ovf_time)
        except TableEntryDoesntExistsError as e:
            await interaction.response.send_message(e)

    @client.tree.command(name="pilotkill", description="Pilot and register kill")
    @app_commands.describe(tc_name="Name of team composition",
                           piloted_player_name='Name of the player that was piloted', ovf_time="Ovf time")
    async def pilot_kill(interaction: discord.Interaction, tc_name: str, piloted_player_name: str, ovf_time: str):
        """ Record hit on boss """
        try:
            guild = await service.get_guild_by_id(interaction.guild.id)
            if not guild:
                raise TableEntryDoesntExistsError("Server doesn't exist! Please run **/server setup**")

            player = await service.get_player_by_name(piloted_player_name)
            clan_player_tuple = await service.get_clan_player(player.player_id)
            clan = await service.get_clan_battle_by_id(guild.guild_id)
            if not clan_player_tuple:
                raise TableEntryDoesntExistsError(f'Player {piloted_player_name} is not in clan.')
            clan_player_clan = clan_player_tuple[1]
            if clan_player_clan.clan_id != clan.clan_id:
                raise TableEntryDoesntExistsError(f'Player {piloted_player_name} is not in clan.')

            await hit_kill(interaction, player.discord_id, tc_name, ovf_time=ovf_time)
        except (TableEntryDoesntExistsError, PlayerNotInClanError, ValueError) as e:
            await interaction.response.send_message(e)

    @client.tree.command(name="ovfhit", description="Removes ovf from your profile")
    async def ovf_hit(interaction: discord.Interaction):
        """ Record ovf """
        try:
            guild = await service.get_guild_by_id(interaction.guild.id)
            players = await service.get_player_by_discord_id(interaction.user.id)
            clan = await service.get_clan_by_guild(interaction.guild_id)
            cb = await service.get_clan_battle_active_by_clan_id(clan.clan_id)

            day_of_cb = get_cb_day(cb)
            if len(players) == 1:
                player = players[0]
                if day_of_cb:
                    pcdi = await service.get_pcdi_by_player_id_and_cb_id_and_day(player.player_id, cb.cb_id, day_of_cb)
                    if pcdi.overflow:
                        pcdi.overflow = False
                        pcdi.ovf_time = ''
                        pcdi.ovf_comp = ''
                        pcdi = await service.update_pcdi(pcdi)
                        await interaction.response.send_message(f"You have used your ovf")
                    else:
                        await interaction.response.send_message(f"You dont have ovf")
                else:
                    await interaction.response.send_message(f"Today is not cb day")
        except (ParameterIsNullError, ClanBattleCantHaveMoreThenFiveDaysError, TableEntryDoesntExistsError) as e:
            return await interaction.response.send_message(e)

    @client.tree.command(name="pilotovfhit", description="Removes ovf from your profile")
    @app_commands.describe(piloted_player_name='Name of the player that was piloted')
    async def pilot_ovf_hit(interaction: discord.Interaction,  piloted_player_name: str):
        """ pilot and record ovf """
        try:
            guild = await service.get_guild_by_id(interaction.guild.id)
            if not guild:
                raise TableEntryDoesntExistsError("Server doesn't exist! Please run **/server setup**")

            player = await service.get_player_by_name(piloted_player_name)
            clan_player_tuple = await service.get_clan_player(player.player_id)
            clan = await service.get_clan_battle_by_id(guild.guild_id)
            if not clan_player_tuple:
                raise TableEntryDoesntExistsError(f'Player {piloted_player_name} is not in clan.')
            clan_player_clan = clan_player_tuple[1]
            if clan_player_clan.clan_id != clan.clan_id:
                raise TableEntryDoesntExistsError(f'Player {piloted_player_name} is not in clan.')

            clan = await service.get_clan_by_guild(interaction.guild_id)
            cb = await service.get_clan_battle_active_by_clan_id(clan.clan_id)

            day_of_cb = get_cb_day(cb)

            if day_of_cb:
                pcdi = await service.get_pcdi_by_player_id_and_cb_id_and_day(player.player_id, cb.cb_id, day_of_cb)
                if pcdi.overflow:
                    pcdi.overflow = False
                    pcdi.ovf_time = ''
                    pcdi.ovf_comp = ''
                    pcdi = await service.update_pcdi(pcdi)
                    await interaction.response.send_message(f"You have used your ovf")
                else:
                    await interaction.response.send_message(f"You dont have ovf")
            else:
                await interaction.response.send_message(f"Today is not cb day")
        except (ParameterIsNullError, ClanBattleCantHaveMoreThenFiveDaysError, TableEntryDoesntExistsError, ValueError) as e:
            return await interaction.response.send_message(e)

    @client.tree.command(name="ovfkill", description="Kill boss with ovf and removes ovf from your profile")
    async def ovf_kill(interaction: discord.Interaction):
        """  Record ovf and moves to another (updates lap and tier if needed)"""
        try:
            guild = await service.get_guild_by_id(interaction.guild.id)
            if not guild:
                raise TableEntryDoesntExistsError("Server doesn't exist! Please run **/server setup**")
            players = await service.get_player_by_discord_id(interaction.user.id)
            clan = await service.get_clan_by_guild(interaction.guild_id)
            cb = await service.get_clan_battle_active_by_clan_id(clan.clan_id)

            day_of_cb = get_cb_day(cb)
            if len(players) == 1:
                player = players[0]
                if day_of_cb:
                    pcdi = await service.get_pcdi_by_player_id_and_cb_id_and_day(player.player_id, cb.cb_id, day_of_cb)
                    if pcdi.overflow:
                        pcdi.overflow = False
                        pcdi.ovf_time = ''
                        pcdi.ovf_comp = ''
                        pcdi = await service.update_pcdi(pcdi)

                        await update_lap_and_tier(interaction, cb, pcdi)
                    else:
                        await interaction.response.send_message(f"You dont have ovf")
                else:
                    await interaction.response.send_message(f"Today is not cb day")
        except (ParameterIsNullError, ClanBattleCantHaveMoreThenFiveDaysError, TableEntryDoesntExistsError) as e:
            return await interaction.response.send_message(e)

    @client.tree.command(name="pilotovfkill", description="Kill boss with ovf and removes ovf from your profile")
    @app_commands.describe(piloted_player_name='Name of the player that was piloted')
    async def pilot_ovf_kill(interaction: discord.Interaction,  piloted_player_name: str):
        """  Record ovf and moves to another (updates lap and tier if needed)"""
        try:
            guild = await service.get_guild_by_id(interaction.guild.id)
            if not guild:
                raise TableEntryDoesntExistsError("Server doesn't exist! Please run **/server setup**")

            player = await service.get_player_by_name(piloted_player_name)
            clan_player_tuple = await service.get_clan_player(player.player_id)
            clan = await service.get_clan_battle_by_id(guild.guild_id)
            if not clan_player_tuple:
                raise TableEntryDoesntExistsError(f'Player {piloted_player_name} is not in clan.')
            clan_player_clan = clan_player_tuple[1]
            if clan_player_clan.clan_id != clan.clan_id:
                raise TableEntryDoesntExistsError(f'Player {piloted_player_name} is not in clan.')

            clan = await service.get_clan_by_guild(interaction.guild_id)
            cb = await service.get_clan_battle_active_by_clan_id(clan.clan_id)

            day_of_cb = get_cb_day(cb)

            if day_of_cb:
                pcdi = await service.get_pcdi_by_player_id_and_cb_id_and_day(player.player_id, cb.cb_id, day_of_cb)
                if pcdi.overflow:
                    pcdi.overflow = False
                    pcdi.ovf_time = ''
                    pcdi.ovf_comp = ''
                    pcdi = await service.update_pcdi(pcdi)

                    await update_lap_and_tier(interaction, cb, pcdi)
                else:
                    await interaction.response.send_message(f"{piloted_player_name} dont have ovf")
            else:
                await interaction.response.send_message(f"Today is not cb day")
        except (ParameterIsNullError, ClanBattleCantHaveMoreThenFiveDaysError, TableEntryDoesntExistsError, ValueError) as e:
            return await interaction.response.send_message(e)

    @client.tree.command(name="check", description="Checks status of clan")
    async def check(interaction: discord.Interaction):
        """ Check status of the clan """
        try:
            guild = await service.get_guild_by_id(interaction.guild.id)
            if not guild:
                raise TableEntryDoesntExistsError("Server doesn't exist! Please run **/server setup**")
            clan = await service.get_clan_by_guild(interaction.guild_id)
            cb = await service.get_clan_battle_active_by_clan_id(clan.clan_id)
            cb_day = get_cb_day(cb)
            if cb_day:
                hits_left = await service.get_today_hits_left(cb_day, cb.cb_id)
                ranking = await scrape_clan_rankings(clan.name)
                boss = await service.get_active_boss_by_cb_id(cb.cb_id)
                await interaction.response.send_message(f"Hits left: {hits_left}/90\n"
                                                        f"Current lap: {cb.lap}\n"
                                                        f"Current boss: {boss.name}\n"
                                                        f"Clan ranking: {ranking}")
            else:
                await interaction.response.send_message(f"Today is not cb day")
        except (ParameterIsNullError, ClanBattleCantHaveMoreThenFiveDaysError, TableEntryDoesntExistsError) as e:
            return await interaction.response.send_message(e)

    @client.tree.command(name="selfcheck", description="Checks status of yourself")
    async def self_check(interaction: discord.Interaction):
        """ Check status of yourself """
        try:
            guild = await service.get_guild_by_id(interaction.guild.id)
            if not guild:
                raise TableEntryDoesntExistsError("Server doesn't exist! Please run **/server setup**")
            clan = await service.get_clan_by_guild(interaction.guild_id)
            players = await service.get_player_by_discord_id(interaction.user.id)
            cb = await service.get_clan_battle_active_by_clan_id(clan.clan_id)
            if not cb:
                raise ValueError('There is not active cb')
            if len(players) == 1:
                player = players[0]
                cb_day = get_cb_day(cb)
                if cb_day:
                    pcdi = await service.get_pcdi_by_player_id_and_cb_id_and_day(player.player_id, cb.cb_id, cb_day)
                    has_ovf = 'yes' if pcdi.overflow else 'no'
                    ovf_time = f'Ovf time: {pcdi.ovf_time}\n' if pcdi.overflow else ''
                    ovf_comp = f'Ovf comp: {pcdi.ovf_comp}\n' if pcdi.overflow else ''

                    await interaction.response.send_message(f"Hits left: {pcdi.hits}/3\n"
                                                            f"Reset: {pcdi.reset}\n"
                                                            f"Ovf: {has_ovf}\n"
                                                            f"{ovf_time}"
                                                            f"{ovf_comp}")
                else:
                    await interaction.response.send_message(f"Today is not cb day")
        except (ParameterIsNullError, ClanBattleCantHaveMoreThenFiveDaysError, TableEntryDoesntExistsError, ValueError) as e:
            return await interaction.response.send_message(e)

    @client.tree.command(name="getoverflows", description="Gets all available overflows in clan")
    async def get_ovf_players(interaction: discord.Interaction):
        """ Get players with ovf """
        try:
            await service.get_guild_by_id(interaction.guild.id)
            clan = await service.get_clan_by_guild(interaction.guild_id)
            cb = await service.get_clan_battle_active_by_clan_id(clan.clan_id)
            cb_day = get_cb_day(cb)
            if cb_day:
                pcdi_player_tup = await service.get_all_pcdi_ovf_by_cb_id(cb.cb_id, True, cb_day)
                message_string = ''
                for i in range(len(pcdi_player_tup)):
                    pcdi = pcdi_player_tup[i][0]
                    player = pcdi_player_tup[i][1]
                    message_string += f'Player: {player.name}, ovf comp is {pcdi.ovf_comp}, ovf time: {pcdi.ovf_time}\n'
                if message_string:
                    await interaction.response.send_message(message_string)
                else:
                    await interaction.response.send_message(f'There are no ovf in clan')
            else:
                await interaction.response.send_message(f"Today is not cb day")
        except (ParameterIsNullError, ClanBattleCantHaveMoreThenFiveDaysError, TableEntryDoesntExistsError) as e:
            return await interaction.response.send_message(e)

    @client.tree.command(name="bossavailability", description="Gets all available booking for boss in lap")
    @app_commands.describe(lap="Desired lap", boss_num='Boss number')
    async def boss_availability(interaction: discord.Interaction, lap: str, boss_num: str):

        try:
            lap_int = int(lap)
            boss_num_int = int(boss_num)
            await service.get_guild_by_id(interaction.guild.id)

            clan = await service.get_clan_by_guild(interaction.guild.id)
            if not clan:
                raise TableEntryDoesntExistsError("Clan doesn't exist!")
            cb = await service.get_clan_battle_active_by_clan_id(clan.clan_id)
            boss = await service.get_active_boss_by_cb_id(cb.cb_id)
            booking_tup = await service.get_all_boss_bookings_by_lap(boss.boss_number, boss_num_int, cb.lap, lap_int, cb.cb_id)
            boss_char = boss_char_by_lap(cb.lap)

            message_string = ''
            for i in range(len(booking_tup)):
                booking = booking_tup[i][0]
                boss = booking_tup[i][1]
                player = booking_tup[i][2]
                boss_name = f'{boss_char}{boss.name[1:]}'
                ovf_time = f'ovf time: {booking.ovf_time}\n' if booking.overflow else ''
                has_ovf = f'ovf: yes, {ovf_time}' if booking.overflow else 'ovf: no'

                message_string += f'Boss: {boss_name}, player: {player.name}, team composition: {booking.comp_name}, ' \
                                  f'{has_ovf}\n'
            if not message_string:
                message_string = f'For lap: {lap} and boss: {boss_num} doesnt exists any booking'
            return await interaction.response.send_message(message_string)

        except (ParameterIsNullError, ClanBattleCantHaveMoreThenFiveDaysError, TableEntryDoesntExistsError, ValueError) as e:
            return await interaction.response.send_message(e)

    @client.tree.command(name="bookboss", description="Creates booking for desired boss")
    @app_commands.describe(comp_name='Name of team composition', lap="Desired lap", boss_num='Boss number')
    async def book_boss(interaction: discord.Interaction, comp_name: str, lap: str, boss_num: str):
        try:
            await service.get_guild_by_id(interaction.guild.id)

            await book_boss_help(interaction, '', lap, boss_num, comp_name)

        except TableEntryDoesntExistsError as e:
            return await interaction.response.send_message(e)

    @client.tree.command(name="bookbossovf", description="Creates booking for desired boss for ovf hit")
    @app_commands.describe(comp_name='Name of team composition', ovf_time='Overflow time', lap="Desired lap",
                           boss_num='Boss number')
    async def book_boss_ovf(interaction: discord.Interaction, comp_name: str, ovf_time: str, lap: str, boss_num: str):
        try:
            await service.get_guild_by_id(interaction.guild.id)

            await book_boss_help(interaction, ovf_time, lap, boss_num, comp_name)

        except TableEntryDoesntExistsError as e:
            return await interaction.response.send_message(e)
    @hit.error
    async def say_error(interaction: discord.Interaction, error):
        await interaction.response.send_message("Not allowed.", ephemeral=True)

    client.run(TOKEN)
