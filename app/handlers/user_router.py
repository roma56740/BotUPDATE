from aiogram import Router, F
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, CallbackQuery
from aiogram.fsm.context import FSMContext
from app.keyboards import common, user, admin
from app.states import RegistrationState, HelpColleagueState
from app.database import add_user, get_user, get_user_by_username
from app.google_api import get_manager_names, get_manager_stats
from app.config import ADMIN_ID
from app.utils import format_user_info
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

user_router = Router()

# ─────────────── /start ───────────────

@user_router.message(F.text == "/start")
async def start_handler(msg: Message, state: FSMContext):
    if msg.from_user.id == ADMIN_ID:
        await msg.answer("👑 Вы администратор.", reply_markup=admin.admin_main_keyboard)
        return

    user = get_user(msg.from_user.id)
    if user:
        role = user[2]
        if role == "Менеджер":
            await msg.answer("Вы в меню менеджера", reply_markup=user.manager_menu_keyboard)
        else:
            await msg.answer("Вы в главном меню", reply_markup=common.main_menu_keyboard)
    else:
        await state.set_state(RegistrationState.choosing_role)
        await msg.answer("Выберите вашу роль:", reply_markup=common.role_keyboard)

# ─────────────── Регистрация ───────────────

@user_router.message(RegistrationState.choosing_role)
async def choose_role(msg: Message, state: FSMContext):
    role = msg.text
    if role == "Менеджер":
        managers = get_manager_names()
        buttons = [[KeyboardButton(text=name)] for name in managers]
        await state.set_state(RegistrationState.choosing_manager_name)
        await msg.answer("Выберите своё имя:", reply_markup=ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True))
    else:
        add_user(msg.from_user.id, msg.from_user.username, role, msg.from_user.full_name)
        await msg.answer("Вы зарегистрированы!", reply_markup=common.main_menu_keyboard)
        await state.clear()

@user_router.message(RegistrationState.choosing_manager_name)
async def choose_manager_name(msg: Message, state: FSMContext):
    manager_name = msg.text
    text = (
        f"🆕 Заявка на регистрацию менеджера\n"
        f"👤 @{msg.from_user.username} ({msg.from_user.full_name})\n"
        f"Имя в таблице: {manager_name}"
    )
    markup = admin.get_decision_keyboard(
        f"approve_reg:{msg.from_user.id}:{manager_name}",
        f"decline_reg:{msg.from_user.id}"
    )
    await msg.bot.send_message(ADMIN_ID, text, reply_markup=markup)
    await msg.answer("Заявка отправлена админу на рассмотрение.")
    await state.clear()

# ─────────────── Профиль ───────────────

@user_router.message(F.text == "Профиль")
async def profile_handler(msg: Message):
    user = get_user(msg.from_user.id)
    if user:
        await msg.answer(format_user_info(user))
    else:
        await msg.answer("Вы ещё не зарегистрированы. Нажмите /start")

# ─────────────── Моя статистика ───────────────

@user_router.message(F.text == "Моя статистика")
async def manager_stats(msg: Message):
    user = get_user(msg.from_user.id)
    if not user or user[2] != "Менеджер":
        await msg.answer("⛔ Эта команда доступна только менеджерам.")
        return

    stats = get_manager_stats(user[1])  # user[1] — username
    if not stats:
        await msg.answer("Google: Нет данных по вашей статистике.")
        return

    text = (
        f"📊 Статистика менеджера @{user[1]}:\n"
        f"Взято заказов: {stats.get('Взято', 0)}\n"
        f"Закрыто заказов: {stats.get('Закрыто', 0)}\n"
        f"Конверсия: {stats.get('Конверсия', '—')}\n"
        f"Сумма: {stats.get('Сумма', 0)}"
    )
    await msg.answer(text)

# ─────────────── Помог коллеге ───────────────

@user_router.message(F.text == "Помог коллеге")
async def help_colleague_start(msg: Message, state: FSMContext):
    await state.set_state(HelpColleagueState.entering_description)
    await msg.answer("📝 Напишите, как вы помогли коллеге:")

@user_router.message(HelpColleagueState.entering_description)
async def help_colleague_description(msg: Message, state: FSMContext):
    await state.update_data(description=msg.text)
    await state.set_state(HelpColleagueState.entering_username)
    await msg.answer("👤 Напишите @username коллеги, кому добавить сердце:")

@user_router.message(HelpColleagueState.entering_username)
async def help_colleague_username(msg: Message, state: FSMContext):
    data = await state.get_data()
    description = data.get("description")
    target_username = msg.text.strip("@")

    text = (
        f"📩 Заявка на помощь коллеге\n"
        f"👤 От: @{msg.from_user.username} ({msg.from_user.full_name})\n"
        f"👉 Кому: @{target_username}\n"
        f"📝 Описание: {description}"
    )

    markup = admin.get_decision_keyboard(
        f"approve_heart:{msg.from_user.username}:{target_username}:{description}",
        f"decline_heart:{msg.from_user.username}:{target_username}"
    )

    await msg.bot.send_message(ADMIN_ID, text, reply_markup=markup)
    await msg.answer("Заявка на добавление сердца отправлена админу.")
    await state.clear()
