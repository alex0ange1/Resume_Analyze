import torch
from pathlib import Path
from datasets import load_from_disk
from transformers import (
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
    AutoTokenizer
)
import numpy as np
from sklearn.metrics import accuracy_score, f1_score


MODEL_NAME = "DeepPavlov/rubert-base-cased"
NUM_LABELS = 3   # классы: 0,1,2


def compute_metrics(pred):
    logits, labels = pred
    preds = np.argmax(logits, axis=1)

    acc = accuracy_score(labels, preds)
    f1_macro = f1_score(labels, preds, average="macro")

    return {
        "accuracy": acc,
        "f1_macro": f1_macro
    }


def main():
    base_dir = Path(__file__).resolve().parent.parent
    data_dir = base_dir / "data"
    tokenized_dir = data_dir / "tokenized_dataset"

    train_path = tokenized_dir / "train"
    val_path = tokenized_dir / "validation"

    # 1️⃣ Загружаем токенизированные датасеты
    train_dataset = load_from_disk(train_path)
    val_dataset = load_from_disk(val_path)

    # 2️⃣ Загружаем токенизатор и модель
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME,
        num_labels=NUM_LABELS
    )

    # 3️⃣ Class Weights на основе тренировочного датасета
    # Class weights на основе тренировочного датасета
    labels = np.array(train_dataset["labels"])
    min_label = labels.min()
    labels = labels - min_label

    train_dataset = train_dataset.map(lambda x: {"labels": x["labels"] - min_label})
    val_dataset = val_dataset.map(lambda x: {"labels": x["labels"] - min_label})

    class_counts = np.bincount(labels, minlength=NUM_LABELS)
    class_weights = 1.0 / class_counts
    class_weights = class_weights / class_weights.sum() * NUM_LABELS

    # Преобразуем в тензор PyTorch
    class_weights = torch.tensor(class_weights, dtype=torch.float)
    print(f"Class weights = {class_weights}")

    # передаём веса в loss через Trainer
    def custom_loss(model, inputs, return_outputs=False, **kwargs):
        labels = inputs["labels"]
        outputs = model(**inputs)
        logits = outputs.logits

        loss_fct = torch.nn.CrossEntropyLoss(weight=class_weights.to(logits.device))
        loss = loss_fct(logits, labels)

        if return_outputs:
            # Trainer хочет вернуть (loss, outputs)
            return loss, outputs

        return loss

    # 4️⃣ Папка для чекпоинтов
    checkpoints_dir = data_dir / "checkpoints"
    checkpoints_dir.mkdir(exist_ok=True)

    # 5️⃣ TrainingArguments
    training_args = TrainingArguments(
        output_dir=str(checkpoints_dir),
        eval_strategy="epoch",
        save_strategy="epoch",
        logging_steps=50,
        learning_rate=3e-5,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        num_train_epochs=5,
        weight_decay=0.01,
        load_best_model_at_end=True,
        save_total_limit=3,
        fp16=torch.cuda.is_available(),  # включаем AMP, если есть GPU
    )

    # 6️⃣ Trainer
    trainer = Trainer(
        model=model,  # оставить только это
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        tokenizer=tokenizer,
        compute_metrics=compute_metrics,
    )

    # костыль для custom_loss: overriding trainer.compute_loss
    trainer.compute_loss = custom_loss

    # 7️⃣ Старт обучения
    trainer.train()

    # 8️⃣ Финальное сохранение
    final_dir = data_dir / "final_model"
    trainer.save_model(str(final_dir))
    print(f"Модель сохранена в: {final_dir}")


if __name__ == "__main__":
    main()
