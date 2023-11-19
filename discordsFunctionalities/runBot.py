from .sendMessages import menu, on_ready, asin_isbn, getdataByLink, productReview
import discord
import os
import re


Token = os.getenv('MY_TOKEN')
intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents = intents)


def run_discord_bot():
    """
    Function to run the Discord bot. Registers the event handlers.
    """
    # Event handler for when the bot ready:
    @client.event
    async def initiation():
        await on_ready()
    # Event handler for when a message is received
    @client.event
    async def on_message(message):
        # Ignore messages ent by the bot itself:
        if message.author == client.user:
            return
        # Extract the username, user message, and channel from the message.
        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)
        print(f'{username} said: {user_message} {channel}.')
        # Define regular expressions to match the message:
        regex_pattern = r"""^hi|hello|hey|yo"""
        amazon_pattern = r'^!asin (https?://)?(www\.)?amazon\.(com|in|co\.uk|fr|com\.mx|com\.br|com\.au|co\.jp|se|de|it|com\.be)/.+'
        review_pattern = r"""^!rev https:\/\/www\.amazon\.(com|in|co\.uk|fr|com\.mx|com\.br|com\.au|co\.jp|se|de|it|com\.be)\/[^\s]+$"""
        info_pattern = r"""^!info https:\/\/www\.amazon\.(com|in|co\.uk|fr|com\.mx|com\.br|com\.au|co\.jp|se|de|it|com\.be)\/[^\s]+$"""

        # If the message is a greeting and is sent in a direct message:
        if message.guild is None and re.match(regex_pattern, message.content, re.IGNORECASE):
            await message.author.send(f"Hey {username}. Type '!general' or '!help' to know the overview of bot.")
        # If the message is !general and is sent in a direct message:
        elif message.content == '!commands':
            await menu(message.content, message.author)
        elif message.content == '!general' or message.content == '!help':
            await menu(message.content, message.author)
        elif message.content == '!about':
            await menu(message.content, message.author)
        elif message.content == '!ping':
            await menu(message.content, message.author, client)
        elif message.content == '!status':
            await menu(message.content, message.author)
        # If the message is an Amazon product link and is sent in a direct message:
        elif message.guild is None and re.search(amazon_pattern, user_message):
            url = user_message.split()[-1]
            await asin_isbn(url, message.author)
        # IF the message is an ASIN/ISBN and is sent in a direct message:
        elif message.guild is None and re.search(info_pattern, user_message):
            url = user_message.split()[-1]
            await message.author.send(f"Please wait. Fetching data from Amazon.")
            await getdataByLink(url, message.author)
        elif message.guild is None and (re.match(review_pattern, message.content)):
            url = user_message.split()[-1]
            await message.author.send(f"Please wait. Fetching reviews.")
            await productReview(url, message.author)
        else:
            await message.author.send(f"Invalid command. Type '!general | !help' or '!commands' to know the purpose of the bot.")
    # Run the client with the TOKEN:
    client.run(Token)

