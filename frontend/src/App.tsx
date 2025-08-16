import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ProjectMap from './components/ProjectMap';
import './App.css';

// Типы данных
interface Project {
  id: number;
  name: string;
  region: string;
  organization: string;
  winner: boolean;
  money_req_grant: number;
  year?: number;
  lat?: number;
  lng?: number;
}

interface Stats {
  total_projects: number;
  total_winners: number;
  total_money: number;
  regions_count: number;
  organizations_count: number;
}

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001';

function App() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'map' | 'table'>('table');
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredProjects, setFilteredProjects] = useState<Project[]>([]);

  // Загрузка данных
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        
        // Загружаем статистику
        const statsResponse = await axios.get(`${API_URL}/api/v1/stats/overview`);
        setStats(statsResponse.data);

        // Загружаем проекты
        const projectsResponse = await axios.get(`${API_URL}/api/v1/projects?limit=1000`);
        setProjects(projectsResponse.data);
        setFilteredProjects(projectsResponse.data);
        
        setError(null);
      } catch (err) {
        console.error('Error loading data:', err);
        setError('Ошибка загрузки данных. Проверьте подключение к серверу.');
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  // Поиск
  useEffect(() => {
    if (!searchTerm) {
      setFilteredProjects(projects);
    } else {
      const filtered = projects.filter(project =>
        project.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        project.region?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        project.organization?.toLowerCase().includes(searchTerm.toLowerCase())
      );
      setFilteredProjects(filtered);
    }
  }, [searchTerm, projects]);

  // Форматирование денег
  const formatMoney = (amount: number) => {
    return new Intl.NumberFormat('ru-RU').format(amount) + ' ₽';
  };

  if (loading) {
    return (
      <div className="App">
        <div className="loading">
          <h1>🎯 SocFinder</h1>
          <p>Загрузка данных...</p>
          <div className="spinner"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="App">
        <div className="error">
          <h1>🎯 SocFinder</h1>
          <p>❌ {error}</p>
          <button onClick={() => window.location.reload()}>
            Попробовать снова
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="App">
      {/* Заголовок */}
      <header className="app-header">
        <h1>🎯 SocFinder</h1>
        <p>Интерактивная платформа анализа грантов</p>
      </header>

      {/* Статистика */}
      {stats && (
        <div className="stats-panel">
          <h2>Общая статистика</h2>
          <div className="stats-grid">
            <div className="stat-item">
              <div className="stat-number">{stats.total_projects.toLocaleString('ru-RU')}</div>
              <div className="stat-label">Всего проектов</div>
            </div>
            <div className="stat-item">
              <div className="stat-number">{stats.total_winners.toLocaleString('ru-RU')}</div>
              <div className="stat-label">Победителей</div>
            </div>
            <div className="stat-item">
              <div className="stat-number">{formatMoney(stats.total_money)}</div>
              <div className="stat-label">Общая сумма грантов</div>
            </div>
            <div className="stat-item">
              <div className="stat-number">{stats.regions_count}</div>
              <div className="stat-label">Регионов</div>
            </div>
            <div className="stat-item">
              <div className="stat-number">{stats.organizations_count.toLocaleString('ru-RU')}</div>
              <div className="stat-label">Организаций</div>
            </div>
          </div>
        </div>
      )}

      {/* Переключатель режимов */}
      <div className="view-controls">
        <button
          className={viewMode === 'map' ? 'active' : ''}
          onClick={() => setViewMode('map')}
        >
          🗺️ Карта
        </button>
        <button
          className={viewMode === 'table' ? 'active' : ''}
          onClick={() => setViewMode('table')}
        >
          📊 Таблица
        </button>
      </div>

      {/* Поиск */}
      <div className="search-panel">
        <input
          type="text"
          placeholder="Поиск по названию, региону или организации..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="search-input"
        />
        <span className="search-results">
          Найдено: {filteredProjects.length} из {projects.length} проектов
        </span>
      </div>

      {/* Основной контент */}
      <main className="main-content">
        {viewMode === 'map' ? (
          <div className="map-container">
            <h3>🗺️ Карта проектов</h3>
            <p>📍 {filteredProjects.length} проектов на карте</p>
            <ProjectMap projects={filteredProjects} />
          </div>
        ) : (
          <div className="table-container">
            <h3>📊 Таблица проектов</h3>
            <div className="table-wrapper">
              <table className="projects-table">
                <thead>
                  <tr>
                    <th>Название</th>
                    <th>Регион</th>
                    <th>Организация</th>
                    <th>Статус</th>
                    <th>Сумма гранта</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredProjects.slice(0, 100).map((project) => (
                    <tr key={project.id}>
                      <td className="project-name" title={project.name}>
                        {project.name}
                      </td>
                      <td>{project.region}</td>
                      <td className="organization" title={project.organization}>
                        {project.organization}
                      </td>
                      <td>
                        <span className={`status ${project.winner ? 'winner' : 'participant'}`}>
                          {project.winner ? '🏆 Победитель' : '👥 Участник'}
                        </span>
                      </td>
                      <td className="money">
                        {formatMoney(project.money_req_grant)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {filteredProjects.length > 100 && (
                <div className="table-footer">
                  Показано первых 100 из {filteredProjects.length} проектов
                </div>
              )}
            </div>
          </div>
        )}
      </main>

      {/* Подвал */}
      <footer className="app-footer">
        <p>SocFinder - Платформа анализа грантовых программ</p>
        <p>Данных загружено: {projects.length} проектов</p>
      </footer>
    </div>
  );
}

export default App;