from bs4 import BeautifulSoup
from signal import signal, SIGINT
from requests import get as rget
from urllib.parse import quote as q
from random import choice as rchoice
from os import path as ospath, remove as osremove, execl as osexecl
from subprocess import run as srun, check_output
from datetime import datetime
from psutil import disk_usage, cpu_percent, swap_memory, cpu_count, virtual_memory, net_io_counters, boot_time
from time import time
from sys import executable
from pytz import timezone
from telegram.ext import CommandHandler

from .helper.ext_utils.bot_utils import get_readable_file_size, get_readable_time
from .helper.ext_utils.db_handler import DbManger
from .helper.ext_utils.fs_utils import start_cleanup, clean_all, exit_clean_up
from .helper.ext_utils.telegraph_helper import telegraph
from .helper.telegram_helper.bot_commands import BotCommands
from .helper.telegram_helper.message_utils import sendMessage, editMessage, sendLogFile, sendPhoto
from .helper.telegram_helper.filters import CustomFilters
from .helper.telegram_helper.button_build import ButtonMaker
from bot import config_dict, botStartTime, Interval, QbInterval, LOGGER, DATABASE_URL, bot, dispatcher, updater, IGNORE_PENDING_REQUESTS, \
                app, main_loop
from .modules import authorize, list, cancel_mirror, mirror_status, mirror_leech, clone, ytdlp, shell, eval, bot_settings, \
                     delete, count, users_settings, search, rss, wayback, speedtest, anilist, imdb, bt_select, mediainfo, hash, \
                     scraper, pictures, save_msg, sel_cat

version = "5.0.0"

def progress_bar(percentage):
    p_used = config_dict['FINISHED_PROGRESS_STR']
    p_total = config_dict['UN_FINISHED_PROGRESS_STR']
    if isinstance(percentage, str):
        return 'NaN'
    try:
        percentage=int(percentage)
    except:
        percentage = 0
    return ''.join(
        p_used if i <= percentage // 10 else p_total for i in range(1, 11)
    )


timez = config_dict['TIMEZONE']
now=datetime.now(timezone(f'{timez}'))

