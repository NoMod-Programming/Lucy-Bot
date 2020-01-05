#!/usr/bin/env python3
"""
lucy.py - A Discord bot that proxies messages through Kik. 

I made this because the kik app kept crashing for me on
iOS 12.4 on an iPhone 6, and it was becoming a hassle to
use.
"""
# Discord imports
import discord
import requests
import asyncio

# Kik imports
import logging
import threading
import time
from kik_unofficial.client import KikClient
from kik_unofficial.callbacks import KikClientCallback
from kik_unofficial.datatypes.peers import User
from kik_unofficial.datatypes.xmpp.chatting import IncomingChatMessage, IncomingGroupChatMessage, IncomingStatusResponse, IncomingGroupStatus
from kik_unofficial.datatypes.xmpp.roster import FetchRosterResponse, PeersInfoResponse
from kik_unofficial.datatypes.xmpp.login import ConnectionFailedResponse
from kik_unofficial.datatypes.xmpp.errors import LoginError

# Get our discord token, and kik credentials.
from secret import DISCORD_TOKEN, KIK_USERNAME, KIK_PASSWORD


users = {}

discordClient = None
kikClient = None

class KikChatClient(KikClientCallback):

    def on_authenticated(self):
        print("Authenticated with Kik")

    def on_roster_received(self, response: FetchRosterResponse):
        for m in response.peers:
            if m:
                users[m.jid] = m

    def on_chat_message_received(self, chat_message: IncomingChatMessage):
        kikClient.add_friend(chat_message.from_jid)
        kikClient.request_info_of_users(chat_message.from_jid)
        time.sleep(1)
        print("{}: {}".format(jid_to_username(chat_message.from_jid), chat_message.body))
        discord_fut = asyncio.run_coroutine_threadsafe(discordClient.post_direct_message(chat_message), discordClient.loop)
        discord_fut.result()

    def on_group_message_received(self, chat_message: IncomingGroupChatMessage):
        kikClient.request_info_of_users(chat_message.from_jid)
        kikClient.request_roster()
        time.sleep(1)
        print("{} - {}: {}".format(users[chat_message.group_jid].name, jid_to_username(chat_message.from_jid),
                                   jid_to_username(chat_message.body)))
        discord_fut = asyncio.run_coroutine_threadsafe(discordClient.post_group_message(chat_message), discordClient.loop)
        discord_fut.result()

    def on_connection_failed(self, response: ConnectionFailedResponse):
        print("Connection failed")

    def on_status_message_received(self, response: IncomingStatusResponse):
        print(response.status)
        kikClient.add_friend(response.from_jid)

    def on_group_status_received(self, response: IncomingGroupStatus):
        kikClient.request_info_of_users(response.status_jid)

    def on_login_error(self, login_error: LoginError):
        if login_error.is_captcha():
            login_error.solve_captcha_wizard(kikClient)
    
    def on_peer_info_received(self, response: PeersInfoResponse):
        for m in response.users:
            users[m.jid] = m

def jid_to_username(jid):
    return jid.split('@')[0][0:-4]

class LucyBot(discord.Client):
    """
    The main class that handles interactions with the Lucy bot
    """
    async def on_ready(self):
        print("Logged in as ", self.user)

    async def on_message(self, message):
        if message.author.bot:
            return
        chat_jid = await self.getChatForChannel(message.channel)
        if chat_jid is None:
            return

        kikClient.send_chat_message(chat_jid, message.content)
        print("{} - Sent message \"{}\"".format(chat_jid, message.content))

    async def post_direct_message(self, kik_message):
        # Post a message received by the kik client to the discord server
        webhook = await self.getWebhookForChat(kik_message.from_jid)
        discord_msg = {}
        discord_msg['username'] = users[kik_message.from_jid].display_name
        discord_msg['content'] = kik_message.body
        discord_msg['avatar_url'] = users[kik_message.from_jid].pic + "/orig.jpg"
        await webhook.send(**discord_msg)

    async def post_group_message(self, kik_message):
        # Post a message received by the kik client to the discord server
        webhook = await self.getWebhookForChat(kik_message.group_jid)
        discord_msg = {}
        discord_msg['username'] = users[kik_message.from_jid].display_name
        discord_msg['content'] = kik_message.body
        discord_msg['avatar_url'] = users[kik_message.from_jid].pic + "/orig.jpg"
        await webhook.send(**discord_msg)

    async def getWebhookForChat(self, jid):
        guild = self.guilds[0]
        webhooks = await guild.webhooks()
        for wh in webhooks:
            if wh.name == jid:
                return wh
        # Make a new channel and webhook for it
        category = None
        for cat in guild.categories:
            if cat.name.lower() == "kik chats":
                category = cat
                break
        else:
            category = await guild.create_category("kik chats")
        channel_name = users[jid].username if type(users[jid]) == User else users[jid].name
        if not channel_name:
            channel_name = "Misc. Chat"
        chan = await guild.create_text_channel(channel_name, topic=jid, category=category)
        wh = await chan.create_webhook(name=jid)
        return wh

    async def getChatForChannel(self, channel):
        if not channel.category.name.lower() == "kik chats":
            # Not a kik chat
            return None
        return channel.topic
        

def startKikClient():
    global kikClient
    asyncio.set_event_loop(asyncio.new_event_loop())
    callback = KikChatClient()
    kikClient = KikClient(callback=callback, kik_username=KIK_USERNAME, kik_password=KIK_PASSWORD, log_level=logging.WARNING)

if __name__ == '__main__':
    # The kik and discord clients both try and use the same event loop.
    # So as a bit of a hack to get it working, just run the kik one in a
    # different thread.
    threading.Thread(target=startKikClient).start()
    discordClient = LucyBot()
    discordClient.run(DISCORD_TOKEN)
