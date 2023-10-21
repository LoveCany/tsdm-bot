from nonebot import on_command
from nonebot.adapters.telegram.message import File
from nonebot.rule import to_me
from nonebot.matcher import Matcher
from nonebot.params import Arg, ArgPlainText, CommandArg
from nonebot.adapters.telegram import Message
from nonebot.adapters.telegram.event import MessageEvent

from .account import *
from .utils import *

tsdm_login = on_command("/tsdm_login", aliases={"TSDM登录"}, priority=1)
tsdm_refresh = on_command("/tsdm_refresh", aliases={"TSDM刷新"}, priority=2)
tsdm_get = on_command("/tsdm_get", aliases={"嫖", "给点"}, priority=5)
tsdm_help = on_command("/tsdm_help", aliases={"帮助", "help"}, priority=10)

status = on_start()


@tsdm_help.handle()
async def handle_help():
    await tsdm_help.finish("如何使用tsdm-bot：\n" + "/tsdm_help (alias: 帮助/help) - 查看帮助\n" + "/tsdm_login (alias: TSDM登录) - 登录账号，后面不带验证码则会返回验证码对应base64，复制消息直接在浏览器地址栏打开可查看验证码，带验证码\n" +"/tsdm_get (alias: 嫖/给点) - 获取TSDM资源，需要提供对应的tid"+"/tsdm_refresh (alias: TSDM刷新) - 刷新账号cookie\n")


@tsdm_login.handle()
async def handle_first_receive(event: MessageEvent, matcher: Matcher, args: Message = CommandArg()):
    code = args.extract_plain_text()
    if len(code) > 0:
        global status
        login_response = account.login(code)
        if login_response == '':
            status = True
            await tsdm_login.finish("登录成功", reply_to_message_id=event.message_id)

        else:
            await tsdm_login.finish("登录失败\n" + login_response, reply_to_message_id=event.message_id)
    else:
        verify_code = get_verify_code_img()
        if verify_code:
            await tsdm_login.send(File.photo(verify_code) + "请输入验证码", reply_to_message_id=event.message_id)
        else:
            await tsdm_login.finish("获取验证码失败", reply_to_message_id=event.message_id)

@tsdm_refresh.handle()
async def handle_refresh(event: MessageEvent):
    global status
    if not status:
        await tsdm_refresh.finish("未登录")
    else:
        refresh_response = account.refresh_cookie()
        if refresh_response == '':
            await tsdm_refresh.finish("刷新成功", reply_to_message_id=event.message_id)
        else:
            await tsdm_refresh.finish("刷新失败\n" + refresh_response, reply_to_message_id=event.message_id)


@tsdm_get.handle()
async def handle_first_get(event: MessageEvent, matcher: Matcher, args: Message = CommandArg()):
    global status
    if not status:
        await tsdm_get.finish("未登录", reply_to_message_id=event.message_id)
    else:
        tid = args.extract_plain_text()
        if tid:
            matcher.set_arg("tid", args)


@tsdm_get.got("tid", prompt="请输入帖子ID")
async def handle_tid(event: MessageEvent, tid: Message = Arg(), tid_id=ArgPlainText("tid")):
    forum_data = account.get_forum_data(tid_id)
    if forum_data:
        link_raw = utils.pastebin_send(forum_data, False)
        link_html = utils.pastebin_send(forum_data, True)
        await tsdm_get.send(f'解析: {link_html}\n源代码: {link_raw}', reply_to_message_id=event.message_id)
    else:
        await tsdm_get.finish("获取失败", reply_to_message_id=event.message_id)
