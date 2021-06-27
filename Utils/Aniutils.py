import math

import discord
from math import floor

rarityDict = {
    "COMMON":1,
    "C":1,
    "UNCOMMON":2,
    "UC":2,
    "RARE":3,
    "R":3,
    "SUPER":4,
    "SR":4,
    "SUPER RARE": 4,
    "ULTRA":5,
    "UR":5,
    "ULTRA RARE":5
}

def process_card(embed, config, linkConfig):
    lines = embed.description.splitlines()
    name = (embed.title.split("*")[2])
    cardtype = lines[2].split("*")[4].strip()
    hp = int(lines[3].split("*")[4].strip())
    atk = int(lines[4].split("*")[4].strip())
    defense = int(lines[5].split("*")[4].strip())
    speed = int(lines[6].split("*")[4].strip())
    total = hp + atk + defense + speed
    series = lines[0].split("*")[4].strip()
    loc = 0
    floor = 0
    talent = embed.fields[0].value.split("*")[2]
    quote = embed.footer.text
    link =  embed.image.url
    new_card = True
    if(config[name]):
        loc = config[name]["LOC"]
        floor = config[name]["FLOOR"]
        new_card = False
    config[name] = {
                       "ELEMENT":cardtype,
                       "HP":hp, "ATK":atk, "DEF":defense, "SPD":speed, "TOTAL":total,
                       "SERIES":series, "LOC":loc, "FLOOR":floor, "TALENT":talent,
                       "QUOTE":quote, "LINK":link
                    }
    if(new_card):
        print(f"New Card: {name}")
    return new_card

def process_rarity(arg):
    if(rarityDict.get(arg.upper())):
        return rarityDict.get(arg.upper())
    return False
def hpbar(emojis, hpamount: int, hptotal: int):
    hpBar = []
    hpBar.append(str(emojis['greenOpen']))
    for i in range(0, 8):
        hpBar.append(str(emojis['greenFull']))
    hpBar.append(str(emojis["greenClose"]))
    percentage = (hpamount / hptotal) * 100
    if percentage <= 10:
        hpBar[0] = str(emojis['redOpen'])
        for i in range(1, len(hpBar) - 1):
            hpBar[i] = str(emojis["emptyFull"])
        hpBar[len(hpBar) - 1] = str(emojis['emptyClose'])
    elif percentage <= 50:
        hpBar[0] = str(emojis["yellowOpen"])
        for i in range(1, int(percentage / 10)):
            hpBar[i] = str(emojis["yellowFull"])
        for i in range(int(percentage / 10), len(hpBar) - 1):
            hpBar[i] = str(emojis["emptyFull"])
        hpBar[len(hpBar) - 1] = str(emojis['emptyClose'])
    elif percentage <= 90:
        hpBar[0] = str(emojis["greenOpen"])
        for i in range(1, int(percentage / 10)):
            hpBar[i] = str(emojis["greenFull"])
        for i in range(int(percentage / 10), len(hpBar) - 1):
            hpBar[i] = str(emojis["emptyFull"])
        hpBar[len(hpBar) - 1] = str(emojis["emptyClose"])
    return (''.join(hpBar))

