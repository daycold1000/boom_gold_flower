import asyncio
import base64
from distutils.command.build import build
import os
import random
from re import M, T, match
import sqlite3
from datetime import datetime, timedelta
from io import SEEK_CUR, BytesIO
from winsound import PlaySound
from xmlrpc.client import TRANSPORT_ERROR
from PIL import Image
from httpx import AsyncByteStream
from hoshino import Service, priv
from hoshino.modules.mgss.mengguisushe import coin
from hoshino.typing import CQEvent
from hoshino.util import DailyNumberLimiter
import copy
import json
import math
import pytz
import nonebot
from nonebot import on_command, on_request
from hoshino import sucmd
from nonebot import get_bot
from hoshino.typing import NoticeSession

###写在前面：请注意！！本功能数据均为多次测试后的最终确定值，非常不推荐修改！！！除非你愿意优化代码（真的有人会来优化吗？
sv = Service('炸金花', enable_on_default=True)

DB_PATH = os.path.expanduser('~/.q2bot/chouka.db')
DB2_PATH = os.path.expanduser('~/.q2bot/boom_gold_flower.db')
# 创建DB数据
class chouka:
    def __init__(self):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        self._create_shitou()
        

    def _connect(self):
        return sqlite3.connect(DB_PATH)
#母猪石数量
    def _create_shitou(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS SHITOU
                          (GID             INT    NOT NULL,
                           UID             INT    NOT NULL,
                           SHITOU           INT    NOT NULL,
                           PRIMARY KEY(GID, UID));''')
        except:
            raise Exception('创建表发生错误')
    def _set_shitou(self, gid, uid, shitou):
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO SHITOU (GID, UID, SHITOU) VALUES (?, ?, ?)",
                (gid, uid, shitou,),
            )
    def _get_shitou(self, gid, uid):
        try:
            r = self._connect().execute("SELECT SHITOU FROM SHITOU WHERE GID=? AND UID=?", (gid, uid)).fetchone()
            return 0 if r is None else r[0]
        except:
            raise Exception('查找表发生错误')
    def _add_shitou(self, gid, uid, num):
        num1 = self._get_shitou(gid, uid)
        if num1 == None:
            num1 = 0
        num1 += num
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO SHITOU (GID, UID, SHITOU) VALUES (?, ?, ?)",
                (gid, uid, num1),
            )
    def _reduce_shitou(self, gid, uid, num):
        msg1 = self._get_shitou(gid, uid)
        msg1 -= num
        msg1 = max(msg1,0)
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO SHITOU (GID, UID, SHITOU) VALUES (?, ?, ?)",
                (gid, uid, msg1),
            )

# 创建DB数据
class zhajinhua:
    def __init__(self):
        os.makedirs(os.path.dirname(DB2_PATH), exist_ok=True)
        self._create_shuzi()
        
    def _connect(self):
        return sqlite3.connect(DB2_PATH)
# 存储炸金花数据
    def _create_shuzi(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS SHUZI
                          (GID             INT    NOT NULL,
                           UID             INT    NOT NULL,
                           SHUZI           INT    NOT NULL,
                           PRIMARY KEY(GID, UID));''')
        except:
            raise Exception('创建表发生错误')
    def _set_shuzi(self, gid, uid, shuzi):
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO SHUZI (GID, UID, SHUZI) VALUES (?, ?, ?)",
                (gid, uid, shuzi,),
            )

    def _get_shuzi(self, gid, uid):
        try:
            r = self._connect().execute("SELECT SHUZI FROM SHUZI WHERE GID=? AND UID=?", (gid, uid)).fetchone()
            return 0 if r is None else r[0]
        except:
            raise Exception('查找表发生错误')

    def _add_shuzi(self, gid, uid, num):
        num1 = self._get_shuzi(gid, uid)
        if num1 == None:
            num1 = 0
        num1 += num
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO SHUZI (GID, UID, SHUZI) VALUES (?, ?, ?)",
                (gid, uid, num1),
            )

    def _reduce_shuzi(self, gid, uid, num):
        msg1 = self._get_shuzi(gid, uid)
        msg1 -= num
        msg1 = max(msg1,0)
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO SHUZI (GID, UID, SHUZI) VALUES (?, ?, ?)",
                (gid, uid, msg1),
            )

