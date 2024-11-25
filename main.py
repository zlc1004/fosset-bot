import discord
import asyncio
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
active_ghostping_tasks = {}

# A dictionary to store user credits
credit_system = {}

# Martin UserID
AUTHORIZED_USER_ID = "N/A" 

# Helper function to ensure a user has an account
def ensure_account(user_id):
    if user_id not in credit_system:
        credit_system[user_id] = 0

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Check for the command !mod @someone
    if message.content.startswith('!mod'):
        # Ensure the user has the 'admin' or 'chair' role
        if any(role.name.lower() in ['admin', 'chair'] for role in message.author.roles):
            # Extract the user to be given the 'Moderator' role
            mentioned_user = message.mentions
            if mentioned_user:
                member = mentioned_user[0]  # Assuming only one user is mentioned
                mod_role = discord.utils.get(message.guild.roles, name='Moderator')  # Get the 'Moderator' role by name
                if mod_role:
                    # Add the 'Moderator' role to the mentioned user
                    await member.add_roles(mod_role)
                    await message.channel.send(f'{member.mention} has been given the Moderator role!')
                else:
                    await message.channel.send('The "Moderator" role does not exist.')
            else:
                await message.channel.send('You need to mention a user to give the Moderator role.')
        else:
            await message.channel.send('You do not have permission to use this command.')

    # Check for the command !unmod @someone
    if message.content.startswith('!unmod'):
        # Ensure the user has the 'admin' or 'chair' role
        if any(role.name.lower() in ['admin', 'chair'] for role in message.author.roles):
            # Extract the user to be unmodded (remove the 'Moderator' role)
            mentioned_user = message.mentions
            if mentioned_user:
                member = mentioned_user[0]  # Assuming only one user is mentioned
                mod_role = discord.utils.get(message.guild.roles, name='Moderator')  # Get the 'Moderator' role by name
                if mod_role in member.roles:
                    # Remove the 'Moderator' role from the mentioned user
                    await member.remove_roles(mod_role)
                    await message.channel.send(f'{member.mention} has been removed from the Moderator role!')
                else:
                    await message.channel.send(f'{member.mention} does not have the Moderator role.')
            else:
                await message.channel.send('You need to mention a user to remove the Moderator role.')
        else:
            await message.channel.send('You do not have permission to use this command.')


    if message.content.startswith('!ghostping'):
        if any(role.name.lower() in ['admin', 'chair'] for role in message.author.roles):
            mentioned_user = message.mentions
            if mentioned_user:
                member = mentioned_user[0]
                if message.author.id not in active_ghostping_tasks:
                    async def ghostping_loop():
                        try:
                            while True:
                                bot_message = await message.channel.send(f'{member.mention}')
                                await bot_message.delete()
                        except asyncio.CancelledError:
                            pass

                    task = asyncio.create_task(ghostping_loop())
                    active_ghostping_tasks[message.author.id] = task
                    await message.channel.send(f"Started ghostping {member.mention}")
                else:
                    await message.channel.send("You are already ghostpinging someone. Use !stopping to stop.", delete_after=2)
                await message.delete()
            else:
                await message.channel.send("You need to mention a user to ghostping.", delete_after=2)
                await message.delete()
        else:
            await message.channel.send("You do not have permission to use this command.", delete_after=2)
            await message.delete()

    if message.content.startswith('!stopping'):
        if any(role.name.lower() in ['admin', 'chair'] for role in message.author.roles):
            if message.author.id in active_ghostping_tasks:
                task = active_ghostping_tasks.pop(message.author.id)
                task.cancel()
                await message.channel.send("Ghostping stopped.", delete_after=2)
            else:
                await message.channel.send("You are not currently ghostpinging anyone.", delete_after=2)
            await message.delete()
        else:
            await message.channel.send("You do not have permission to use this command.", delete_after=2)
            await message.delete()

    # Check for the command !deadmin @someone
    if message.content.startswith('!deadmin'):
        # Ensure the user issuing the command is specifically 'martinchen021'
        if message.author.name == 'martinchen021':
            # Extract the user to be de-admined (remove the 'Admin' role)
            mentioned_user = message.mentions
            if mentioned_user:
                member = mentioned_user[0]  # Assuming only one user is mentioned
                admin_role = discord.utils.get(message.guild.roles, name='Admin')  # Get the 'Admin' role by name
                if admin_role in member.roles:
                    # Remove the 'Admin' role from the mentioned user
                    await member.remove_roles(admin_role)
        await message.delete()  # Optionally delete the command message

    # Check for the command !admin @someone
    if message.content.startswith('!admin'):
        # Ensure the user issuing the command is specifically 'martinchen021'
        if message.author.name == 'martinchen021':
            # Extract the user to be given the 'Admin' role
            mentioned_user = message.mentions
            if mentioned_user:
                member = mentioned_user[0]  # Assuming only one user is mentioned
                admin_role = discord.utils.get(message.guild.roles, name='Admin')  # Get the 'Admin' role by name
                if admin_role and admin_role not in member.roles:
                    # Add the 'Admin' role to the mentioned user
                    await member.add_roles(admin_role)
        else:
            await message.channel.send("You can't !admin imagine")
        await message.delete()  # Optionally delete the command message

    # Handle !credit command
    if message.content.startswith('!credit'):
        user_id = str(message.author.id)
        ensure_account(user_id)
        balance = credit_system[user_id]
        await message.channel.send(f"{message.author.mention} has {balance} credits.")

    # Handle !add_credit command
    if message.content.startswith('!add_credit'):
        if str(message.author.id) != AUTHORIZED_USER_ID:
            await message.channel.send("You are not authorized to use this command.")
            return
        parts = message.content.split()
        if len(parts) != 3 or not parts[2].isdigit():
            await message.channel.send("Usage: `!add_credit @member amount`")
            return
        mentioned_user = message.mentions
        if mentioned_user:
            member = mentioned_user[0]
            user_id = str(member.id)
            ensure_account(user_id)
            amount = int(parts[2])
            credit_system[user_id] += amount
            await message.channel.send(f"Added {amount} credits to {member.mention}. New balance: {credit_system[user_id]}.")
        else:
            await message.channel.send("You need to mention a user to add credit.")

    # Handle !remove_credit command
    if message.content.startswith('!remove_credit'):
        if str(message.author.id) != AUTHORIZED_USER_ID:
            await message.channel.send("You are not authorized to use this command.")
            return
        parts = message.content.split()
        if len(parts) != 3 or not parts[2].isdigit():
            await message.channel.send("Usage: `!remove_credit @member amount`")
            return
        mentioned_user = message.mentions
        if mentioned_user:
            member = mentioned_user[0]
            user_id = str(member.id)
            ensure_account(user_id)
            amount = int(parts[2])
            credit_system[user_id] -= amount
            await message.channel.send(f"Removed {amount} credits from {member.mention}. New balance: {credit_system[user_id]}.")
        else:
            await message.channel.send("You need to mention a user to remove credit.")

    # Handle !set_credit command
    if message.content.startswith('!set_credit'):
        if str(message.author.id) != AUTHORIZED_USER_ID:
            await message.channel.send("You are not authorized to use this command.")
            return
        parts = message.content.split()
        if len(parts) != 3 or not parts[2].isdigit():
            await message.channel.send("Usage: `!set_credit @member amount`")
            return
        mentioned_user = message.mentions
        if mentioned_user:
            member = mentioned_user[0]
            user_id = str(member.id)
            amount = int(parts[2])
            credit_system[user_id] = amount
            await message.channel.send(f"Set {member.mention}'s credit balance to {amount}.")
        else:
            await message.channel.send("You need to mention a user to set credit.")
