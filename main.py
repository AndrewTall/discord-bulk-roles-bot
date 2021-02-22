#!/usr/bin/python

import asyncio
import discord
from discord.ext import commands
import os

token = os.getenv('BOT_TOKEN')
prefix = os.getenv('BOT_PREFIX')
if not prefix:
    prefix = '!'
full_prefix = '{}bulkroles '.format(prefix)
channel_id = os.getenv('ADMIN_CHANNEL_ID')


if not token:
    raise RuntimeError('<BOT_TOKEN> environment variable is not set')


if not channel_id:
    raise RuntimeError('<ADMIN_CHANNEL_ID> environment variable is not set')
else:
    try:
        channel_id = int(channel_id)
    except:
        raise RuntimeError('Invalid <ADMIN_CHANNEL_ID> environment variable: should be number')


def is_correct_channel(ctx: commands.Context):
    return ctx.channel.id == channel_id


async def check_permissions(ctx: commands.Context):
    if not ctx.message.channel.guild.me.guild_permissions.manage_roles:
        await ctx.message.reply('Sorry, it seems that I have no permissions to manage roles!')
        raise commands.errors.CommandInvokeError('no <manage_roles> permission')


async def check_arguments(ctx: commands.Context, role: discord.Role, members: commands.Greedy[discord.Member]):
    if role is None:
        await ctx.message.reply('Please specify role')
        raise commands.errors.CommandInvokeError('no <role> argument')
    elif members is None:
        await ctx.message.reply('Please specify members')
        raise commands.errors.CommandInvokeError('no <members> argument')


client = commands.Bot(command_prefix=full_prefix)


@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.idle, activity=discord.Game('Listening to {}help'.format(full_prefix)))
    print('I am online')


@client.event
async def on_command_error(ctx: commands.Context, error: str):
    await ctx.message.reply('Unknown error!\nPlease check my role is above any user roles in server settings.\nOtherwise contact developer.')
    print(error)


@commands.check(is_correct_channel)
@client.command(brief='Add role to each member in list')
async def add(ctx: commands.Context, role: discord.Role=None, members: commands.Greedy[discord.Member]=None):
    await check_arguments(ctx, role, members)
    await check_permissions(ctx)
    async with ctx.typing():
        members_with_role = []
        for member in members:
            if role in member.roles:
                members_with_role.append(member.name)
            else:
                await member.add_roles(role)
                await asyncio.sleep(1)
        message = 'Done!'
        if len(members_with_role) > 0:
            message += '\nNext users already have this role, skipping: {}'.format(', '.join(members_with_role))
        await ctx.message.reply(message)


@commands.check(is_correct_channel)
@client.command(brief='Remove role from each member in list')
async def remove(ctx: commands.Context, role: discord.Role, members: commands.Greedy[discord.Member]):
    await check_arguments(ctx, role, members)
    await check_permissions(ctx)
    async with ctx.typing():
        members_without_role = []
        for member in members:
            if role not in member.roles:
                members_without_role.append(member.name)
            else:
                await member.remove_roles(role)
                await asyncio.sleep(1)
        message = 'Done!'
        if len(members_without_role) > 0:
            message += '\nNext users do not have this role, skipping: {}'.format(
                ', '.join(members_without_role))
        await ctx.message.reply(message)

client.run(token)
