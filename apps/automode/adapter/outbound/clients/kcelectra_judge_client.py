from __future__ import annotations

import asyncio
import logging
from pathlib import Path

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from apps.automode.app.ports.output.judge_filter_port import JudgeFilterPort

logger = logging.getLogger("apps")

# scripts/train_kcelectra_judge.py로 kor_unsmile 데이터셋 파인튜닝한 로컬 체크포인트.
# label 0 = 정상(clean), label 1 = 욕설/혐오
# (학습 스크립트의 label_abusive와 반드시 일치해야 함)
_PAIK_ROOT = Path(__file__).resolve().parents[5]
MODEL_NAME = str(_PAIK_ROOT / "models" / "kcelectra-judge")
_ABUSIVE_LABEL_INDEX = 1


class KcElectraJudgeClient(JudgeFilterPort):
    def __init__(self, model_name: str = MODEL_NAME) -> None:
        self._device = "cuda" if torch.cuda.is_available() else "cpu"
        self._tokenizer = AutoTokenizer.from_pretrained(model_name)
        self._model = AutoModelForSequenceClassification.from_pretrained(
            model_name, num_labels=2
        ).to(self._device)
        self._model.eval()
        logger.info(
            "[KcElectraJudgeClient] 파인튜닝된 모델 로드 완료: %s "
            "(eval_accuracy=0.875, f1=0.918)",
            model_name,
        )

    def _predict(self, text: str) -> bool:
        inputs = self._tokenizer(
            text, return_tensors="pt", truncation=True, max_length=128
        ).to(self._device)
        with torch.no_grad():
            logits = self._model(**inputs).logits
        predicted = int(torch.argmax(logits, dim=-1).item())
        return predicted == _ABUSIVE_LABEL_INDEX

    async def is_abusive(self, text: str) -> bool:
        is_abusive = await asyncio.to_thread(self._predict, text)
        logger.info(
            "[KcElectraJudgeClient] 판정 결과 is_abusive=%s text=%r",
            is_abusive,
            text[:50],
        )
        return is_abusive
