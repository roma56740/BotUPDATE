from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from app.keyboards.admin import admin_main_keyboard, get_decision_keyboard
from app.keyboards.common import role_keyboard
from app.keyboards.user import manager_menu_keyboard
from app.database import (
    get_all_users, delete_user_by_username, get_user_by_username,
    update_user_hearts, update_user_penalty, add_user
)
from app.utils import format_user_info, notify_user_by_username
from app.google_api import get_sales_plan, get_manager_stats, update_manager_username
from app.states import AdminUsernameInput, AdminHeartAction, AdminRemoveHeartState
from app.config import ADMIN_ID

admin_router = Router()

@admin_router.message(F.from_user.id == ADMIN_ID, F.text == "/admin")
async def admin_panel(msg: Message):
    await msg.answer("Добро пожаловать в админ-панель", reply_markup=admin_main_keyboard)

@admin_router.message(F.text == "Все пользователи")
async def all_users(msg: Message):
    users = get_all_users(exclude_role="Менеджер")
    if not users:
        await msg.answer("Нет обычных пользователей.")
    for u in users:
        await msg.answer(format_user_info(u))

@admin_router.message(F.text == "Удалить пользователя")
async def ask_delete(msg: Message, state: FSMContext):
    await state.set_state(AdminUsernameInput.waiting_username)
    await msg.answer("Введите @username пользователя для удаления")

@admin_router.message(AdminUsernameInput.waiting_username)
async def delete_user(msg: Message, state: FSMContext):
    username = msg.text.strip("@")
    delete_user_by_username(username)
    await msg.answer(f"Пользователь @{username} удалён.")
    await state.clear()

@admin_router.message(F.text == "План продаж")
async def sales_plan(msg: Message):
    data = get_sales_plan()
    text = "📊 План продаж:\n"
    for row in data:
        text += f"- День: {row['день']}, Месяц: {row['месяц']}\n"
    await msg.answer(text)

@admin_router.message(F.text == "Все менеджеры")
async def all_managers(msg: Message):
    users = get_all_users()
    for u in users:
        if u[2] == "Менеджер":
            gstats = get_manager_stats(u[1])
            await msg.answer(format_user_info(u) + f"\n📈 Google: {gstats or 'Нет данных'}")

@admin_router.message(F.text == "Добавить сердце")
async def add_heart_start(msg: Message, state: FSMContext):
    await state.set_state(AdminHeartAction.waiting_username)
    await msg.answer("Введите @username пользователя")

@admin_router.message(AdminHeartAction.waiting_username)
async def add_heart_reason(msg: Message, state: FSMContext):
    username = msg.text.strip("@")
    user = get_user_by_username(username)
    if not user:
        await msg.answer("Пользователь не найден.")
        return
    await state.update_data(user=user)
    await msg.answer(format_user_info(user) + "\nВведите причину добавления:")
    await state.set_state(AdminHeartAction.reason_input)

@admin_router.message(AdminHeartAction.reason_input)
async def add_heart_logic(msg: Message, state: FSMContext):
    data = await state.get_data()
    user = data['user']
    reason = msg.text
    hearts = user[4]
    penalty = user[5]
    user_id = user[0]

    if penalty > 0:
        await msg.answer(f"⚠️ У пользователя есть штраф ({penalty}). Напишите сколько вычесть:")
        await state.set_state(AdminHeartAction.penalty_amount)
        return

    if hearts >= 3:
        await msg.answer("❤️ У пользователя уже максимум сердец.")
    else:
        update_user_hearts(user_id, hearts + 1)
        await msg.answer("Сердце добавлено.")
        await notify_user_by_username(msg.bot, user[1], "❤️ Вам добавлено сердце!\nПричина: " + reason)
    await state.clear()

@admin_router.message(AdminHeartAction.penalty_amount)
async def reduce_penalty(msg: Message, state: FSMContext):
    amount = int(msg.text)
    data = await state.get_data()
    user = data['user']
    new_penalty = max(0, user[5] - amount)
    update_user_penalty(user[0], new_penalty)
    await msg.answer(f"⚖️ Штраф уменьшен. Новый штраф: {new_penalty}")
    await notify_user_by_username(msg.bot, user[1], f"🔻 Ваш штраф уменьшен на {amount}. Текущий штраф: {new_penalty}")
    await state.clear()

@admin_router.message(F.text == "Снять сердце")
async def remove_heart_start(msg: Message, state: FSMContext):
    await state.set_state(AdminRemoveHeartState.waiting_username)
    await msg.answer("Введите @username пользователя")

