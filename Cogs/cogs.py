from discord.ext import commands
import discord
from Utils.Checks import is_botadmin, is_serveradmin
from Utils.Config import Config
import sys,os,logging
import datetime, pytz
class Cogs(commands.Cog):
    def __init__(self,client):
        self.client = client
        self.server_prefixes = Config("./JSONs/prefixes.json")
    @commands.command(name="prefix")
    @is_serveradmin()
    async def _prefix(self, ctx, prefix):
        if len(prefix) > 2:
            await ctx.channel.send("`Prefix too long!`")
            return
        #self.server_prefixes[str(ctx.guild.id)] = prefix
        self.client.server_prefixes[str(ctx.guild.id)] = prefix
        await ctx.channel.send(f"Prefix is now {prefix}")
    @commands.command(name="reload")
    @is_botadmin()
    async def _reload(self,ctx, cog):
        cog = cog.lower()
        emb = discord.Embed()
        # Unload Cog
        try:
            self.client.unload_extension(f'Cogs.{cog}')
        except commands.ExtensionNotFound:
            pass
        except commands.ExtensionNotLoaded:
            print(f"{cog} was not unloaded when reloading.")
        # If there are attachments
        if len(ctx.message.attachments) > 0:
            attached_file = ctx.message.attachments[0]
            # IF the attachment is a python file
            if attached_file.filename[-3:] == ".py":
                # Try and save it.
                try:
                    await attached_file.save(f"./CogStore/{attached_file.filename}")
                except FileExistsError:
                    emb.title="File Already Exists!",
                    emb.colour=discord.Colour.red()
                    await ctx.channel.send(embed=emb)
            else:
                emb = discord.Embed(
                    title="Not a python file!",
                    color=discord.Colour.red()
                )
                await ctx.channel.send(embed=emb)
        # Try to load the extension.
        try:
            self.client.load_extension(f'Cogs.{cog}')
            emb.title = f"Reloaded: {cog.capitalize()}"
            emb.colour = discord.Colour.green()
            await ctx.send(embed=emb)
            return
        except commands.ExtensionNotFound:
            emb.title = f"Extension Not Found: {cog.capitalize()}"
            emb.colour = discord.Colour.red()
            await ctx.send(embed=emb)
            return
        except commands.ExtensionNotLoaded:
            emb.title = f"Extension Not Loaded: {cog.capitalize()}"
            emb.colour = discord.Colour.red()
            await ctx.send(embed=emb)
            return
    @commands.command(name="load")
    @is_botadmin()
    async def _load(self,ctx,cog):
        cog = cog.lower()
        try:
            self.client.load_extension(f'Cogs.{cog}')
            successfulEmbed = discord.Embed(
                title=f"Loaded: {cog.capitalize()}",
                color=discord.Colour.green()
            )
            await ctx.send(embed=successfulEmbed)
        except commands.ExtensionNotFound:
            failedEmbed = discord.Embed(
                title=f"Could not find: {cog.capitalize()}",
                color=discord.Colour.red()
            )
            await ctx.send(embed=failedEmbed)

    @commands.command(name="unload")
    @is_botadmin()
    async def _unload(self,ctx,cog):
        cog = cog.lower()
        try:
            self.client.unload_extension(f'Cogs.{cog}')
            successfulEmbed = discord.Embed(
                title=f"Unloaded: {cog.capitalize()}",
                color=discord.Colour.orange()
            )
            await ctx.send(embed=successfulEmbed)
        except commands.ExtensionNotFound:
            failedEmbed = discord.Embed(
                title=f"Unable to unload: {cog.capitalize()}",
                color=discord.Colour.red()
            )
            await ctx.send(embed=failedEmbed)
        except commands.ExtensionNotLoaded:
            failedEmbed = discord.Embed(
                title=f"Extension either Not Found or Not Active: {cog.capitalize()}",
                color=discord.Colour.red()
            )
            await ctx.send(embed=failedEmbed)
    @commands.command(name="restart")
    @is_botadmin()
    async def _restart(self, ctx):
        await ctx.channel.send("Restarting the bot, this might take a few seconds!")
        print("RESTARTING!")
        await self.client.close()
        try:
            os.execv(sys.argv[0], sys.argv)
        except Exception as e:
            logging.error(e)
        os.execv(sys.executable, [sys.executable, __file__] + sys.argv)

    @commands.command(name="ping")
    async def ping(self,ctx):
        await ctx.channel.send(f"Pong :ping_pong:!  `{round(self.client.latency * 1000)}ms`")
    @commands.command(name="uptime")
    async def uptime(self,ctx):
        oldtz = pytz.timezone("UTC")
        newtz = pytz.timezone("US/Pacific")
        localizedtz = oldtz.localize(self.client.uptime)
        timdelta = datetime.datetime.now(newtz) - localizedtz.astimezone(newtz)
        hours, remainder = divmod(timdelta.total_seconds(), 3600)
        minutes,seconds = divmod(remainder, 60)
        await ctx.channel.send(f"`{round(hours)} hours {round(minutes)} minutes {round(seconds)} seconds`")


def setup(client):
    client.add_cog(Cogs(client))