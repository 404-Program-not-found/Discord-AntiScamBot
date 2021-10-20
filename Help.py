import discord
from discord.ext import commands


class help(commands.Cog):
    def __init__(self, bot):
        bot.help_command = HelpClass()
        bot.help_command.cog = self


class HelpClass(commands.HelpCommand):

    def __init__(self):
        attrs = {
            "aliases": ["helpme", "halp"],
            "hidden": True
        }
        super().__init__(command_attrs=attrs, verify_checks=False)

    async def send_command_help(self, command):
        embed = discord.Embed(title=command.qualified_name, color=0x0084ff)
        if command.help:
            embed.add_field(name="Description", value=command.help)
        embed.add_field(name="Usage", value=f"`{self.get_command_signature(command)}`", inline=False)
        alias = command.aliases
        if alias:
            embed.add_field(name="Aliases", value=", ".join(alias), inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)

    def get_command_signature(self, command):
        return '%s%s %s' % (self.context.clean_prefix, command.qualified_name, command.signature)

    async def send_bot_help(self, mapping):
        embed = discord.Embed(title=f"Command List", color=0x0084ff)
        for cog, commands in mapping.items():
            filtered = await self.filter_commands(commands, sort=True)
            command_signatures = [self.get_command_signature(c) for c in filtered]
            if command_signatures:
                cog_name = getattr(cog, "qualified_name", "No Category")
                embed.add_field(
                    name=cog_name.title(),
                    value=f"`{self.context.clean_prefix}help {cog_name}`", inline=True)

        channel = self.get_destination()
        await channel.send(embed=embed)

    async def send_cog_help(self, cog):
        embed = discord.Embed(
            title=cog.qualified_name.title(),
            color=0x0084ff)
        filtered = await self.filter_commands(cog.walk_commands(), sort=True)
        if filtered:
            for command in filtered:
                embed.add_field(name=command, value=f"`{self.context.clean_prefix}help {command.qualified_name}`",
                                inline=True)
            channel = self.get_destination()
            await channel.send(embed=embed)
        else:
            await self.send_error_message("Cog not found or is empty")

    async def send_error_message(self, error):
        embed = discord.Embed(title="Error", description=error, colour=0xff0033)
        channel = self.get_destination()
        await channel.send(embed=embed)


def setup(bot):
    bot.add_cog(help(bot))