def stats(update, context):
    if ospath.exists('.git'):
        if config_dict['EMOJI_THEME']:
            last_commit = check_output(["git log -1 --date=short --pretty=format:'%cd \n<b>├</b> 🛠<b>From:</b> %cr'"], shell=True).decode()
            botVersion = check_output(["git log -1 --date=format:v%y.%m%d.%H%M --pretty=format:%cd"], shell=True).decode()
        else:
            last_commit = check_output(["git log -1 --date=short --pretty=format:'%cd \n<b>├  From:</b> %cr'"], shell=True).decode()
            botVersion = check_output(["git log -1 --date=format:v%y.%m%d.%H%M --pretty=format:%cd"], shell=True).decode()
    else:
        botVersion = 'No UPSTREAM_REPO'
        last_commit = 'No UPSTREAM_REPO'
    currentTime = get_readable_time(time() - botStartTime)
    current = now.strftime('%m/%d %I:%M:%S %p')
    osUptime = get_readable_time(time() - boot_time())
    total, used, free, disk= disk_usage('/')
    total = get_readable_file_size(total)
    used = get_readable_file_size(used)
    free = get_readable_file_size(free)
    sent = get_readable_file_size(net_io_counters().bytes_sent)
    recv = get_readable_file_size(net_io_counters().bytes_recv)
    cpuUsage = cpu_percent(interval=0.5)
    p_core = cpu_count(logical=False)
    t_core = cpu_count(logical=True)
    swap = swap_memory()
    swap_p = swap.percent
    swap_t = get_readable_file_size(swap.total)
    swap_u = get_readable_file_size(swap.used)
    memory = virtual_memory()
    mem_p = memory.percent
    mem_t = get_readable_file_size(memory.total)
    mem_a = get_readable_file_size(memory.available)
    mem_u = get_readable_file_size(memory.used)
    if config_dict['EMOJI_THEME']:
            stats = f'<b>╭─《🔰 وضعیت فعلی ربات》</b>\n' \
                    f'<b>├ 🛠 اپدیت: </b>{last_commit}\n'\
                    f'<b>├ ⌛ آپتایم: </b>{currentTime}\n'\
                    f'<b>├ 🟢 آپتایم سیستم: </b>{osUptime}\n'\
                    f'<b>├ 🖥️ پردازنده:</b> [{progress_bar(cpuUsage)}] {cpuUsage}%\n'\
                    f'<b>├ 🎮 رم:</b> [{progress_bar(mem_p)}] {mem_p}%\n'\
                    f'<b>├ 💾 دیسک:</b> [{progress_bar(disk)}] {disk}%\n'\
                    f'<b>├ 💿 فضای ازاد:</b> {free}\n'\
                    f'<b>├ 🔺 آپلود:</b> {sent}\n'\
                    f'<b>╰ 🔻 دانلود:</b> {recv}\n\n'

    else:
            stats = f'<b>╭─《🌐 BOT STATISTICS 🌐》</b>\n' \
                    f'<b>├  Updated On: </b>{last_commit}\n'\
                    f'<b>├  Uptime: </b>{currentTime}\n'\
                    f'<b>├  Version: </b>{version}\n'\
                    f'<b>├  OS Uptime: </b>{osUptime}\n'\
                    f'<b>├  CPU:</b> [{progress_bar(cpuUsage)}] {cpuUsage}%\n'\
                    f'<b>├  RAM:</b> [{progress_bar(mem_p)}] {mem_p}%\n'\
                    f'<b>├  Disk:</b> [{progress_bar(disk)}] {disk}%\n'\
                    f'<b>├  Disk Free:</b> {free}\n'\
                    f'<b>├  Upload Data:</b> {sent}\n'\
                    f'<b>╰  Download Data:</b> {recv}\n\n'



    if config_dict['SHOW_LIMITS_IN_STATS']:

        TORRENT_DIRECT_LIMIT = config_dict['TORRENT_DIRECT_LIMIT']
        CLONE_LIMIT = config_dict['CLONE_LIMIT']
        MEGA_LIMIT = config_dict['MEGA_LIMIT']
        LEECH_LIMIT = config_dict['LEECH_LIMIT']
        ZIP_UNZIP_LIMIT = config_dict['ZIP_UNZIP_LIMIT']
        TOTAL_TASKS_LIMIT = config_dict['TOTAL_TASKS_LIMIT']
        USER_TASKS_LIMIT = config_dict['USER_TASKS_LIMIT']

        torrent_direct = 'No Limit Set' if TORRENT_DIRECT_LIMIT == '' else f'{TORRENT_DIRECT_LIMIT}GB/Link'
        clone_limit = 'No Limit Set' if CLONE_LIMIT == '' else f'{CLONE_LIMIT}GB/Link'
        mega_limit = 'No Limit Set' if MEGA_LIMIT == '' else f'{MEGA_LIMIT}GB/Link'
        leech_limit = 'No Limit Set' if LEECH_LIMIT == '' else f'{LEECH_LIMIT}GB/Link'
        zip_unzip = 'No Limit Set' if ZIP_UNZIP_LIMIT == '' else f'{ZIP_UNZIP_LIMIT}GB/Link'
        total_task = 'No Limit Set' if TOTAL_TASKS_LIMIT == '' else f'{TOTAL_TASKS_LIMIT} Total Tasks/Time'
        user_task = 'No Limit Set' if USER_TASKS_LIMIT == '' else f'{USER_TASKS_LIMIT} Tasks/user'

        if config_dict['EMOJI_THEME']: 
            stats += f'<b>╭─《 ⚠️ BOT LIMITS ⚠️ 》</b>\n'\
                     f'<b>├ 🧲 Torrent/Direct: </b>{torrent_direct}\n'\
                     f'<b>├ 🔐 Zip/Unzip: </b>{zip_unzip}\n'\
                     f'<b>├ 🔷 Leech: </b>{leech_limit}\n'\
                     f'<b>├ ♻️ Clone: </b>{clone_limit}\n'\
                     f'<b>├ 🔰 Mega: </b>{mega_limit}\n'\
                     f'<b>├ 💣 Total Tasks: </b>{total_task}\n'\
                     f'<b>╰ 🔫 User Tasks: </b>{user_task}\n\n'
        else: 
            stats += f'<b>╭─《 ⚠️ لیمیت های بات ⚠️ 》</b>\n'\
                     f'<b>├ 🧲 تورنت: </b>{torrent_direct}\n'\
                     f'<b>├ 🔐 انزیپ: </b>{zip_unzip}\n'\
                     f'<b>├ 🔷 لیچ: </b>{leech_limit}\n'\
                     f'<b>├ ♻️ کلون: </b>{clone_limit}\n'\
                     f'<b>├ 🔰 مگا: </b>{mega_limit}\n'\
                     f'<b>├ 💣 مجموع تسک: </b>{total_task}\n'\
                     f'<b>╰ 🔫 تسک کاربر: </b>{user_task}\n\n'

    if config_dict['PICS']:
        sendPhoto(stats, context.bot, update.message, rchoice(config_dict['PICS']))
    else:
        sendMessage(stats, context.bot, update.message)

