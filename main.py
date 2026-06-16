# build: python3.12 clean rebuild
import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from config import *

import os
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.dm_messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Store appeals temporarily
appeals = {}

# ------------------ !see COMMAND ------------------
@bot.command()
async def see(ctx):

    embed = discord.Embed(
        title="Roblox Fans Ban Appeals",
        description="""
**Welcome to Roblox Fans Ban Appeals**

**How To Appeal:**
To appeal your ban, click the button attached to this message and submit the required information. You must appeal using the account that you were banned on; you will not be able to access the appeal form if your current account is not banned from Roblox Fans.

**After You Appeal:**
Your appeal will be sent to and reviewed by our moderators. If you are not unbanned 3 days after appealing, your appeal has been denied, but you are free to reappeal. Asking staff to read or accept your appeal will result in an immediate denial of your appeal.

**If Your Appeal Is Accepted:**
You will be notified via DMs and <#1393807581541044264> and will be given the @Unbanned role. If you have been unbanned but are still unable to rejoin Roblox Fans after 30 minutes, you may request support by dming any staffs or admins. If you choose to stay in this server after rejoining Roblox Fans, your @Unbanned role will be automatically removed.
"""
    )

    view = AppealView()
    await ctx.send(embed=embed, view=view)

# ------------------ APPEAL BUTTON ------------------
class AppealView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Click To Appeal", style=discord.ButtonStyle.primary)
    async def appeal(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.send_message(
            "I sent you a DM with the appeal form.",
            ephemeral=True
        )

        questions = [
            "Why were you banned?",
            "What did you do wrong?",
            "Why should we unban you?",
            "What's your Discord username?"
        ]

        answers = []

        try:
            dm = await interaction.user.create_dm()

            for q in questions:
                await dm.send(q)

                def check(m):
                    return m.author.id == interaction.user.id and isinstance(m.channel, discord.DMChannel)

                msg = await bot.wait_for("message", check=check, timeout=600)
                answers.append(msg.content)

            # Save appeal
            appeals[interaction.user.id] = answers

            admin_channel = bot.get_channel(ADMIN_CHANNEL_ID)

            embed = discord.Embed(title="New Ban Appeal")
            for q, a in zip(questions, answers):
                embed.add_field(name=q, value=a, inline=False)

            view = ReviewView(interaction.user.id)

            await admin_channel.send(embed=embed, view=view)

        except asyncio.TimeoutError:
            await dm.send("You took too long. Appeal cancelled.")

# ------------------ ADMIN REVIEW BUTTONS ------------------
class ReviewView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=None)
        self.user_id = user_id

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.success)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):

        user = await bot.fetch_user(self.user_id)

        try:
            await user.send(
                f"Congratulations! You've been Unbanned from Roblox Fans Server, you may rejoin the server at {SERVER_INVITE}"
            )
        except:
            pass

        channel = bot.get_channel(ANNOUNCEMENT_CHANNEL_ID)
        await channel.send(f"🎉 Congratulations! {user.name} has been Unbanned from Roblox Fans!")

        await interaction.response.send_message("Approved.", ephemeral=True)

    @discord.ui.button(label="Deny", style=discord.ButtonStyle.danger)
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):

        user = await bot.fetch_user(self.user_id)

        try:
            await user.send(
                "Sorry but your appeal has been denied. You may reappeal sometime later."
            )
        except:
            pass

        await interaction.response.send_message("Denied.", ephemeral=True)

# ------------------ BOT READY ------------------
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

bot.run(TOKEN)
