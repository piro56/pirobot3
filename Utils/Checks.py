from discord.ext import commands
import discord
import json
# @is_serveradmin()
from discord.ext.commands import BucketType, Cooldown, CooldownMapping, Command


def is_serveradmin():
    async def predicate(ctx):
        return ctx.author.guild_permissions.administrator
    return commands.check(predicate)

# def shared_cooldown(rate, per, type=BucketType.default):
#     cooldown = Cooldown(rate, per, type=type)
#     def decorator(func):
#         if isinstance(func, Command):
#             func._buckets = CooldownMapping(cooldown)
#         else:
#             func.__commands_cooldown__ = cooldown
#         return func
#     return decorator

def is_botadmin():
    async def predicate(ctx):
        with open("./JSONs/botadmins.json", 'r') as f:
            botadmins = json.load(f)
            if ctx.author.id in botadmins["admins"]:
                return True
            else:
                await ctx.channel.send(f"{ctx.author.mention} you are not a Bot Admin!")
                return False
    return commands.check(predicate)

def OnlyCCSD():
    async def predicate(ctx):
        return ctx.guild.id == 654323128369020949
    return commands.check(predicate)



def anisearchWhitelist():
    async def predicate(ctx):
        with open("./JSONs/anisearch.json", 'r') as f:
            whitelisted = json.load(f)
            if whitelisted.get(str(ctx.author.id)):
                return True
            else:
                await ctx.channel.send(f"{ctx.author.mention} you are not whitelisted for PiroSearch!")
                return False
    return commands.check(predicate)





def shared_cooldown(rate, per, type=BucketType.default):
    cooldown = Cooldown(rate, per, type=type)
    cooldown_mapping = CooldownMapping(cooldown)
    def decorator(func):
        if isinstance(func, Command):
            func._buckets = cooldown_mapping
        else:
            raise ValueError("Decorator must be applied to command, not the function")
        return func
    return decorator