def start(update, context):
    buttons = ButtonMaker()
    if config_dict['EMOJI_THEME']:
        buttons.buildbutton(f"🟡 کانال", "https://t.me/King_network7")
        buttons.buildbutton(f"🔴 دونیت", "https://payping.ir/d/WiZG")
    else:
        buttons.buildbutton(f"{config_dict['START_BTN1_NAME']}", f"{config_dict['START_BTN1_URL']}")
        buttons.buildbutton(f"{config_dict['START_BTN2_NAME']}", f"{config_dict['START_BTN2_URL']}")
    reply_markup = buttons.build_menu(2)
    if CustomFilters.authorized_user(update) or CustomFilters.authorized_chat(update):
        start_string = f'''
🗳 به ربات کینگ لیچر خوش آمدید. برای مشاهده راهنما ربات دستور /help را ارسال کنید.

🆔 @King_Network7
'''
        if config_dict['PICS']:
            sendPhoto(start_string, context.bot, update.message, rchoice(config_dict['PICS']), reply_markup)
        else:
            sendMessage(start_string, context.bot, update.message, reply_markup)
    else:
        text = f"برای استفاده از امکانات . به گروه ما بپیوندید  https://t.me/kingleech"
        if config_dict['PICS']:
            sendPhoto(text, context.bot, update.message, rchoice(config_dict['PICS']), reply_markup)
        else:
            sendMessage(text, context.bot, update.message, reply_markup)


def restart(update, context):
    restart_message = sendMessage("Restarting...", context.bot, update.message)
    if Interval:
        Interval[0].cancel()
        Interval.clear()
    if QbInterval:
        QbInterval[0].cancel()
        QbInterval.clear()
    clean_all()
    srun(["pkill", "-9", "-f", "gunicorn|aria2c|qbittorrent-nox|ffmpeg"])
    srun(["python3", "update.py"])
    with open(".restartmsg", "w") as f:
        f.truncate(0)
        f.write(f"{restart_message.chat.id}\n{restart_message.message_id}\n")
    osexecl(executable, executable, "-m", "bot")


def ping(update, context):
    if config_dict['EMOJI_THEME']:
        start_time = int(round(time() * 1000))
        reply = sendMessage("Starting_Ping ⛔", context.bot, update.message)
        end_time = int(round(time() * 1000))
        editMessage(f'{end_time - start_time} ms 🔥', reply)
    else:
        start_time = int(round(time() * 1000))
        reply = sendMessage("Starting_Ping ", context.bot, update.message)
        end_time = int(round(time() * 1000))
        editMessage(f'{end_time - start_time} ms ', reply)

def log(update, context):
    sendLogFile(context.bot, update.message)


help_string = '''
📘 با ورود به لینک زیر راهنمای کامل دستورات ربات را میتوانید به صورت فارسی مشاهده نمایید

🆔 @King_Network7
'''

help_string_telegraph_user = f'''
<b><u>👤 User Commands</u></b>
<br><br>
• <b>/{BotCommands.HelpCommand}</b>: To get this message
<br><br>
'''

