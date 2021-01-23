import json
import sys
import os
import Lib.util as _util
import Lib.user as _user
import Lib.item as _item
import discord


class Backend:
    def __init__(self):
        self.internal: list = []

    def GetToken(self) -> str:
        t: str = ""
        with open(_util.TokenPath, "r") as tfile:
            t = tfile.read()
            t.strip()
        return t

    def Load(self):
        # Log that we're overwriting savedata if the internal memory is not empty (Loaded outside of startup)
        if len(self.internal) != 0:
            _util.WARN(
                "Loading memory but internal is not empty, internal storage overwritten."
            )
        # Read the persistent json db
        with open(_util.StoragePath, "r") as persistent:
            self.internal = list(json.load(persistent))
        # Check that we loaded successfully
        if len(self.internal) != 0:
            _util.INFO("Loaded persistent data!")
        # Report an error if loading was unsuccessful
        else:
            _util.ERROR("Failed to load persistent data!")
        for user in self.internal:
            self.internal[self.internal.index(user)] = _user.unpack(user)

    def Save(self):
        # Report an error if we're saving an empty state
        if len(self.internal) == 0:
            _util.ERROR("Attempted to save, but internal is empty!")
        # Pack userdata before storage
        _util.INFO("Packing ...")
        for user in self.internal:
            self.internal[self.internal.index(user)] = _user.pack(user)
        # Save to persistent storage
        _util.INFO("Writing ...")
        with open(_util.StoragePath, "w") as persistent:
            json.dump(self.internal, persistent)
        # Unpack after storage
        _util.INFO("Unpacking ...")
        for user in self.internal:
            self.internal[self.internal.index(user)] = _user.unpack(user)
        _util.INFO("Save complete!")

    def RegisterUser(self, user: discord.User) -> None:
        u: _user.User = _user.User(user.id)
        u.NewUser()
        self.internal.append(u)
        self.Save()
        _util.INFO("Registered user {}@{}".format(user.name, user.id))

    def GetUserData(self, user: discord.User) -> _user.User:
        for _user in self.internal:
            if _user.id == user.id:
                return _user
        _util.WARN(
            "Attempted to get user data from unknown user ({} / {})".format(
                user.name, user.id
            )
        )
        return None
