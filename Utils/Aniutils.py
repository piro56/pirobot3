import math

import discord
from math import floor
from Utils.AnidexConfig import AniConfig
cards = AniConfig("./JSONs/cards2.json")
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

def process_rarity(arg):
    if(rarityDict.get(arg.upper())):
        return rarityDict.get(arg.upper())
    return False
