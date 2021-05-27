from asyncio import BaseEventLoop

import pytest

from aiogram import Bot, types
from . import FakeTelegram, TOKEN

py_test_mark = pytest.mark.asyncio


@pytest.fixture(name='bot')
async def bot_fixture():
    _bot = Bot(TOKEN, parse_mode=types.ParseMode.HTML)
    yield _bot
    await _bot.close()


@pytest.fixture()
async def message(bot):
    from .types.dataset import MESSAGE
    msg = types.Message(**MESSAGE)
    async with FakeTelegram(message_data=MESSAGE):
        _message = await bot.send_message(chat_id=msg.chat.id, text=msg.text)
    yield _message


class TestMiscCases:
    async def test_calling_bot_not_from_context(self, message):
        with pytest.raises(RuntimeError):
            await message.edit_text('test_calling_bot_not_from_context')