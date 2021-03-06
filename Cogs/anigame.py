import asyncio

from discord.ext import commands
import discord
import json
from Utils.Config import Config
from Utils.AnidexConfig import AniConfig
from Utils import Aniutils
from Utils.Functions import intTryParse
from math import floor
from Utils import Checks
from Utils.Checks import is_botadmin
import time
import random
import typing
elementDict = {
    "Grass 🍃": discord.Colour.from_rgb(21, 173, 34),
    "Dark 🌙": discord.Colour.from_rgb(53, 8, 92),
    "Fire 🔥": discord.Colour.from_rgb(232, 45, 16),
    "Light ☀️": discord.Colour.from_rgb(255, 252, 133),
    "Neutral ✨": discord.Colour.from_rgb(189, 182, 143),
    "Electric ⚡": discord.Colour.from_rgb(225, 232, 9),
    "Ground ⛰️": discord.Colour.from_rgb(191, 109, 21),
    "Water 💧": discord.Colour.from_rgb(31, 151, 242)
}
class AnigameCog(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.anidex = AniConfig("./JSONs/cards.json")
        self.linkConfig = Config("./JSONs/cardlinks.json")
        self.talents = Config("./JSONs/talents.json")
        self.searchsettings = Config("./JSONs/anisearch.json")
        self.locations = Config("./JSONs/locationinfo.json")
        self._raidsearchlist = Config("./JSONs/anisearch.json")
        self.load_emojis()
        self.messages = Config("./JSONs/messages.json")
        self.cinforeplace = True
        self.seriesupdate = False
    @commands.Cog.listener(name="on_message")
    async def on_message(self, msg):
        if self.client.user.mentioned_in(msg) and str(self.client.user.id) in msg.content:
            await msg.channel.send(f"{random.choice(self.messages['PINGED'])} "
                                   f"`Prefix: {self.client.server_prefixes.get(msg.guild.id, '~')}`")
            return
        elif".rd lobbies" in msg.content and str(msg.author.id) in self.searchsettings:
            if self.searchsettings[str(msg.author.id)]["DELETESEARCH"]:
                await msg.delete(delay=10)
            return

        if(len(msg.embeds) != 0 and msg.author.id == 571027211407196161):
            # .cinfo
            if(msg.embeds[0].description and "**Card Series:**" in msg.embeds[0].description and not ("**Familiarity" in msg.embeds[0].description)):
                await self.process_card(msg.embeds[0], self.anidex, msg)
                cardinfo = self.anidex.get_precise(msg.embeds[0].title.split("*")[2])
                if(self.cinforeplace):
                    await msg.delete()
                    await msg.channel.send(embed=self.cardEmbed(cardinfo))
            # Raid Search
            elif msg.embeds[0].footer.text and "Type .rd battle when you have Energy!" in msg.embeds[0].footer.text:
                #if "Note: You have to clear a location/stage" in msg.embeds[0].footer.text and "393982976125435934" in msg.embeds[0].author.icon_url:
                #    await self.locationstuff(msg)
                partyEmbed = self.processRaidParty(msg.embeds[0], self.emojis)
                await msg.channel.send(embed=partyEmbed)
                await msg.delete()
            # .bt delete
            elif "Challenging Floor" in msg.embeds[0].title:
                await self.deleting_battles_func(msg, msg.embeds[0])
            # Series & Card Assignment
            elif self.seriesupdate and "Anidex" in msg.embeds[0].title and "393982976125435934" in msg.embeds[0].author.icon_url:
                numCards = int(msg.embeds[0].footer.text.split("/")[1].strip())
                cardsTracked = 0
                if(numCards == 0):
                    return
                series = []
                ts = time.time()
                def check(before, after):
                    return before.author.id == 571027211407196161 and before.id == msg.id
                def reactioncheck(reaction, user):
                    return reaction.message.id == msg.id and user.id == 393982976125435934
                while(time.time() < ts+60):
                    embed = msg.embeds[0]
                    desc = embed.description.splitlines()
                    for i in range(0, len(desc)):
                        if(desc[i].startswith("**ID")):
                            card = desc[i] + "\n" + desc[i+1]
                            series.append(card.encode("ascii", "ignore").decode())
                            cardsTracked += 1
                    if cardsTracked == numCards:
                        break
                    try:
                        await self.client.wait_for('message_edit', check = check, timeout=60)
                    except asyncio.TimeoutError:
                        break
                index = 0
                resultStr = ""
                completedSeries = {}
                for card in series:
                    cardname = card.split("|")[1].split("<")[0].strip()
                    index = index+1
                    completedSeries[cardname] = f"{index}, {index+numCards}, {index+numCards*2}\n"
                    resultStr += f"{cardname} - {index}, {index+numCards}, {index+numCards*2}\n"
                msg = await msg.channel.send(resultStr)
                await msg.add_reaction("✅")
                await msg.add_reaction("❌")
                try:
                    reaction, user = await self.client.wait_for('reaction_add', check=reactioncheck, timeout=30)
                except asyncio.TimeoutError:
                    await msg.delete()
                if reaction.emoji == "✅":
                    for key in completedSeries.keys():
                        if key in self.anidex:
                            changed = self.anidex[key]
                            changed["FLOOR"] = completedSeries[key]
                            self.anidex[key] = changed
                    await msg.channel.send(f"Done!")
                elif reaction.emoji == "❌":
                    await msg.delete()






    @commands.command(aliases=["cinfo","ci"])
    async def cardinfo(self,ctx,*, card):
        # this should be an array
        cardinfo = self.anidex.get_precise(card)
        await ctx.channel.send(embed=self.cardEmbed(cardinfo))
    @commands.command(name='aniadmin')
    @is_botadmin()
    async def _admincinfo(self, ctx, arg=""):
        arg = arg.upper()
        if arg == "":
            emb = discord.Embed(title="Admin Commands", color=discord.Color.random(),
                                description="**Toggles:**\n`cinfo` `seriesupdate`\n"
                                            "**Commands:**\n`applylocs` - Applies location numbers with series on cards.\n")
            await ctx.channel.send(embed=emb)
        elif arg == "CINFO":
            self.cinforeplace = not self.cinforeplace
            await ctx.channel.send(f".cinfo replacement is: {self.cinforeplace}")
        elif arg == "SERIESUPDATE":
            self.seriesupdate = not self.seriesupdate
            await ctx.channel.send(f"Series updates for Piro are: {self.seriesupdate}")
    @commands.command(name="applylocs")
    @is_botadmin()
    async def _applylocs(self, ctx):
        with open("./JSONs/locationinfo.json", 'r') as f:
            db = json.load(f)
        dex = self.anidex.all()
        keys = dex.keys()
        for key in keys:
            if dex[key]["SERIES"] in db:
                dex[key]["LOC"] = db[dex[key]["SERIES"]]["Number"]
        self.anidex.dump(dex)

    @commands.command(aliases=["cstat", "raidstat"])
    async def cardstat(self, ctx, *, cstats = ""):
        usageString = "**Correct Usage:**\n`Rarity Evo Level Card Name`\n" \
                      "`SR 3 1350 Alice Zuberg`\n" \
                      "`Super Rare Level 1350 Alice Zuberg`" \
                      "\n(copy the top part of .rd view)"
        if cstats == "":
            await ctx.channel.send(usageString)
            return
        args = cstats.split(" ")
        rarity = Aniutils.process_rarity(args[0])
        if rarity == False:
            await ctx.channel.send(usageString)
            return
        args.pop(0)
        # Remove unnecessary words
        argstwo = []
        for i in range(0,len(args)):
            if(len(args) == 0):
                await ctx.channel.send(usageString)
                return
            if not (args[i].upper() == "RARE" or args[i].upper() == "LEVEL"
                    or args[i].upper() == "EVO"):
                argstwo.append(args[i])
        args = argstwo.copy()
        evo = 3
        level = 50
        if(len(args) <= 1):
            await ctx.channel.send(usageString)
            return
        if(intTryParse(args[0])[1]):
            args[0] = int(args[0])
            if(args[0] <= 3):
                evo = args[0]
                args.pop(0)
            else:
                level = args[0]
                args.pop(0)
        if(intTryParse(args[0])[1]):
            args[0] = int(args[0])
            if(args[0] <= 3):
                evo = args[0]
                args.pop(0)
            else:
                level = args[0]
                args.pop(0)
        await ctx.send(f"Rarity: {rarity} Evo: {evo} Level {level}")
        cardinf = self.anidex.get_precise(" ".join(args))
        if not cardinf:
            await ctx.channel.send("Card not found!")
            return
        stats = self.cardStat(cardinf[0], rarity, evo, level)
        await ctx.channel.send(embed=self.cardEmbed(cardinf, stats))
        pass

    def dict_to_array(self, carddict):
        keys = carddict.keys()
        carray = []
        for key in keys:
            carray.append(carddict[key])
        return carray

    def cardStat(self, cardinfo, rarity, evo, level):
        if type(rarity) == str:
            rarity = rarity.upper()
            if(rarity == "C"): rarity = 1
            elif rarity == "UC": rarity = 2
            elif rarity == "R": rarity = 3
            elif rarity == "SR": rarity = 4
            else:   rarity = 5
        statMultiplier = (1 + float(rarity) * 0.2) * (1 + float(level) * 0.005) * (1 + 0.15 * (float(evo) - 1))
        stats = [floor(cardinfo["HP"]*statMultiplier), floor(cardinfo["ATK"]*statMultiplier),
                floor(cardinfo["DEF"]*statMultiplier), floor(cardinfo["SPD"]*statMultiplier), 0]
        total = sum(stats)
        stats[4] = total
        return stats

    # Returns Card Embed of cinfo
    def cardEmbed(self, cardinfo, altstats=None):
        #element, hp, atk, def, spd, total, locname, loc, fl, talent, footer, name
        cname = cardinfo[1]
        cardinfo = cardinfo[0]
        embDesc = f"""
            **Card Series:** {cardinfo["SERIES"]}\n**Location:** {cardinfo["LOC"]}\n**Floor:** {cardinfo["FLOOR"]}
            **Type:** {cardinfo["ELEMENT"]}"""
        emb = discord.Embed(
            title= cname,
            color= elementDict[cardinfo["ELEMENT"]],
            description=embDesc
        )
        if altstats is None:
            hp = cardinfo['HP']
            atk = cardinfo['ATK']
            defense = cardinfo['DEF']
            spd = cardinfo['SPD']
            total = cardinfo['TOTAL']
        else:
            hp = altstats[0]
            atk = altstats[1]
            defense = altstats[2]
            spd = altstats[3]
            total = altstats[4]
        if altstats is None:
            emb.add_field(name="**BASE**",
                          value=f"**HP:** {hp}\n**ATK:** {atk}\n"
                                f"**DEF:** {defense}\n**SPD:** {spd}\n**TOTAL:** {total}",
                          inline=True)
            emb.add_field(name="**Maxed SR**",
                          value=f"**HP:** {floor(hp*2.925)}\n**ATK:** {floor(atk*2.925)}\n"
                                f"**DEF:** {floor(defense*2.925)}\n**SPD:** {floor(spd*2.925)}\n"
                                f"**TOTAL:** {floor(hp*2.925)+floor(atk*2.925)+floor(defense*2.925)+floor(spd*2.925)}",
                          inline=True)
            emb.add_field(name="**Maxed UR**",
                          value=f"**HP:** {floor(hp*3.38)}\n**ATK:** {floor(atk*3.38)}\n"
                                f"**DEF:** {floor(defense*3.38)}\n**SPD:** {floor(spd*3.38)}\n"
                                f"**TOTAL:** {floor(hp*3.38)+floor(atk*3.38)+floor(defense*3.38)+floor(spd*3.38)}",
                          inline=True)
        else:
            emb.add_field(name="**Stats**",
                          value=f"**HP:** {hp}\n**ATK:** {atk}\n"
                                f"**DEF:** {defense}\n**SPD:** {spd}\n**TOTAL:** {total}",
                          inline=True)
        try:
            emb.add_field(name="**Talent**", value=f"**{cardinfo['TALENT']}**: {cardinfo['ABILITY']}", inline=False)
        except:
            pass
        emb.set_image(url=cardinfo['LINK'])
        emb.set_footer(text=cardinfo['QUOTE'])
        return emb

    def load_emojis(self):
        emojis = {}
        emojis["greenOpen"] = self.client.get_emoji(804100604192227329)
        emojis["greenFull"] = self.client.get_emoji(804100707233693798)
        emojis["greenClose"] = self.client.get_emoji(804100733267476521)
        emojis["emptyClose"] = self.client.get_emoji(804100782654750810)
        emojis["redOpen"] = self.client.get_emoji(804100541637459998)
        emojis["emptyFull"] = self.client.get_emoji(804100642641149992)
        emojis["yellowOpen"] = self.client.get_emoji(804100575921700912)
        emojis["yellowFull"] = self.client.get_emoji(804108415395823687)
        self.emojis = emojis
    async def dexseriesprocess(self,msg):
        pass
    async def locationstuff(self, msg):
        embed = msg.embeds[0]
        locations = {}
        def check(before, after):
            return before.author.id == 571027211407196161 and before.id == msg.id
        ts = time.time()
        while time.time() < ts + 60:
            embed = msg.embeds[0]
            lines = embed.description.splitlines()
            locName = ""
            for i in range(0, len(lines)):
                line = lines[i]
                if "**Location" not in line:
                    continue
                locnum = int(line.split(" ")[1][:-2])
                if (len(lines) > i + 2):
                    if ("**Location" not in lines[i + 2]):
                        locName = (lines[i + 1] + lines[i + 2]).split("(")[1][:-1]
                else:
                    locName = (lines[i + 1]).split("(")[1][:-1]
                locations[locName] = {"Number": locnum}
                self.locations.dump(locations)
                print(f"{locnum} - {locName}")
            try:
                await self.client.wait_for('message_edit', check=check, timeout=60)
            except asyncio.TimeoutError:
                break
    async def deleting_battles_func(self, msg, embed):
        await msg.add_reaction("🗑️")
        def reaction_check(reaction: discord.Reaction, user: discord.user):
            if msg.embeds and msg.author.id == 571027211407196161:
                try:
                    if user.name in reaction.message.embeds[0].description.splitlines()[0] and "Challenging Floor" in embed.title:
                        return reaction.message == msg
                except:
                    return False
            return False
        try:
            reaction, user = await self.client.wait_for('reaction_add', check=reaction_check, timeout=180.0)
        except:
            return
        if reaction.emoji == "🗑️":
            await msg.channel.send(random.choice(self.messages["DELETE"]))
            await msg.delete()

    """
    ANISEARCH
    """

    @commands.group(aliases=["rs", "raidsearch"], invoke_without_command=True)
    @Checks.anisearchWhitelist()
    async def _raidsearch(self, ctx):
        _embed = discord.Embed(title="Raid Search Commands!", color=discord.Colour.blurple())
        _embed.add_field(name="~rs Enable/Disable:",
                         value="enabled, mobile, highchanceonly, delete, deletesearch, deletedelay",
                         inline=True)
        _embed.add_field(name="Settings:", value="~rs settings\n~rs rgb R G B\n~rs set (int setting) (value)",
                         inline=False)
        _embed.add_field(name="Admin's Only:",
                         value="whitelist add/remove (userid)\nprivate(list/role/channel)\nprivatetoggle (pt)",
                         inline=False)
        await ctx.send(embed=_embed)

    @_raidsearch.command(name="list")
    @Checks.is_botadmin()
    async def _raidsearchlist(self, ctx):
        rsList = self._raidsearchlist.all()
        output = ""
        for k in rsList.keys():
            if (k == "SEARCHCARDS" or k == "DEFAULT"):
                continue
            if rsList[k]["LASTUSERNAME"] != "":
                output += rsList[k]["LASTUSERNAME"] + f" ({k})" + "\n"
            else:
                output += k + "\n"
        emb = discord.Embed(
            title="Piro Search Whitelist",
            description=output,
            color=discord.Colour.random())
        await ctx.channel.send(embed=emb)

    @_raidsearch.command(name="add")
    @Checks.is_botadmin()
    async def _raidsearchadd(self, ctx, id: typing.Optional[int], dUser: typing.Optional[discord.User]):
        if (id):
            usr = await self.client.fetch_user(id)
        elif dUser:
            usr = dUser
            id = dUser.id
        else:
            await ctx.send("Please specify a person!")
        if (usr is not None):
            rsList = self._raidsearchlist.all()
            rsList[str(id)] = self._raidsearchlist["DEFAULT"].copy()
            rsList[str(id)]["LASTUSERNAME"] = usr.name
            self._raidsearchlist.dump(rsList)
        emb = discord.Embed(
            title=f"Added {usr.name} to Piro Search"
        )
        await ctx.channel.send(embed=emb)

    @_raidsearch.command(name="remove")
    @Checks.is_botadmin()
    async def _raidsearchremove(self, ctx, id: typing.Optional[int], dUser: typing.Optional[discord.User]):
        if (id):
            usr = await self.client.fetch_user(id)
        elif dUser:
            usr = dUser
            id = dUser.id
        self._raidsearchlist.pop(str(id))
        if usr is not None:
            emb = discord.Embed(
                title=f"Removed {usr.name}",
                color=discord.Colour.random()
            )
            await ctx.channel.send(embed=emb)
        else:
            await ctx.channel.send(f"`Removed: {id}`")

    @_raidsearch.command(name="settings")
    @Checks.anisearchWhitelist()
    async def _raidsearchsetting(self, ctx):
        author_settings = self._raidsearchlist[str(ctx.author.id)]
        rgb = author_settings["RGB"]
        _embed = discord.Embed(title="Raid Search Settings",
                               color=discord.Color.from_rgb(rgb[0], rgb[1], rgb[2]))
        for setting in author_settings.keys():
            _embed.add_field(name=setting.capitalize(), value=str(author_settings[setting]), inline=False)
        await ctx.channel.send(embed=_embed)

    @_raidsearch.command(name="set")
    @Checks.anisearchWhitelist()
    async def _raidsearchset(self, ctx, setting, value):
        author_settings = self._raidsearchlist[str(ctx.author.id)]
        setting = setting.upper()
        value = value.upper()
        intval = intTryParse(value)
        if setting not in author_settings.keys() or setting == "LASTUSERNAME":
            await ctx.channel.send(f"`Unknown Setting {setting}`")
            return
        if value == "TRUE":
            value = True
        elif value == "FALSE":
            value = False
        elif intval[1]:
            value = intval[0]
        else:
            await ctx.channel.send(f"`Unknown Setting Value! {value}`")
            return
        if type(author_settings[setting]) != type(value):
            await ctx.channel.send("Invalid type for this setting!")
            return
        author_settings[setting] = value
        self._raidsearchlist[str(ctx.author.id)] = author_settings
        rgb = author_settings["RGB"]
        _emb = discord.Embed(title='Success!', color=discord.Color.from_rgb(rgb[0], rgb[1], rgb[2]))
        _emb.description = f'{setting} is now {value}'
        await ctx.channel.send(embed=_emb)

    async def process_card(self, embed, config, msg):
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
        talent = "".join(embed.fields[0].value.split("*")[2:]).split(":")[0]
        ability = "".join(embed.fields[0].value.split("*")[4:]).split(":")[1].strip()
        quote = embed.footer.text
        link = embed.image.url
        new_card = True
        if (config[name]):
            loc = config[name]["LOC"]
            floor = config[name]["FLOOR"]
            new_card = False
        config[name] = {
            "ELEMENT": cardtype,
            "HP": hp, "ATK": atk, "DEF": defense, "SPD": speed, "TOTAL": total,
            "SERIES": series, "LOC": loc, "FLOOR": floor, "TALENT": talent,
            "QUOTE": quote, "LINK": link, "ABILITY": ability
        }
        if (new_card):
            print(f"New Card: {name}")
            await msg.add_reaction("✅")
        return new_card

    def processRaidParty(self, embed, emojis):
        piroEmbed = discord.Embed(
            title=embed.title,
            color=discord.Color.from_rgb(114, 141, 237)
        )
        piroEmbed.set_author(name=embed.author.name, icon_url=embed.author.icon_url)
        piroEmbed.set_footer(text=embed.footer.text)
        # piroEmbed.set_thumbnail(url=embed.thumbnail.url)
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
        name = (" ".join(list_Lines[0].split("[")[0].split("Level")[1].split(" ")[2:])).strip()
        if(self.anidex[name]):
            piroEmbed.set_thumbnail(url=self.anidex[name]["LINK"])
        else:
            piroEmbed.set_thumbnail(url=embed.thumbnail.url)
        list_Lines[1] = list_Lines[1].replace("**", "")
        firstnum = list_Lines[1].split('/')[0].replace('\u200b' or ' ', '')
        hp_left = int(firstnum)
        totalHP = int(list_Lines[1].split('/')[1].split('<')[0].replace('\u200b' or ' ', ''))
        list_Lines[1] = f"**{hp_left:,} / {totalHP:,} = {round(((hp_left / totalHP) * 100), 2)}% :heart:**"
        list_Lines[2] = self.hpbar(emojis, hp_left, totalHP)
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
                    # player_str += re.sub('\(.+?\)', '', list_Lines[j]) + '\n'
                self.processPlayerString(player_str, players, totalHP)

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

    def processPlayerString(self, playerString, playerArr, totalHP):
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
        elif (totalHP / 100) * 0.97 <= floor(t_dmg / t_atks) <= totalHP / 100:
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

    def hpbar(self, emojis, hpamount: int, hptotal: int):
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

def setup(client):
    client.add_cog(AnigameCog(client))