import pandas as pd
from datasets import Dataset
from transformers import AutoTokenizer
from pathlib import Path

MODEL_NAME = "DeepPavlov/rubert-base-cased"

def main():
    # 1. Читаем train.csv
    base_dir = Path(__file__).resolve().parent.parent  # поднимаемся на уровень выше: /model/
    data_path = base_dir / "data" / "train.csv"
    data_dir = base_dir / "data"
    output_dir = data_dir / "tokenized_dataset"        # -> /model/data/tokenized_dataset
    df = pd.read_csv(data_path)
    # 2. Преобразуем в HuggingFace Dataset
    dataset = Dataset.from_pandas(df)

    # 3. Загружаем токенизатор
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    # 4. Токенизируем пары (резюме, компетенция)
    def tokenize(batch):
        return tokenizer(
            batch["resume_text"], batch["competency"],
            truncation=True, padding="max_length", max_length=512
        )

    tokenized = dataset.map(tokenize, batched=True)

    # 5. Переименовываем колонку уровня в labels и сохраняем формат
    tokenized = tokenized.rename_column("level", "labels")
    tokenized.set_format("torch", columns=["input_ids", "attention_mask", "labels"])

    # 6. (по желанию) Сохраняем токенизированный датасет в файл
    tokenized.save_to_disk(output_dir)

    print("Dataset готов к обучению!")

if __name__ == "__main__":
    main()
