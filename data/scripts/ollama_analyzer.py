#!/usr/bin/env python3
"""
Скрипт для анализа заявок президентских грантов через ollama API
Использует модель llama3.1:8b для выделения проблем и решений
"""

import urllib.request
import urllib.parse
import json
import logging
import time
from typing import Dict, List, Optional

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ollama_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class OllamaAnalyzer:
    def __init__(self, model_name: str = "llama3.1:8b", base_url: str = "http://localhost:11434"):
        """
        Инициализация анализатора
        
        Args:
            model_name: название модели ollama
            base_url: URL API ollama (по умолчанию localhost:11434)
        """
        self.model_name = model_name
        self.base_url = base_url
        self.api_url = f"{base_url}/api/generate"
        
        # Системный промпт для анализа
        self.system_prompt = """Ты - эксперт по анализу социальных проектов и заявок на президентские гранты. 
Твоя задача - анализировать тексты заявок и выявлять КОНКРЕТНЫЕ социальные проблемы и предлагаемые решения.

## ТРЕБОВАНИЯ К ОПИСАНИЮ ПРОБЛЕМ:
Каждая проблема должна содержать:
1. КТО страдает (конкретная группа людей: "пенсионеры 60+ лет", "дети-сироты", "инвалиды по слуху")
2. ОТ ЧЕГО страдает (конкретная проблема: "не имеют доступа к спортивным объектам", "не знают о существующих программах")
3. ГДЕ происходит (если указано: "в сельских районах", "в городе Омск", "в Советском административном округе")
4. КАК проявляется (конкретные последствия: "только 25% участвуют в мероприятиях", "нет специализированных тренеров")

## ТРЕБОВАНИЯ К ОПИСАНИЮ РЕШЕНИЙ:
Каждое решение должно содержать:
1. ЧТО конкретно делается ("организуем зимний фестиваль здоровья", "строим спортивную площадку")
2. ДЛЯ КОГО ("для пенсионеров Ульяновской области", "для детей с ограниченными возможностями")
3. ГДЕ реализуется ("в 20 местных отделениях", "на территории школы №15")
4. КАКИЕ ресурсы используются ("привлечем 5 специалистов", "закупим спортивный инвентарь на 550,000 рублей")

## ПРИМЕРЫ ХОРОШИХ ОПИСАНИЙ:
❌ ПЛОХО: "Недостаточное информирование о возможностях"
✅ ХОРОШО: "Пенсионеры Ульяновской области не знают о существующих спортивных программах и мероприятиях для пожилых людей"

❌ ПЛОХО: "Укрепление материальной базы"
✅ ХОРОШО: "Оснащаем 20 клубов пенсионеров спортивным оборудованием и инвентарем для тренировок на общую сумму 550,000 рублей"

Отвечай ТОЛЬКО валидным JSON в следующем формате:
{
  "grant_id": "ID_заявки",
  "problems": [
    "конкретная проблема с указанием КТО, ОТ ЧЕГО, ГДЕ и КАК страдает"
  ],
  "solutions": [
    "конкретное решение с указанием ЧТО, ДЛЯ КОГО, ГДЕ и КАКИЕ ресурсы"
  ],
  "summary": "краткое описание сути проекта"
}

ВАЖНО:
- Используй двойные кавычки
- Не добавляй лишнего текста до или после JSON
- Если проблем/решений не найдено - используй пустые массивы []
- Ограничивай количество проблем и решений до 5 штук
- Каждое описание должно быть самодостаточным и понятным без контекста"""
    
    def test_connection(self) -> bool:
        """Проверка подключения к ollama API"""
        try:
            req = urllib.request.Request(f"{self.base_url}/api/tags")
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    logger.info("✅ Подключение к ollama API успешно")
                    return True
                else:
                    logger.error(f"❌ Ошибка подключения к ollama API: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к ollama API: {e}")
            return False
    
    def analyze_grant(self, grant_data: Dict) -> Optional[Dict]:
        """
        Анализ одной заявки на грант
        
        Args:
            grant_data: словарь с данными гранта
            
        Returns:
            Словарь с анализом или None при ошибке
        """
        try:
            # Формируем текст для анализа
            analysis_text = self._prepare_analysis_text(grant_data)
            
            # Формируем промпт
            user_prompt = f"""Проанализируй эту заявку на президентский грант и выдели социальные проблемы и решения.

Данные заявки:
{analysis_text}

Отвечай только валидным JSON без дополнительного текста."""

            # Параметры для генерации
            payload = {
                "model": self.model_name,
                "prompt": user_prompt,
                "system": self.system_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "max_tokens": 1000
                }
            }
            
            logger.info(f"Отправляю запрос к модели {self.model_name}...")
            start_time = time.time()
            
            # Отправляем запрос к ollama
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(
                self.api_url,
                data=data,
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req, timeout=120) as response:
                if response.status != 200:
                    logger.error(f"❌ Ошибка API ollama: {response.status}")
                    return None
                
                # Получаем ответ
                response_data = response.read().decode('utf-8')
                result = json.loads(response_data)
                response_text = result.get('response', '')
            
            processing_time = time.time() - start_time
            logger.info(f"✅ Ответ получен за {processing_time:.2f} сек")
            
            # Парсим JSON ответ
            try:
                analysis = json.loads(response_text.strip())
                logger.info(f"✅ JSON успешно распарсен: {len(analysis.get('problems', []))} проблем, {len(analysis.get('solutions', []))} решений")
                return analysis
                
            except json.JSONDecodeError as e:
                logger.error(f"❌ Ошибка парсинга JSON: {e}")
                logger.error(f"Полученный текст: {response_text[:200]}...")
                return None
                
        except Exception as e:
            logger.error(f"❌ Ошибка при анализе гранта: {e}")
            return None
    
    def _prepare_analysis_text(self, grant_data: Dict) -> str:
        """Подготовка текста для анализа"""
        fields = [
            ('Название', grant_data.get('name', '')),
            ('Описание', grant_data.get('description', '')),
            ('Цели', grant_data.get('goal', '')),
            ('Задачи', grant_data.get('tasks', '')),
            ('Социальная значимость', grant_data.get('soc_signif', '')),
            ('География', grant_data.get('pj_geo', '')),
            ('Целевые группы', grant_data.get('target_groups', ''))
        ]
        
        text_parts = []
        for label, value in fields:
            if value and str(value).strip():
                text_parts.append(f"{label}: {value}")
        
        return "\n\n".join(text_parts)
    
    def batch_analyze(self, grants_data: List[Dict], batch_size: int = 5) -> List[Dict]:
        """
        Пакетный анализ грантов
        
        Args:
            grants_data: список словарей с данными грантов
            batch_size: размер пакета
            
        Returns:
            Список результатов анализа
        """
        results = []
        total_grants = len(grants_data)
        
        logger.info(f"🚀 Начинаю пакетный анализ {total_grants} грантов (пакет: {batch_size})")
        
        for i in range(0, total_grants, batch_size):
            batch = grants_data[i:i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (total_grants + batch_size - 1) // batch_size
            
            logger.info(f"📦 Обрабатываю пакет {batch_num}/{total_batches} ({len(batch)} грантов)")
            
            for j, grant_data in enumerate(batch):
                grant_num = i + j + 1
                logger.info(f"  📋 Анализирую грант {grant_num}/{total_grants}: {grant_data.get('name', 'N/A')[:50]}...")
                
                analysis = self.analyze_grant(grant_data)
                if analysis:
                    # Добавляем ID гранта из исходных данных
                    analysis['grant_id'] = grant_data.get('req_num', f'grant_{grant_num}')
                    results.append(analysis)
                    logger.info(f"    ✅ Успешно проанализирован")
                else:
                    logger.warning(f"    ⚠️ Ошибка анализа гранта {grant_num}")
                
                # Небольшая пауза между запросами
                time.sleep(1)
            
            logger.info(f"📦 Пакет {batch_num} завершен. Обработано: {len(results)}/{total_grants}")
        
        logger.info(f"🎉 Пакетный анализ завершен! Успешно обработано: {len(results)}/{total_grants}")
        return results

def main():
    """Тестовая функция"""
    analyzer = OllamaAnalyzer()
    
    # Проверяем подключение
    if not analyzer.test_connection():
        logger.error("Не удалось подключиться к ollama API")
        return
    
    # Тестовые данные
    test_grant = {
        'req_num': 'TEST-001',
        'name': 'Тестовый проект',
        'description': 'Проект направлен на решение проблем пожилых людей',
        'goal': 'Повышение качества жизни пожилых людей',
        'tasks': 'Организация мероприятий, создание клубов',
        'soc_signif': 'Социальная изоляция пожилых людей',
        'pj_geo': 'Москва',
        'target_groups': 'Пожилые люди 60+ лет'
    }
    
    logger.info("🧪 Тестирую анализ на тестовых данных...")
    result = analyzer.analyze_grant(test_grant)
    
    if result:
        logger.info("✅ Тест успешен!")
        logger.info(f"Результат: {json.dumps(result, ensure_ascii=False, indent=2)}")
    else:
        logger.error("❌ Тест не прошел")

if __name__ == "__main__":
    main()