@sv.on_fullmatch(['炸金花'])
async def boom(bot,ev:CQEvent):
    zjh = zhajinhua()
    gid = ev.group_id
    uid = ev.user_id
    if zjh._get_shuzi(gid,1) == 0 and zjh._get_shuzi(gid,0) == 1:
        await bot.finish(ev,'请等待本轮结束',at_sender=True)
    if zjh._get_shuzi(gid,0) == 1:
        await bot.finish(ev,'不能重复开启',at_sender=True)
    #开启游戏
    zjh._set_shuzi(gid,0,1) 
    await bot.send(ev,'梭哈开始，使用<炸[数量]>梭哈！')
    zjh._set_shuzi(gid,1,30) #30秒时间记录数据（其实就是为了过上面本轮结束的判断）
    await asyncio.sleep(20) #等30秒
    await bot.send(ev,'梭哈还剩10秒')
    await asyncio.sleep(10)
    zjh._set_shuzi(gid,1,0) #时间到了（本轮结束的判断生效）
    await bot.send(ev,'梭哈结束，正在提升拿回倍率')
    num = random.randint(88,1000) #设置一个爆炸数
    num2 = 0 #初始数字
    #提升阶段
    while num2 != num: #只要初始数字不等于爆炸数就不炸
        await asyncio.sleep(0.1)
        num2 += 1
        zjh._set_shuzi(gid,2,num2)  #注意！这里的代码会发生大量的硬盘读写操作 #实在是想不到能优化的方案了，特别是几个玩家一起拿的时候确保能获取到多个数据
        if  num2==100  or num2==200 or num2==400 or num2==800:  #当初始数字为100、200、400、800时进行提升提示
            num3 = num2 /284
            num3 = round(num3,2)
            await bot.send(ev,f'当前倍率：x{num3}%')
        if num2 ==1000:
            num = 1000  #设置的上限，防止出现bug导致无限的上升初始数从而无法爆炸
    #爆炸阶段
    zjh._set_shuzi(gid,0,0)#群游戏状态设置为关闭
    zjh._set_shuzi(gid,2,0)#初始数字还原为0
    #展示结果
    num3 = num2 /284
    num3 = round(num3,2)
    await bot.finish(ev,f'它炸了... x{num3}%')
    
@sv.on_rex(r'^炸(.*)$')
async def zha(bot,ev:CQEvent):
    zjh = zhajinhua()
    ck = chouka()
    gid = ev.group_id
    uid = ev.user_id
    if zjh._get_shuzi(gid,0) ==0:#没检测到群游戏为开启状态，无视命令
        return 0
    if zjh._get_shuzi(gid,1) ==0 and zjh._get_shuzi(gid,0) ==1:
        await bot.finish(ev,'梭哈已结束了',at_sender=True)
    if zjh._get_shuzi(gid,uid) !=0:
        await bot.finish(ev,'你已经梭哈了',at_sender=True)
    match = (ev['match'])
    num = int(match.group(1))
    num2 = ck._get_shitou(0,uid)
    if num2 < num:#检查玩家货币是否足够梭哈
        await bot.finish(ev,'喵喵石头数量不足',at_sender=True)
    zjh._set_shuzi(gid,uid,num)#记录梭哈数量
    ck._reduce_shitou(0,uid,num)#扣除玩家货币
    await bot.send(ev,'梭哈成功，请在爆炸之前<拿>',at_sender=True)
    while zjh._get_shuzi(gid,0) == 1:#循环检测 拿 命令是否处于有效状态，一旦失效清除记录的梭哈货币数量
        xh = 1
        await asyncio.sleep(1)
    bank = zjh._get_shuzi(gid,uid)
    ck._add_shitou(0,0,bank)#给银行加钱
    zjh._set_shuzi(gid,uid,0)#清零

@sv.on_fullmatch(['拿'])
async def na(bot,ev:CQEvent):
    zjh = zhajinhua()
    ck = chouka()
    gid = ev.group_id
    uid = ev.user_id
    if zjh._get_shuzi(gid,0) ==0 or zjh._get_shuzi(gid,uid) ==0:#检查群游戏是否开启或者玩家是否有押注
        return 0
    num = zjh._get_shuzi(gid,2) #获取初始数字
    num5 = num / 284    
    player = zjh._get_shuzi(gid,uid)#获取玩家押注数量
    coin_add = player * num5
    coinadd2 = round(coin_add,0)
    ck._add_shitou(0,uid,coinadd2)#换算完成后添加到玩家账户
    num2 = ck._get_shitou(0,uid)
    zjh._set_shuzi(gid,uid,0)
    num5 = round(num5,2)
    ck._reduce_shitou(0,0,coinadd2)#从银行扣钱
    await bot.finish(ev,f'你拿了\n{num5}%\n+{coinadd2}✔️  , 💰 {num2}',at_sender=True)