# TODO:
#       Add failsafes and replies to misused commands that inform the user of how they work properly
#       Add gambling elements (/casino.py)
#       Add a shop where you can buy the three most common materials
#       Finish the Path -> Mastery -> Ascendance system
#       Add a Trial where you fight in turnbased combat against a boss that has a chance to drop a unique item
#       Make an auction house where users can sell eachother items and materials
#       Finish documentation (UML, PDF, Comments)
#       Make aliases for every command (where its natural) and update the help message
#       (*)Crafting system? Professions?
import discord
from discord.ext import commands
from discord.ext.commands import CommandNotFound
import asyncio
import datetime
import random
import Lib.util as _util
import Lib.backend as _backend
import Lib.user as _user
import Lib.item as _item
import Lib.casino as _casino


Client_Prefix: str = "."
Version: str = "0.7.3"
Database: _backend.Backend = _backend.Backend()
TOKEN: str = Database.GetToken()
SaveFrequency: int = 300
EX_RatingBounds: (int, int) = (175, 250)
DG_RatingBounds: (int, int) = (15000, 20000)
TW_RatingBounds: (int, int) = (100000, 110000)
# Users that are currently occupied are sent to time gaol, and cannot start any other timed tasks while there
# Adding/Removing is automatic by command by async timeouts
TimeGaol: list = []
# Users that have recently been granted xp from talking are added to this list
XpCooldown: list = []
# Users that have claimed their once-a-day boost are added to this list
DailyCooldown: list = []

client = commands.Bot(command_prefix=Client_Prefix, case_insensitive=True)


@client.event
async def on_command_error(ctx, error) -> None:
    if isinstance(error, CommandNotFound):
        return
    raise error


async def save_internal_task():
    global Database, SaveFrequency
    while True:
        Database.Save()
        await asyncio.sleep(SaveFrequency)


@client.event
async def on_ready():
    global Database
    global Client_Prefix, Version
    await client.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching, name="{}help".format(Client_Prefix)
        )
    )
    if not hasattr(client, "appinfo"):
        client.appinfo = await client.application_info()
    Database.Load()
    _util.INFO("Invo v{} Running ...".format(Version))
    client.loop.create_task(save_internal_task())


@client.event
async def on_message(message):
    global Database, XpCooldown
    if not message.author.bot:
        user: _user.User = Database.GetUserData(message.author)
        if user == None:  # Register new users when they chat
            Database.RegisterUser(message.author)
            user = Database.GetUserData(message.author)
        if message.author.id not in XpCooldown:
            # Give XP for activity every now and then, cooldown to stop spam
            user.UpdateXP(random.randint(10, 15))
            XpCooldown.append(message.author.id)
            await asyncio.sleep(15)
            XpCooldown.remove(message.author.id)
    await client.process_commands(message)


@client.event
async def on_disconnect():
    _util.WARN("Client disconnected.")


client.remove_command("help")


@client.command(aliases=["h", "commands", "c"])
async def help(ctx):
    e: discord.Embed = _util.ComposeEmbed(0xFFFFFF, "Invo", "Help")
    e.add_field(
        name="{}help".format(Client_Prefix), value="Display this message", inline=False
    )
    e.add_field(
        name="{}stats [@]".format(Client_Prefix),
        value="Display user stats, yours or another (@user)",
        inline=False,
    )
    e.add_field(
        name="{}inventory (DM)".format(Client_Prefix),
        value="Check user inventory",
        inline=False,
    )
    e.add_field(
        name="{}equip <inventory slot>".format(Client_Prefix),
        value="Equip an item from your inventory",
        inline=False,
    )
    e.add_field(
        name="{}balance [@]".format(Client_Prefix),
        value="Display user balance, yours or another (@user)",
        inline=False,
    )
    e.add_field(
        name="{}explore".format(Client_Prefix),
        value="Attempt an exploration (15min, small chance of failure based on stats)",
        inline=False,
    )
    e.add_field(
        name="{}dungeon".format(Client_Prefix),
        value="Attemt to clear a dungeon (30min, chance of failure based on stats)",
        inline=False,
    )
    e.add_field(
        name="{}tower".format(Client_Prefix),
        value="Attempt to climb the Antilight Tower (1hr, high chance of failure based on stats)",
        inline=False,
    )
    e.add_field(
        name="{}train".format(Client_Prefix),
        value="Train to grow stronger (2hrs, gain xp based on level and stats, no chance of failure)",
        inline=False,
    )
    e.add_field(
        name="{}path".format(Client_Prefix),
        value="At level 10+, you may choose a path",
        inline=False,
    )
    e.add_field(
        name="{}mastery".format(Client_Prefix),
        value="At level 30+, you may choose a mastery",
        inline=False,
    )
    e.add_field(
        name="{}ascend".format(Client_Prefix),
        value="At level 60+, you may choose an ascension",
        inline=False,
    )
    e.add_field(
        name="{}pay <@> <amount>".format(Client_Prefix),
        value="Send someone some money.",
        inline=False,
    )
    e.add_field(
        name="{}shop (DM)".format(Client_Prefix),
        value="Open the shop, allowing for trades",
        inline=False,
    )
    e.add_field(
        name="{}daily".format(Client_Prefix),
        value="Get a reward every 24 hours.",
        inline=False,
    )
    e.add_field(
        name="{}upgrade <inventory slot>".format(Client_Prefix),
        value="Upgrade an item in your inventory with your collected materials",
        inline=False,
    )
    await ctx.send(embed=e)


