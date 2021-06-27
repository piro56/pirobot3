from discord.ext import commands
import discord
from dotenv import load_dotenv
from Utils.Config import Config
import os
import logging
import traceback
import datetime
import sys
import math
# PRELOADING
###TODO: except missing arg error
load_dotenv()
log = logging.getLogger(__name__)
description = """This is PiroBot, a bot written by Piro#0056 for random commands!"""
startup_cogs = [
    "Cogs.cogs",
    "Cogs.anigame",
    "Cogs.datamanager"
]
def _prefix_callable(bot,msg):
    if msg.guild is not None:
        return bot.server_prefixes.get(str(msg.guild.id), "~")
    else:
        return "~"
class PiroBot(commands.Bot):
    def __init__(self):
        allowed_mentions = discord.AllowedMentions(roles=True,everyone=False,users=True)
        intents = discord.Intents(
            guilds=True,
            members=True,
            bans=True,
            emojis=True,
            voice_states=False,
            messages=True,
            reactions=True
        )
        super().__init__(command_prefix=_prefix_callable,
                         description=description,
                         allowed_mentions=allowed_mentions,
                         intents=intents,
                         fetch_offline_members=False,
                         case_insensitive=True)
        self.client_token = os.getenv('DISCORD_TOKEN')
        self.server_prefixes = Config('./JSONs/prefixes.json')

    async def on_ready(self):
        if not hasattr(self, 'uptime'):
            self.uptime = datetime.datetime.utcnow()
            self.remove_command('help')
            for cog in startup_cogs:
                self.load_extension(cog)
                print(f"Loaded: {cog}")
            print("---GUILDS---")
            for guild in self.guilds:
                print(guild.name)
            print("------------")
    async def on_guild_join(self,guild):
        self.server_prefixes[str(guild.id)] = "~"
    async def on_guild_remove(self,guild):
        self.server_prefixes.pop(str(guild.id))
    async def on_command_error(self, ctx, exception):
        cog = ctx.cog
        if cog:
            if cog._get_overridden_method(cog.cog_command_error) is not None:
                return
        ignored = (commands.CommandNotFound, TimeoutError, commands.MissingRequiredArgument, commands.MissingPermissions)
        if isinstance(exception, ignored):
            return
        elif isinstance(exception, commands.CommandOnCooldown):
            await ctx.channel.send(f"This command is on cooldown, try again in {math.floor(exception.retry_after)} seconds!")
        else:
            # All other Errors not returned come here. And we can just print the default TraceBack.
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(exception), exception, exception.__traceback__, file=sys.stderr)
    async def on_message(self, message):
        await self.process_commands(message)

        if(message.author.id == 393982976125435934):
            if("TEST123" in message.content):
                await message.channel.send("TEST!!!")
    def run(self):
        try:
            super().run(self.client_token, reconnect=True)
        finally:
            pass

def main():
    piroBot = PiroBot()
    piroBot.run()
if __name__ == '__main__':
    main()