

import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Optional
from inspect import iscoroutinefunction

import socketio
import uvicorn

from llm_client import LLMChatSession
from tool_funcs import TOOL_MAP

# ---------- Logging ----------
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("socketio_server")

HOST = "127.0.0.1"
PORT = 5000

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",
    ping_interval=20,
    ping_timeout=20,
    logger=False,
    engineio_logger=False,
)
app = socketio.ASGIApp(sio)

# Per-socket state
sid_to_chat: Dict[str, LLMChatSession] = {}
sid_to_room: Dict[str, str] = {}

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

@sio.event
async def connect(sid, environ, auth):
    logger.info(f"[connect] sid={sid}")
    await sio.emit("welcome_message", "Hello, I am your assistant. How can I help you?", to=sid)

@sio.event
async def disconnect(sid):
    logger.info(f"[disconnect] sid={sid}")
    room = sid_to_room.pop(sid, None)
    if room:
        try:
            await sio.leave_room(sid, room)
        except Exception:
            pass
    sid_to_chat.pop(sid, None)

# Optional: join a "room" keyed by sessionId
# Client: socket.emit('join_session', { sessionId })
@sio.on("join_session")
async def join_session(sid, payload):
    payload = payload or {}
    session_id = payload.get("sessionId")
    if not session_id:
        await sio.emit("ai_chat_response", {"data": "Missing sessionId"}, to=sid)
        return

    prev = sid_to_room.get(sid)
    if prev and prev != str(session_id):
        await sio.leave_room(sid, prev)

    sid_to_room[sid] = str(session_id)
    await sio.enter_room(sid, str(session_id))
    logger.info(f"[join_session] sid={sid} -> room={session_id}")
    await sio.emit(
        "ai_chat_response",
        {"data": f"Joined session {session_id}", "sessionId": session_id, "timestamp": now_iso()},
        to=sid,
    )

# Frontend emits: socket.emit('ai_chat_success', { message, userId, accessToken, sessionId, response?, timestamp })
@sio.on("ai_chat_success")
async def handle_ai_chat_success(sid, payload):
    payload = payload or {}
    message = payload.get("message") or payload.get("input") or ""
    user_id = payload.get("userId")
    access_token = payload.get("accessToken")
    session_id = payload.get("sessionId")
    client_ts = payload.get("timestamp")

    meta = {
        "message": message,
        "userId": user_id,
        "accessToken": access_token,
        "sessionId": session_id,
        "timestamp": client_ts,
    }
    print("--------------------------------------------")
    print(meta)
    print("--------------------------------------------")

    logger.info(f"[ai_chat_success] sid={sid} sessionId={session_id} userId={user_id} message={message!r}")

    chat = sid_to_chat.get(sid)
    if not chat:
        chat = LLMChatSession(user_id=user_id)
        sid_to_chat[sid] = chat
        
    try:
        # support both sync and async ask()
        if iscoroutinefunction(chat.ask):
            reply_text = await chat.ask(message)  # <-- NO meta here
        else:
            loop = asyncio.get_running_loop()
            reply_text = await loop.run_in_executor(None, chat.ask, message)  # <-- NO meta here
    except Exception as e:
        logger.exception("LLM error")
        reply_text = f"Sorry, I hit an error: {type(e).__name__}"

    out = {
        "data": reply_text,
        "sessionId": session_id,
        "userId": user_id,
        "message": message,
        "timestamp": client_ts or now_iso(),
    }

    # reply to this socket
    await sio.emit("ai_chat_response", out, to=sid)

    # also broadcast to the room (if using rooms)
    if session_id is not None:
        await sio.emit("ai_chat_response", out, room=str(session_id))

# Optional: simple typing passthrough
# Client: socket.emit('typing', { sessionId, username })
@sio.on("typing")
async def typing(sid, payload):
    payload = payload or {}
    session_id = payload.get("sessionId")
    if session_id is not None:
        await sio.emit("typing", payload, room=str(session_id))
    else:
        await sio.emit("typing", payload, to=sid)

if __name__ == "__main__":
    logger.info(f"Starting Socket.IO server on http://{HOST}:{PORT}")
    uvicorn.run(app, host=HOST, port=PORT)