help_user = telegraph.create_page(
    title=f"{config_dict['TITLE_NAME']} Help",
    content=help_string_telegraph_user)["path"]

help_string_telegraph_admin = f'''
<b><u>🛡️ Admin Commands</u></b>
<br><br>
• <b>/{BotCommands.PingCommand}</b>: Check how long it takes to Ping the Bot
<br><br>
• <b>/{BotCommands.AuthorizeCommand}</b>: Authorize a chat or a user to use the bot (Can only be invoked by Owner & Sudo of the bot)
<br><br>
• <b>/{BotCommands.UnAuthorizeCommand}</b>: Unauthorize a chat or a user to use the bot (Can only be invoked by Owner & Sudo of the bot)
<br><br>
• <b>/{BotCommands.UsersCommand}</b>: show users settings (Only Owner & Sudo).
<br><br>
• <b>/{BotCommands.AddSudoCommand}</b>: Add sudo user (Only Owner)
<br><br>
• <b>/{BotCommands.RmSudoCommand}</b>: Remove sudo users (Only Owner)
<br><br>
• <b>/{BotCommands.PaidUsersCommand}</b>: Show Paid users (Only Owner & Sudo)
<br><br>
• <b>/{BotCommands.AddPaidCommand}</b>: Authorize Paid users (Only Owner)
<br><br>
• <b>/{BotCommands.RmPaidCommand}</b>: Unauthorize Paid users (Only Owner)
<br><br>
• <b>/{BotCommands.RestartCommand}</b>: Restart and update the bot (Only Owner & Sudo)
<br><br>
• <b>/{BotCommands.LogCommand}</b>: Get a log file of the bot. Handy for getting crash reports
'''

help_admin = telegraph.create_page(
    title=f"{config_dict['TITLE_NAME']} Help",
    content=help_string_telegraph_admin)["path"]


def bot_help(update, context):
    button = ButtonMaker()
    if config_dict['EMOJI_THEME']:
        button.buildbutton("🔎 مشاهده راهنما 🔍", f"https://telegra.ph/%D8%AA%D9%88%D8%B6%DB%8C%D8%AD-%D9%81%D8%A7%D8%B1%D8%B3%DB%8C-%D8%AF%D8%B3%D8%AA%D9%88%D8%B1%D8%A7%D8%AA-%D8%B1%D8%A8%D8%A7%D8%AA-07-15")
    else:
        button.buildbutton("User", f"https://telegra.ph/{help_user}")
        button.buildbutton("Admin", f"https://telegra.ph/{help_admin}")
    sendMessage(help_string, context.bot, update.message, button.build_menu(2))


