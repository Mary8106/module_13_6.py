from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
from config import Token

bot = Bot(token=Token)
dp = Dispatcher(bot, storage=MemoryStorage())

kb_man = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
butt_man = KeyboardButton(text='мужчина')
butt_woman = KeyboardButton(text='женщина')
kb_man.add(butt_man, butt_woman)

kb = InlineKeyboardMarkup(resize_keyboard=True)
kb1 = InlineKeyboardMarkup(resize_keyboard=True)
button = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
button1 = InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
kb.add(button, button1)


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()
    man = State()

@dp.message_handler(commands=['start'])
async def start(message):
    await message.answer('Привет! Я бот, помогающий вашему здоровью.\n'
                         'Нажмите одну из кнопок для продолжения', reply_markup=kb)

@dp.message_handler(text=['Рассчитать'], state=None)
async def main_menu(message: types.Message, state: FSMContext):
    await message.reply('Выберите опцию:', reply_markup=kb)
    await call.answer()

@dp.callback_query_handler(text=['formulas'])
async def get_formula(call: types.CallbackQuery):
    await call.message.answer('Формула расcчёта Миффлина-Сан Жеора:\n'
                              '(10*вес(кг) + 6.25*рост(см) + 5*возраст(г) + 5) - для мужчин\n'
                              '(10*вес(кг) + 6.25*рост(см) + 5*возраст(г) - 161) - для женщин')
    await call.answer()

@dp.callback_query_handler(text=['calories'])
async def set_age(call: types.CallbackQuery):
    await call.message.answer('Введите свой возраст:')
    await call.answer()
    await UserState.age.set()

@dp.message_handler(state=UserState.age)
async def set_growth(message: types.Message, state: FSMContext):
    await state.update_data(age_=message.text)
    await message.reply('Введите свой рост:')
    await UserState.growth.set()

@dp.message_handler(state=UserState.growth)
async def set_weight(message: types.Message, state: FSMContext):
    await state.update_data(growth_=message.text)
    await message.reply('Введите свой вес:')
    await UserState.weight.set()

@dp.message_handler(state=UserState.weight)
async def set_weight(message: types.Message, state: FSMContext):
    await state.update_data(weight_=message.text)
    await message.reply('Выберите свой пол (мужчина / женщина):', reply_markup=kb_man)
    await UserState.man.set()

@dp.message_handler(state=UserState.man)
async def set_calories(message: types.Message, state: FSMContext):
    await state.update_data(man_=message.text)
    data = await state.get_data()
    if str(data['man_']) == 'мужчина':
        calories = int(data['weight_']) * 10 + int(data['growth_']) * 6.25 - int(data['age_']) * 5 + 5
        await message.reply(f'Ваша норма калорий {calories} в день')
    elif str(data['man_']) == 'женщина':
        calories = int(data['weight_']) * 10 + int(data['growth_']) * 6.25 - int(data['age_']) * 5 - 161
        await message.reply(f'Ваша норма калорий {calories} в день')
    await state.finish()

@dp.message_handler(text=['Информация'])
async def inform(message):
    await message.answer("Бот поможет рассчитать суточный рацион в калориях для вашего возраста, роста, веса и пола")

@dp.message_handler()
async def all_messages(message):
    await message.answer('Введите команду /start, чтобы начать общение.')


if __name__ == '__main__':
    # запуск бота (dp - аргумент через что стартовать)
    executor.start_polling(dp, skip_updates=True)