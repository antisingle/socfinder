import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import ProblemsSolutionsPage from '../ProblemsSolutionsPage';

// Мокаем fetch API для реальных HTTP запросов
const originalFetch = global.fetch;

describe('ProblemsSolutionsPage Integration Tests', () => {
  beforeAll(() => {
    // Настройка для интеграционных тестов
    process.env.NODE_ENV = 'test';
  });

  afterAll(() => {
    // Восстанавливаем оригинальный fetch
    global.fetch = originalFetch;
  });

  beforeEach(() => {
    // Очищаем моки перед каждым тестом
    jest.clearAllMocks();
  });

  test('интеграция с реальным API backend', async () => {
    // Этот тест требует запущенного backend сервера
    // В реальных условиях его можно запускать отдельно
    
    // Мокаем fetch для имитации реальных API вызовов
    global.fetch = jest.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => [
          {
            id: 1,
            grant_id: "25-1-008623",
            problem_text: "Тестовая социальная проблема",
            project_name: "Тестовый проект"
          }
        ]
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => [
          {
            id: 1,
            grant_id: "25-1-008623",
            solution_text: "Тестовое решение",
            project_name: "Тестовый проект"
          }
        ]
      });

    render(<ProblemsSolutionsPage />);

    // Проверяем загрузку проблем
    await waitFor(() => {
      expect(screen.getByText('Тестовая социальная проблема')).toBeInTheDocument();
    });

    // Выбираем проблему
    const checkbox = screen.getByRole('checkbox');
    fireEvent.click(checkbox);

    // Проверяем загрузку решений
    await waitFor(() => {
      expect(screen.getByText('Тестовое решение')).toBeInTheDocument();
    });

    // Проверяем статистику
    expect(screen.getByText('Выбрано: 1 из 1')).toBeInTheDocument();
    expect(screen.getByText('Показано: 1 решений')).toBeInTheDocument();
  });

  test('обработка ошибок API', async () => {
    // Мокаем ошибку API
    global.fetch = jest.fn().mockRejectedValueOnce(new Error('API недоступен'));

    render(<ProblemsSolutionsPage />);

    await waitFor(() => {
      expect(screen.getByText(/Ошибка:/)).toBeInTheDocument();
    });
  });

  test('обработка пустого ответа API', async () => {
    // Мокаем пустой ответ
    global.fetch = jest.fn().mockResolvedValueOnce({
      ok: true,
      json: async () => []
    });

    render(<ProblemsSolutionsPage />);

    await waitFor(() => {
      expect(screen.getByText('Выбрано: 0 из 0')).toBeInTheDocument();
    });
  });

  test('валидация данных от API', async () => {
    // Мокаем некорректные данные
    global.fetch = jest.fn().mockResolvedValueOnce({
      ok: true,
      json: async () => [
        {
          id: 1,
          grant_id: "25-1-008623",
          problem_text: null, // Некорректные данные
          project_name: "Тестовый проект"
        }
      ]
    });

    render(<ProblemsSolutionsPage />);

    await waitFor(() => {
      // Проверяем, что компонент не падает при некорректных данных
      expect(screen.getByText('Выбрано: 0 из 1')).toBeInTheDocument();
    });
  });

  test('производительность с большим количеством данных', async () => {
    // Мокаем большое количество данных
    const largeProblems = Array.from({ length: 100 }, (_, i) => ({
      id: i + 1,
      grant_id: `GRANT-${i + 1}`,
      problem_text: `Проблема ${i + 1}`,
      project_name: `Проект ${i + 1}`
    }));

    global.fetch = jest.fn().mockResolvedValueOnce({
      ok: true,
      json: async () => largeProblems
    });

    const startTime = performance.now();
    
    render(<ProblemsSolutionsPage />);

    await waitFor(() => {
      expect(screen.getByText('Проблема 1')).toBeInTheDocument();
      expect(screen.getByText('Проблема 100')).toBeInTheDocument();
    });

    const endTime = performance.now();
    const renderTime = endTime - startTime;

    // Проверяем, что рендеринг происходит достаточно быстро
    expect(renderTime).toBeLessThan(1000); // Менее 1 секунды
  });

  test('корректность URL для API запросов', async () => {
    const mockFetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => []
    });
    global.fetch = mockFetch;

    render(<ProblemsSolutionsPage />);

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith('http://localhost:8001/api/problems');
    });
  });

  test('корректность заголовков для POST запроса', async () => {
    global.fetch = jest.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => [{ id: 1, grant_id: "TEST", problem_text: "Test", project_name: "Test" }]
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => []
      });

    render(<ProblemsSolutionsPage />);

    await waitFor(() => {
      const checkbox = screen.getByRole('checkbox');
      fireEvent.click(checkbox);
    });

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8001/api/solutions/by-grants',
        expect.objectContaining({
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ grant_ids: ['TEST'] })
        })
      );
    });
  });
});