@client.command()
async def stats(ctx, user: discord.User = None):
    global Database
    if user == None:  # If they havent specified a user, assume they mean themselves
        user = ctx.author
    data = Database.GetUserData(user)
    e: discord.Embed = _util.ComposeEmbed(
        0xFF00FF, "Invo", "Stats for {}".format(user.name)
    )
    e.add_field(
        name="Level: {}".format(data.level),
        value="xp {} | {}".format(data.xp, data.next_level),
        inline=False,
    )
    e.add_field(
        name="¤{}".format(data.balance),
        value="{} / {} / {}".format(data.path, data.mastery, data.ascendance),
        inline=False,
    )
    e.add_field(
        name="{} +{} (IL: {}) - ATTACK {} | GUARD {}".format(
            data.weapon.name,
            data.weapon.tier,
            data.weapon.level,
            data.weapon.atk,
            data.weapon.grd,
        ),
        value="¤{} | {}".format(data.weapon.value, data.weapon.rarity),
        inline=False,
    )
    e.add_field(
        name="{} +{} (IL: {}) - ATTACK {} | GUARD {}".format(
            data.armor.name,
            data.armor.tier,
            data.armor.level,
            data.armor.atk,
            data.armor.grd,
        ),
        value="¤{} | {}".format(data.armor.value, data.armor.rarity),
        inline=False,
    )
    await ctx.send(embed=e)


@client.command()
async def inventory(ctx):
    global Database
    channel = await ctx.author.create_dm()
    e: discord.Embed = _util.ComposeEmbed(0x00FF00, "Invo", "Inventory")
    data = Database.GetUserData(ctx.author)
    itemslot: int = 0  # Structure the inventory, displaying the itemslot for inventory commands (equip, upgrade)
    for item in data.inventory:
        e.add_field(
            name="{}: {} +{} (IL: {}) - ATTACK {} | GUARD {}".format(
                itemslot, item.name, item.tier, item.level, item.atk, item.grd
            ),
            value="¤{} | {}".format(item.value, item.rarity),
            inline=False,
        )
        itemslot += 1
    e.add_field(
        name="Materials",
        value="α-Crystal | {}\nγ-Ore\t|\t{}\nε-Sand\t|\t{}\nλ-Steel\t|\t{}\nω-Essence\t|\t{}\n".format(
            data.materials["α-Crystal"],
            data.materials["γ-Ore"],
            data.materials["ε-Sand"],
            data.materials["λ-Steel"],
            data.materials["ω-Essence"],
        ),
    )
    await channel.send(embed=e)


@client.command()
async def balance(ctx, user: discord.User = None):
    global Database
    if user == None:  # If they dont specify a user, assume they mean themselves
        user = ctx.author
    data = Database.GetUserData(user)
    e: discord.Embed = _util.ComposeEmbed(
        0x00FF00, "Invo", "{} has ¤{}".format(user.name, data.balance)
    )
    await ctx.send(embed=e)


