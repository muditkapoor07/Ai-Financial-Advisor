"""
FINAI Web Server
================
FastAPI-based web interface for the AI Financial Advisor agent.
Serves a chat UI at GET / and handles real-time agent turns over WebSocket.

Run:
    uvicorn app:app --host 0.0.0.0 --port 8000 --reload

Requires:
    GROQ_API_KEY (and optionally MODEL) in .env
"""

import os
import sys
import json
import traceback
from pathlib import Path

# ── Ensure the project root is on sys.path so agent.py imports work ──────────
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv()

from groq import Groq
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

# ── Import everything we need from agent.py ───────────────────────────────────
from agent import TOOLS, TOOL_MAP, SYSTEM_PROMPT, execute_tool, _sanitize_params

# ─────────────────────────────────────────────────────────────────────────────
# Groq client
# ─────────────────────────────────────────────────────────────────────────────

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL = os.getenv("MODEL", "llama-3.3-70b-versatile")

client = Groq(api_key=GROQ_API_KEY)

# ─────────────────────────────────────────────────────────────────────────────
# FastAPI app
# ─────────────────────────────────────────────────────────────────────────────

app = FastAPI(title="FINAI — AI Financial Advisor", version="1.0.0")

# Mount static files directory (serves index.html, CSS, JS assets)
STATIC_DIR = ROOT / "static"
STATIC_DIR.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", response_class=FileResponse)
async def serve_index():
    """Serve the main chat UI."""
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path), media_type="text/html")
    return HTMLResponse("<h1>index.html not found in static/</h1>", status_code=404)


# ─────────────────────────────────────────────────────────────────────────────
# Agent loop (WebSocket-aware)
# ─────────────────────────────────────────────────────────────────────────────

async def run_agent_turn_ws(websocket: WebSocket, messages: list) -> str:
    """
    Run the full agent loop for one user turn.
    Sends incremental JSON messages to the WebSocket client:
      - {"type": "tool_call",   "name": "...", "input": {...}}
      - {"type": "tool_result", "name": "...", "ok": true/false}
      - {"type": "response",    "text": "..."}
      - {"type": "error",       "message": "..."}
    Returns the final assistant text (empty string on error).
    """
    full_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages

    while True:
        # ── Call Groq ─────────────────────────────────────────────────────────
        response = client.chat.completions.create(
            model=MODEL,
            messages=full_messages,
            tools=TOOLS,
            tool_choice="auto",
            max_tokens=8096,
        )

        message = response.choices[0].message
        finish_reason = response.choices[0].finish_reason

        # ── Final response (no more tool calls) ───────────────────────────────
        if finish_reason == "stop" or not message.tool_calls:
            final_text = message.content or ""
            await websocket.send_json({"type": "response", "text": final_text})
            return final_text

        # ── Tool call round ───────────────────────────────────────────────────
        if message.tool_calls:
            # Append the assistant's "I want to call these tools" message
            full_messages.append({
                "role": "assistant",
                "content": message.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in message.tool_calls
                ],
            })

            # Execute each tool and feed results back
            for tc in message.tool_calls:
                tool_name = tc.function.name

                try:
                    tool_input = json.loads(tc.function.arguments)
                except json.JSONDecodeError:
                    tool_input = {}

                tool_input = _sanitize_params(tool_input)

                # Notify client: tool is being called
                await websocket.send_json({
                    "type": "tool_call",
                    "name": tool_name,
                    "input": tool_input,
                })

                # Run the tool
                result_str = execute_tool(tool_name, tool_input)

                try:
                    result = json.loads(result_str)
                    ok = "error" not in result
                except Exception:
                    ok = False

                # Notify client: tool result
                await websocket.send_json({
                    "type": "tool_result",
                    "name": tool_name,
                    "ok": ok,
                })

                # Feed result back to the model
                full_messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result_str,
                })

            # Loop → model will now produce its final response (or call more tools)
            continue

        # Fallback (should not happen)
        fallback = message.content or f"[Unexpected finish_reason: {finish_reason}]"
        await websocket.send_json({"type": "response", "text": fallback})
        return fallback


# ─────────────────────────────────────────────────────────────────────────────
# WebSocket endpoint
# ─────────────────────────────────────────────────────────────────────────────

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint. Each connection maintains its own conversation history.
    Expects plain-text user messages; sends back JSON event objects.
    """
    await websocket.accept()

    # Per-connection conversation history (excludes system prompt)
    conversation: list[dict] = []

    try:
        while True:
            # Receive the next user message
            user_text = await websocket.receive_text()
            user_text = user_text.strip()

            if not user_text:
                continue

            # Append to history
            conversation.append({"role": "user", "content": user_text})

            try:
                # Run agent turn — sends WS events internally
                final_response = await run_agent_turn_ws(websocket, conversation)
                # Store assistant reply in history
                if final_response:
                    conversation.append({"role": "assistant", "content": final_response})

            except Exception as exc:
                err_msg = f"Agent error: {str(exc)}"
                tb = traceback.format_exc()
                print(f"[ERROR] {err_msg}\n{tb}", file=sys.stderr)
                try:
                    await websocket.send_json({"type": "error", "message": err_msg})
                except Exception:
                    pass  # Connection may have closed

    except WebSocketDisconnect:
        # Client disconnected — clean up silently
        pass
    except Exception as exc:
        print(f"[WS ERROR] {exc}\n{traceback.format_exc()}", file=sys.stderr)
        try:
            await websocket.send_json({"type": "error", "message": str(exc)})
        except Exception:
            pass


# ─────────────────────────────────────────────────────────────────────────────
# Entry point (direct run)
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    if not GROQ_API_KEY:
        print("ERROR: GROQ_API_KEY is not set. Add it to your .env file.", file=sys.stderr)
        sys.exit(1)

    print("Starting FINAI Web Server at http://0.0.0.0:8000")
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
