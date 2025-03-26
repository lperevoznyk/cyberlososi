import discord
from discord.ext import commands


class CustomHelp(commands.HelpCommand):

    async def send_bot_help(self, mapping):
        embed = discord.Embed(title="📚 All Available Commands", color=discord.Color.blue())

        for cog, commands_list in mapping.items():
            commands_info = ""
            for cmd in commands_list:
                if cmd.hidden:
                    continue  # skip hidden commands
                usage = f" {cmd.usage}" if cmd.usage else ""
                aliases = f" (Aliases: {', '.join(cmd.aliases)})" if cmd.aliases else ""
                description = cmd.help or "No description provided."
                commands_info += f"`{self.context.prefix}{cmd.name}{usage}`{aliases}\n{description}\n\n"

            if commands_info:
                cog_name = getattr(cog, "qualified_name", "General")
                embed.add_field(name=f"**{cog_name}**", value=commands_info, inline=False)

        await self.context.send(embed=embed)

    async def send_command_help(self, command):
        embed = discord.Embed(title=f"🔹 Command: {self.context.prefix}{command.name}",
                              description=command.help or "No description provided.",
                              color=discord.Color.green())
        if command.usage:
            embed.add_field(name="Usage", value=f"`{self.context.prefix}{command.name} {command.usage}`", inline=False)
        if command.aliases:
            embed.add_field(name="Aliases", value=", ".join(command.aliases), inline=False)
        await self.context.send(embed=embed)

    async def send_error_message(self, error):
        await self.context.send(f"⚠️ {error}")


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.help_command = CustomHelp()
        bot.help_command.cog = self

    @commands.command(name="permcheck")
    async def permcheck(self, ctx: commands.Context):
        permissions = ctx.channel.permissions_for(ctx.guild.me)
        missing = [perm for perm, value in permissions if not value]
        await ctx.send(f"Missing Permissions: {', '.join(missing)}")


def setup(bot):
    bot.add_cog(Help(bot))
