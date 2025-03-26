from discord.ext import commands


class TextCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="progriv", help="This is a hello world command.")
    async def foo(self, ctx: commands.Context):
        await ctx.send("Анло купи баратрауму")


def setup(bot: commands.Bot):
    bot.add_cog(TextCommands(bot))
