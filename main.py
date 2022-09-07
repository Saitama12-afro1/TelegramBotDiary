import asyncio
import logging
import datetime
import aioschedule
import re
from tkinter import Pack
from aiogram import Bot, Dispatcher, executor, types, filters
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from models import Base, Plan, User, Item
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup 
from aiogram.dispatcher import FSMContext


engine = create_engine("postgresql+psycopg2://postgres:danila2001@localhost:5432/TeleBot", echo = True)
session = sessionmaker(bind=engine)
db = session()

API_TOKEN = "5426871089:AAF0yXucwAmd9WQH_P9DTuoDw501iRH0CGs" # поместить в конфиг

logging.basicConfig(level=logging.INFO)

storage = MemoryStorage()
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot,storage=storage)

class Mydialog(StatesGroup):
    otvet = State()
 
    
# @dp.async_task # отвечает за получение текущего времмени
@dp.message_handler(commands=["dsds"])
async def dt(user_id :str):
    print(user_id)
    await bot.send_message(user_id,"Напоминалка")
 
 
async def scheduler():
    all_plans = db.query(Plan).all()
    loop = asyncio.get_event_loop()
    for i in all_plans:
        for j in i.item:
            time = j.time_end
            time = j.time_end
            year, month, day, hour, minute = time.strftime("%Y"), time.strftime("%m"),time.strftime("%d"),time.strftime("%H"),time.strftime("%M")
            aioschedule.every().day(day).hour(hour).minute(minute).do(dt,"date",user_id = i.user,)#.hour = и тд
            while True:
                await aioschedule.run_pending()
                await asyncio.sleep(1)          


async def on_startup(dp): 
    asyncio.create_task(scheduler())        

            
@dp.message_handler(commands = ["show"])
async def test(message :types.Message):
    pl = db.query(Plan).order_by(desc(Plan.id_plan)).first()
    time_format = "%Y-%m-%d %H:%M:%S"
    s = f"Дата создания плана{pl.time_create:{time_format}}\n" + f"Дата окончнания плана{pl.time_end:{time_format}}\n"
    for i,val in enumerate(pl.item):
        s += f"{i}) {str(val.item)}\n"
    await bot.send_message(message.from_user.id, s)
    
        
@dp.message_handler(filters.Regexp(regexp=r"plan\s*\w*"))#отвечает за ккоманду plan
async def plan_command(message: types.Message):
    await Mydialog.otvet.set()
    if message.text == "/plan":
        await bot.send_message(message.from_user.id,f"План будет создан на завтра\n"
                               f"Вводите построчно каждый пункт в формате пункт - время\n"
                               f"Время не обязательно, если не указать, то бот не напомнит\n"
                               f"когда закончите напишите /end")
        a = db.query(User).filter(User.id_user_telegram == str(message.from_user.id)).first()
        if a == None:
            user = User(id_user_telegram = str(message.from_user.id))#сделать проверку на уникальность
            db.add(user)
            db.commit()
        else:
            user = a
        plan = Plan(time_end = datetime.datetime.now() + datetime.timedelta(days=1), user = user.id_user)
        db.add(plan)
        db.commit()
    else:
        date = re.split(' ', message.text) # сделать обработку времмени
        date_time_str = date[1] +" " + date[2]
        print(date_time_str)
        date_time_obj = datetime.datetime.strptime(date_time_str, '%d/%m/%y %H:%M:%S')
        a = db.query(User).filter(User.id_user_telegram == str(message.from_user.id)).first()
        if a == None:
            user = User(id_user_telegram = str(message.from_user.id))#сделать проверку на уникальность
            db.add(user)
            db.commit()
        else:
            user = a
        plan = Plan(time_end = date_time_obj, user = user.id_user)
        db.add(plan)
        db.commit()
        await bot.send_message(message.from_user.id,f"план будет создан на  {date[1]} {date[2]}\n"
                               f"Вводите построчно каждый пункт в формате пункт - время\n"
                               f"Время не обязательно, если не указать, то бот не напомнит\n"
                               f"когда закончите напишите /end")
        
        
@dp.message_handler(state = Mydialog.otvet)
async def plan_drafting(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data['text'] = message.text
            user_message = data['text']
        
        if message.text == "/end":
            await state.finish()
            await bot.send_message(message.from_user.id,"План создан, посмотреть его можете с помощьюк команды /show_plan")
        else:
            plan = db.query(Plan).order_by(desc(Plan.id_plan)).first()
            a = datetime.datetime.now()
            b = a + datetime.timedelta(days=1)
            item = Item(plan = plan.id_plan, item = user_message, time_end = b, time_create = a)
            db.add(item)
            db.commit()


@dp.message_handler(commands=['start'])# отвеачет за команду старт
async def start_command(message :types.Message):
    all_plans = db.query(Plan).all()
    await message.reply(f"Хэй йоу,я бот-плановик\n ты пишешь мне свой план и я слежу что бы ты его выполнил")




@dp.message_handler(commands=['help'])# отвечает за команду help
async def help_command(message :types.Message):
    msg  = (f"Вот список всех моих комманд\n"
            f"1) plan *    - создает план на завтра, следующий месяц или год, если ничего не написать, то автоматом создаться на завтра ")
    await message.reply(msg)
    
    
if __name__ == "__main__":
    # loop = asyncio.get_event_loop()
    # loop.create_task(dt())
    executor.start_polling(dp, on_startup= on_startup)
    