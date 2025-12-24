from typing import Dict

from fastapi import UploadFile, File
import PyPDF2
from docx import Document
import tempfile
import os

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from api.depends import get_current_user

ml_router = APIRouter()


class ResumeEvaluationRequest(BaseModel):
    resume_text: str
    profession: str


class MLServiceResponse(BaseModel):
    final_levels: Dict[str, int]
    evaluation: dict


import sys
import os

# Добавьте корень проекта в sys.path
project_root = '/Users/alexandro/Desktop/Resume_Analyze'
sys.path.insert(0, project_root)

print(f"🔍 Пути Python: {sys.path}")

try:
    # Пробуем разные варианты импорта
    try:
        from model.src.infer import full_evaluation, load_model

        print("✅ Импорт через model.src.infer")
    except ImportError:
        try:
            # Альтернативный путь
            sys.path.insert(0, '/Users/alexandro/Desktop/Resume_Analyze/model/src')
            from model.src.infer import full_evaluation, load_model

            print("✅ Импорт через прямой путь к infer")
        except ImportError as e:
            print(f"❌ Ошибка импорта infer: {e}")
            raise

    print("📦 Импорт модели успешен, загружаю...")

    # Пробуем загрузить модель явно
    load_model()

    # Тестируем модель
    test_result = full_evaluation("Python разработчик с SQL", "Data Scientist")

    print(f"✅ ML модель загружена! Тестовый результат получен")
    ML_MODEL_AVAILABLE = True

except Exception as e:
    print(f"❌ Ошибка загрузки ML модели: {e}")
    print(f"📂 Текущая директория: {os.getcwd()}")
    print(
        f"📁 Содержимое model/: {os.listdir('/Users/alexandro/Desktop/Resume_Analyze/model') if os.path.exists('/Users/alexandro/Desktop/Resume_Analyze/model') else 'Папка не существует'}")

    ML_MODEL_AVAILABLE = False


    # Создайте заглушку
    def full_evaluation(resume_text, profession):
        print(f"⚠️  Использую заглушку для: {profession}")
        return {
            "final_levels": {"Python": 2, "SQL": 1, "ML": 1},
            "evaluation": {
                "match_percent": 65.5,
                "missing_skills": []
            }
        }

try:
    from model.src.infer import full_evaluation

    ML_MODEL_AVAILABLE = True
except ImportError as e:
    print(f"Warning: ML model not available: {e}")
    ML_MODEL_AVAILABLE = False


    # Создайте заглушку
    def full_evaluation(resume_text, profession):
        return {
            "final_levels": {"Python": 2, "SQL": 1, "ML": 1},
            "evaluation": {
                "match_percent": 65.5,
                "missing_skills": []
            }
        }


@ml_router.post(
    "/evaluate-resume",
    response_model=MLServiceResponse,
)
async def evaluate_resume(request: ResumeEvaluationRequest):
    """Использует реальную ML модель или заглушку для анализа"""

    # Отладочная информация
    print(f"📄 Анализируем резюме для профессии: {request.profession}")
    print(f"📏 Длина текста: {len(request.resume_text)} символов")

    if not ML_MODEL_AVAILABLE:
        print("⚠️  Используется заглушка (модель недоступна)")
        # Заглушка если модель не загрузилась
        return {
            "final_levels": {"Python": 2, "SQL": 1, "Машинное обучение": 1},
            "evaluation": {
                "score": 65,
                "match_percentage": 65,
                "recommendations": ["ML модель временно недоступна"]
            }
        }

    try:
        print("🚀 Используем реальную ML модель...")
        # Используем реальную модель
        result = full_evaluation(request.resume_text, request.profession)

        print(f"✅ Модель вернула результат: {len(result.get('final_levels', {}))} навыков")

        # Преобразуем формат под ваш фронтенд
        response_data = {
            "final_levels": result["final_levels"],
            "evaluation": {
                "score": result["evaluation"]["match_percent"],
                "match_percentage": result["evaluation"]["match_percent"],
                "missing_skills": result["evaluation"]["missing_skills"],
                "recommendations": [
                    f"Необходимо улучшить {skill['name']} с уровня {skill['candidate_level']} до {skill['required_level']}"
                    for skill in result["evaluation"]["missing_skills"]
                ] if result["evaluation"]["missing_skills"] else [
                    "Отличное соответствие требованиям профессии!"
                ]
            }
        }

        print(f"📊 Готовый ответ: {response_data}")
        return response_data

    except Exception as e:
        print(f"❌ Ошибка ML модели: {str(e)}")
        # При ошибке модели возвращаем заглушку
        return {
            "final_levels": {"Python": 2, "SQL": 1, "Машинное обучение": 1},
            "evaluation": {
                "score": 60,
                "match_percentage": 60,
                "recommendations": [f"Ошибка модели: {str(e)[:100]}..."]
            }
        }


@ml_router.post("/upload-resume")
async def upload_resume(
        file: UploadFile = File(...)
):
    """
    Загружает файл резюме и извлекает текст
    Поддерживает: PDF, DOCX, TXT
    """

    # Проверяем тип файла
    if file.content_type not in [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain"
    ]:
        raise HTTPException(
            status_code=400,
            detail="Неподдерживаемый формат файла. Используйте PDF, DOCX или TXT"
        )

    try:
        # Читаем содержимое файла
        contents = await file.read()

        text = ""

        if file.filename.endswith('.pdf'):
            # Обработка PDF
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                tmp.write(contents)
                tmp_path = tmp.name

            try:
                with open(tmp_path, 'rb') as pdf_file:
                    pdf_reader = PyPDF2.PdfReader(pdf_file)
                    for page in pdf_reader.pages:
                        text += page.extract_text()
            finally:
                os.unlink(tmp_path)

        elif file.filename.endswith('.docx'):
            # Обработка DOCX
            with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp:
                tmp.write(contents)
                tmp_path = tmp.name

            try:
                doc = Document(tmp_path)
                for para in doc.paragraphs:
                    text += para.text + "\n"
            finally:
                os.unlink(tmp_path)

        else:
            # Обработка TXT
            text = contents.decode('utf-8')

        # Очищаем текст
        text = text.strip()
        if not text:
            raise HTTPException(status_code=400, detail="Не удалось извлечь текст из файла")

        return {
            "filename": file.filename,
            "text": text,
            "text_preview": text[:500] + "..." if len(text) > 500 else text
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка обработки файла: {str(e)}"
        )