@client.command()
async def pay(ctx, user: discord.User, amount: int):
    global Database
    if user.bot:  # Stop people from paying bots
        e: discord.Embed = _util.ComposeEmbed(
            0xFF0000, "Invo", "Bots don't need money, trust me."
        )
        await ctx.send(embed=e)
        return
    sender = Database.GetUserData(ctx.author)
    recv = Database.GetUserData(user)
    if recv == None:  # Register the recipient if they dont already exist in the db
        Database.RegisterUser(user)
        recv = Database.GetUserData(user)
    if amount <= 0:  # Negative amounts would let them steal, which is, well, not good
        e: discord.Embed = _util.ComposeEmbed(0xFF0000, "Invo", "Nice try, buddy.")
        await ctx.send(embed=e)
        return
    if amount > sender.balance:  # Make sure they can afford the transaction
        e: discord.Embed = _util.ComposeEmbed(
            0xFF0000, "Invo", "You're too poor to do this; maybe try the casino?"
        )
        await ctx.send(embed=e)
        return  # Update balances
    sender.UpdateBalance(-amount)
    recv.UpdateBalance(amount)
    e: discord.Embed = _util.ComposeEmbed(
        0x00FF00,
        "Invo",
        "{} sent ¤{} to {}.".format(ctx.author.name, amount, user.name),
    )
    if amount == 69:  # Nice.
        e.add_field(name="Nice.", value="Nice.", inline=False)
    await ctx.send(embed=e)


@client.command()
async def daily(ctx):  # Let people claim a reward every 24hrs
    global Database, DailyCooldown
    user = Database.GetUserData(ctx.author)
    if ctx.author.id in DailyCooldown:
        e: discord.Embed = _util.ComposeEmbed(
            0xFF0000, "Invo", "You have already claimed your reward."
        )
        await ctx.send(embed=e)
        return
    b: int = random.randint(2500, 10000)
    x: int = random.randint(50, 100)
    user.UpdateBalance(b)
    user.UpdateXP(x)
    e: discord.Embed = _util.ComposeEmbed(
        0x00FF00,
        "Invo",
        "You gained ¤{} and {}xp! You can claim again in 24 hours.".format(b, x),
    )
    await ctx.send(embed=e)
    DailyCooldown.append(ctx.author.id)
    await asyncio.sleep(86400)
    DailyCooldown.remove(ctx.author.id)


