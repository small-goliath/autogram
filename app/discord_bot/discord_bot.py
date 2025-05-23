import os
import discord
from dotenv import load_dotenv
from datetime import timedelta

from app.database import Database
from app.exception.custom_exception import FollowersError, FollowingsError
from app.insta import Insta
from app.logger import get_logger
from app.model.entity import ActionTarget
from app.util import get_today


log = get_logger("discord_bot")
bot = discord.Bot(command_prefix="!")

limit_by_weeks = 7

# def get_kst_now():
#     return datetime.now(timezone(timedelta(hours=9)))

# def get_date_range(weeks_ago: int):
#     today = get_kst_now()
#     start_date = (today - timedelta(days=today.weekday() + (7 * weeks_ago))).replace(hour=0, minute=0, second=0, microsecond=0)
#     if weeks_ago == 0:
#         end_date = today
#     else:
#         end_date = (today - timedelta(days=today.weekday() + (1 * weeks_ago))).replace(hour=0, minute=0, second=0, microsecond=0)
#     return start_date, end_date

# async def parse_messages(ctx: discord.ApplicationContext, weeks_ago: int):
#     start_date, end_date = get_date_range(weeks_ago)
#     message_pattern = re.compile(r"(.*?)\s*(https://www\.instagram\.com[^\s]+)")
#     messages = [
#         message async for message in ctx.history(limit=None, after=start_date, before=end_date)
#     ]

#     action_targets = []
#     for message in messages:
#         message_match = message_pattern.match(message.content)
#         if message_match:
#             action_targets.append(ActionTarget(
#                 username=message.author.name,
#                 link=message_match[2].strip(),
#                 monday=message.created_at.strftime("%Y-%m-%d"),
#                 sunday=message.created_at.strftime("%Y-%m-%d")
#             ))
#     return action_targets

# @bot.slash_command(name="수집", description="지난주 품앗이 요청 수집.")
# async def aggregate(ctx: discord.ApplicationContext,
#                     weeks_ago: discord.Option(int, description="몇 주 전 메시지를 수집하시겠습니까?", default=1, min_value=1, max_value=4, required=True)):
#     if not ctx.author.guild_permissions.administrator:
#         await ctx.respond("이 명령어를 사용할 권한이 없습니다.", ephemeral=True)
#         return
    
#     action_targets = await parse_messages(ctx, weeks_ago)

#     db = Database()
#     db.save_action_targets(action_targets)

#     await ctx.respond(f'{weeks_ago}주일 전의({start_date.strftime("%Y-%m-%d")} - {end_date.strftime("%Y-%m-%d")}) 메시지 수: {len(action_targets)}개')

# @bot.slash_command(name="현황", description="품앗이 요청 현황을 조회합니다.")
# async def status(ctx: discord.ApplicationContext,
#                  weeks_ago: discord.Option(int, description="몇 주 전 메시지를 조회하시겠습니까?", default=1, min_value=0, max_value=4, required=True)):
#     action_targets = await parse_messages(ctx, weeks_ago)

#     if not action_targets:
#         await ctx.respond(f"{weeks_ago}주일 전 품앗이 요청건이 없습니다.")
#         return

#     link_count_dict = defaultdict(list)

#     for target in action_targets:
#         link_count_dict[target.username].append(target.link)
    
#     embeds: List[discord.Embed] = []
#     for username, links in link_count_dict.items():
#         embed = discord.Embed(color=discord.Colour.random(), description=f"{username}님의 {weeks_ago}주일 전 현황")
#         embed.add_field(name="링크 수", value=f"{len(links)}개", inline=True)
#         embed.add_field(name="링크", value="\n\n".join(links), inline=True)
#         embeds.append(embed)

#     for i in range(0, len(embeds), 10):
#         chunk = embeds[i:i + 10]
#         await ctx.respond(embeds=chunk)

