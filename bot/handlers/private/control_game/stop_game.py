from aiogram.dispatcher.router import Router
from bot.filters.chat_type import ChatType
from magic_filter import F
from aiogram import types, Bot
from bot.services.repo import SQLAlchemyRepo, GameRepo, ScriptRepo
from aiogram.fsm.context import FSMContext
from bot.texts.private.control_game import tx_control_game
from bot.keyboards.private.control_game import kb_control_game
from .control_game_panel import control_game
from bot.engine import game_api
from apscheduler.schedulers.asyncio import AsyncIOScheduler


stop_game_router = Router()
stop_game_router.message.bind_filter(ChatType)


@stop_game_router.callback_query(F.data == "stop_game")
async def stop_game(call: types.CallbackQuery, repo: SQLAlchemyRepo):
    await call.answer()
    await call.message.delete()
    await call.message.answer(text=await tx_control_game.stop_game_text(repo=repo),
                              reply_markup=await kb_control_game.stop_game())


@stop_game_router.callback_query(kb_control_game.CompleteCallback.filter(F.check))
async def stop_game(call: types.CallbackQuery, repo: SQLAlchemyRepo,
                    state: FSMContext, bot: Bot, scheduler: AsyncIOScheduler):
    await call.answer()
    idx = await repo.get_repo(ScriptRepo).get_script_id()
    await repo.get_repo(GameRepo).stop_game(game_id=idx)
    await game_api.stop_game(repo=repo, bot=bot, scheduler=scheduler)
    await control_game(call=call, repo=repo)


@stop_game_router.callback_query(kb_control_game.CompleteCallback.filter(F.check.is_(False)))
async def not_stop_game(call: types.CallbackQuery, repo: SQLAlchemyRepo, state: FSMContext):
    await call.answer()
    await control_game(call=call, repo=repo)