def processRaidParty(embed, emojis):
    piroEmbed = discord.Embed(
        title=embed.title,
        color=discord.Color.from_rgb(114, 141, 237)
    )
    piroEmbed.set_author(name=embed.author.name, icon_url=embed.author.icon_url)
    piroEmbed.set_footer(text=embed.footer.text)
    piroEmbed.set_thumbnail(url=embed.thumbnail.url)
    desc = embed.description
    time_left_line = ""
    for line in embed.title.splitlines():
        if "Timer" in line:
            time_left_line += line[22:]
            break
    time_left_line = time_left_line.split('h')
    hrs = (int)(time_left_line[0].replace('\u200b' or ' ', ''))
    timeLeft = (int)(time_left_line[1].split('m')[0].replace('\u200b' or ' ', '')) + hrs * 60
    list_Lines = desc.splitlines()
    list_Lines[1] = list_Lines[1].replace("**", "")
    firstnum = list_Lines[1].split('/')[0].replace('\u200b' or ' ', '')
    hp_left = int(firstnum)
    totalHP = int(list_Lines[1].split('/')[1].split('<')[0].replace('\u200b' or ' ', ''))
    list_Lines[1] = f"**{hp_left:,} / {totalHP:,} = {round(((hp_left / totalHP) * 100), 2)}% :heart:**"
    list_Lines[2] = hpbar(emojis, hp_left, totalHP)
    # Get the value of each player
    # Get all players into player_data string.
    players = []
    player_str = ""
    for i in range(0, len(list_Lines)):
        if (not len(list_Lines[i]) > 0):
            continue
        if (list_Lines[i][2] == '#'):
            player_str = ""
            for j in range(i, i + 5):
                player_str += list_Lines[j] + '\n'
                #player_str += re.sub('\(.+?\)', '', list_Lines[j]) + '\n'
            processPlayerString(player_str, players, totalHP)

    teamDamage = 0
    energyDamage = 0
    for player in players:
        teamDamage += player['DMG']
        energyDamage += player["EDMG"]

    # Combine Array into full string
    finishMsg = ""
    if (timeLeft > 0):
        pass
    else:
        timeLeft += 1
    for line in range(0, 3):
        finishMsg += list_Lines[line] + '\n'
    finishMsg += f'**Total Team Damage/Atk: {floor(teamDamage):,}**\n'
    finishMsg += f'**Team Damage/Atk to Finish: {round(hp_left / (timeLeft / 5)):,}**\n'
    if (teamDamage == 0):
        teamDamage += 1
    if (hp_left - energyDamage < 0):
        finishMsg += f'**Current time to finish: __NOW__**\n'
    else:
        finishMsg += f'**Ideal Time to Completion: {floor(((((hp_left - energyDamage) / teamDamage) * 5)) / 60)}h {round(((((hp_left - energyDamage) / teamDamage) * 5)) % 60)}m **\n\n'
        # finishMsg += f'**Ideal Time to Completion: {floor((math.ceil((hp_left - energyDamage) / teamDamage) * 5) / 60)}h ' \
        #              f'{round((math.ceil((hp_left - energyDamage) / teamDamage) * 5) % 60)}m **\n\n'
    for player in players:
        finishMsg += player["STR"] + "\n"
    piroEmbed.description = finishMsg
    return piroEmbed

def processPlayerString(playerString, playerArr, totalHP):
    playerInfo = {}
    player_split = playerString.splitlines()

    # remove energy line and add it to first line
    player_split[0] = player_split[0].replace("Power Level", "PL")
    player_split[0] = player_split[0].replace("Level", "LVL")
    t_energy = (int)(player_split[1][7:].split('/')[0].replace('\u200b' or ' ', ''))
    # Get total damage.
    t_dmg = (int)(player_split[2][13:].replace('\u200b' or ' ', ''))
    t_atks = (int)(player_split[3][14:].replace('\u200b' or ' ', ''))
    if t_atks == 0:
        player_split[2] = f"**Total Damage:** {t_dmg:,}"
    elif (totalHP/100)*0.97 <= floor(t_dmg / t_atks) <= totalHP / 100:
        player_split[2] = f"**Total Damage:** {t_dmg:,} ** ** ** **({floor(t_dmg / t_atks):,}) **__MAX__**"
    elif t_atks > 0:
        player_split[2] = f"**Total Damage:** {t_dmg:,} ** ** ** **({floor(t_dmg / t_atks):,})"

    last_atk_time = (int)(player_split[4][13:].split('m')[0].replace('\u200b' or ' ', ''))
    if (t_atks > 0 and last_atk_time < 40):
        playerInfo["DMG"] = (t_dmg / t_atks)
        t_energy_dmg = ((t_energy - (t_energy % 5)) / 5) * t_dmg / t_atks
    else:
        playerInfo["DMG"] = 0
        t_energy_dmg = 0
    final_str = ""
    for line in player_split:
        final_str += line + '\n'
    playerInfo["STR"] = final_str
    playerInfo["EDMG"] = t_energy_dmg
    playerArr.append(playerInfo)