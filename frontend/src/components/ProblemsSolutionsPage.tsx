import React, { useState, useEffect } from 'react';
import './ProblemsSolutionsPage.css';

interface Problem {
  id: number;
  grant_id: string;
  problem_text: string;
  project_name: string;
}

interface Solution {
  id: number;
  grant_id: string;
  solution_text: string;
  project_name: string;
}

const ProblemsSolutionsPage: React.FC = () => {
  // API URL для backend
  const API_BASE_URL = 'http://localhost:8001';
  
  const [problems, setProblems] = useState<Problem[]>([]);
  const [solutions, setSolutions] = useState<Solution[]>([]);
  const [selectedProblems, setSelectedProblems] = useState<Set<number>>(new Set());
  const [filteredSolutions, setFilteredSolutions] = useState<Solution[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Загрузка проблем при монтировании компонента
  useEffect(() => {
    fetchProblems();
  }, []);

  // Фильтрация решений при изменении выбранных проблем
  useEffect(() => {
    if (selectedProblems.size > 0) {
      fetchSolutionsForProblems();
    } else {
      setFilteredSolutions([]);
    }
  }, [selectedProblems]);

  const fetchProblems = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/api/problems`);
      if (!response.ok) {
        throw new Error('Ошибка загрузки проблем');
      }
      const data = await response.json();
      setProblems(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Неизвестная ошибка');
    } finally {
      setLoading(false);
    }
  };

  const fetchSolutionsForProblems = async () => {
    try {
      const selectedGrantIds = Array.from(selectedProblems).map(
        problemId => problems.find(p => p.id === problemId)?.grant_id
      ).filter(Boolean);

      if (selectedGrantIds.length === 0) return;

      const response = await fetch(`${API_BASE_URL}/api/solutions/by-grants`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ grant_ids: selectedGrantIds }),
      });

      if (!response.ok) {
        throw new Error('Ошибка загрузки решений');
      }

      const data = await response.json();
      setFilteredSolutions(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Неизвестная ошибка');
    }
  };

  const handleProblemToggle = (problemId: number) => {
    const newSelected = new Set(selectedProblems);
    if (newSelected.has(problemId)) {
      newSelected.delete(problemId);
    } else {
      newSelected.add(problemId);
    }
    setSelectedProblems(newSelected);
  };

  const handleGrantClick = (grantId: string) => {
    // Переход на страницу деталей гранта
    window.open(`/project/${grantId}`, '_blank');
  };

  if (loading) {
    return (
      <div className="problems-solutions-page">
        <div className="loading">Загрузка данных...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="problems-solutions-page">
        <div className="error">Ошибка: {error}</div>
      </div>
    );
  }

  return (
    <div className="problems-solutions-page">
      <header className="page-header">
        <h1>Проблемы и Решения</h1>
        <p className="subtitle">
          Выберите проблемы для просмотра соответствующих решений
        </p>
      </header>

      <div className="content-grid">
        {/* Левая таблица - Проблемы */}
        <div className="problems-section">
          <div className="section-header">
            <h2>Социальные проблемы</h2>
            <div className="selection-info">
              Выбрано: {selectedProblems.size} из {problems.length}
            </div>
          </div>
          
          <div className="table-container">
            <table className="problems-table">
              <thead>
                <tr>
                  <th className="checkbox-column">Выбор</th>
                  <th>Проблема</th>
                  <th>Грант</th>
                  <th>Проект</th>
                </tr>
              </thead>
              <tbody>
                {problems.map((problem) => (
                  <tr key={problem.id} className={selectedProblems.has(problem.id) ? 'selected' : ''}>
                    <td>
                      <input
                        type="checkbox"
                        checked={selectedProblems.has(problem.id)}
                        onChange={() => handleProblemToggle(problem.id)}
                      />
                    </td>
                    <td className="problem-text">{problem.problem_text}</td>
                    <td>
                      <button
                        className="grant-link"
                        onClick={() => handleGrantClick(problem.grant_id)}
                      >
                        {problem.grant_id}
                      </button>
                    </td>
                    <td className="project-name">{problem.project_name}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Правая таблица - Решения */}
        <div className="solutions-section">
          <div className="section-header">
            <h2>Предложенные решения</h2>
            <div className="solutions-info">
              Показано: {filteredSolutions.length} решений
            </div>
          </div>

          <div className="table-container">
            {filteredSolutions.length > 0 ? (
              <table className="solutions-table">
                <thead>
                  <tr>
                    <th>Решение</th>
                    <th>Грант</th>
                    <th>Проект</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredSolutions.map((solution) => (
                    <tr key={solution.id}>
                      <td className="solution-text">{solution.solution_text}</td>
                      <td>
                        <button
                          className="grant-link"
                          onClick={() => handleGrantClick(solution.grant_id)}
                        >
                          {solution.grant_id}
                        </button>
                      </td>
                      <td className="project-name">{solution.project_name}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div className="no-selection">
                {selectedProblems.size === 0 ? (
                  <p>Выберите проблемы слева для просмотра решений</p>
                ) : (
                  <p>Для выбранных проблем не найдено решений</p>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Информационная панель */}
      <div className="info-panel">
        <div className="info-item">
          <strong>Всего проблем:</strong> {problems.length}
        </div>
        <div className="info-item">
          <strong>Выбрано проблем:</strong> {selectedProblems.size}
        </div>
        <div className="info-item">
          <strong>Показано решений:</strong> {filteredSolutions.length}
        </div>
        <div className="info-item">
          <strong>Уникальных грантов:</strong> {new Set(problems.map(p => p.grant_id)).size}
        </div>
      </div>
    </div>
  );
};

export default ProblemsSolutionsPage;
