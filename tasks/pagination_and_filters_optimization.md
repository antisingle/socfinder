# План реализации пагинации и оптимизации фильтров SocFinder

## Задача
Реализовать две ключевые функции:
1. **Пагинация в таблице** - отображать все заявки с пагинацией по 25 штук
2. **Создение оптимизированных по высоте фильтров** - сделать фильтры по навправлению проектов, году и региону, а также успешности (описание тут ./socfinder/sources/pres_grants_data_description.md )

## Анализ текущего состояния

### Текущая таблица
- **Ограничение:** показывается только 10 строк
- **Проблема:** пользователи не видят все данные
- **Нужно:** пагинация по 25 записей с возможностью просмотра всех данных

### Текущие фильтры
- отсутствуют

## Целевые размеры

### Фильтры (компактная версия)
- **Высота:** ≤ 50px 
- **Структура:** поиск (уже есть) + результаты в одну строку
- **Адаптивность:** корректная работа на мобильных устройствах

### Пагинация
- **Размер страницы:** 25 записей
- **Навигация:** кнопки "Предыдущая", "Следующая", номера страниц
- **Информация:** "Показано X-Y из Z записей"

## План изменений

### 1. Оптимизация фильтров

#### 1.1 Изменение структуры HTML
```jsx
// Было:
<div className="search-panel-compact">
  <input type="text" placeholder="Поиск..." />
  <span className="search-results">Найдено: X из Y</span>
</div>

// Станет:
<div className="filters-compact">
  <div className="search-section">
    <input type="text" placeholder="Поиск..." />
    <span className="search-results">X из Y</span>
  </div>
  <div className="pagination-info">
    Показано X-Y из Z
  </div>
</div>
```

#### 1.2 CSS изменения
```css
/* Компактные фильтры */
.filters-compact {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 15px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  max-height: 50px;
  margin: 10px 20px;
}

.search-section {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
}

.search-section input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 14px;
}

.search-results {
  font-size: 12px;
  color: #718096;
  white-space: nowrap;
}

.pagination-info {
  font-size: 12px;
  color: #718096;
  white-space: nowrap;
}
```

### 2. Реализация пагинации

#### 2.1 Состояние пагинации
```jsx
// Новые состояния в App.tsx
const [currentPage, setCurrentPage] = useState(1);
const [itemsPerPage] = useState(25);
const [totalItems, setTotalItems] = useState(0);
```

#### 2.2 Логика пагинации
```jsx
// Вычисление данных для текущей страницы
const indexOfLastItem = currentPage * itemsPerPage;
const indexOfFirstItem = indexOfLastItem - itemsPerPage;
const currentItems = filteredProjects.slice(indexOfFirstItem, indexOfLastItem);

// Обновление общего количества при изменении фильтров
useEffect(() => {
  setTotalItems(filteredProjects.length);
  setCurrentPage(1); // Сброс на первую страницу при изменении фильтров
}, [filteredProjects]);
```

#### 2.3 Компонент пагинации
```jsx
const Pagination = ({ currentPage, totalPages, onPageChange }) => {
  const pages = [];
  const maxVisiblePages = 5;
  
  let startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
  let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);
  
  if (endPage - startPage + 1 < maxVisiblePages) {
    startPage = Math.max(1, endPage - maxVisiblePages + 1);
  }
  
  for (let i = startPage; i <= endPage; i++) {
    pages.push(i);
  }
  
  return (
    <div className="pagination">
      <button 
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage === 1}
        className="pagination-btn"
      >
        ← Предыдущая
      </button>
      
      {startPage > 1 && (
        <>
          <button onClick={() => onPageChange(1)} className="pagination-btn">1</button>
          {startPage > 2 && <span className="pagination-dots">...</span>}
        </>
      )}
      
      {pages.map(page => (
        <button
          key={page}
          onClick={() => onPageChange(page)}
          className={`pagination-btn ${currentPage === page ? 'active' : ''}`}
        >
          {page}
        </button>
      ))}
      
      {endPage < totalPages && (
        <>
          {endPage < totalPages - 1 && <span className="pagination-dots">...</span>}
          <button onClick={() => onPageChange(totalPages)} className="pagination-btn">
            {totalPages}
          </button>
        </>
      )}
      
      <button 
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage === totalPages}
        className="pagination-btn"
      >
        Следующая →
      </button>
    </div>
  );
};
```

