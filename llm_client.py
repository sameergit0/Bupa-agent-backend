# from google import genai
# from tool_config import GEMINI_API_KEY, CONFIG
# from tool_funcs import TOOL_MAP
# from google.genai import types

# client = genai.Client(api_key=GEMINI_API_KEY)
# contents = []

# def web_io(input: str)-> str:
#     while True:
#         user_input = f"User: {input}"
#         contents.append(types.Content(role="user", parts=[types.Part(text=user_input)]))

#         while True:
#             resp = client.models.generate_content(
#                 model="gemini-2.5-flash",
#                 contents=contents,
#                 config=CONFIG
#             )
#             content = resp.candidates[0].content

#             part = None
#             if getattr(content, "parts", None):
#                 part = content.parts[0]

#             if part and getattr(part, "function_call", None):
#                 name, args = part.function_call.name, part.function_call.args
#                 print("Function name", name)
#                 func = TOOL_MAP.get(name)
#                 if not func:
#                     raise RuntimeError(f"No implementation for tool '{name}'")
                
#                 result = func(**args)

#                 contents.append(content)  # this has the function_call
#                 contents.append(types.Content(
#                     role="function",
#                     parts=[types.Part.from_function_response(name=name, response=result)]
#                 ))
#                 continue
#             break

#         contents.append(content)
#         if part:
#             return part.text
#         else:
#             return "Try Again!"

from datetime import datetime
import logging
import time
import random
from typing import Any, Dict, Optional

from google import genai
from google.genai import types
from google.genai.errors import ClientError

from tool_config import GEMINI_API_KEY, TOOLS
from tool_funcs import TOOL_MAP
from constants import DynamicConstants
from system_prompt import get_system_prompt

logger = logging.getLogger("llm_client")
logger.setLevel(logging.INFO)

MODEL_NAME = "gemini-2.5-flash"
MAX_TOOL_STEPS = 8
MAX_RETRIES = 5
BASE_BACKOFF = 0.5
BACKOFF_CAP = 8.0

_client = genai.Client(api_key=GEMINI_API_KEY)

def _sleep_with_jitter(base: float, attempt: int) -> None:
    delay = min(BACKOFF_CAP, base * (2 ** (attempt - 1)))
    delay = delay * (0.5 + random.random())
    print(f"[retry] sleeping {delay:.2f}s before attempt {attempt+1}")
    time.sleep(delay)

class LLMChatSession:
    def __init__(self, user_id: str, access_token: str):
        self.user_id = user_id
        self.access_token = access_token
        self.dynamic_constants = DynamicConstants(user_id, access_token)
        self.dynamic_constants.load()
        
        session_tool_map = {}
        for name, func in TOOL_MAP.items():
            session_tool_map[name] = lambda *args, func=func, **kwargs: func(self.dynamic_constants, *args, **kwargs)
            
        self.tool_map = session_tool_map
        self.contents: list[types.Content] = []
        
        system_prompt = get_system_prompt(self.dynamic_constants)
        self.config = types.GenerateContentConfig(
            tools=TOOLS,
            system_instruction=types.Content(role="system", parts=[types.Part(text=system_prompt)])
        )

    def _generate_with_retries(self, req_contents: list[types.Content]):
        last_err = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                print(f"[llm] attempt {attempt}, contents len={len(req_contents)}")
                resp = _client.models.generate_content(
                    model=MODEL_NAME,
                    contents=req_contents,
                    config=self.config
                )
                # minimal sanity prints
                has_cands = bool(getattr(resp, "candidates", None))
                print(f"[llm] got response, candidates={has_cands}")
                return resp
            except ClientError as e:
                code = getattr(e, "code", None)
                print(f"[llm] ClientError code={code} msg={getattr(e,'message',str(e))}")
                last_err = e
                if code and int(code) in (400, 401, 403):
                    break
            except Exception as e:
                print(f"[llm] Unexpected error: {type(e).__name__}: {e}")
                last_err = e
            if attempt < MAX_RETRIES:
                _sleep_with_jitter(BASE_BACKOFF, attempt)
        if last_err:
            raise last_err

    def _safe_text_from_content(self, content: types.Content) -> str:
        texts = []
        if getattr(content, "parts", None):
            for p in content.parts:
                t = getattr(p, "text", None)
                if t:
                    texts.append(t)
        return "\n".join(texts).strip() if texts else "No text response."

    def ask(self, user_message: str) -> str:
        try:
            print(f"[ask] User says: {user_message}")
            user_part = types.Part(text=f"User: {user_message}")
            self.contents.append(types.Content(role="user", parts=[user_part]))
            print(f"[ask] contents now has {len(self.contents)} messages")

            for step in range(MAX_TOOL_STEPS):
                print(f"[loop] step {step+1}/{MAX_TOOL_STEPS}")
                resp = self._generate_with_retries(self.contents)
                if not resp or not getattr(resp, "candidates", None):
                    print("[loop] no candidates, returning Try Again!")
                    return "Try Again!"

                content = resp.candidates[0].content
                if not content:
                    print("[loop] empty content, returning Try Again!")
                    return "Try Again!"

                # inspect for function call
                part = content.parts[0] if getattr(content, "parts", None) else None
                function_call = getattr(part, "function_call", None) if part else None

                if function_call:
                    name = getattr(function_call, "name", None)
                    args = getattr(function_call, "args", {}) or {}
                    print(f"[tool] model wants to call: {name} with args={args}")

                    if not name:
                        print("[tool] missing tool name; bail")
                        return "Try Again!"

                    func = self.tool_map.get(name)
                    if not func:
                        print(f"[tool] not implemented: {name}")
                        return f"Tool '{name}' is not implemented."

                    try:
                        result = func(**args)
                        print(f"[tool] result: {result}")
                    except Exception as e:
                        print(f"[tool] error in {name}: {e}")
                        result = {"error": f"Tool '{name}' failed", "detail": str(e)}

                    # append tool call (model) and tool result (function) back
                    self.contents.append(content)
                    self.contents.append(types.Content(
                        role="function",
                        parts=[types.Part.from_function_response(name=name, response=result)]
                    ))
                    print(f"[tool] appended tool result; contents size={len(self.contents)}")
                    continue

                # final text
                final_text = self._safe_text_from_content(content)
                print(f"[final] {final_text}")
                self.contents.append(content)
                print("--------------------------------------------")
                print(f"model's response: {final_text}")
                print("--------------------------------------------")
                print("Start time", datetime.now())
                return final_text

            print("[loop] reached MAX_TOOL_STEPS")
            return "The request required too many tool steps. Please try a simpler request."

        except Exception as e:
            print(f"[ask] Fatal error: {type(e).__name__}: {e}")
            return f"Internal error: {type(e).__name__}: {str(e)}"

def web_io(input: str) -> str:
    session = LLMChatSession(tool_map=TOOL_MAP)
    return session.ask(input)