@client.command()
async def explore(ctx):
    global Database, TimeGaol, EX_RatingBounds
    if ctx.author.id in TimeGaol:  # Stop people from doing everything at once
        await ctx.send(
            embed=_util.ComposeEmbed(
                0xFF0000, "Invo", "You are already occupied with something else."
            )
        )
        return
    success_limit: int = random.randint(
        EX_RatingBounds[0], EX_RatingBounds[1]
    )  # Calculate the rating needed to complete the exploration
    e: discord.Embed = _util.ComposeEmbed(
        0xFFFFFF, "Invo", "You embark on an exploration..."
    )
    await ctx.send(embed=e)
    data = Database.GetUserData(ctx.author)
    # Path, mastery and ascendance boosts
    # Please for the love of god tell me that theres a better way to do this that I dont
    # know about.
    rating_boost: float = 0.0  # Percentage increase to rating
    reward_boost: float = 0.0  # Percentage increase to rewards
    time_boost: float = 0.0  # Percentage decrease in completiontime
    if (
        data.path == "Ruler"
        and data.mastery == "Emperor"
        and data.ascendance == "Deity"
    ):
        time_boost += 5.0
        rating_boost += 5.0
        reward_boost += 5.0
    if data.path == "Divine":
        rating_boost += 0.15
        reward_boost += 0.15
        time_boost += 0.15
    if data.path == "Void":
        rating_boost += 0.4
        time_boost += 0.2
    if data.path == "Summoner":
        reward_boost += 0.4
        time_boost += 0.2
    if data.mastery in ["Body", "Flare", "Atromancy"]:
        rating_boost += 0.5
        reward_boost += 0.2
    if data.mastery in ["Mind", "Ruin", "Demonology"]:
        reward_boost += 0.5
        time_boost += 0.1
    if data.mastery in ["Soul", "Shadow", "Necromancer"]:
        rating_boost += 0.5
        time_boost += 0.1
    if data.ascendance in ["Justice", "Guardian", "Death"]:
        rating_boost += 0.75
        reward_boost += 0.75
    if data.ascendance in ["Judgment", "Wrath", "Calamity"]:
        rating_boost += 0.75
        time_boost += 0.5

    rating: int = (
        random.randint(1, 5) * data.level
        + int((data.weapon.atk + data.weapon.grd) / 2)
        + int((data.armor.atk + data.armor.grd) / 2)
    ) * 3
    rating += int(rating * rating_boost)
    TimeGaol.append(ctx.author.id)
    sTime = 900 - (int(900 * time_boost))
    await asyncio.sleep(sTime if sTime > 0 else 0)
    TimeGaol.remove(ctx.author.id)
    if rating >= success_limit:  # If they complete the exploration, generate rewards
        xpr: int = int(random.randint(250, 1000) * reward_boost)
        br: int = int(random.randint(500, 5000) * reward_boost)
        ir: _item.Item = _item.Item()
        ir.Randomize("Uncommon")
        reward: discord.Embed = _util.ComposeEmbed(
            0x00FF00,
            "Invo",
            "{} returns victorious from an exploration!".format(ctx.author.name),
        )
        material: str = random.choice(
            random.choices(
                ["α-Crystal", "γ-Ore", "ε-Sand", "λ-Steel", "ω-Essence"],
                [50, 25, 15, 7, 3],
            )
        )
        # TODO: Make the inventory size maximum a separate variable, and not a hardcoded value
        amount: int = int(random.randint(1, 3) * reward_boost)
        reward.add_field(
            name="+¤{} | +{}xp | +{} {}s".format(br, xpr, amount, material),
            value="and a(n) {} item!".format(  # Make sure that you cant get more than your max inventory spoace
                ir.rarity if len(data.inventory) < 10 else "Your inventory is full."
            ),
            inline=False,
        )
        if len(data.inventory) < 10:
            reward.add_field(
                name="{} +0 (IL: {}) - ATTACK {} | GUARD {}".format(
                    ir.name, ir.level, ir.atk, ir.grd
                ),
                value="¤{} | {}".format(ir.value, ir.rarity),
            )
        data.UpdateXP(xpr)
        data.UpdateBalance(br)
        data.UpdateMaterials(material, amount)
        if len(data.inventory) < 10:
            data.inventory.append(ir)
        await ctx.send(embed=reward)
    else:
        await ctx.send(
            embed=_util.ComposeEmbed(
                0xFF0000,
                "Invo",
                "{} has failed an exploration!".format(ctx.author.name),
            )
        )


