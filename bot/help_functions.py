import discord
from datetime import datetime, timezone
import re
from bs4 import BeautifulSoup
from fake_useragent import UserAgent  # pip install fake-useragent
import aiohttp
from exceptions.exceptions import ObjectDoesntExistsInDBError, ParameterIsNullError, \
    ClanBattleCantHaveMoreThenFiveDaysError, NoActiveCBError, CantBookDeadBossError


user_agent = UserAgent(browsers=["chrome", "edge", "firefox", "safari", "opera"])


def get_cb_day(cb):
    current_time_object = datetime.now(tz=timezone.utc).replace(minute=0, second=0, microsecond=0)
    current_time = current_time_object.strftime("%d-%m-%Y %H:%M:%S")
    current_time_object = datetime.strptime(current_time, "%d-%m-%Y %H:%M:%S")
    start_date_object = datetime.strptime(cb.start_date, "%d-%m-%Y %H:%M:%S")
    end_date_object = datetime.strptime(cb.end_date, "%d-%m-%Y %H:%M:%S")
    if start_date_object <= current_time_object <= end_date_object:
        day_of_cb = (current_time_object - start_date_object).days + 1
        return day_of_cb
    else:
        return None


async def update_bosses_when_tier_change(service, cb, boss_char, boss_tier, change_active=True):
    bosses = await service.get_bosses(cb.cb_id)
    active_boss = None
    for boss_iter in bosses:
        boss_iter.name = f'{boss_char}{boss_iter.boss_number}'
        boss_iter.ranking = boss_tier
        if boss_iter.boss_number == 1 and change_active:
            boss_iter.active = True
            active_boss = boss_iter
        await service.update_boss(boss_iter)
    active_boss = active_boss if active_boss else await service.get_active_boss_by_cb_id(cb.cb_id)
    return active_boss


async def update_lap_and_tier(service, interaction, cb, pcdi):
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
            await update_bosses_when_tier_change(service, cb, boss_char, boss_tier)
            boss = await service.get_active_boss_by_cb_id(cb.cb_id)
        elif cb.lap == tier3_lap:
            boss_tier = 3
            boss_char = 'C'
            await update_bosses_when_tier_change(service, cb, boss_char, boss_tier)
            boss = await service.get_active_boss_by_cb_id(cb.cb_id)
        elif cb.lap == tier4_lap:
            boss_tier = 4
            boss_char = 'D'
            await update_bosses_when_tier_change(service, cb, boss_char, boss_tier)
            boss = await service.get_active_boss_by_cb_id(cb.cb_id)
        else:
            boss = await service.get_boss_by_boss_number(1, cb.cb_id)
            boss.active = True
            boss = await service.update_boss(boss)
    else:
        boss_number += 1
        boss = await service.get_boss_by_boss_number(boss_number, cb.cb_id)
        boss.active = True
        boss = await service.update_boss(boss)
    embed=discord.Embed(title="Success!", color=0xffff00,
                        description=f"You recorded your hit with ovf time {pcdi.ovf_time} and killed the {boss_killed_name}"
                                    f"\nActive Boss: {boss.name}")
    return await interaction.response.send_message(embed=embed, ephemeral=False)


def multiple_players_check(player_name, players):
    player = None
    if len(players) > 1 and not player_name:
        error_message = 'You have multiple account please choose name from one of them as optional parameter:\n'
        for index, player in enumerate(players):
            error_message += f'{index + 1}. {player.name}\n'
        raise ValueError(error_message)
    elif len(players) > 1 and player_name:
        for player_iter in players:
            if player_iter.name == player_name:
                player = player_iter
                break
        if not player:
            raise ValueError(f'You dont have account with name {player_name}')
    elif len(players) == 1:
        player = players[0]
    else:
        raise ValueError(f'Wtf are you even doing here?')
    return player


async def hit_kill(service, interaction, tc_name, player_name, ovf_time='', pilot=False):
    """ help function for hit and kill functions """
    try:
        if not pilot:
            players = await service.get_player_by_discord_id(interaction.user.id)
            player = multiple_players_check(player_name, players)
            clan_player = await service.get_clan_player(player.player_id)
            clan = clan_player[1]
        else:
            player = await service.get_player_by_name(player_name)
            clan_player = await service.get_clan_player(player.player_id)
            clan = clan_player[1]
            guild = await service.get_guild_by_id(clan.guild_id)
            if interaction.guild.id != guild.guild_id:
                embed = discord.Embed(title="Error", color=0xff0000,
                                  description=f"You can't pilot {player_name} because they are not in this discord server!")
                return await interaction.response.send_message(embed=embed, ephemeral=True)

        cb = await service.get_clan_battle_active_by_clan_id(clan.clan_id)
        day_of_cb = get_cb_day(cb)

        if day_of_cb:
            pcdi = await service.get_pcdi_by_player_id_and_cb_id_and_day(player.player_id, cb.cb_id, day_of_cb)
            if pcdi.overflow:
                embed = discord.Embed(title="Error", color=0xff0000,
                                          description=f"You have overflow active, you can't use hit command")
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            if pcdi.hits == 0:
                embed = discord.Embed(title="Error", color=0xff0000,
                                          description=f"You dont have any hits left")
                return await interaction.response.send_message(embed=embed, ephemeral=True)

            else:
                tc = await service.get_team_composition_by_comp_name_and_pcdi_id(tc_name, pcdi.pcbdi_id)
                if not tc:
                    tc = await service.create_team_composition(tc_name, pcdi.pcbdi_id)

                if tc.used and not ovf_time:
                    embed = discord.Embed(title="Error", color=0xff0000,
                                          description=f"You already used {tc.name}")
                    return await interaction.response.send_message(embed=embed, ephemeral=True)

                pcdi.hits -= 1
                tc.used = True
                tc = await service.update_team_composition(tc)

                if ovf_time:
                    pcdi.overflow = True
                    pcdi.ovf_time = ovf_time
                    pcdi.ovf_comp = tc_name

                    pcdi = await service.update_pcdi(pcdi)

                    return await update_lap_and_tier(service, interaction, cb, pcdi)
                else:
                    await service.update_pcdi(pcdi)
                    embed = discord.Embed(title="Success!", color=0xffff00,
                                          description=f"Logged hit **{tc.name}**")
                    return await interaction.response.send_message(embed=embed, ephemeral=False)
        else:
            embed = discord.Embed(title="Error", color=0xff0000,
                                          description="Today is not cb day")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
    except (ParameterIsNullError, ClanBattleCantHaveMoreThenFiveDaysError, ObjectDoesntExistsInDBError) as e:
        embed = discord.Embed(title="Error", color=0xff0000,
                                          description=e)
        return await interaction.response.send_message(embed=embed, ephemeral=True)


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
    return 'Clan is not top 150'


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


