import fitz  # PyMuPDF (устанавливается через: pip install PyMuPDF)
import os
import re

def extract_images_with_names(pdf_path: str, output_dir: str):
    """
    Извлекает изображения из PDF и называет их на основе текста на странице.
    """
    # Создаем папку для сохранения, если ее нет
    os.makedirs(output_dir, exist_ok=True)
    
    # Открываем PDF документ
    pdf_document = fitz.open(pdf_path)
    
    print(f"Обработка документа: {pdf_path} (Всего страниц: {len(pdf_document)})")

    for page_num in range(len(pdf_document)):
        page = pdf_document[page_num]
        
        # 1. Пытаемся получить имя блюда из текста страницы
        text = page.get_text()
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Пропускаем страницы без текста (или страницы оглавления, если нужно - можно добавить фильтр)
        if not lines:
            continue
            
        # Эвристика: название блюда обычно находится в первой строке текста страницы
        raw_name = lines[0]
        
        # Очищаем строку от запрещенных для имен файлов символов, 
        # а также удаляем пробелы, запятые и точки по краям строки
        safe_name = re.sub(r'[\\/*?:"<>|]', "", raw_name).strip(" .,;")
        
        # Если имя почему-то пустое, даем дефолтное
        if not safe_name:
            safe_name = f"unknown_item_page_{page_num + 1}"

        # 2. Получаем список всех изображений на странице
        image_list = page.get_images(full=True)
        
        for img_index, img in enumerate(image_list):
            xref = img[0] # Уникальный идентификатор изображения (XREF)
            
            # Извлекаем байты изображения
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"] # Обычно 'png' или 'jpeg'
            
            # Если изображений на странице больше одного, добавляем индекс, чтобы не перезаписать
            suffix = f"_{img_index}" if len(image_list) > 1 else ""
            filename = f"{safe_name}{suffix}.{image_ext}"
            filepath = os.path.join(output_dir, filename)
            
            # Сохраняем файл на диск
            with open(filepath, "wb") as f:
                f.write(image_bytes)
                
            print(f"Сохранено: {filename} (Страница {page_num + 1})")

    pdf_document.close()
    print("Готово!")

if __name__ == "__main__":
    ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    PDF_FILE_PATH = os.path.join(ROOT, "docs", "source-assets", "Scotts Bibles - New-23.pdf")
    OUTPUT_DIRECTORY = os.path.join(ROOT, "extracted_menu_images")
    
    extract_images_with_names(PDF_FILE_PATH, OUTPUT_DIRECTORY)
