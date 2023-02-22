import discord
from discord import app_commands
from discord.ext import commands
from exceptions.exceptions import ParameterIsNullError, ObjectExistsInDBError, TableEntryDoesntExistsError, \
    ClanBattleCantHaveMoreThenFiveDaysError, DesiredBossIsDeadError, PlayerNotInClanError, ObjectDoesntExistsInDBError
import json
import os
from service.service import Service
from .help_functions import get_cb_day, hit_kill, multiple_players_check, update_lap_and_tier, scrape_clan_rankings, \
    boss_char_by_lap, book_boss_help
from typing import Optional

# Open config.json file
# If doesn't exist, create with empty TOKEN field
if os.path.exists(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config.json'))):
    with open("./config.json") as f:
        configData = json.load(f)
else:
    configTemplate = {"TOKEN": "", "Prefix": "!"}
    with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config.json')), "w+") as f:
        json.dump(configTemplate, f)

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
        await client.load_extension("bot.server-commands")
        try:
            # Don't do this. Should move elsewhere after testing is done
            synced = await client.tree.sync()
            print(f"Synced {len(synced)} command(s)")
        except Exception as e:
            print(e)

    ### TESTING / MISC COMMANDS ###

    @client.tree.command(name="hello")
    async def hello(interaction: discord.Interaction):
        await interaction.response.send_message(
            f"Hi fellow cosplayer {interaction.user.mention}! Your Discord ID is {interaction.user.id}. I'm Marin",
            ephemeral=False)

    @client.tree.command(name="help")
    async def help_func(interaction: discord.Interaction):
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
    @app_commands.describe(date="Start date of CB")
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
    @app_commands.describe(tc_name="Name of team composition", player_name='Name of your account')
    async def hit(interaction: discord.Interaction, tc_name: str, player_name: Optional[str] = None):
        """ Record hit on boss """
        try:
            await service.get_guild_by_id(interaction.guild.id)
            await hit_kill(service, interaction, interaction.user.id, tc_name, player_name)
        except (TableEntryDoesntExistsError, ValueError) as e:
            await interaction.response.send_message(e)

    @client.tree.command(name="pilothit", description="Pilot and register hit")
    @app_commands.describe(tc_name="Name of team composition",
                           piloted_player_name='Name of the player that was piloted')
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

            await hit_kill(service, interaction, player.discord_id, tc_name, piloted_player_name)
        except (TableEntryDoesntExistsError, PlayerNotInClanError, ValueError) as e:
            await interaction.response.send_message(e)

    @client.tree.command(name="kill", description="Record hit and killing of the boss")
    @app_commands.describe(tc_name="Team composition name", player_name='Name of your account', ovf_time="Ovf time")
    async def kill(interaction: discord.Interaction, tc_name: str, ovf_time: str, player_name: Optional[str] = None):
        """ Record hit on boss and moves to another (updates lap and tier if needed)"""
        try:
            await service.get_guild_by_id(interaction.guild.id)
            await hit_kill(service, interaction, interaction.user.id, tc_name, player_name, ovf_time=ovf_time)
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

            await hit_kill(service, interaction, player.discord_id, tc_name, piloted_player_name, ovf_time=ovf_time)
        except (TableEntryDoesntExistsError, PlayerNotInClanError, ValueError) as e:
            await interaction.response.send_message(e)

    @client.tree.command(name="ovfhit", description="Removes ovf from your profile")
    @app_commands.describe(player_name='Name of your account')
    async def ovf_hit(interaction: discord.Interaction, player_name: Optional[str] = None):
        """ Record ovf """
        try:
            await service.get_guild_by_id(interaction.guild.id)
            players = await service.get_player_by_discord_id(interaction.user.id)
            clan = await service.get_clan_by_guild(interaction.guild_id)
            cb = await service.get_clan_battle_active_by_clan_id(clan.clan_id)

            day_of_cb = get_cb_day(cb)

            player = multiple_players_check(player_name, players)
            if day_of_cb:
                pcdi = await service.get_pcdi_by_player_id_and_cb_id_and_day(player.player_id, cb.cb_id, day_of_cb)
                if pcdi.overflow:
                    pcdi.overflow = False
                    pcdi.ovf_time = ''
                    pcdi.ovf_comp = ''
                    await service.update_pcdi(pcdi)
                    await interaction.response.send_message(f"You have used your ovf")
                else:
                    await interaction.response.send_message(f"You dont have ovf")
            else:
                await interaction.response.send_message(f"Today is not cb day")
        except (ParameterIsNullError, ClanBattleCantHaveMoreThenFiveDaysError, TableEntryDoesntExistsError) as e:
            return await interaction.response.send_message(e)

    @client.tree.command(name="pilotovfhit", description="Removes ovf from your profile")
    @app_commands.describe(piloted_player_name='Name of the player that was piloted')
    async def pilot_ovf_hit(interaction: discord.Interaction, piloted_player_name: str):
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
                    await service.update_pcdi(pcdi)
                    await interaction.response.send_message(f"You have used your ovf")
                else:
                    await interaction.response.send_message(f"You dont have ovf")
            else:
                await interaction.response.send_message(f"Today is not cb day")
        except (ParameterIsNullError, ClanBattleCantHaveMoreThenFiveDaysError, TableEntryDoesntExistsError,
                ValueError) as e:
            return await interaction.response.send_message(e)

    @client.tree.command(name="ovfkill", description="Kill boss with ovf and removes ovf from your profile")
    @app_commands.describe(player_name='Name of your account')
    async def ovf_kill(interaction: discord.Interaction, player_name: Optional[str] = None):
        """  Record ovf and moves to another (updates lap and tier if needed)"""
        try:
            guild = await service.get_guild_by_id(interaction.guild.id)
            if not guild:
                raise TableEntryDoesntExistsError("Server doesn't exist! Please run **/server setup**")
            players = await service.get_player_by_discord_id(interaction.user.id)
            clan = await service.get_clan_by_guild(interaction.guild_id)
            cb = await service.get_clan_battle_active_by_clan_id(clan.clan_id)

            day_of_cb = get_cb_day(cb)

            player = multiple_players_check(player_name, players)
            if day_of_cb:
                pcdi = await service.get_pcdi_by_player_id_and_cb_id_and_day(player.player_id, cb.cb_id, day_of_cb)
                if pcdi.overflow:
                    pcdi.overflow = False
                    pcdi.ovf_time = ''
                    pcdi.ovf_comp = ''
                    pcdi = await service.update_pcdi(pcdi)

                    await update_lap_and_tier(service, interaction, cb, pcdi)
                else:
                    await interaction.response.send_message(f"You dont have ovf")
            else:
                await interaction.response.send_message(f"Today is not cb day")
        except (ParameterIsNullError, ClanBattleCantHaveMoreThenFiveDaysError, TableEntryDoesntExistsError) as e:
            return await interaction.response.send_message(e)

    @client.tree.command(name="pilotovfkill", description="Kill boss with ovf and removes ovf from your profile")
    @app_commands.describe(piloted_player_name='Name of the player that was piloted')
    async def pilot_ovf_kill(interaction: discord.Interaction, piloted_player_name: str):
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

                    await update_lap_and_tier(service, interaction, cb, pcdi)
                else:
                    await interaction.response.send_message(f"{piloted_player_name} dont have ovf")
            else:
                await interaction.response.send_message(f"Today is not cb day")
        except (ParameterIsNullError, ClanBattleCantHaveMoreThenFiveDaysError, TableEntryDoesntExistsError,
                ValueError) as e:
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
    @app_commands.describe(player_name='Name of your account')
    async def self_check(interaction: discord.Interaction, player_name: Optional[str] = None):
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
            player = multiple_players_check(player_name, players)
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
        except (ParameterIsNullError, ClanBattleCantHaveMoreThenFiveDaysError, TableEntryDoesntExistsError,
                ValueError) as e:
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
            booking_tup = await service.get_all_boss_bookings_by_lap(boss.boss_number, boss_num_int, cb.lap, lap_int,
                                                                     cb.cb_id)
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

        except (ParameterIsNullError, ClanBattleCantHaveMoreThenFiveDaysError, TableEntryDoesntExistsError,
                ValueError) as e:
            return await interaction.response.send_message(e)

    @client.tree.command(name="bookboss", description="Creates booking for desired boss")
    @app_commands.describe(comp_name='Name of team composition', lap="Desired lap",
                           boss_num='Boss number', player_name='Name of your account')
    async def book_boss(interaction: discord.Interaction, comp_name: str, lap: str, boss_num: str,
                        player_name: Optional[str] = None):
        try:
            await service.get_guild_by_id(interaction.guild.id)

            await book_boss_help(service, interaction, '', lap, boss_num, comp_name, player_name)

        except TableEntryDoesntExistsError as e:
            return await interaction.response.send_message(e)

    @client.tree.command(name="bookbossovf", description="Creates booking for desired boss for ovf hit")
    @app_commands.describe(comp_name='Name of team composition', ovf_time='Overflow time', lap="Desired lap",
                           boss_num='Boss number', player_name='Name of your account')
    async def book_boss_ovf(interaction: discord.Interaction, comp_name: str, ovf_time: str, lap: str, boss_num: str,
                            player_name: Optional[str] = None):
        try:
            await service.get_guild_by_id(interaction.guild.id)

            await book_boss_help(service, interaction, ovf_time, lap, boss_num, comp_name, player_name)

        except TableEntryDoesntExistsError as e:
            return await interaction.response.send_message(e)

    @hit.error
    async def say_error(interaction: discord.Interaction, error):
        await interaction.response.send_message("Not allowed.", ephemeral=True)

    client.run(TOKEN)