@admin_router.message(AdminRemoveHeartState.waiting_username)
async def remove_heart_reason(msg: Message, state: FSMContext):
    username = msg.text.strip("@")
    user = get_user_by_username(username)
    if not user:
        await msg.answer("Пользователь не найден.")
        return
    await state.update_data(user=user)
    await msg.answer(format_user_info(user) + "\nВведите причину удаления:")
    await state.set_state(AdminRemoveHeartState.reason_input)

@admin_router.message(AdminRemoveHeartState.reason_input)
async def remove_heart_logic(msg: Message, state: FSMContext):
    data = await state.get_data()
    user = data['user']
    reason = msg.text
    hearts = user[4]
    user_id = user[0]

    if hearts > 0:
        update_user_hearts(user_id, hearts - 1)
        await msg.answer("Сердце удалено.")
        await notify_user_by_username(msg.bot, user[1], "❌ У вас удалено сердце.\nПричина: " + reason)
    else:
        await msg.answer("У пользователя 0 сердец. Введите причину штрафа:")
        await state.set_state(AdminRemoveHeartState.penalty_reason)
        return
    await state.clear()

@admin_router.message(AdminRemoveHeartState.penalty_reason)
async def penalty_reason_input(msg: Message, state: FSMContext):
    await state.update_data(penalty_reason=msg.text)
    await msg.answer("Введите размер штрафа:")
    await state.set_state(AdminRemoveHeartState.penalty_value)

@admin_router.message(AdminRemoveHeartState.penalty_value)
async def add_penalty(msg: Message, state: FSMContext):
    amount = int(msg.text)
    data = await state.get_data()
    user = data['user']
    new_penalty = user[5] + amount
    update_user_penalty(user[0], new_penalty)
    await msg.answer(f"Штраф добавлен. Новый штраф: {new_penalty}")
    await notify_user_by_username(msg.bot, user[1],
        f"⚠️ Вам добавлен штраф: {amount}\nПричина: {data['penalty_reason']}")
    await state.clear()

@admin_router.callback_query(F.data.startswith("approve_reg:"))
async def approve_manager(callback: CallbackQuery):
    _, user_id, name = callback.data.split(":")
    user_id = int(user_id)
    tg_user = await callback.bot.get_chat(user_id)

    # ✅ Добавляем username в Google таблицу
    update_manager_username(name, tg_user.username)

    add_user(user_id, tg_user.username, "Менеджер", name)
    await callback.bot.send_message(
        user_id,
        "Ваша заявка одобрена! Вы зарегистрированы как менеджер.",
        reply_markup=manager_menu_keyboard
    )
    await callback.message.edit_text("✅ Менеджер зарегистрирован")

@admin_router.callback_query(F.data.startswith("decline_reg:"))
async def decline_manager(callback: CallbackQuery):
    _, user_id = callback.data.split(":")
    user_id = int(user_id)
    await callback.bot.send_message(
        user_id,
        "❌ Ваша заявка отклонена. Попробуйте выбрать роль заново.",
        reply_markup=role_keyboard
    )
    await callback.message.edit_text("Отклонено")


from app.database import get_user_by_username, update_user_hearts
from app.utils import notify_user_by_username

@admin_router.callback_query(F.data.startswith("approve_heart:"))
async def approve_heart(callback: CallbackQuery):
    try:
        _, from_user, to_user, *desc_parts = callback.data.split(":")
        description = ":".join(desc_parts)
        to_user_data = get_user_by_username(to_user)
        if not to_user_data:
            await callback.message.edit_text(f"⛔ Пользователь @{to_user} не найден.")
            return

        current_hearts = to_user_data[4]
        if current_hearts >= 3:
            await callback.message.edit_text(f"❗ У @{to_user} уже максимум ❤️ (3/3).")
            return

        update_user_hearts(to_user_data[0], current_hearts + 1)

        await notify_user_by_username(callback.bot, to_user, f"❤️ Вам добавлено сердце за помощь от @{from_user}!\n📎 {description}")
        await callback.bot.send_message(to_user_data[0], "✅ Ваше сердце одобрено администратором.")
        await callback.message.edit_text("✅ Сердце добавлено.")
    except Exception as e:
        await callback.message.edit_text(f"⚠️ Ошибка при обработке: {e}")

@admin_router.callback_query(F.data.startswith("decline_heart:"))
async def decline_heart(callback: CallbackQuery):
    _, from_user, to_user = callback.data.split(":")
    await notify_user_by_username(callback.bot, from_user, f"❌ Заявка на помощь @{to_user} была отклонена админом.")
    await callback.message.edit_text("❌ Заявка отклонена.")
