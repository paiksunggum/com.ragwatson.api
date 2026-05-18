"""GET /chat 브라우저용 단순 채팅 HTML."""

FAST_MODEL = "gemini-2.5-flash"


def chat_page_html() -> str:
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>RagWatson Chat</title>
  <style>
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: system-ui, -apple-system, sans-serif;
      background: #f8fafc;
      color: #0f172a;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }}
    header {{
      padding: 1rem 1.25rem;
      border-bottom: 1px solid #e2e8f0;
      background: #fff;
    }}
    header h1 {{ margin: 0; font-size: 1.125rem; }}
    header p {{ margin: 0.25rem 0 0; font-size: 0.875rem; color: #64748b; }}
    #messages {{
      flex: 1;
      overflow-y: auto;
      padding: 1rem 1.25rem;
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
    }}
    .bubble {{
      max-width: 85%;
      padding: 0.65rem 0.9rem;
      border-radius: 1rem;
      line-height: 1.5;
      white-space: pre-wrap;
      word-break: break-word;
    }}
    .user {{ align-self: flex-end; background: #2563eb; color: #fff; }}
    .assistant {{ align-self: flex-start; background: #fff; border: 1px solid #e2e8f0; }}
    #error {{
      display: none;
      margin: 0 1.25rem;
      padding: 0.75rem 1rem;
      background: #fef2f2;
      color: #b91c1c;
      border-radius: 0.5rem;
      font-size: 0.875rem;
    }}
    form {{
      display: flex;
      gap: 0.5rem;
      padding: 1rem 1.25rem;
      border-top: 1px solid #e2e8f0;
      background: #fff;
    }}
    #input {{
      flex: 1;
      padding: 0.75rem 1rem;
      border: 1px solid #cbd5e1;
      border-radius: 999px;
      font-size: 1rem;
      outline: none;
    }}
    #input:focus {{ border-color: #2563eb; }}
    button {{
      padding: 0.75rem 1.25rem;
      border: none;
      border-radius: 999px;
      background: #2563eb;
      color: #fff;
      font-size: 1rem;
      cursor: pointer;
    }}
    button:disabled {{ opacity: 0.5; cursor: not-allowed; }}
  </style>
</head>
<body>
  <header>
    <h1>Titanic QA Assistant</h1>
    <p>빠른 모델 ({FAST_MODEL})</p>
  </header>
  <div id="messages"></div>
  <div id="error"></div>
  <form id="form">
    <input id="input" type="text" placeholder="Gemini에게 물어보기" autocomplete="off" />
    <button type="submit" id="send">전송</button>
  </form>
  <script>
    const MODEL = "{FAST_MODEL}";
    const messagesEl = document.getElementById("messages");
    const errorEl = document.getElementById("error");
    const form = document.getElementById("form");
    const input = document.getElementById("input");
    const sendBtn = document.getElementById("send");
    const thread = [];

    function showError(msg) {{
      errorEl.textContent = msg;
      errorEl.style.display = msg ? "block" : "none";
    }}

    function appendBubble(role, text) {{
      const el = document.createElement("div");
      el.className = "bubble " + role;
      el.textContent = text;
      messagesEl.appendChild(el);
      messagesEl.scrollTop = messagesEl.scrollHeight;
    }}

    form.addEventListener("submit", async (e) => {{
      e.preventDefault();
      const text = input.value.trim();
      if (!text) return;

      showError("");
      input.value = "";
      input.disabled = true;
      sendBtn.disabled = true;

      thread.push({{ role: "user", text }});
      appendBubble("user", text);

      try {{
        const res = await fetch("/chat", {{
          method: "POST",
          headers: {{ "Content-Type": "application/json" }},
          body: JSON.stringify({{ messages: thread, model: MODEL }}),
        }});
        const data = await res.json();
        if (!res.ok) {{
          const detail = typeof data.detail === "string" ? data.detail : "요청에 실패했습니다.";
          throw new Error(detail);
        }}
        thread.push({{ role: "assistant", text: data.answer }});
        appendBubble("assistant", data.answer);
      }} catch (err) {{
        thread.pop();
        showError(err.message || "알 수 없는 오류");
      }} finally {{
        input.disabled = false;
        sendBtn.disabled = false;
        input.focus();
      }}
    }});
  </script>
</body>
</html>"""
