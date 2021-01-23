import discord
import colorama
from colorama import init
from colorama import Fore as f
from colorama import Back as b
from colorama import Style as st

init()

StoragePath: str = "Data/userdata.json"
TokenPath: str = "token.dat"


def WARN(s: str) -> None:
    print(f.YELLOW + st.BRIGHT + "Warning!\t{}".format(s) + st.RESET_ALL)


def INFO(s: str) -> None:
    print(f.GREEN + st.BRIGHT + "Info\t\t{}".format(s) + st.RESET_ALL)


def DBUG(s: str) -> None:
    print(f.BLUE + st.BRIGHT + "#DEBUG#\t\t{}".format(s) + st.RESET_ALL)


def LOG(s: str) -> None:
    print(f.MAGENTA + st.BRIGHT + "Log\t\t{}".format(s) + st.RESET_ALL)


def ERROR(s: str) -> None:
    print(f.RED + st.BRIGHT + "ERROR!\t\t{}".format(s.upper()) + st.RESET_ALL)


def ComposeEmbed(clr, name, value) -> discord.Embed:
    e: discord.Embed = discord.Embed(title=name, description=value, color=clr)
    return e