# TODO: Maybe find a way to merge explore, dungeon and tower? Maybe specify with an argument?
@client.command()
async def dungeon(
    ctx
):  # See [async def explore(ctx)] for documentation, as the methods are very similar
    global Database, TimeGaol, DG_RatingBounds
    if ctx.author.id in TimeGaol:
        await ctx.send(
            embed=_util.ComposeEmbed(
                0xFF0000, "Invo", "You are already occupied with something else."
            )
        )
        return
    success_limit: int = random.randint(DG_RatingBounds[0], DG_RatingBounds[1])
    e: discord.Embed = _util.ComposeEmbed(0xFFFFFF, "Invo", "You enter a dungeon...")
    await ctx.send(embed=e)
    data = Database.GetUserData(ctx.author)
    rating_boost: float = 0.0  # Percentage increase to rating
    reward_boost: float = 0.0  # Percentage increase to rewards
    time_boost: float = 0.0  # Percentage decrease in completiontime
    if (
        data.path == "Ruler"
        and data.mastery == "Emperor"
        and data.ascendance == "Deity"
    ):
        time_boost += 5.0
        rating_boost += 5.0
        reward_boost += 5.0
    if data.path == "Divine":
        rating_boost += 0.15
        reward_boost += 0.15
        time_boost += 0.15
    if data.path == "Void":
        rating_boost += 0.4
        time_boost += 0.2
    if data.path == "Summoner":
        reward_boost += 0.4
        time_boost += 0.2
    if data.mastery in ["Body", "Flare", "Atromancy"]:
        rating_boost += 0.5
        reward_boost += 0.2
    if data.mastery in ["Mind", "Ruin", "Demonology"]:
        reward_boost += 0.5
        time_boost += 0.1
    if data.mastery in ["Soul", "Shadow", "Necromancer"]:
        rating_boost += 0.5
        time_boost += 0.1
    if data.ascendance in ["Justice", "Guardian", "Death"]:
        rating_boost += 0.75
        reward_boost += 0.75
    if data.ascendance in ["Judgment", "Wrath", "Calamity"]:
        rating_boost += 0.75
        time_boost += 0.5

    rating: int = (
        random.randint(1, 5) * data.level
        + int((data.weapon.atk + data.weapon.grd) / 2)
        + int((data.armor.atk + data.armor.grd) / 2)
    ) * 3
    rating += int(rating * rating_boost)
    TimeGaol.append(ctx.author.id)
    sTime = 1800 - (int(1800 * time_boost))
    await asyncio.sleep(sTime if sTime > 0 else 0)
    TimeGaol.remove(ctx.author.id)
    if rating >= success_limit:
        xpr: int = int(random.randint(2500, 10000) * reward_boost)
        br: int = int(random.randint(10000, 100000) * reward_boost)
        if len(data.inventory) < 10:
            ir: _item.Item = _item.Item()
            ir.Randomize("Epic")
        material: str = random.choice(
            random.choices(
                ["α-Crystal", "γ-Ore", "ε-Sand", "λ-Steel", "ω-Essence"],
                [25, 50, 15, 7, 3],
            )
        )
        amount: int = int(random.randint(1, 3) * reward_boost)
        reward: discord.Embed = _util.ComposeEmbed(
            0x00FF00, "Invo", "{} completed a dungeon!".format(ctx.author.name)
        )
        reward.add_field(
            name="+¤{} | +{}xp | +{} {}s".format(br, xpr, amount, material),
            value="and a(n) {} item!".format(
                ir.rarity if len(data.inventory) < 10 else "Your inventory is full."
            ),
            inline=False,
        )
        if len(data.inventory) < 10:
            reward.add_field(
                name="{} +0 (IL: {}) - ATTACK {} | GUARD {}".format(
                    ir.name, ir.level, ir.atk, ir.grd
                ),
                value="¤{} | {}".format(ir.value, ir.rarity),
            )
        data.UpdateXP(xpr)
        data.UpdateBalance(br)
        data.UpdateMaterials(material, amount)
        if len(data.inventory) < 10:
            data.inventory.append(ir)
        await ctx.send(embed=reward)
    else:
        await ctx.send(
            embed=_util.ComposeEmbed(
                0xFF0000,
                "Invo",
                "{} failed to clear a dungeon!".format(ctx.author.name),
            )
        )


