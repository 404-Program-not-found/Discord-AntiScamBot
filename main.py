from abc import ABC

from discord.ext import commands
import discord

intents = discord.Intents.default()
startup_extensions = ["Moderation", "Help"]

guild_ids_list = ["ID HERE"]  # integer Only


class ScamBot(commands.Bot, ABC):
    def __init__(self):
        super().__init__(intents=intents, command_prefix=commands.when_mentioned_or("!"), help_command=None)

    async def on_ready(self):
        for extension in startup_extensions:
            try:
                bot.load_extension(extension)
                print('{} Loaded!'.format(extension))
            except Exception as e:
                exc = '{}: {}'.format(type(e).__name__, e)
                print('Failed to load extension {}\n{}'.format(extension, exc))
        print('Logged in as')
        print(bot.user.name)
        print(bot.user.id)
        print('------')


bot = ScamBot()

# Slash commands. To use guild_id_list, add the guild_ids=guild_ids_list argument to every @bot.slash_command

@commands.is_owner()
@bot.slash_command(hidden=True)
async def load(ctx, extension_name: str):
    try:
        bot.load_extension(extension_name)
    except (AttributeError, ImportError, discord.ExtensionNotFound, discord.ExtensionAlreadyLoaded) as e:
        await ctx.respond("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
        return
    await ctx.respond("{} loaded.".format(extension_name))


@commands.is_owner()
@bot.slash_command(hidden=True)
async def unload(ctx, extension_name: str):
    try:
        bot.unload_extension(extension_name)
    except (AttributeError, ImportError, discord.ExtensionNotFound, discord.ExtensionNotLoaded) as e:
        await ctx.respond("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
        return
    await ctx.respond("{} unloaded.".format(extension_name))


@commands.is_owner()
@bot.slash_command(hidden=True)
async def reload(ctx, extension_name: str):
    try:
        bot.reload_extension(extension_name)
    except (AttributeError, ImportError, discord.ExtensionNotLoaded) as e:
        await ctx.respond("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
        return
    await ctx.respond("{} reloaded.".format(extension_name))


if __name__ == "__main__":
    bot.run('Bot Token Here')
