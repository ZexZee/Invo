import Lib.util as _util
import Lib.item as _item


class User:
    def __init__(self, _id):
        self.id = _id
        self.level: int = 1
        self.xp: int = 0
        self.next_level: int = 100
        self.balance: int = 0
        self.path: str = None
        self.mastery: str = None
        self.ascendance: str = None
        self.weapon: _item.Item = _item.Item(0)
        self.armor: _item.Item = _item.Item(1)
        self.inventory: list = []
        self.materials: dict = {
            "α-Crystal": 0,
            "γ-Ore": 0,
            "ε-Sand": 0,
            "λ-Steel": 0,
            "ω-Essence": 0,
            "z-Materia": 0,
        }

    def NewUser(self):
        self.weapon.Randomize("Common", 0)
        self.armor.Randomize("Common", 1)

    # Update user xp, leveling them up and scaling xp values as necessary
    def UpdateXP(self, value: int) -> (int, int, int):
        self.xp += value
        self.next_level -= value
        while self.next_level <= 0:
            self.level += 1
            self.xp = self.next_level * -1
            self.next_level = int(self.level * 100 * (0.9 * self.level))
            self.next_level -= self.xp
        return (self.level, self.xp, self.next_level)

    def UpdateBalance(self, value: int) -> int:
        self.balance += value
        return self.balance

    def UpdateMaterials(self, material: str, amount: int) -> dict:
        self.materials[material] += amount
        return self.materials

    def UpdatePaths(self, p: str, m: str, a: str) -> (str, str, str):
        # TODO: Find a better way of doing this for the love of all that is holy
        # If the user has no path and a path was provided, assign them one, IF the provided path is valid
        # NOTE: Maybe set global variabled for them just to avoid having to assign and read raw strings? Should
        # make comparisons easier at a later date i think.
        if self.path == None and p != None:
            if p in ["Divine", "Void", "Summoning"]:
                self.path = p
                return (self.path, self.mastery, self.ascendance)
            else:
                _util.ERROR("Illegal Path")
                return (None, None, None)
        # If the user has no mastery but DOES have a path, assign them one, IF the provided mastery is valid
        if self.mastery == None and m != None and self.path != None:
            if self.path == "Divine":
                if m in ["Body", "Mind", "Soul"]:
                    self.mastery = m
                    return (self.path, self.mastery, self.ascendance)
                else:
                    _util.ERROR("Illegal Mastery")
                    return (None, None, None)
            if self.path == "Void":
                if m in ["Flare", "Ruin", "Shadow"]:
                    self.mastery = m
                    return (self.path, self.mastery, self.ascendance)
                else:
                    _util.ERROR("Illegal Mastery")
                    return (None, None, None)
            if self.path == "Summoning":
                if m in ["Atromancy", "Demonology", "Necromancy"]:
                    self.mastery = m
                    return (self.path, self.mastery, self.ascendance)
                else:
                    _util.ERROR("Illegal Mastery")
                    return (None, None, None)
        # If the user has no ascendance but DOES have a mastery, assign them one, IF the provided ascendance is valid
        if self.ascendance == None and a != None and self.mastery != None:
            if self.mastery in ["Body", "Flare", "Atromancy"]:
                if a in ["Justice", "Judgment"]:
                    self.ascendance = a
                    return (self.path, self.mastery, self.ascendance)
                else:
                    _util.ERROR("Illegal Ascendance")
                    return (None, None, None)
            if self.mastery in ["Mind", "Ruin", "Demonology"]:
                if a in ["Guardian", "Wrath"]:
                    self.ascendance = a
                    return (self.path, self.mastery, self.ascendance)
                else:
                    _util.ERROR("Illegal Ascendance")
                    return (None, None, None)
            if self.mastery in ["Soul", "Shadow", "Necromancy"]:
                if a in ["Death", "Calamity"]:
                    self.ascendance = a
                    return (self.path, self.mastery, self.ascendance)
                else:
                    _util.ERROR("Illegal Ascendance")
                    return (None, None, None)


# Pack userdata into a list for easier storage
def pack(user: User) -> list:
    for item in user.inventory:
        user.inventory[user.inventory.index(item)] = _item.pack(item)
    return [
        user.id,
        user.level,
        user.xp,
        user.next_level,
        user.balance,
        user.path,
        user.mastery,
        user.ascendance,
        _item.pack(user.weapon),
        _item.pack(user.armor),
        user.inventory,
        user.materials,
    ]


# Unpack a list into userdata
def unpack(l: list) -> User:
    user: User = User(l[0])
    user.level = l[1]
    user.xp = l[2]
    user.next_level = l[3]
    user.balance = l[4]
    user.path = l[5]
    user.mastery = l[6]
    user.ascendance = l[7]
    user.weapon = _item.unpack(l[8])
    user.armor = _item.unpack(l[9])
    user.inventory = l[10]
    user.materials = l[11]
    for item in user.inventory:
        user.inventory[user.inventory.index(item)] = _item.unpack(item)
    return user
