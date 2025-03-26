import discord
from discord.ext import commands
import sqlite3

from bot_config import config


class Permissions(commands.Cog):
    def __init__(self, bot, db_path: str = config.get('database', 'filename')):
        self.bot = bot
        self.db_path = db_path

        # Connect to (or create) the SQLite database
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

        # Create a table to store permissions if it doesn't exist
        # We'll store command_name and role_id for each allowed role.
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS command_permissions (
                command_name TEXT NOT NULL,
                role_id INTEGER NOT NULL
            )
        """)
        self.conn.commit()

        # Initialize in-memory dict: {'command_name': set([role_id, role_id, ...])}
        self.command_permissions = {}

        # Load any existing records from the database
        self._load_permissions_from_db()

    def _load_permissions_from_db(self):
        """Load all permissions from the database into self.command_permissions."""
        self.cursor.execute("SELECT command_name, role_id FROM command_permissions")
        rows = self.cursor.fetchall()
        for cmd_name, role_id in rows:
            if cmd_name not in self.command_permissions:
                self.command_permissions[cmd_name] = set()
            self.command_permissions[cmd_name].add(role_id)

    def _save_permission_to_db(self, command_name: str, role_id: int):
        """Insert a new (command_name, role_id) entry into the database."""
        self.cursor.execute(
            "INSERT INTO command_permissions (command_name, role_id) VALUES (?, ?)",
            (command_name, role_id)
        )
        self.conn.commit()

    def _remove_permission_from_db(self, command_name: str, role_id: int):
        """Remove the (command_name, role_id) entry from the database."""
        self.cursor.execute(
            "DELETE FROM command_permissions WHERE command_name = ? AND role_id = ?",
            (command_name, role_id)
        )
        self.conn.commit()

    def has_permission(self, ctx):
        # Administrators always bypass
        if ctx.author.guild_permissions.administrator:
            return True

        # Get roles allowed for this command
        allowed_role_ids = self.command_permissions.get(ctx.command.name, set())

        # Check if the user has at least one of the allowed roles
        return any(role.id in allowed_role_ids for role in ctx.author.roles)

    async def cog_check(self, ctx):
        """This is called by default before any command in this Cog is invoked."""
        return self.has_permission(ctx)

    @commands.command(name="allow_role",
                      usage="<command> <role>",
                      help="Allow a role to use a specific command.")
    @commands.has_permissions(administrator=True)
    async def allow_role(self, ctx, command_name: str, *, role: discord.Role):
        # Check command exists
        if command_name not in self.bot.all_commands:
            await ctx.send(f"⚠️ Command `{command_name}` not found.")
            return

        # Insert into the in-memory dict
        self.command_permissions.setdefault(command_name, set()).add(role.id)

        # Insert into the database
        self._save_permission_to_db(command_name, role.id)

        await ctx.send(f"✅ Role {role.mention} can now use `{command_name}` command.")

    @commands.command(name="remove_role",
                      usage="<command> <role>",
                      help="Remove a role's access to a specific command.")
    @commands.has_permissions(administrator=True)
    async def remove_role(self, ctx, command_name: str, *, role: discord.Role):
        roles = self.command_permissions.get(command_name, set())

        if role.id in roles:
            roles.remove(role.id)
            self._remove_permission_from_db(command_name, role.id)

            await ctx.send(f"❌ Role {role.mention} can no longer use `{command_name}` command.")
        else:
            await ctx.send(f"⚠️ Role {role.mention} wasn’t assigned to `{command_name}`.")

    @commands.command(name="list_roles",
                      usage="<command>",
                      help="List roles allowed for a specific command.")
    @commands.has_permissions(administrator=True)
    async def list_roles(self, ctx, command_name: str):
        role_ids = self.command_permissions.get(command_name, set())

        if role_ids:
            # Mention the roles in the server that match the stored role IDs
            mention_list = []
            for r_id in role_ids:
                role_obj = ctx.guild.get_role(r_id)
                if role_obj:  # if role still exists
                    mention_list.append(role_obj.mention)

            if mention_list:
                await ctx.send(f"📌 Roles allowed for `{command_name}`: {', '.join(mention_list)}")
            else:
                await ctx.send(f"No valid roles (still in guild) found for `{command_name}`.")
        else:
            await ctx.send(f"No roles assigned yet for `{command_name}`. (Admin only)")

    def cog_unload(self):
        """Called automatically when the cog is unloaded or the bot shuts down."""
        self.conn.close()


def setup(bot):
    bot.add_cog(Permissions(bot))
