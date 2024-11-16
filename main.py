import discord

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

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