if config_dict['SET_BOT_COMMANDS']:
    botcmds = [
        (f'{BotCommands.MirrorCommand[0]}', 'Mirror'),
        (f'{BotCommands.ZipMirrorCommand[0]}','Mirror and upload as zip'),
        (f'{BotCommands.UnzipMirrorCommand[0]}','Mirror and extract files'),
        (f'{BotCommands.QbMirrorCommand[0]}','Mirror torrent using qBittorrent'),
        (f'{BotCommands.QbZipMirrorCommand[0]}','Mirror torrent and upload as zip using qb'),
        (f'{BotCommands.QbUnzipMirrorCommand[0]}','Mirror torrent and extract files using qb'),
        (f'{BotCommands.YtdlCommand[0]}','Mirror yt-dlp supported link'),
        (f'{BotCommands.YtdlZipCommand[0]}','Mirror yt-dlp supported link as zip'),
        (f'{BotCommands.CloneCommand[0]}','Copy file/folder to Drive'),
        (f'{BotCommands.LeechCommand[0]}','Leech'),
        (f'{BotCommands.ZipLeechCommand[0]}','Leech and upload as zip'),
        (f'{BotCommands.UnzipLeechCommand[0]}','Leech and extract files'),
        (f'{BotCommands.QbLeechCommand[0]}','Leech torrent using qBittorrent'),
        (f'{BotCommands.QbZipLeechCommand[0]}','Leech torrent and upload as zip using qb'),
        (f'{BotCommands.QbUnzipLeechCommand[0]}','Leech torrent and extract using qb'),
        (f'{BotCommands.YtdlLeechCommand[0]}','Leech yt-dlp supported link'),
        (f'{BotCommands.YtdlZipLeechCommand[0]}','Leech yt-dlp supported link as zip'),
        (f'{BotCommands.ScrapeCommand[0]}','Scrape Links from Website'),
        (f'{BotCommands.CountCommand}','Count file/folder of Drive'),
        (f'{BotCommands.DeleteCommand}','Delete file/folder from Drive'),
        (f'{BotCommands.CancelMirror}','Cancel a task'),
        (f'{BotCommands.CancelAllCommand}','Cancel all downloading tasks'),
        (f'{BotCommands.ListCommand}','Search in Drive'),
        (f'{BotCommands.SearchCommand}','Search in Torrent'),
        (f'{BotCommands.UserSetCommand[0]}','Users settings'),
        (f'{BotCommands.BotSetCommand[0]}','BOT settings'),
        (f'{BotCommands.StatusCommand}','Get mirror status message'),
        (f'{BotCommands.SpeedCommand[0]}','Speedtest'),
        (f'{BotCommands.WayBackCommand}','Internet Archive'),
        (f'{BotCommands.MediaInfoCommand[0]}','Get Information of telegram Files'),
        (f'{BotCommands.HashCommand}','Get Hash of telegram Files'),
        (f'{BotCommands.PingCommand}','Ping the bot'),
        (f'{BotCommands.RestartCommand}','Restart the bot'),
        (f'{BotCommands.LogCommand}','Get the bot Log'),
        (f'{BotCommands.HelpCommand}','Get detailed help')
    ]


