import pandas as pd
from datasets import Dataset
from transformers import AutoTokenizer
from pathlib import Path
from sklearn.model_selection import train_test_split

MODEL_NAME = "DeepPavlov/rubert-base-cased"

def main():
    base_dir = Path(__file__).resolve().parent.parent
    data_dir = base_dir / "data"
    csv_path = data_dir / "competency_500.csv"
    output_dir = data_dir / "tokenized_dataset"
    output_dir.mkdir(exist_ok=True)

    # 1️⃣ Загружаем CSV
    df = pd.read_csv(csv_path)

    # 1.1 Очистка текстовых полей
    df["resume_text"] = df["resume_text"].fillna("").astype(str).str.strip()
    df["competency"] = df["competency"].fillna("").astype(str).str.strip()
    # 1.2 Удаляем пустые строки
    df = df[(df["resume_text"] != "") & (df["competency"] != "")]
    # 1.3 Удаляем полные дубликаты записи
    df = df.drop_duplicates(subset=["competency", "resume_text", "level"]).reset_index(drop=True)
    print(f"Rows after cleaning: {len(df)}")

    # 2️⃣ Убираем класс 0 (нет в обучении)
    df = df[df["level"] != 0]

    # 3️⃣ Сдвигаем уровни: 1→0, 2→1, 3→2
    df["level"] = df["level"] - 1

    # 4️⃣ Делим на train/val (stratify будет работать корректно)
    train_df, val_df = train_test_split(df, test_size=0.1, random_state=42, stratify=df["level"])

    # 5️⃣ Конвертация в Dataset
    train_dataset = Dataset.from_pandas(train_df)
    val_dataset = Dataset.from_pandas(val_df)

    # 6️⃣ Токенизатор
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    # 7️⃣ Функция токенизации
    def tokenize(batch):
        return tokenizer(
            batch["resume_text"],
            batch["competency"],
            truncation=True,
            padding="max_length",
            max_length=256
        )

    # 8️⃣ Токенизация
    tokenized_train = train_dataset.map(tokenize, batched=True)
    tokenized_val = val_dataset.map(tokenize, batched=True)

    # 9️⃣ labels
    tokenized_train = tokenized_train.rename_column("level", "labels")
    tokenized_val = tokenized_val.rename_column("level", "labels")

    # 🔟 Формат + сохранение
    tokenized_train.set_format("torch", columns=["input_ids", "attention_mask", "labels"])
    tokenized_val.set_format("torch", columns=["input_ids", "attention_mask", "labels"])

    tokenized_train.save_to_disk(output_dir / "train")
    tokenized_val.save_to_disk(output_dir / "validation")

    print(f"Датасеты сохранены в {output_dir}/train и {output_dir}/validation")

if __name__ == "__main__":
    main()
