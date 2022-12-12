from nonebot import on_command
from nonebot.adapters.onebot.v11.message import MessageSegment
from nonebot.rule import to_me
from nonebot.matcher import Matcher
from nonebot.params import Arg, ArgPlainText, CommandArg
from nonebot.adapters.onebot.v11 import Message

from .account import *
from .utils import *

tsdm_login = on_command("tsdm_login", rule=to_me(), priority=1)
tsdm_refresh = on_command("tsdm_refresh", rule=to_me(), priority=2)
tsdm_get = on_command("tsdm_get", rule=to_me(), priority=5)

status = on_start()


@tsdm_login.handle()
async def handle_first_receive():
    verify_code = get_verify_code_img()
    if verify_code:
        await tsdm_login.send(MessageSegment.image("file:///{}".format(verify_code)))
    else:
        await tsdm_login.finish("获取验证码失败")


@tsdm_login.got("verify_code", prompt="请输入验证码")
async def handle_verify_code(verify_code: str = ArgPlainText("verify_code")):
    global status
    login_response = account.login(verify_code)
    if login_response == '':
        status = True
        await tsdm_login.finish("登录成功")
            
    else:
        message = Message([
            MessageSegment.text("登录失败"),
            MessageSegment.text(login_response)
        ])
        await tsdm_login.finish(message)


@tsdm_refresh.handle()
async def handle_refresh():
    global status
    if not status:
        await tsdm_refresh.finish("未登录")
    else:
        refresh_response = account.refresh_cookie()
        if refresh_response == '':
            await tsdm_refresh.finish("刷新成功")
        else:
            message = Message([
                MessageSegment.text("刷新失败"),
                MessageSegment.text(refresh_response)
            ])
            await tsdm_refresh.finish(message)


@tsdm_get.handle()
async def handle_first_get(matcher: Matcher, args: Message = CommandArg()):
    global status
    if not status:
        await tsdm_get.finish("未登录")
    else:
        tid = args.extract_plain_text()
        if tid:
            matcher.set_arg("tid", args)


@tsdm_get.got("tid", prompt="请输入帖子ID")
async def handle_tid(tid: Message = Arg(), tid_id = ArgPlainText("tid")):
    # aoba说op权限下不需要购买就可以直接获得thread全文，故不再调用
    # account.purchase(tid_id)
    forum_data = account.get_forum_data(tid_id)
    if forum_data:
        link = utils.pastebin_send(forum_data)
        await tsdm_get.send(link)
    else:
        await tsdm_get.finish("获取失败")