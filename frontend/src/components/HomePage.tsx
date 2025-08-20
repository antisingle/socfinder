import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import ProjectMap from './ProjectMap';
import Pagination from './Pagination';
import './HomePage.css';

// Типы данных
interface Project {
  id: number;
  name: string;
  region: string;
  org: string;
  winner: boolean;
  money_req_grant: number;
  year?: number;
  direction?: string;
  contest?: string;
  coordinates?: { lat: number; lng: number };
}

interface Stats {
  total_projects: number;
  total_winners: number;
  total_money: number;
  regions_count: number;
  organizations_count: number;
}

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001/api';

const HomePage: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'map' | 'table'>('table');
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredProjects, setFilteredProjects] = useState<Project[]>([]);
  
  // Состояние пагинации
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(25);
  const [totalItems, setTotalItems] = useState(0);
  
  // Состояние фильтров
  const [selectedDirection, setSelectedDirection] = useState<string | null>(null);
  const [selectedYear, setSelectedYear] = useState<number | null>(null);
  const [selectedRegion, setSelectedRegion] = useState<string | null>(null);
  const [selectedStatus, setSelectedStatus] = useState<string | null>(null);

  // Загрузка данных
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        
        const statsResponse = await axios.get(`${API_URL}/v1/stats/overview`);
        setStats(statsResponse.data);

        const projectsResponse = await axios.get(`${API_URL}/v1/projects?limit=100000`);
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

  // Поиск и фильтрация
  useEffect(() => {
    let filtered = projects;
    
    if (searchTerm) {
      filtered = filtered.filter(project =>
        project.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        project.region?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        project.org?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    
    if (selectedDirection) {
      filtered = filtered.filter(project => project.direction === selectedDirection);
    }
    
    if (selectedYear) {
      filtered = filtered.filter(project => project.year === selectedYear);
    }
    
    if (selectedRegion) {
      filtered = filtered.filter(project => project.region === selectedRegion);
    }
    
    if (selectedStatus) {
      if (selectedStatus === 'winner') {
        filtered = filtered.filter(project => project.winner === true);
      } else if (selectedStatus === 'participant') {
        filtered = filtered.filter(project => project.winner === false);
      }
    }
    
    setFilteredProjects(filtered);
    setTotalItems(filtered.length);
    setCurrentPage(1);
  }, [projects, searchTerm, selectedDirection, selectedYear, selectedRegion, selectedStatus]);

  // Вычисление элементов для текущей страницы
  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentItems = filteredProjects.slice(indexOfFirstItem, indexOfLastItem);

  const formatMoney = (amount: number) => {
    return new Intl.NumberFormat('ru-RU').format(amount) + ' ₽';
  };

  if (loading) {
    return <div className="loading">Загрузка данных...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div className="home-page">
      {/* Компактная верхняя панель: один ряд */}
      <div className="top-panel">
        {/* Левая часть: заголовок */}
        <div className="header-section">
          <h1>🎯 SocFinder</h1>
          <p>Интерактивная платформа анализа грантов</p>
        </div>

        {/* Центральная часть: переключатели */}
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

        {/* Правая часть: компактная статистика */}
        {stats && (
          <div className="stats-compact">
            <div className="stat-item-compact">
              <div className="stat-number">{stats?.total_projects?.toLocaleString('ru-RU') || 0}</div>
              <div className="stat-label">Проектов</div>
            </div>
            <div className="stat-item-compact">
              <div className="stat-number">{stats?.total_winners?.toLocaleString('ru-RU') || 0}</div>
              <div className="stat-label">Победителей</div>
            </div>
            <div className="stat-item-compact">
              <div className="stat-number">{formatMoney(stats?.total_money || 0)}</div>
              <div className="stat-label">Сумма</div>
            </div>
            <div className="stat-item-compact">
              <div className="stat-number">{stats.regions_count}</div>
              <div className="stat-label">Регионов</div>
            </div>
            <div className="stat-item-compact">
              <div className="stat-number">{stats?.organizations_count?.toLocaleString('ru-RU') || 0}</div>
              <div className="stat-label">Организаций</div>
            </div>
          </div>
        )}
      </div>

      {/* Фильтры */}
      <div className="filters-compact">
        <div className="search-section">
          <input
            type="text"
            placeholder="Поиск по названию, региону, организации..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
          <span className="search-results">
            {filteredProjects.length} результатов
          </span>
        </div>
        
        <div className="filters-section">
          <select 
            className="filter-select direction"
            value={selectedDirection || ''}
            onChange={(e) => setSelectedDirection(e.target.value || null)}
          >
            <option value="">Направление</option>
            {Array.from(new Set(projects.map(p => p.direction).filter(Boolean))).sort().map(direction => (
              <option key={direction} value={direction} title={direction}>
                {(direction || '').length > 35 ? (direction || '').substring(0, 35) + '...' : direction}
              </option>
            ))}
          </select>
          
          <select 
            className="filter-select year"
            value={selectedYear || ''}
            onChange={(e) => setSelectedYear(e.target.value ? parseInt(e.target.value) : null)}
          >
            <option value="">Год</option>
            {Array.from(new Set(projects.map(p => p.year).filter(Boolean))).sort((a, b) => (b || 0) - (a || 0)).map(year => (
              <option key={year} value={year}>{year}</option>
            ))}
          </select>
          
          <select 
            className="filter-select region"
            value={selectedRegion || ''}
            onChange={(e) => setSelectedRegion(e.target.value || null)}
          >
            <option value="">Регион</option>
            {Array.from(new Set(projects.map(p => p.region).filter(Boolean))).sort().map(region => (
              <option key={region} value={region} title={region}>
                {(region || '').length > 25 ? (region || '').substring(0, 25) + '...' : region}
              </option>
            ))}
          </select>
          
          <select 
            className="filter-select status"
            value={selectedStatus || ''}
            onChange={(e) => setSelectedStatus(e.target.value || null)}
          >
            <option value="">Статус</option>
            <option value="winner">Победители</option>
            <option value="participant">Участники</option>
          </select>
        </div>
        <div className="pagination-info">
          Показано {indexOfFirstItem + 1}-{Math.min(indexOfLastItem, totalItems)} из {totalItems}
        </div>
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
          <>
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
                    {Array.isArray(currentItems) && currentItems.map((project) => (
                      <tr key={project.id}>
                        <td className="project-name" title={project.name}>
                          <Link to={`/project/${project.id}`} className="project-link">
                            {project.name}
                          </Link>
                        </td>
                        <td>{project.region}</td>
                        <td className="organization" title={project.org}>
                          {project.org}
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
              </div>
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
      </main>

      {/* Подвал */}
      <footer className="app-footer">
        <p>SocFinder - Платформа анализа грантовых программ</p>
        <p>Данных загружено: {projects.length} проектов</p>
      </footer>
    </div>
  );
};

export default HomePage;
