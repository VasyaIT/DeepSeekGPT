from json import loads, dumps
from typing import AsyncGenerator

from aiohttp import ClientSession

from bot.infrastructure.deepseek.const import DEEPSEEK_API_URL, REQUEST_HEADERS


async def generate_answer(prompt: str, chat_id: str, parent_message_id: int | None) -> AsyncGenerator[tuple[str, int], None]:
    data = (
        f'''{{"chat_session_id":{dumps(chat_id)},"parent_message_id":{dumps(parent_message_id)},"prompt":{
            dumps(prompt, ensure_ascii=False)},"ref_file_ids":[],"thinking_enabled":false}}'''
    )

    async with ClientSession(headers=REQUEST_HEADERS) as session:
        async with session.post(f"{DEEPSEEK_API_URL}/chat/completion", data=data) as response:
            async for line in response.content:
                chunk = line.decode('utf-8').split("data: ")[-1].strip()
                if not chunk:
                    continue
                if chunk == "[DONE]":
                    break
                chunk_data = loads(chunk.strip())
                try:
                    yield chunk_data["choices"][0]["delta"]["content"], chunk_data.get("message_id", 0)
                except KeyError:
                    continue


async def create_new_chat() -> str:
    async with ClientSession(headers=REQUEST_HEADERS) as session:
        async with session.post(f"{DEEPSEEK_API_URL}/chat_session/create", data='{"agent":"chat"}') as response:
            data = await response.json()
    return data["data"]["biz_data"]["id"]


async def delete_chat_session(chat_id: str) -> None:
    data = f'''{{"chat_session_id":{dumps(chat_id)}}}'''
    async with ClientSession(headers=REQUEST_HEADERS) as session:
        async with session.post(f"{DEEPSEEK_API_URL}/chat_session/delete", data=data):
            pass
