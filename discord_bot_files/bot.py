import discord
import responses

async def send_message(message, user_message, is_private):
    try:
        response = responses.handle_response(user_message)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)

def run_discord_bot():
    TOKEN = 'MTA3MzEwODc1NTI2NjQwODQ0OA.GzdlXQ.5MFPwmg3-Ii_GtnG7xg2pgtGlW3Vhmp9-1HL2g'
    client = discord.Client()

    @client.event
    async def on_ready():
        print(f'{client.user} is now running!')
        
    @client.event
    async def on_message(message):
        # So bot doesn't take it's own output as input
        if message.author == client.user:
            return

        # For now, only work in #bot-testchannel
        if message.channel.name == 'bot-testchannel':

            # print(f"{message}")
            username = str(message.author)
            user_message = str(message.content)
            channel = str(message.channel)

            print(f"{username} said: '{user_message}' ({channel})")
            # print(f"{user_message[0:6]}")
            # print(f"{ user_message[7:]}")

            # If the user message contains '!marin' do something with bot
            if user_message[0:6] == '!marin':
                user_message = user_message[7:]  # [7:] Removes the '!marin '
                await send_message(message, user_message, is_private=False)

    client.run(TOKEN)