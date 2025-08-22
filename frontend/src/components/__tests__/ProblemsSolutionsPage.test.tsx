import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import ProblemsSolutionsPage from '../ProblemsSolutionsPage';

// Мокаем fetch API
global.fetch = jest.fn();

// Мокаем window.open
Object.defineProperty(window, 'open', {
  writable: true,
  value: jest.fn(),
});

const mockProblems = [
  {
    id: 1,
    grant_id: "25-1-008623",
    problem_text: "Социальная проблема 1",
    project_name: "Проект 1"
  },
  {
    id: 2,
    grant_id: "15-2-001234",
    problem_text: "Социальная проблема 2",
    project_name: "Проект 2"
  }
];

const mockSolutions = [
  {
    id: 1,
    grant_id: "25-1-008623",
    solution_text: "Решение проблемы 1",
    project_name: "Проект 1"
  },
  {
    id: 2,
    grant_id: "25-1-008623",
    solution_text: "Решение проблемы 1 (вариант 2)",
    project_name: "Проект 1"
  }
];

describe('ProblemsSolutionsPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('отображает заголовок страницы', () => {
    render(<ProblemsSolutionsPage />);
    
    expect(screen.getByText('Проблемы и Решения')).toBeInTheDocument();
    expect(screen.getByText('Выберите проблемы для просмотра соответствующих решений')).toBeInTheDocument();
  });

  test('показывает состояние загрузки', () => {
    (fetch as jest.Mock).mockImplementation(() => new Promise(() => {}));
    
    render(<ProblemsSolutionsPage />);
    
    expect(screen.getByText('Загрузка данных...')).toBeInTheDocument();
  });

  test('показывает ошибку при неудачной загрузке', async () => {
    (fetch as jest.Mock).mockRejectedValueOnce(new Error('Ошибка сети'));
    
    render(<ProblemsSolutionsPage />);
    
    await waitFor(() => {
      expect(screen.getByText(/Ошибка:/)).toBeInTheDocument();
    });
  });

  test('загружает и отображает проблемы', async () => {
    (fetch as jest.Mock)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockProblems
      });
    
    render(<ProblemsSolutionsPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Социальная проблема 1')).toBeInTheDocument();
      expect(screen.getByText('Социальная проблема 2')).toBeInTheDocument();
    });
  });

  test('позволяет выбирать проблемы через чекбоксы', async () => {
    (fetch as jest.Mock)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockProblems
      });
    
    render(<ProblemsSolutionsPage />);
    
    await waitFor(() => {
      const checkboxes = screen.getAllByRole('checkbox');
      expect(checkboxes).toHaveLength(2);
    });
    
    const firstCheckbox = screen.getAllByRole('checkbox')[0];
    fireEvent.click(firstCheckbox);
    
    expect(firstCheckbox).toBeChecked();
  });

  test('загружает решения при выборе проблем', async () => {
    (fetch as jest.Mock)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockProblems
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockSolutions
      });
    
    render(<ProblemsSolutionsPage />);
    
    await waitFor(() => {
      const firstCheckbox = screen.getAllByRole('checkbox')[0];
      fireEvent.click(firstCheckbox);
    });
    
    await waitFor(() => {
      expect(screen.getByText('Решение проблемы 1')).toBeInTheDocument();
      expect(screen.getByText('Решение проблемы 1 (вариант 2)')).toBeInTheDocument();
    });
  });

  test('показывает информацию о выбранных проблемах', async () => {
    (fetch as jest.Mock)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockProblems
      });
    
    render(<ProblemsSolutionsPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Выбрано: 0 из 2')).toBeInTheDocument();
    });
    
    const firstCheckbox = screen.getAllByRole('checkbox')[0];
    fireEvent.click(firstCheckbox);
    
    expect(screen.getByText('Выбрано: 1 из 2')).toBeInTheDocument();
  });

  test('открывает детали гранта при клике на grant_id', async () => {
    (fetch as jest.Mock)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockProblems
      });
    
    render(<ProblemsSolutionsPage />);
    
    await waitFor(() => {
      const grantButton = screen.getByText('25-1-008623');
      fireEvent.click(grantButton);
    });
    
    expect(window.open).toHaveBeenCalledWith('/project/25-1-008623', '_blank');
  });

  test('показывает сообщение когда не выбрано проблем', async () => {
    (fetch as jest.Mock)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockProblems
      });
    
    render(<ProblemsSolutionsPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Выберите проблемы слева для просмотра решений')).toBeInTheDocument();
    });
  });

  test('показывает сообщение когда нет решений для выбранных проблем', async () => {
    (fetch as jest.Mock)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockProblems
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => []
      });
    
    render(<ProblemsSolutionsPage />);
    
    await waitFor(() => {
      const firstCheckbox = screen.getAllByRole('checkbox')[0];
      fireEvent.click(firstCheckbox);
    });
    
    await waitFor(() => {
      expect(screen.getByText('Для выбранных проблем не найдено решений')).toBeInTheDocument();
    });
  });

  test('отображает информационную панель с статистикой', async () => {
    (fetch as jest.Mock)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockProblems
      });
    
    render(<ProblemsSolutionsPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Всего проблем:')).toBeInTheDocument();
      expect(screen.getByText('2')).toBeInTheDocument();
      expect(screen.getByText('Уникальных грантов:')).toBeInTheDocument();
      expect(screen.getByText('2')).toBeInTheDocument();
    });
  });

  test('корректно обрабатывает множественный выбор проблем', async () => {
    (fetch as jest.Mock)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockProblems
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockSolutions
      });
    
    render(<ProblemsSolutionsPage />);
    
    await waitFor(() => {
      const checkboxes = screen.getAllByRole('checkbox');
      fireEvent.click(checkboxes[0]); // Выбираем первую проблему
      fireEvent.click(checkboxes[1]); // Выбираем вторую проблему
    });
    
    expect(screen.getByText('Выбрано: 2 из 2')).toBeInTheDocument();
  });

  test('сбрасывает выбор проблем', async () => {
    (fetch as jest.Mock)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockProblems
      });
    
    render(<ProblemsSolutionsPage />);
    
    await waitFor(() => {
      const firstCheckbox = screen.getAllByRole('checkbox')[0];
      fireEvent.click(firstCheckbox); // Выбираем
      fireEvent.click(firstCheckbox); // Снимаем выбор
    });
    
    expect(screen.getByText('Выбрано: 0 из 2')).toBeInTheDocument();
  });
});
