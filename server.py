import discord
import asyncio
import dateparser
import datetime
import math
import sqlite3
from aiohttp import web

class Bot():
    def __init__(self, loop, client):
        self.alarms = []
        self.client = client
        self.connection = self.connect_to_database()

        client.event(self.on_message)
        client.event(self.on_ready)
        loop.create_task(self.alarm_checker(client))

    def check(message):
        try:
            int(message.content)
            return True
        except ValueError:
            return False

    async def on_message(self, message):
        if message.author == self.client.user:
            return

        if message.content.startswith('$hello'):
            await message.channel.send('Hello!')

        if message.content.startswith('test'):
            await message.channel.send('testing 123')

        if message.content.startswith('$timer'):
            timer = 0
            await message.channel.send('Understood!')
            await message.channel.send('Will be back in one minute!')

            await asyncio.sleep(60)
            await message.channel.send('One minute is up!')

        if message.content.startswith('$settimer'):
            # Example: $settimer in 5 minutes with message blabla

            author = message.author.name
            author_user_id = message.author.id
            channel_id = message.channel.id

            # This string delimits the beginning of a message associated with the timer
            timer_message_prefix = "with message"
            timer_message_prefix_index = message.content.find(timer_message_prefix)
            if timer_message_prefix_index != -1:
                when = message.content[len('$settimer'):timer_message_prefix_index].strip()
                timer_message = message.content[timer_message_prefix_index + len(timer_message_prefix):].strip()
            else: 
                when = message.content[len('$settimer'):].strip()
                timer_message = ''

            alarm_time = dateparser.parse(when)

            self.create_alarm(alarm_time, author, author_user_id, timer_message, channel_id)
            print('Timer set {} by {}'.format(when, author))

    def create_alarm(self, alarm_time, author, author_user_id, message, channel_id):
        c = self.connection.cursor()

        #@TODO sql injection protection with author name and message
        query = 'INSERT INTO timers VALUES ({}, {}, "{}", {}, "{}", {})'.format(
            math.floor(alarm_time.timestamp()),
            math.floor(datetime.datetime.now().timestamp()),
            author,
            int(author_user_id),
            message,
            int(channel_id)
        )
        c.execute(query)
        self.connection.commit()

    async def on_ready(self):
        print('We have logged in as {0.user}'.format(self.client))

    async def alarm_checker(self, client):
        c = self.connection.cursor()
        while True:
            now = math.floor(datetime.datetime.now().timestamp())

            c.execute('SELECT rowid, * FROM timers WHERE alarm_time <= {} ORDER BY alarm_time ASC'.format(now))
            for record in c.fetchall():
                author_user_id = int(record[4])
                message = record[5]
                channel = client.get_channel(int(record[6]))

                await channel.send('{}, <@{}>'.format(message, author_user_id))

            c.execute('DELETE FROM timers WHERE alarm_time <= {} '.format(now))
            self.connection.commit()

            await asyncio.sleep(60)
                

    def connect_to_database(self):
        connection = sqlite3.connect('timers.db')
        print('Connected to timer registry')

        c = connection.cursor()        
        c.execute('SELECT count(name) FROM sqlite_master WHERE type="table" AND name="timers"')

        # Create a table if it doesn't exist
        if c.fetchone()[0] == 0:
            c.execute('''CREATE TABLE timers
                     (
                        alarm_time timestamp,
                        created_at timestamp,
                        author text, 
                        author_user_id integer, 
                        message text, 
                        channel_id integer   
                    )''')

        return connection

    async def hello(self, request):
        c = self.connection.cursor()        
        c.execute('SELECT rowid, * FROM timers ORDER BY alarm_time ASC')
        for record in c.fetchall():
            data = [{'alarm_time': int(record[1]), 'created_at': int(record[2]), 'message': record[5], 'author': record[3]}]
            return web.json_response(data, headers={'Access-Control-Allow-Origin': 'http://localhost:3000'})


def main():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:

        client = discord.Client(loop=loop)

        bot = Bot(loop, client)

        api_server = web.Application()
        api_server.router.add_get('/timers', bot.hello)

        runner = web.AppRunner(api_server)
        loop.run_until_complete(runner.setup())
        site = web.TCPSite(runner)    
        loop.run_until_complete(site.start())

        client.run('NzUzMjQ5MjEyMDk1MDA0ODA0.X1jb_g.NMyBMC_PMqRfZxIfK3zCodF0WB4')
    finally:
        loop.close()

main()

