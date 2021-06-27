import typing

from discord.ext import commands
from Utils.Config import Config
import discord
from Utils import Checks
from Utils.Functions import intTryParse

class DataManager(commands.Cog):
    def __init__(self,client):
        self.client = client
        self._raidsearchlist = Config("./JSONs/anisearch.json")


    # ANISEARCH
    @commands.group(aliases=["rs", "raidsearch"], invoke_without_command=True)
    @Checks.anisearchWhitelist()
    async def _raidsearch(self, ctx):
        _embed = discord.Embed(title="Raid Search Commands!", color=discord.Colour.blurple())
        _embed.add_field(name="~rs Enable/Disable:", value="enabled, mobile, highchanceonly, delete, deletesearch, deletedelay",
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
            if(k == "SEARCHCARDS" or k == "DEFAULT"):
                continue
            if rsList[k]["LASTUSERNAME"] != "":
                output += rsList[k]["LASTUSERNAME"] + f" ({k})" + "\n"
            else:
                output += k + "\n"
        emb = discord.Embed(
            title= "Piro Search Whitelist",
            description= output,
            color=discord.Colour.random())
        await ctx.channel.send(embed=emb)
    @_raidsearch.command(name="add")
    @Checks.is_botadmin()
    async def _raidsearchadd(self,ctx, id: typing.Optional[int], dUser: typing.Optional[discord.User]):
        if(id):
            usr = await self.client.fetch_user(id)
        elif dUser:
            usr = dUser
            id = dUser.id
        else:
            await ctx.send("Please specify a person!")
        if(usr is not None):
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
    async def _raidsearchremove(self,ctx,id: typing.Optional[int], dUser: typing.Optional[discord.User]):
        if(id):
            usr = await self.client.fetch_user(id)
        elif dUser:
            usr = dUser
            id = dUser.id
        self._raidsearchlist.pop(str(id))
        if usr is not None:
            emb = discord.Embed(
                title=f"Removed {usr.name}",
                color = discord.Colour.random()
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
                               color=discord.Color.from_rgb(rgb[0],rgb[1],rgb[2]))
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
        _emb = discord.Embed(title='Success!', color=discord.Color.from_rgb(rgb[0],rgb[1],rgb[2]))
        _emb.description=f'{setting} is now {value}'
        await ctx.channel.send(embed=_emb)

def setup(client):
    client.add_cog(DataManager(client))