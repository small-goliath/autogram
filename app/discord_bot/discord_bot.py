import os
import re
import discord
from typing import List
from dotenv import load_dotenv
from collections import defaultdict
from datetime import datetime, timedelta, timezone

from app.database import Database
from app.logger import get_logger
from app.model.entity import ActionTarget


log = get_logger("discord_bot")
bot = discord.Bot(command_prefix="!")

limit_by_weeks = 3

def get_kst_now():
    return datetime.now(timezone(timedelta(hours=9)))

def get_date_range(weeks_ago: int):
    today = get_kst_now()
    start_date = (today - timedelta(days=today.weekday() + (7 * weeks_ago))).replace(hour=0, minute=0, second=0, microsecond=0)
    if weeks_ago == 0:
        end_date = today
    else:
        end_date = (today - timedelta(days=today.weekday() + (1 * weeks_ago))).replace(hour=0, minute=0, second=0, microsecond=0)
    return start_date, end_date

async def parse_messages(ctx: discord.ApplicationContext, weeks_ago: int):
    start_date, end_date = get_date_range(weeks_ago)
    message_pattern = re.compile(r"(.*?)\s*(https://www\.instagram\.com[^\s]+)")
    messages = [
        message async for message in ctx.history(limit=None, after=start_date, before=end_date)
    ]

    action_targets = []
    for message in messages:
        message_match = message_pattern.match(message.content)
        if message_match:
            action_targets.append(ActionTarget(
                username=message.author.name,
                link=message_match[2].strip(),
                monday=message.created_at.strftime("%Y-%m-%d"),
                sunday=message.created_at.strftime("%Y-%m-%d")
            ))
    return action_targets

@bot.slash_command(name="수집", description="지난주 품앗이 요청 수집.")
async def aggregate(ctx: discord.ApplicationContext,
                    weeks_ago: discord.Option(int, description="몇 주 전 메시지를 수집하시겠습니까?", default=1, min_value=1, max_value=4, required=True)):
    if not ctx.author.guild_permissions.administrator:
        await ctx.respond("이 명령어를 사용할 권한이 없습니다.", ephemeral=True)
        return
    
    action_targets = await parse_messages(ctx, weeks_ago)

    db = Database()
    db.save_action_targets(action_targets)

    await ctx.respond(f'{weeks_ago}주일 전의({start_date.strftime("%Y-%m-%d")} - {end_date.strftime("%Y-%m-%d")}) 메시지 수: {len(action_targets)}개')

@bot.slash_command(name="현황", description="품앗이 요청 현황을 조회합니다.")
async def status(ctx: discord.ApplicationContext,
                 weeks_ago: discord.Option(int, description="몇 주 전 메시지를 조회하시겠습니까?", default=1, min_value=0, max_value=4, required=True)):
    action_targets = await parse_messages(ctx, weeks_ago)

    if not action_targets:
        await ctx.respond(f"{weeks_ago}주일 전 품앗이 요청건이 없습니다.")
        return

    link_count_dict = defaultdict(list)

    for target in action_targets:
        link_count_dict[target.username].append(target.link)
    
    embeds: List[discord.Embed] = []
    for username, links in link_count_dict.items():
        embed = discord.Embed(color=discord.Colour.random(), description=f"{username}님의 {weeks_ago}주일 전 현황")
        embed.add_field(name="링크 수", value=f"{len(links)}개", inline=True)
        embed.add_field(name="링크", value="\n\n".join(links), inline=True)
        embeds.append(embed)

    for i in range(0, len(embeds), 10):
        chunk = embeds[i:i + 10]
        await ctx.respond(embeds=chunk)

@bot.slash_command(name="횟수수정", description="주당 제한 횟수 변경")
async def set_limit_by_weeks(ctx: discord.ApplicationContext,
                             limit: discord.Option(int, description="변경할 주당 제한 횟수를 입력해주세요.", default=3, min_value=1, required=True)):
    if not ctx.author.guild_permissions.administrator:
        await ctx.respond("이 명령어를 사용할 권한이 없습니다.", ephemeral=True)
        return
    
    global limit_by_weeks
    limit_by_weeks = limit
    
    await ctx.respond(f'일주일에 {limit}회까지 요청할 수 있도록 변경되었습니다.', ephemeral=True)

@bot.slash_command(name="횟수보기", description="주당 제한 횟수 조회")
async def get_limit_by_weeks(ctx: discord.ApplicationContext):    
    await ctx.respond(f'일주일에 {limit_by_weeks}회까지 요청할 수 있습니다.', ephemeral=True)

load_dotenv()
bot.run(os.environ.get('DISCORD_BOT_TOKEN'))