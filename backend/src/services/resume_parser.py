import os
import logging
from pathlib import Path
from typing import Optional

import PyPDF2
import docx

logger = logging.getLogger(__name__)


class ResumeParser:
    """Парсер резюме из различных форматов"""

    @staticmethod
    def parse(file_path: str, file_ext: str) -> str:
        """
        Парсит файл резюме и возвращает текст

        Args:
            file_path: путь к файлу
            file_ext: расширение файла (.pdf, .docx, .txt)

        Returns:
            str: извлеченный текст
        """
        file_ext = file_ext.lower()

        if file_ext == ".txt":
            return ResumeParser._parse_txt(file_path)
        elif file_ext == ".pdf":
            return ResumeParser._parse_pdf(file_path)
        elif file_ext == ".docx":
            return ResumeParser._parse_docx(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")

    @staticmethod
    def _parse_txt(file_path: str) -> str:
        """Парсит txt файл"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except UnicodeDecodeError:
            # Пробуем другие кодировки
            with open(file_path, "r", encoding="cp1251") as f:
                return f.read()

    @staticmethod
    def _parse_pdf(file_path: str) -> str:
        """Парсит PDF файл"""
        try:
            import PyPDF2

            text = []
            with open(file_path, "rb") as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text.append(page_text)

            return "\n".join(text)
        except Exception as e:
            logger.error(f"Error parsing PDF: {str(e)}")
            raise ValueError(f"Failed to parse PDF file: {str(e)}")

    @staticmethod
    def _parse_docx(file_path: str) -> str:
        """Парсит DOCX файл"""
        try:
            import docx

            doc = docx.Document(file_path)
            text = [paragraph.text for paragraph in doc.paragraphs]
            return "\n".join(text)
        except Exception as e:
            logger.error(f"Error parsing DOCX: {str(e)}")
            raise ValueError(f"Failed to parse DOCX file: {str(e)}")
