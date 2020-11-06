"""This is a cog for a discord.py bot.
It drops random cheese for people to pick up
"""
from collections import defaultdict
from datetime import datetime as dt
from discord import Activity, Client, DMChannel, Embed, Message
from discord.ext import commands
import asyncio
import json
import random


class Cheese(commands.Cog, command_attrs=dict(hidden=True)):

    def __init__(self, client):
        self.client = client
        self.client.log.info("loading ze cheese!")
        self.DEBUG = self.client.config.get("debug", False)
        self.cheese_emoji = u"\U0001F9C0"
        self.thumbup_emoji = u"\U0001F44D"
        self.thumbdown_emoji = u"\U0001F44E"
        self.last_cheese = dt.utcnow()
        self.client.log.info(self.client.config)
        cheese_weight = self.client.config.get("cheese_weight")
        if not cheese_weight:
            cheese_weight = 30
            client.config["cheese_weight"] = cheese_weight
            client.config.save()
        self.cheese_weight = (100 - cheese_weight, 100)
        self.cooldown = 30
        self.store_file = 'cheese_store.json'
        self.scores = self.load_memory()
        random.seed()

    async def save_memory(self):
        try:
            with open(self.store_file, 'w', encoding='utf-8') as f:
                json.dump(dict(self.scores), f)
        except Exception as e:
            self.client.log.warning(f"Unable to save cheese memory! : {e}")
        finally:
            if self.DEBUG:
                self.client.log.info(f"{await self.list_current_store_users()}")

    async def list_current_store_users(self, limit=5):
        output = []
        counter = 1
        for k, v in sorted(self.scores.items(), key=lambda x: x[1], reverse=True):
            output.append(f"{counter}. {await self.client.fetch_user(int(k))}: {v}")
            if counter > limit:
                break
            counter += 1
        return output

    def load_memory(self):
        try:
            with open(self.store_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.client.log.warning(
                f"Unable to load cheese memory from file! : {e}")
            return defaultdict(int)

    async def add_cheese(self, client: Client, msg: Message):
        message = 'A wild cheese appeared!'
        await msg.channel.send(message)
        await msg.add_reaction(self.cheese_emoji)
        await msg.channel.send(await self.check_reaction(client, msg))

    async def check_reaction(self, client: Client, msg: Message):
        def check(reaction, user):
            return not user.bot \
                and msg.id == reaction.message.id \
                and str(reaction.emoji) == self.cheese_emoji
        message_store = ""
        try:
            reaction, user = await client.wait_for('reaction_add', timeout=60.0, check=check)
            self.scores[str(user.id)] += 1
            await self.save_memory()
            message_store += f"{self.thumbup_emoji} {user} collected the cheese!"
            return message_store
        except asyncio.TimeoutError:
            message_store += f"{self.thumbdown_emoji} nobody collected the cheese"
            return message_store

    @commands.Cog.listener()
    async def on_message(self, msg: Message):
        if msg.author.bot or isinstance(msg.channel, DMChannel):
            # Ignore DM or mesage from a bot
            return
        client = self.client
        chance_result = random.choices(
            [0, 1], cum_weights=self.cheese_weight)[0]
        client.log.debug(f"{chance_result=}")
        if chance_result:
            if (dt.utcnow() - self.last_cheese).total_seconds() < self.cooldown:
                return
            self.last_cheese = dt.utcnow()
            await self.add_cheese(client, msg)

    @commands.command()
    async def scores(self, ctx, *, limit=5):
        """Get cheese scores"""
        scores = "\n".join(await self.list_current_store_users())
        e = Embed(title='Cheese collected',
                  description=scores,
                  color=0xFF8000)
        await ctx.send(embed=e)


def setup(client):
    """This is called when the cog is loaded via load_extension"""
    client.add_cog(Cheese(client))
