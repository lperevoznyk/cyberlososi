import discord
from discord.ext import commands


class Permissions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # permissions storage: {'command_name': set(['role_name1', 'role_name2'])}
        self.command_permissions = {}

    def has_permission(self, ctx):
        if ctx.author.guild_permissions.administrator:
            return True  # Admin bypass
        allowed_roles = self.command_permissions.get(ctx.command.name, set())
        return any(role.name in allowed_roles for role in ctx.author.roles)

    async def cog_check(self, ctx):
        return self.has_permission(ctx)

    @commands.command(name="allow_role",
                      usage="<command> <role>",
                      help="Allow a role to use a specific command.")
    @commands.has_permissions(administrator=True)
    async def allow_role(self, ctx, command_name: str, *, role: discord.Role):
        if command_name not in self.bot.all_commands:
            await ctx.send(f"⚠️ Command `{command_name}` not found.")
            return
        self.command_permissions.setdefault(command_name, set()).add(role.name)
        await ctx.send(f"✅ Role {role.mention} can now use `{command_name}` command.")

    @commands.command(name="remove_role",
                      usage="<command> <role>",
                      help="Remove a role's access to a specific command.")
    @commands.has_permissions(administrator=True)
    async def remove_role(self, ctx, command_name: str, *, role: discord.Role):
        roles = self.command_permissions.get(command_name, set())
        if role.name in roles:
            roles.remove(role.name)
            await ctx.send(f"❌ Role {role.mention} can no longer use `{command_name}` command.")
        else:
            await ctx.send(f"⚠️ Role {role.mention} wasn't assigned to `{command_name}`.")

    @commands.command(name="list_roles",
                      usage="<command>",
                      help="List roles allowed for a specific command.")
    @commands.has_permissions(administrator=True)
    async def list_roles(self, ctx, command_name: str):
        roles = self.command_permissions.get(command_name, set())
        if roles:
            roles_mentions = [discord.utils.get(ctx.guild.roles, name=r).mention for r in roles]
            await ctx.send(f"📌 Roles allowed for `{command_name}`: {', '.join(roles_mentions)}")
        else:
            await ctx.send(f"No roles assigned yet for `{command_name}`. (Admin only)")


def setup(bot):
    bot.add_cog(Permissions(bot))
