import os
import discord
from dotenv import load_dotenv

from app.database import Database
from app.exception.custom_exception import FollowersError, FollowingsError
from app.insta import Insta
from app.logger import get_logger


log = get_logger("discord_bot")
bot = discord.Bot(command_prefix="!")


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
