import Lib.util as _util
import random

WeaponTypes: list = [
    "Orb",
    "Staff",
    "Wand",
    "Scepter",
    "Symbol",
    "Artifact",
    "Relic",
    "Spellblade",
    "Crystal",
    "Rod",
]

ArmorTypes: list = [
    "Occult Robe",
    "Elven Robe",
    "Bloodweave Robe",
    "Opura Robe",
    "Silk Robe",
    "Monk's Robe",
    "Plated Robe",
    "Scaled Robe",
]

ItemPrefixes: list = [
    "Masterwork",
    "Old",
    "Archaic",
    "Bright",
    "Heavy",
    "Ornate",
    "Gilded",
    "Regal",
    "Opulent",
    "Savage",
    "Cursed",
    "Balanced",
]

ItemRarities: dict = {
    "Common": 0,
    "Uncommon": 1,
    "Rare": 2,
    "Epic": 3,
    "Legendary": 4,
    "Mythic": 5,
}


class Item:
    def __init__(self, slot=-1):
        self.name: str = ""
        self.slot: int = slot if slot != -1 else 0
        self.atk: int = 5
        self.grd: int = 5
        self.rarity: str = "Common"
        self.level: int = 1
        self.value: int = 1
        self.tier: int = 0

    def Randomize(self, max_rarity: str = "Rare", slot: int = -1):
        isWeapon: bool = random.randint(0, 1) == 0
        if slot != -1:
            isWeapon = slot == 0
        # Random names for fun
        if isWeapon:
            self.slot = 0
            self.name = "{} {}".format(
                random.choice(ItemPrefixes), random.choice(WeaponTypes)
            )
        else:
            self.slot = 1
            self.name = "{} {}".format(
                random.choice(ItemPrefixes), random.choice(ArmorTypes)
            )
        _rarity: int = 6
        while _rarity > ItemRarities[max_rarity]:
            _rarity = random.randint(0, 5)
        # This should really be an enum, 'cuz this is lowkey disgusting
        self.rarity = list(ItemRarities.keys())[
            list(ItemRarities.values()).index(_rarity)
        ]
        # "Very" "mathematical" and "logical" way of calculating stats
        self.atk = (
            random.randint(
                1 + (ItemRarities[self.rarity] * 10),
                10 + (ItemRarities[self.rarity] * 10),
            )
            * (ItemRarities[self.rarity] + 1)
            * (10 if self.slot == 0 else 1)
        )
        self.grd = (
            random.randint(
                1 + (ItemRarities[self.rarity] * 10),
                10 + (ItemRarities[self.rarity] * 10),
            )
            * (ItemRarities[self.rarity] + 1)
            * (10 if self.slot == 1 else 1)
        )
        self.level = int(
            (ItemRarities[self.rarity] + 1) * (int(self.atk + self.grd / 10))
        )
        self.value = int((self.atk + self.grd) * self.level) + 1000 * self.tier

    def Upgrade(self):
        global ItemRarities
        self.tier += 1
        self.atk += random.randint(
            10 * self.tier + int(self.level * (ItemRarities[self.rarity]) / 10),
            10 * self.tier + int(self.level * (ItemRarities[self.rarity]) / 10) + 40,
        )
        self.grd += random.randint(
            10 * self.tier + int(self.level * (ItemRarities[self.rarity]) / 10),
            10 * self.tier + int(self.level * (ItemRarities[self.rarity]) / 10) + 40,
        )
        self.value = int((self.atk + self.grd) * self.level) + 1000 * self.tier


# Pack itemdata into a list for easier storage
def pack(item: Item) -> list:
    return [
        item.name,
        item.slot,
        item.atk,
        item.grd,
        item.rarity,
        item.level,
        item.value,
        item.tier,
    ]


# Unpack a list into itemdata
def unpack(l: list) -> Item:
    i: Item = Item()
    i.name = l[0]
    i.slot = l[1]
    i.atk = l[2]
    i.grd = l[3]
    i.rarity = l[4]
    i.level = l[5]
    i.value = l[6]
    i.tier = l[7]
    return i
