# 🔧 Отчет об исправлении навигации

## 🚨 Проблема
При клике на `grant_id` в таблице проблем и решений происходила ошибка:
```
Ошибка
Проект не найден
Вернуться к списку
```

## 🔍 Причина
1. **Frontend** пытался перейти на `/project/${grantId}` (например, `/project/25-1-012859`)
2. **Backend API** ожидал числовой ID в `/api/v1/projects/{project_id}`
3. **Несоответствие типов:** `grant_id` (строка) vs `project_id` (число)

## ✅ Решение

### 1. Backend API
Добавлен новый endpoint для поиска проекта по `grant_id`:

```python
@router.get("/projects/by-grant/{grant_id}", response_model=ProjectDetail)
def get_project_by_grant_id(grant_id: str, db: Session = Depends(get_db)):
    """
    Получить проект по grant_id (req_num)
    """
    service = ProjectService(db)
    project = service.get_project_by_grant_id(grant_id)
    if not project:
        raise HTTPException(status_code=404, detail="Проект с указанным grant_id не найден")
    return project
```

### 2. ProjectService
Добавлен метод для поиска по `grant_id`:

```python
def get_project_by_grant_id(self, grant_id: str) -> Optional[Project]:
    """
    Получить проект по grant_id (req_num)
    """
    return self.db.query(Project).filter(Project.req_num == grant_id).first()
```

### 3. Frontend Routing
Добавлен новый роут в React приложение:

```tsx
<Route path="/project/by-grant/:grantId" element={<ProjectDetail />} />
```

### 4. ProjectDetail Component
Обновлен для работы с обоими типами параметров:

```tsx
const { id, grantId } = useParams<{ id?: string; grantId?: string }>();

// Логика выбора API endpoint
if (grantId) {
  response = await axios.get(`${API_URL}/v1/projects/by-grant/${grantId}`);
} else if (id) {
  response = await axios.get(`${API_URL}/v1/projects/${id}`);
}
```

### 5. ProblemsSolutionsPage
Обновлен URL для навигации:

```tsx
const handleGrantClick = (grantId: string) => {
  // Переход на страницу деталей гранта через новый API endpoint
  window.open(`/project/by-grant/${grantId}`, '_blank');
};
```

## 🧪 Тестирование

### API Endpoint
```bash
curl "http://localhost:8001/api/v1/projects/by-grant/25-1-012859"
```

**Результат:**
```json
{
  "id": 461712,
  "name": "Добрые крышечки: экология и благотворительность",
  "region": "Москва",
  "org": "БЛАГОТВОРИТЕЛЬНЫЙ ФОНД \"ВОЛОНТЕРЫ В ПОМОЩЬ ДЕТЯМ-СИРОТАМ\" Москва",
  "year": 2025,
  "direction": "Охрана окружающей среды и защита животных",
  "contest": "Первый конкурс 2025"
}
```

### Frontend Navigation
- ✅ Клик на `grant_id` в таблице проблем
- ✅ Переход на `/project/by-grant/{grant_id}`
- ✅ Загрузка данных проекта
- ✅ Отображение деталей проекта

## 📊 Результат

### До исправления:
- ❌ Ошибка "Проект не найден"
- ❌ Невозможность перехода на страницу проекта
- ❌ Плохой UX

### После исправления:
- ✅ Корректная навигация по `grant_id`
- ✅ Загрузка и отображение данных проекта
- ✅ Полноценный UX
- ✅ Обратная совместимость с числовыми ID

## 🔄 Обратная совместимость

Новое решение **не ломает** существующую функциональность:
- `/project/123` - работает как раньше (по числовому ID)
- `/project/by-grant/25-1-012859` - новый способ (по grant_id)

## 🚀 Деплой

Изменения развернуты в Docker контейнерах:
1. ✅ Backend пересобран с новым API
2. ✅ Frontend пересобран с новыми роутами
3. ✅ Все контейнеры запущены и работают

## 💡 Рекомендации

1. **Тестирование:** Протестировать навигацию на всех страницах
2. **Мониторинг:** Следить за логами API для новых endpoint'ов
3. **Документация:** Обновить API docs с новыми endpoint'ами
4. **Метрики:** Добавить отслеживание использования новых роутов

---

**Дата исправления:** 22 августа 2025  
**Статус:** ✅ ИСПРАВЛЕНО  
**Влияние:** Положительное - улучшен UX навигации