async def book_boss_help(service, interaction, ovf_time, lap, boss_num, comp_name, player_name):
    try:
        lap_int = int(lap)
        boss_num_int = int(boss_num)
        players = await service.get_player_by_discord_id(interaction.user.id)
        player = multiple_players_check(player_name, players)
        clan_player = await service.get_clan_player(player.player_id)
        clan = clan_player[1]
        cb = await service.get_clan_battle_active_by_clan_id(clan.clan_id)
        day_of_cb = get_cb_day(cb)

        if day_of_cb:
            boss = await service.get_boss_by_boss_number(boss_num_int, cb.cb_id)
            boss_char = boss_char_by_lap(lap_int)
            boss_name = f'{boss_char}{boss.name[1:]}'
            player = multiple_players_check(player_name, players)
            if ovf_time:
                booking = await service.create_boss_booking(lap_int, cb.lap, True, comp_name, boss.boss_id,
                                                            player.player_id, cb.cb_id, ovf_time=ovf_time)
                embed=discord.Embed(title="OVF Book Success!", color=0xffff00,
                                    description=f'You booked **{booking.comp_name}** with ovf time: **{ovf_time}** for boss: **{boss_name}** on **lap {lap}**')
                return await interaction.response.send_message(embed=embed, ephemeral=False)
            else:
                booking = await service.create_boss_booking(lap_int, cb.lap, False, comp_name, boss.boss_id,
                                                            player.player_id, cb.cb_id)
                embed=discord.Embed(title="Book Success!", color=0xffff00,
                                    description=f'You booked **{booking.comp_name}** for boss: **{boss_name}** on **lap {lap}**')
                return await interaction.response.send_message(embed=embed, ephemeral=False)
        else:
            embed = discord.Embed(title="Error", color=0xff0000,
                                  description="Today is not cb day")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
    except (ObjectDoesntExistsInDBError, CantBookDeadBossError, NoActiveCBError, ParameterIsNullError,
            ClanBattleCantHaveMoreThenFiveDaysError, ValueError) as e:
        embed = discord.Embed(title="Error", color=0xff0000,
                                          description=e)
        return await interaction.response.send_message(embed=embed, ephemeral=True)

async def remove_book_boss_help(service, interaction, ovf_time, lap, boss_num, comp_name, player_name):
    try:
        lap_int = int(lap)
        boss_num_int = int(boss_num)
        players = await service.get_player_by_discord_id(interaction.user.id)
        player = multiple_players_check(player_name, players)
        clan_player = await service.get_clan_player(player.player_id)
        clan = clan_player[1]
        cb = await service.get_clan_battle_active_by_clan_id(clan.clan_id)
        day_of_cb = get_cb_day(cb)

        if day_of_cb:
            boss = await service.get_boss_by_boss_number(boss_num_int, cb.cb_id)
            boss_char = boss_char_by_lap(lap_int)
            boss_name = f'{boss_char}{boss.name[1:]}'
            player = multiple_players_check(player_name, players)
            if ovf_time:
                booking = await service.remove_boss_booking(lap_int, cb.lap, True, comp_name, boss.boss_id,
                                                            player.player_id, cb.cb_id, ovf_time=ovf_time)
                embed=discord.Embed(title="Success!", color=0xffff00,
                                    description=f'You removed **{booking.comp_name}** with ovf time: **{ovf_time}** for boss: **{boss_name}** on **lap {lap}**')
                return await interaction.response.send_message(embed=embed, ephemeral=False)
            else:
                booking = await service.remove_boss_booking(lap_int, cb.lap, False, comp_name, boss.boss_id,
                                                            player.player_id, cb.cb_id)
                embed=discord.Embed(title="Success!", color=0xffff00,
                                    description=f'You removed **{booking.comp_name}** for boss: **{boss_name}** on **lap {lap}**')
                return await interaction.response.send_message(embed=embed, ephemeral=False)
        else:
            embed = discord.Embed(title="Error", color=0xff0000,
                                  description="Today is not cb day")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
    except (ObjectDoesntExistsInDBError, CantBookDeadBossError, NoActiveCBError, ParameterIsNullError,
            ClanBattleCantHaveMoreThenFiveDaysError, ValueError) as e:
        embed = discord.Embed(title="Error", color=0xff0000,
                                  description=e)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