@client.command()
async def tower(
    ctx
):  # See [async def explore(ctx)] for documentation, as the methods are very similar
    global Database, TimeGaol, TW_RatingBounds
    if ctx.author.id in TimeGaol:
        await ctx.send(
            embed=_util.ComposeEmbed(
                0xFF0000, "Invo", "You are already occupied with something else."
            )
        )
        return
    success_limit: int = random.randint(TW_RatingBounds[0], TW_RatingBounds[1])
    e: discord.Embed = _util.ComposeEmbed(
        0xFFFFFF, "Invo", "You start climbing the tower..."
    )
    await ctx.send(embed=e)
    data = Database.GetUserData(ctx.author)
    rating_boost: float = 0.0  # Percentage increase to rating
    reward_boost: float = 0.0  # Percentage increase to rewards
    time_boost: float = 0.0  # Percentage decrease in completiontime
    if (
        data.path == "Ruler"
        and data.mastery == "Emperor"
        and data.ascendance == "Deity"
    ):
        time_boost += 5.0
        rating_boost += 5.0
        reward_boost += 5.0
    if data.path == "Divine":
        rating_boost += 0.15
        reward_boost += 0.15
        time_boost += 0.15
    if data.path == "Void":
        rating_boost += 0.4
        time_boost += 0.2
    if data.path == "Summoner":
        reward_boost += 0.4
        time_boost += 0.2
    if data.mastery in ["Body", "Flare", "Atromancy"]:
        rating_boost += 0.5
        reward_boost += 0.2
    if data.mastery in ["Mind", "Ruin", "Demonology"]:
        reward_boost += 0.5
        time_boost += 0.1
    if data.mastery in ["Soul", "Shadow", "Necromancer"]:
        rating_boost += 0.5
        time_boost += 0.1
    if data.ascendance in ["Justice", "Guardian", "Death"]:
        rating_boost += 0.75
        reward_boost += 0.75
    if data.ascendance in ["Judgment", "Wrath", "Calamity"]:
        rating_boost += 0.75
        time_boost += 0.5

    rating: int = (
        random.randint(1, 5) * data.level
        + int((data.weapon.atk + data.weapon.grd) / 2)
        + int((data.armor.atk + data.armor.grd) / 2)
    ) * 3
    rating += int(rating * rating_boost)
    TimeGaol.append(ctx.author.id)
    sTime = 3600 - (int(3600 * time_boost))
    await asyncio.sleep(sTime if sTime > 0 else 0)
    TimeGaol.remove(ctx.author.id)
    if rating >= success_limit:
        xpr: int = int(random.randint(50000, 100000) * reward_boost)
        br: int = int(random.randint(500000, 1000000) * reward_boost)
        if len(data.inventory) < 10:
            ir: _item.Item = _item.Item()
            ir.Randomize("Mythic")
        material: str = random.choice(
            random.choices(
                ["α-Crystal", "γ-Ore", "ε-Sand", "λ-Steel", "ω-Essence"],
                [10, 15, 50, 15, 10],
            )
        )
        amount: int = int(random.randint(1, 3) * reward_boost)
        reward: discord.Embed = _util.ComposeEmbed(
            0x00FF00,
            "Invo",
            "{} conquered the  Antilight Tower!".format(ctx.author.name),
        )
        reward.add_field(
            name="+¤{} | +{}xp | +{} {}s".format(br, xpr, amount, material),
            value="and a(n) {} item!".format(
                ir.rarity if len(data.inventory) < 10 else "Your inventory is full."
            ),
            inline=False,
        )
        if len(data.inventory) < 10:
            reward.add_field(
                name="{} +0 (IL: {}) - ATTACK {} | GUARD {}".format(
                    ir.name, ir.level, ir.atk, ir.grd
                ),
                value="¤{} | {}".format(ir.value, ir.rarity),
            )
        data.UpdateXP(xpr)
        data.UpdateBalance(br)
        data.UpdateMaterials(material, amount)
        if len(data.inventory) < 10:
            data.inventory.append(ir)
        await ctx.send(embed=reward)
    else:
        await ctx.send(
            embed=_util.ComposeEmbed(
                0xFF0000,
                "Invo",
                "{} failed to climb the tower!".format(ctx.author.name),
            )
        )


@client.command()
async def train(
    ctx
):  # See [async def explore(ctx)] for documentation, as the methods are very similar
    global Database, TimeGaol
    if ctx.author.id in TimeGaol:
        await ctx.send(
            embed=_util.ComposeEmbed(
                0xFF0000, "Invo", "You are already occupied with something else."
            )
        )
        return
    e: discord.Embed = _util.ComposeEmbed(0xFFFFFF, "Invo", "You start training...")
    data = Database.GetUserData(ctx.author)
    TimeGaol.append(ctx.author.id)
    await asyncio.sleep(7200)
    TimeGaol.remove(ctx.author.id)
    xpr: int = random.randint(500 * data.level, 1000 * level)
    reward: discord.Embed = _util.ComposeEmbed(
        0x00FF00, "Invo", "{} finishes their training!".format(ctx.author.name)
    )
    reward.add_field(name="+{}xp".format(xpr), value="Congratulations", inline=False)
    data.UpdateXP(xpr)
    await ctx.send(embed=reward)


@client.command()
async def equip(
    ctx, invslot: int
):  # Equip an item from your inventory, by replacing the slots
    global Database
    data = Database.GetUserData(ctx.author)
    item = data.inventory[invslot]
    if item.slot == 0:
        tmpitem = data.weapon
        data.weapon = item
        data.inventory[invslot] = tmpitem
    else:
        tmpitem = data.armor
        data.armor = item
        data.inventory[invslot] = tmpitem
    e: discord.Embed = _util.ComposeEmbed(
        0x00FF00, "Invo", "You have equipped the {} +{}".format(item.name, item.tier)
    )
    await ctx.send(embed=e)