@bot.slash_command(name="등록", description="품앗이 요청")
async def create_link(ctx: discord.ApplicationContext,
                             link: discord.Option(str, description="등록할 link를 입력해주세요.", required=True)):
    db = Database()
    username = ctx.author.name
    await ctx.respond(f'{username}님의 {link}를 등록 중입니다.', ephemeral=True)
    try:
        account = db.search_instagram_account(username=username)
        if not account:
            await ctx.send_followup(f'{username}은 본 서비스에 등록되지 않은 계정입니다.', ephemeral=True)
            return
        
        today = get_today()
        this_monday = today - timedelta(days=today.weekday())
        action_targets = db.search_action_targets_by_monday(account_id=account.id, target_monday=this_monday)

        if len(action_targets) == limit_by_weeks:
            await ctx.send_followup(f'이미 이번주에 {limit_by_weeks}개를 등록하셨습니다.', ephemeral=True)
            return
        
        db.save_action_targets(targets=[ActionTarget(username=username, link=link, monday=this_monday.strftime("%Y-%m-%d"), sunday=today.strftime("%Y-%m-%d"))])
        
        await ctx.send_followup(f'{username}님이 {link}를 등록했습니다. ({len(action_targets)+1}/{limit_by_weeks})')
    except:
        await ctx.send_followup(f'등록을 할 수 없습니다. 관리자에게 문의해주세요.', ephemeral=True)

@bot.slash_command(name="횟수수정", description="주당 제한 횟수 변경")
async def set_limit_by_weeks(ctx: discord.ApplicationContext,
                             limit: discord.Option(int, description="변경할 주당 제한 횟수를 입력해주세요.", default=3, min_value=1, required=True)):
    if not ctx.author.guild_permissions.administrator:
        await ctx.respond("이 명령어를 사용할 권한이 없습니다.", ephemeral=True)
        return
    
    global limit_by_weeks
    limit_by_weeks = limit
    
    await ctx.respond(f'일주일에 {limit}회까지 요청할 수 있도록 변경되었습니다.', ephemeral=True)

@bot.slash_command(name="횟수", description="나의 품앗이 요청 건수")
async def set_limit_by_weeks(ctx: discord.ApplicationContext):
    db = Database()
    username = ctx.author.name
    await ctx.respond(f'{username}님의 등록 수를 조회 중입니다.', ephemeral=True)

    try:
        account = db.search_instagram_account(username=username)
        if not account:
            await ctx.send_followup(f'{username}은 본 서비스에 등록되지 않은 계정입니다.', ephemeral=True)
            return
        
        today = get_today()
        this_monday = today - timedelta(days=today.weekday())
        action_targets = db.search_action_targets_by_monday(account_id=account.id, target_monday=this_monday)

        await ctx.send_followup(f'현재까지 {len(action_targets)}개를 등록하셨습니다.', ephemeral=True)
    except:
        await ctx.send_followup(f'조회 할 수 없습니다. 관리자에게 문의해주세요.', ephemeral=True)

@bot.slash_command(name="주당횟수", description="주당 제한 횟수 조회")
async def get_limit_by_weeks(ctx: discord.ApplicationContext):
    await ctx.respond(f'일주일에 {limit_by_weeks}회까지 요청할 수 있습니다.', ephemeral=True)

@bot.slash_command(name="언팔보기", description="언팔로워 조회")
async def get_limit_by_weeks(ctx: discord.ApplicationContext):
    username = ctx.author.name
    await ctx.respond("언팔 검색은 팔로워 또는 팔로잉이 많을 수록 시간이 많이 소요됩니다.(1,200명 기준 약 4분 소요)\n집계가 완료된 후 알려드리겠습니다.", ephemeral=True)
    db = Database()
    try:
        account = db.search_instagram_account(username)
        if account is None:
            await ctx.respond("계정을 등록해주세요.", ephemeral=True)
            return
        insta = Insta(account)
        insta.login()
        followers = insta.search_followers()
        followings = insta.search_followings()
        non_followers = set(followings.values()) - set(followers.values())
        prefix = "https://instagram.com/"
        if non_followers:
            message = f"맞팔이 아닌 유저를 찾았습니다.\n" + "\n".join(prefix + non_follower.username for non_follower in non_followers)
        else:
            message = "맞팔이 아닌 유저가 없습니다."
        
        await ctx.send_followup(message, ephemeral=True)
    except FollowersError as e:
        await ctx.respond(f"{username}의 팔로워를 검색할 수 없습니다.", ephemeral=True)
    except FollowingsError as e:
        await ctx.respond(f"{username}의 팔로잉을 검색할 수 없습니다.", ephemeral=True)
    except Exception as e:
        await ctx.respond("다시 시도해주세요.", ephemeral=True)

load_dotenv()
bot.run(os.environ.get('DISCORD_BOT_TOKEN'))
