"""This is a cog for a discord.py bot.
It drops random cheese for people to pick up
"""
import random
from datetime import datetime as dt
from discord.ext import commands
from discord import Activity, DMChannel


class Cheese(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, client):
        self.client = client
        self.last_cheese = dt.utcnow()
        self.cheese_weight = (100 - self.client.config.get("cheese_weight", 50), 100)
        self.cooldown = 30
        self.msg_memory = dict()
        random.seed()

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author.bot:
            return
        if isinstance(msg.channel, DMChannel):
            # Ignore DM
            return

        chance_result = random.choices([0,1], cum_weights=self.cheese_weight)[0]
        self.client.log.debug(f"{chance_result=}")
        if chance_result:
            #if (dt.utcnow() - self.last_cheese).total_seconds() < self.cooldown:
            #    return
            if (msg_id := msg.id) in self.msg_memory.keys():
                return
            self.msg_memory[msg_id] = ""
            await msg.add_reaction('🧀')
            message = 'A wild cheese appeared!'
            await msg.channel.send(message)
            self.last_cheese = dt.utcnow()


def setup(client):
    """This is called when the cog is loaded via load_extension"""
    client.add_cog(Cheese(client))

