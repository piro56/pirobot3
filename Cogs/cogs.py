from discord.ext import commands
import discord
from Utils.Checks import is_botadmin
import sys,os,logging
class Cogs(commands.Cog):
    def __init__(self,client):
        self.client = client
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

def setup(client):
    client.add_cog(Cogs(client))