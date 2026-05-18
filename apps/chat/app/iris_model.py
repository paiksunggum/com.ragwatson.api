import google.generativeai as genai

from ...matrix.app.keymaker import get_keymaker


class IrisModel:
    """Gemini 호출 전용 래퍼."""

    def get_model_name(self) -> str:
        return get_keymaker().gemini_model

    def generate_reply(
        self,
        history: list[dict],
        last_user_text: str,
        model_name: str | None = None,
    ) -> str:
        keymaker = get_keymaker()
        if model_name:
            model = genai.GenerativeModel(model_name)
        else:
            model = keymaker.require_gemini()
        chat = model.start_chat(history=history)
        response = chat.send_message(last_user_text)
        return response.text