@client.command()
async def upgrade(
    ctx, invslot: int
):  # Upgrade an item in your inventory with materials
    global Database
    data = Database.GetUserData(ctx.author)
    item = data.inventory[invslot]
    if item.tier <= 5:
        material = "α-Crystal"
        amount = item.tier * 5 if item.tier != 0 else 5
        if data.materials[material] < amount:
            await ctx.send(
                embed=_util.ComposeEmbed(
                    0xFF0000,
                    "Invo",
                    "You need {} {}s to upgrade this item to tier {}".format(
                        amount, material, item.tier + 1
                    ),
                )
            )
        else:
            data.inventory[invslot].Upgrade()
            data.materials[material] -= amount
            await ctx.send(
                embed=_util.ComposeEmbed(
                    0x00FF00,
                    "Invo",
                    "You successfully upgraded to tier {} for {} {}s".format(
                        item.tier, amount, material
                    ),
                )
            )
    elif item.tier > 5 and item.tier <= 10:
        material = "γ-Ore"
        amount = item.tier * 4
        if data.materials[material] < amount:
            await ctx.send(
                embed=_util.ComposeEmbed(
                    0xFF0000,
                    "Invo",
                    "You need {} {}s to upgrade this item to tier {}".format(
                        amount, material, item.tier + 1
                    ),
                )
            )
        else:
            data.inventory[invslot].Upgrade()
            data.materials[material] -= amount
            await ctx.send(
                embed=_util.ComposeEmbed(
                    0x00FF00,
                    "Invo",
                    "You successfully upgraded to tier {} for {} {}s".format(
                        item.tier, amount, material
                    ),
                )
            )
    elif item.tier > 10 and item.tier <= 15:
        material = "ε-Sand"
        amount = item.tier * 3
        if data.materials[material] < amount:
            await ctx.send(
                embed=_util.ComposeEmbed(
                    0xFF0000,
                    "Invo",
                    "You need {} {}s to upgrade this item to tier {}".format(
                        amount, material, item.tier + 1
                    ),
                )
            )
        else:
            data.inventory[invslot].Upgrade()
            data.materials[material] -= amount
            await ctx.send(
                embed=_util.ComposeEmbed(
                    0x00FF00,
                    "Invo",
                    "You successfully upgraded to tier {} for {} {}s".format(
                        item.tier, amount, material
                    ),
                )
            )
    elif item.tier > 15 and item.tier <= 25:
        material = "λ-Steel"
        amount = item.tier * 2
        if data.materials[material] < amount:
            await ctx.send(
                embed=_util.ComposeEmbed(
                    0xFF0000,
                    "Invo",
                    "You need {} {}s to upgrade this item to tier {}".format(
                        amount, material, item.tier + 1
                    ),
                )
            )
        else:
            data.inventory[invslot].Upgrade()
            data.materials[material] -= amount
            await ctx.send(
                embed=_util.ComposeEmbed(
                    0x00FF00,
                    "Invo",
                    "You successfully upgraded to tier {} for {} {}s".format(
                        item.tier, amount, material
                    ),
                )
            )
    elif item.tier > 25 and item.tier <= 50:
        material = "ω-Essence"
        amount = item.tier
        if data.materials[material] < amount:
            await ctx.send(
                embed=_util.ComposeEmbed(
                    0xFF0000,
                    "Invo",
                    "You need {} {}s to upgrade this item to tier {}".format(
                        amount, material, item.tier + 1
                    ),
                )
            )
        else:
            data.inventory[invslot].Upgrade()
            data.materials[material] -= amount
            await ctx.send(
                embed=_util.ComposeEmbed(
                    0x00FF00,
                    "Invo",
                    "You successfully upgraded to tier {} for {} {}s".format(
                        item.tier, amount, material
                    ),
                )
            )
    else:
        await ctx.send(
            embed=_util.ComposeEmbed(
                0xFF0000, "Invo", "Your item is already at its maximum upgrade level."
            )
        )


# Admin commands:
@client.command()
@commands.has_permissions(administrator=True)  # Debug
async def dump(ctx):
    global Database, XpCooldown, DailyCooldown, TimeGaol
    for user in Database.internal:
        _util.DBUG(_user.pack(user))
    _util.DBUG("XPC: {}".format(XpCooldown))
    _util.DBUG("DC: {}".format(DailyCooldown))
    _util.DBUG("TG: {}".format(TimeGaol))


@client.command()
@commands.has_permissions(administrator=True)
async def save(ctx):
    global Database
    Database.Save()


#
## EOF
### Only have the client.run below this line

client.run(TOKEN)