def main():

    if config_dict['WALLCRAFT_CATEGORY']:
        for page in range(1,20):
            r2 = rget(f"https://wallpaperscraft.com/catalog/{config_dict['WALLCRAFT_CATEGORY']}/1280x720/page{page}")
            soup2 = BeautifulSoup(r2.text, "html.parser")
            x = soup2.select('img[src^="https://images.wallpaperscraft.com/image/single"]')
            for img in x:
              config_dict['PICS'].append((img['src']).replace("300x168", "1280x720"))

    if config_dict['WALLTIP_SEARCH']:
        for page in range(1,3):
            r2 = rget(f"https://www.wallpapertip.com/s/{config_dict['WALLTIP_SEARCH']}/{page}")
            soup2 = BeautifulSoup(r2.text, "html.parser")
            divTag = soup2.select('#flex_grid div.item')
            aTag = [x.find('a') for x in divTag]
            imgsrc = [x.find('img') for x in aTag]
            scrList =  [img['data-original'] for img in imgsrc]
            for o in scrList:
                config_dict['PICS'].append(o)

    if config_dict['WALLFLARE_SEARCH']:
        try:
            for page in range(1,20):
                r2 = rget(f"https://www.wallpaperflare.com/search?wallpaper={config_dict['WALLFLARE_SEARCH']}&width=1280&height=720&page={page}")
                soup2 = BeautifulSoup(r2.text, "html.parser")
                x = soup2.select('img[data-src^="https://c4.wallpaperflare.com/wallpaper"]')  
                for img in x:
                    config_dict['PICS'].append(img['data-src'])
        except Exception as err:
            LOGGER.info(f"WallFlare Error: {err}")

    if config_dict['PIXABAY_API_KEY']:
        try:
            PIXABAY_ENDPOINT = f"https://pixabay.com/api/?key={config_dict['PIXABAY_API_KEY']}&image_type=all&orientation=horizontal&min_width=1280&min_height=720&per_page=200&safesearch=true&editors_choice=true"
            if config_dict['PIXABAY_CATEGORY']: PIXABAY_ENDPOINT += f"&category={config_dict['PIXABAY_CATEGORY']}"
            if config_dict['PIXABAY_SEARCH']: PIXABAY_ENDPOINT += f"&q={q(config_dict['PIXABAY_SEARCH'])}"
            resp = rget(PIXABAY_ENDPOINT)
            jdata = resp.json()
            for x in range(0, 200):
                largeImageURL = jdata['hits'][x]['largeImageURL']
                config_dict['PICS'].append(largeImageURL)
        except Exception as err:
            LOGGER.info(f"Pixabay API Error: {err}")

    if config_dict['SET_BOT_COMMANDS']:
        bot.set_my_commands(botcmds)
    start_cleanup()
    date = now.strftime('%d/%m/%y')
    time = now.strftime('%I:%M:%S %p')
    notifier_dict = False
    if config_dict['INCOMPLETE_TASK_NOTIFIER'] and DATABASE_URL:
        if notifier_dict := DbManger().get_incomplete_tasks():
            for cid, data in notifier_dict.items():
                if ospath.isfile(".restartmsg"):
                    with open(".restartmsg") as f:
                        chat_id, msg_id = map(int, f)
                    msg = f"😎 Restarted Successfully❗\n"
                else:
                    msg = f"😎 Bot Restarted!\n"
                msg += f"📅 DATE: {date}\n"
                msg += f"⌚ TIME: {time}\n"
                msg += f"🌐 TIMEZONE: {timez}\n"
                msg += f"🤖 VERSION: {version}"

                for tag, links in data.items():
                    msg += f"\n{tag}: "
                    for index, link in enumerate(links, start=1):
                        msg += f" <a href='{link}'>{index}</a> |"
                        if len(msg.encode()) > 4000:
                            if '😎 Restarted Successfully❗' in msg and cid == chat_id:
                                try:
                                    bot.editMessageText(msg, chat_id, msg_id)
                                except:
                                    pass
                                osremove(".restartmsg")
                            else:
                                try:
                                    bot.sendMessage(cid, msg)
                                except Exception as e:
                                    LOGGER.error(e)
                            msg = ''
                if '😎 Restarted Successfully❗' in msg and cid == chat_id:
                    try:
                        bot.editMessageText(msg, chat_id, msg_id)
                    except:
                        pass
                    osremove(".restartmsg")
                else:
                    try:
                        bot.sendMessage(cid, msg)
                    except Exception as e:
                        LOGGER.error(e)

    if ospath.isfile(".restartmsg"):
        with open(".restartmsg") as f:
            chat_id, msg_id = map(int, f)
        try:
            msg = f"😎 Restarted Successfully❗\n"
            msg += f"📅 DATE: {date}\n"
            msg += f"⌚ TIME: {time}\n"
            msg += f"🌐 TIMEZONE: {timez}\n"
            msg += f"🤖 VERSION: {version}"            
            bot.edit_message_text(msg, chat_id, msg_id)
        except Exception as e:
            LOGGER.info(e)
        osremove(".restartmsg")



    start_handler = CommandHandler(BotCommands.StartCommand, start)
    log_handler = CommandHandler(BotCommands.LogCommand, log,
                               filters=CustomFilters.owner_filter | CustomFilters.sudo_user)
    restart_handler = CommandHandler(BotCommands.RestartCommand, restart,
                               filters=CustomFilters.owner_filter | CustomFilters.sudo_user)
    ping_handler = CommandHandler(BotCommands.PingCommand, ping,
                               filters=CustomFilters.authorized_chat | CustomFilters.authorized_user)
    help_handler = CommandHandler(BotCommands.HelpCommand, bot_help,
                               filters=CustomFilters.authorized_chat | CustomFilters.authorized_user)
    stats_handler = CommandHandler(BotCommands.StatsCommand, stats,
                               filters=CustomFilters.authorized_chat | CustomFilters.authorized_user)


    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(ping_handler)
    dispatcher.add_handler(restart_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(stats_handler)
    dispatcher.add_handler(log_handler)
    updater.start_polling(drop_pending_updates=IGNORE_PENDING_REQUESTS)
    LOGGER.info("💥𝐁𝐨𝐭 𝐒𝐭𝐚𝐫𝐭𝐞𝐝❗")
    signal(SIGINT, exit_clean_up)

app.start()
main()

main_loop.run_forever()
