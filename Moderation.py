import json
import re

from discord.ext import commands
from thefuzz import process


class moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Default Values. It is not recommended to edit this. Use the built-in commands instead
        self.defaultUpper = 98
        self.defaultLower = 88

    @commands.Cog.listener("on_message")
    async def phishing_detection(self, message):
        with open("database.json", "r") as f:
            master = json.load(f)
            detect = master.get("server_settings").get(str(message.guild.id))
        if detect and detect.get("detect_phishing"):
            links = re.findall(r'(https?://[^\s]+)', message.content)  # Find all links in a message
            if links and not message.author.bot:
                # Get Upper and Lower Bounds
                upper = detect.get("upper") or self.defaultUpper
                lower = detect.get("lower") or self.defaultLower

                links = [re.sub(r'https?://', '', s).split("/")[0].lower() for s in
                         links]  # Clean up link for better fuzzy match

                # Loops through every link to see if it is a suspected phishing domain
                for i in links:
                    extracted = process.extractOne(i, master["domain_whitelist"])
                    if upper >= extracted[1] >= lower:
                        await message.delete()  # Delete the Message
                        await message.channel.send(
                            f"{message.author.mention} **Uh Oh.**\n"
                            f"I detected a possible phishing link and have automatically removed it. "
                            f"Your link matched a known domain by {extracted[1]}%")  # Send a message to the author telling them that the message has been removed
                        break  # Stop looping as it is no longer necessary

    @commands.group(description="Main settings for moderation related commands and features")
    @commands.check_any(commands.has_guild_permissions(administrator=True))
    async def mod_settings(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid sub command passed')

    @mod_settings.command(
        description="Toggles the link detection feature. Off by default")
    async def toggle_link_detect(self, ctx):
        # Get the Database file
        with open('database.json', 'r') as f:
            channels = json.load(f)
            channels.setdefault("server_settings", {})
            settings = channels["server_settings"]

        settings.setdefault(str(ctx.guild.id), {})  # In case if the ctx.guild.id entry does not exist

        if not settings.get(str(ctx.guild.id)).get("detect_phishing"):
            settings[str(ctx.guild.id)]["detect_phishing"] = True
            await ctx.send(f'Phishing link detection is now **on**')

        elif settings.get(str(ctx.guild.id)).get("verify_channel"):
            settings[str(ctx.guild.id)]["detect_phishing"] = False
            await ctx.send(f'Phishing link detection is now **off**')

        # Save the edits
        with open('database.json', 'w') as f:
            channels["server_settings"] = settings
            json.dump(channels, f, indent=4)

    @mod_settings.command(
        description="Sets the upper bound for the detection algorithm in comparison to the similarity to any link (Default = 98).")
    async def set_upper_bound(self, ctx, number: int):
        with open('database.json', 'r') as f:
            channels = json.load(f)
            channels.setdefault("server_settings", {})
            settings = channels["server_settings"]

        settings.setdefault(str(ctx.guild.id), {})  # In case if the ctx.guild.id entry does not exist
        lower = settings[str(ctx.guild.id)].get("lower") or self.defaultLower  # Get the lower bound

        if lower <= number:
            ctx.send(f"Please select a number higher than {lower}")
            return

        settings[str(ctx.guild.id)]["upper"] = number
        await ctx.send(f"Upper bound is {number}")

        with open('database.json', 'w') as f:
            channels["server_settings"] = settings
            json.dump(channels, f, indent=4)

    @mod_settings.command(
        description="Sets the lower bound for the detection algorithm in comparison to the similarity to any link (Default = 88).")
    async def set_lower_bound(self, ctx, number: int):
        with open('database.json', 'r') as f:
            channels = json.load(f)
            channels.setdefault("server_settings", {})
            settings = channels["server_settings"]

        settings.setdefault(str(ctx.guild.id), {})  # In case if the ctx.guild.id entry does not exist
        upper = settings[str(ctx.guild.id)].get("upper") or self.defaultUpper  # Get the upper bound

        if upper <= number:
            ctx.send(f"Please select a number lower than {upper}")
            return

        settings[str(ctx.guild.id)]["lower"] = number
        await ctx.send(f"Lower bound is {number}")

        with open('database.json', 'w') as f:
            channels["server_settings"] = settings
            json.dump(channels, f, indent=4)


def setup(bot):
    bot.add_cog(moderation(bot))