#### 2.4 CSS для пагинации
```css
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin: 20px 0;
  flex-wrap: wrap;
}

.pagination-btn {
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  background: white;
  color: #4a5568;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
  min-width: 40px;
}

.pagination-btn:hover:not(:disabled) {
  background: #f7fafc;
  border-color: #cbd5e0;
}

.pagination-btn.active {
  background: #667eea;
  color: white;
  border-color: #667eea;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-dots {
  color: #718096;
  padding: 0 8px;
}
```

### 3. Обновление таблицы

#### 3.1 Изменение рендеринга таблицы
```jsx
// В таблице использовать currentItems вместо filteredProjects
{currentItems.map((project) => (
  <tr key={project.id}>
    {/* ... существующие колонки ... */}
  </tr>
))}
```

#### 3.2 Добавление пагинации под таблицей
```jsx
{viewMode === 'table' && (
  <>
    <div className="table-container">
      {/* ... существующая таблица ... */}
    </div>
    {totalItems > itemsPerPage && (
      <Pagination
        currentPage={currentPage}
        totalPages={Math.ceil(totalItems / itemsPerPage)}
        onPageChange={setCurrentPage}
      />
    )}
  </>
)}
```

## План тестирования

### Локальное тестирование
1. **Фильтры:**
   - [ ] Высота фильтров ≤ 50px
   - [ ] Поиск работает корректно
   - [ ] Результаты поиска отображаются
   - [ ] Адаптивность на мобильных устройствах

2. **Пагинация:**
   - [ ] Отображается 25 записей на странице
   - [ ] Кнопки "Предыдущая"/"Следующая" работают
   - [ ] Номера страниц кликабельны
   - [ ] Активная страница выделена
   - [ ] При изменении фильтров сброс на первую страницу
   - [ ] Информация "Показано X-Y из Z" корректна

3. **Функциональность:**
   - [ ] Все данные загружаются
   - [ ] Фильтрация работает с пагинацией
   - [ ] Переключение между картой и таблицей
   - [ ] Нет регрессий в существующем функционале

### Продакшен тестирование
1. **Деплой:**
   - [ ] Использовать исправленный deploy.sh
   - [ ] Проверить что изменения применились
   - [ ] Убедиться что все работает на сервере

2. **Визуальная проверка:**
   - [ ] Открыть http://antisingle.fvds.ru:3000
   - [ ] Проверить компактность фильтров
   - [ ] Протестировать пагинацию с большим количеством данных

## Критерии успеха

### Основные
- [ ] Фильтры занимают ≤ 50px по высоте
- [ ] Пагинация работает с 25 записями на странице
- [ ] Все данные доступны через пагинацию
- [ ] Навигация по страницам интуитивна

### Технические
- [ ] Локальная версия работает корректно
- [ ] Деплой прошел без ошибок
- [ ] Продакшен версия идентична локальной
- [ ] Нет регрессий в функциональности
- [ ] Производительность не ухудшилась

## Риски и митигация

### Риск 1: Пагинация замедлит работу
- **Митигация:** использовать slice() для клиентской пагинации, в будущем добавить серверную


## Следующие шаги

1. **Одобрение плана** - получить подтверждение подхода
2. **Локальная реализация** - внести изменения в код
3. **Локальное тестирование** - проверить все критерии
4. **Подготовка к деплою** - проверить конфигурацию
5. **Деплой** - развернуть на сервере
6. **Продакшен тестирование** - финальная проверка

## Ожидаемые результаты

### До изменений:
- Фильтры: только поиск
- Таблица: только 10 записей
- Навигация: отсутствует

### После изменений:
- Фильтры: ≤50px высоты (экономия 37.5%)
- Таблица: 25 записей на странице + пагинация
- Навигация: полная с информацией о страницах

## Дополнительные улучшения (будущие)

1. **Серверная пагинация** - для больших объемов данных
2. **Быстрая навигация** - поле "Перейти на страницу"
3. **Экспорт данных** - возможность скачать все отфильтрованные данные
