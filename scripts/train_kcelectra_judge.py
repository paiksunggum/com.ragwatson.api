"""
KcELECTRA-base를 Korean Unsmile Dataset(smilegate-ai/kor_unsmile)으로
욕설/혐오표현 이진 분류(clean=0 / abusive=1)로 파인튜닝하는 스크립트.

실행: python scripts/train_kcelectra_judge.py
출력: ./models/kcelectra-judge/ 에 파인튜닝된 체크포인트 저장
      (kcelectra_judge_client.py의 MODEL_NAME을 이 경로로 바꾸면 적용됨)
"""

from __future__ import annotations

import numpy as np
import torch
from datasets import load_dataset
from sklearn.metrics import accuracy_score, f1_score
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
)

BASE_MODEL = "beomi/KcELECTRA-base"
OUTPUT_DIR = "./models/kcelectra-judge"
MAX_LENGTH = 128


def label_abusive(example: dict) -> dict:
    # clean == 1 이면 정상(0), 그 외(혐오/욕설 카테고리 중 하나라도 1)면 abusive(1)
    example["label"] = 0 if example["clean"] == 1 else 1
    return example


def compute_metrics(eval_pred) -> dict:
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    return {
        "accuracy": accuracy_score(labels, predictions),
        "f1": f1_score(labels, predictions),
    }


def main() -> None:
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    print(f"device={device}")

    dataset = load_dataset("smilegate-ai/kor_unsmile")
    dataset = dataset.map(label_abusive)

    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)

    def tokenize(batch: dict) -> dict:
        return tokenizer(
            batch["문장"], truncation=True, max_length=MAX_LENGTH, padding="max_length"
        )

    dataset = dataset.map(tokenize, batched=True)
    dataset = dataset.remove_columns(
        [
            "문장",
            "여성/가족",
            "남성",
            "성소수자",
            "인종/국적",
            "연령",
            "지역",
            "종교",
            "기타 혐오",
            "악플/욕설",
            "clean",
            "개인지칭",
            "labels",
        ]
    )
    dataset.set_format("torch")

    model = AutoModelForSequenceClassification.from_pretrained(
        BASE_MODEL, num_labels=2
    ).to(device)

    args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=3,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=32,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        logging_steps=50,
        report_to="none",
    )

    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=dataset["train"],
        eval_dataset=dataset["valid"],
        compute_metrics=compute_metrics,
    )

    trainer.train()
    metrics = trainer.evaluate()
    print("최종 평가 결과:", metrics)

    trainer.save_model(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)
    print(f"저장 완료: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
