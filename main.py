import discord
import asyncio

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
active_ghostping_tasks = {}

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
