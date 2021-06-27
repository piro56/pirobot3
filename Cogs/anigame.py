import asyncio

from discord.ext import commands
import discord
import json
from Utils.Config import Config
from Utils.AnidexConfig import AniConfig
from Utils import Aniutils
from Utils.Functions import intTryParse
from math import floor
from Utils.Checks import is_botadmin
import time
import random
import typing
elementDict = {
    "Grass 🍃": discord.Colour.from_rgb(21, 173, 34),
    "Dark 🌙": discord.Colour.from_rgb(53, 8, 92),
    "Fire 🔥": discord.Colour.from_rgb(232, 45, 16),
    "Light ☀️": discord.Colour.from_rgb(255, 252, 133),
    "Neutral ✨":discord.Colour.from_rgb(189, 182, 143),
    "Electric ⚡":discord.Colour.from_rgb(225, 232, 9),
    "Ground ⛰️":discord.Colour.from_rgb(191, 109, 21),
    "Water 💧":discord.Colour.from_rgb(31, 151, 242)
}
class AnigameCog(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.anidex = AniConfig("./JSONs/cards.json")
        self.linkConfig = Config("./JSONs/cardlinks.json")
        self.talents = Config("./JSONs/talents.json")
        self.searchsettings = Config("./JSONs/anisearch.json")
        self.locations = Config("./JSONs/locationinfo.json")
        self.load_emojis()
        self.messages = Config("./JSONs/messages.json")
    @commands.Cog.listener(name="on_message")
    async def on_message(self, msg):
        if self.client.user.mentioned_in(msg):
            await msg.channel.send(f"{random.choice(self.messages['PINGED'])} "
                                   f"`Prefix: {self.client.server_prefixes.get(msg.guild.id, '~')}`")
        # .cinfo
        if(len(msg.embeds) != 0 and msg.author.id == 571027211407196161):
            if(msg.embeds[0].description and "**Card Series:**" in msg.embeds[0].description and not ("**Familiarity" in msg.embeds[0].description)):
                Aniutils.process_card(msg.embeds[0], self.anidex, self.linkConfig)
                cardinfo = self.anidex.get_precise(msg.embeds[0].title.split("*")[2])
                await msg.delete()
                await msg.channel.send(embed=self.cardEmbed(cardinfo))
            # Raid Search
            elif ".rd lobbies" in msg.content and self.searchsettings.get(str(msg.author.id)):
                if(self.searchsettings[str(msg.author.id)][6]):
                    await msg.delete(delay=10)
            elif msg.embeds[0].footer.text:
                #if "Note: You have to clear a location/stage" in msg.embeds[0].footer.text and "393982976125435934" in msg.embeds[0].author.icon_url:
                #    await self.locationstuff(msg)
                if "Type .rd battle when you have Energy!" in msg.embeds[0].footer.text:
                    partyEmbed = Aniutils.processRaidParty(msg.embeds[0], self.emojis)
                    await msg.channel.send(embed=partyEmbed)
                    await msg.delete()
            elif "Challenging Floor" in msg.embeds[0].title:
                await self.deleting_battles_func(msg, msg.embeds[0])


    @commands.command(aliases=["cinfo","ci"])
    async def cardinfo(self,ctx,*, card):
        # this should be an array
        cardinfo = self.anidex.get_precise(card)
        await ctx.channel.send(embed=self.cardEmbed(cardinfo))

    @commands.command(name='linkcards')
    @is_botadmin()
    async def _linkcards(self, ctx):
        with open('./JSONs/cards.json', 'r') as f:
            carddb = json.load(f)
        with open('./JSONs/cardlinks.json', 'r') as f:
            linkdb = json.load(f)
        keys = carddb.keys()
        for key in keys:
            arr = carddb[key]
            if(len(arr) >= 12):
                continue
            else:
                arr.append(linkdb[key])
                carddb[key] = arr
        with open('./JSONs/cards.json', 'w') as f:
            json.dump(carddb, f, indent=4)
    @commands.command(name='reformatcards')
    @is_botadmin()
    async def _reformat(self, ctx):
        with open('./JSONs/cards.json', 'r') as f:
            carddb = json.load(f)
        cards = {}
        keys = carddb.keys()
        for key in keys:
            #element, hp, atk, def, speed, total, series, loc, floor, talent, quote, link
            cinfo =  carddb[key]
            cards[key] = {
                "Element": cinfo[0],
                "HP": cinfo[1], "ATK": cinfo[2], "DEF": cinfo[3], "SPD":  cinfo[4],
                "TOTAL": cinfo[5], "SERIES": cinfo[6],
                "LOC": cinfo[7], "FLOOR": cinfo[8],"TALENT": cinfo[9],
                "QUOTE": cinfo[10], "LINK": cinfo[11]
            }
        with open('./JSONs/cards.json', 'w') as f:
            json.dump(cards, f, indent=4)
    @commands.command(name='refanisearch')
    @is_botadmin()
    async def _refanisearch(self,ctx):
        newData = {}
        oldsearch = self.searchsettings.all()
        for key in oldsearch.keys():
            if(key == "DEFAULT" or key == "SEARCH CARDS:"):
                continue
            newData[key] = {
                "ENABLED": oldsearch[key][0],
                "MOBILE": oldsearch[key][1],
                "HIGHCHANCEONLY": oldsearch[key][2],
                "RGB": [oldsearch[key][3],oldsearch[key][4],oldsearch[key][5]],
                "DELETE": oldsearch[key][6],
                "DELETEDELAY": oldsearch[key][7],
                "DELETESEARCH": oldsearch[key][8],
                "LASTUSERNAME": oldsearch[key][9]
            }
        self.searchsettings.dump(newData)
        await ctx.channel.send("done.")

    @commands.command(aliases=["cstat"])
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
        print(args)
        await ctx.send(f"Rarity: {rarity} Evo: {evo} Level {level}")
        cardinf = self.anidex.get_precise(" ".join(args))
        if not cardinf:
            await ctx.channel.send("Card not found!")
            return
        self.cardStat(self.dict_to_array(cardinf[0]), rarity, evo, level)
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
        print(statMultiplier)
        stats = [floor(cardinfo[1]*statMultiplier), floor(cardinfo[2]*statMultiplier),
                floor(cardinfo[3]*statMultiplier), floor(cardinfo[4]*statMultiplier), 0]
        total = sum(stats)
        stats[4] = total
        return stats

    # Returns Card Embed of cinfo
    def cardEmbed(self, cardinfo):
        #element, hp, atk, def, spd, total, locname, loc, fl, talent, footer, name
        cname = cardinfo[1]
        cstats = self.dict_to_array(cardinfo[0])
        embDesc = f"""
            **Card Series:** {cstats[6]}\n**Location:** {cstats[7]}\n**Floor:** {cstats[8]}
            **Type:** {cstats[0]}"""
        emb = discord.Embed(
            title= cname,
            color= elementDict[cstats[0]],
            description=embDesc
        )
        emb.add_field(name="**BASE**",
                      value=f"**HP:** {cstats[1]}\n**ATK:** {cstats[2]}\n**DEF:** {cstats[3]}\n**SPD:** {cstats[4]}\n**TOTAL:** {cstats[5]}",
                      inline= True)
        emb.add_field(name="**Maxed SR**",
                      value=f"**HP:** {floor(cstats[1]*2.925)}\n**ATK:** {floor(cstats[2]*2.925)}\n"
                            f"**DEF:** {floor(cstats[3]*2.925)}\n**SPD:** {floor(cstats[4]*2.925)}\n"
                            f"**TOTAL:** {floor(cstats[1]*2.925)+floor(cstats[2]*2.925)+floor(cstats[3]*2.925)+floor(cstats[4]*2.925)}",
                      inline= True)
        emb.add_field(name="**Maxed UR**",
                      value=f"**HP:** {floor(cstats[1]*3.38)}\n**ATK:** {floor(cstats[2]*3.38)}\n"
                            f"**DEF:** {floor(cstats[3]*3.38)}\n**SPD:** {floor(cstats[4]*3.38)}\n"
                            f"**TOTAL:** {floor(cstats[1]*3.38)+floor(cstats[2]*3.38)+floor(cstats[3]*3.38)+floor(cstats[4]*3.38)}",
                      inline= True)
        try:
            emb.add_field(name="**SR Talent**", value=f"{cstats[9]}: {self.talents[cstats[9]]['SR']}", inline= False)
            emb.add_field(name="**UR Talent**", value=f"{cstats[9]}: {self.talents[cstats[9]]['UR']}", inline=False)
        except:
            pass
        if(len(cstats) >= 12):
            emb.set_image(url=cstats[11])
        emb.set_footer(text=cstats[10])
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


def setup(client):
    client.add_cog(AnigameCog(client))