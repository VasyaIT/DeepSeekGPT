from json import loads, dumps

from aiohttp import ClientSession

from bot.infrastructure.deepseek.const import DEEPSEEK_API_URL, REQUEST_HEADERS


async def generate_answer(prompt: str, chat_id: str, parent_message_id: int | None) -> tuple[str, int]:
    data = (
        f'''{{"chat_session_id":{dumps(chat_id)},"parent_message_id":{dumps(parent_message_id)},"prompt":{
            dumps(prompt, ensure_ascii=False)},"ref_file_ids":[],"thinking_enabled":false}}'''
    )

    async with ClientSession(headers=REQUEST_HEADERS) as session:
        async with session.post(f"{DEEPSEEK_API_URL}/chat/completion", data=data) as response:
            text = await response.text()

    message, next_parent_message_id = "", 0
    for chunk in text.split("data: "):
        if not chunk.strip():
            continue
        if chunk.strip() == "[DONE]":
            break
        chunk_data = loads(chunk.strip())

        try:
            message += chunk_data["choices"][0]["delta"]["content"]
        except KeyError:
            continue
        next_parent_message_id = chunk_data["message_id"]
    return message, next_parent_message_id


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
