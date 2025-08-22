import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import './ProjectDetail.css';

interface ProjectDetailData {
  id: number;
  name: string;
  org: string;
  region: string;
  year: number;
  direction: string;
  contest: string;
  winner: boolean;
  money_req_grant: number;
  date_req: string;
  inn: string;
  ogrn: string;
  implem_start: string;
  implem_end: string;
  rate: number;
  cofunding: number;
  total_money: number;
  description: string;
  goal: string;
  tasks: string;
  soc_signif: string;
  pj_geo: string;
  target_groups: string;
  address: string;
  web_site: string;
  req_num: string;
  link: string;
}

const ProjectDetail: React.FC = () => {
  const { id, grantId } = useParams<{ id?: string; grantId?: string }>();
  const navigate = useNavigate();
  const [project, setProject] = useState<ProjectDetailData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001/api';

  useEffect(() => {
    const fetchProject = async () => {
      try {
        setLoading(true);
        let response;
        
        if (grantId) {
          // Если передан grantId, используем новый endpoint
          response = await axios.get(`${API_URL}/v1/projects/by-grant/${grantId}`);
        } else if (id) {
          // Если передан id, используем старый endpoint
          response = await axios.get(`${API_URL}/v1/projects/${id}`);
        } else {
          throw new Error('Не указан ID проекта или grant_id');
        }
        
        setProject(response.data);
      } catch (err) {
        setError('Проект не найден');
        console.error('Error fetching project:', err);
      } finally {
        setLoading(false);
      }
    };

    if (id || grantId) {
      fetchProject();
    }
  }, [id, grantId, API_URL]);

  const formatMoney = (amount: number | null) => {
    if (!amount) return '0 ₽';
    return new Intl.NumberFormat('ru-RU').format(amount) + ' ₽';
  };

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return 'Не указано';
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString('ru-RU');
    } catch {
      return dateStr;
    }
  };

  if (loading) {
    return (
      <div className="project-detail-container">
        <div className="loading">Загрузка проекта...</div>
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className="project-detail-container">
        <div className="error">
          <h2>Ошибка</h2>
          <p>{error || 'Проект не найден'}</p>
          <button onClick={() => navigate('/')} className="back-button">
            Вернуться к списку
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="project-detail-container">
      <div className="project-detail-header">
        <button onClick={() => navigate('/')} className="back-button">
          ← Вернуться к списку
        </button>
        <h1>{project.name || 'Название не указано'}</h1>
        <div className="project-status">
          <span className={`status-badge ${project.winner ? 'winner' : 'loser'}`}>
            {project.winner ? 'Победитель' : 'Не прошел'}
          </span>
        </div>
      </div>

      <div className="project-detail-content">
        <div className="project-main-info">
          <div className="info-section">
            <h3>Основная информация</h3>
            <div className="info-grid">
              <div className="info-item">
                <label>Организация:</label>
                <span>{project.org || 'Не указано'}</span>
              </div>
              <div className="info-item">
                <label>Регион:</label>
                <span>{project.region || 'Не указано'}</span>
              </div>
              <div className="info-item">
                <label>Год:</label>
                <span>{project.year || 'Не указано'}</span>
              </div>
              <div className="info-item">
                <label>Направление:</label>
                <span>{project.direction || 'Не указано'}</span>
              </div>
              <div className="info-item">
                <label>Конкурс:</label>
                <span>{project.contest || 'Не указано'}</span>
              </div>
            </div>
          </div>

          <div className="info-section">
            <h3>Финансовая информация</h3>
            <div className="info-grid">
              <div className="info-item">
                <label>Запрошенная сумма:</label>
                <span className="money">{formatMoney(project.money_req_grant)}</span>
              </div>
              <div className="info-item">
                <label>Рейтинг:</label>
                <span>{project.rate || 'Не указано'}</span>
              </div>
              <div className="info-item">
                <label>Софинансирование:</label>
                <span className="money">{formatMoney(project.cofunding)}</span>
              </div>
              <div className="info-item">
                <label>Общая сумма:</label>
                <span className="money">{formatMoney(project.total_money)}</span>
              </div>
            </div>
          </div>

          <div className="info-section">
            <h3>Сроки реализации</h3>
            <div className="info-grid">
              <div className="info-item">
                <label>Дата подачи заявки:</label>
                <span>{formatDate(project.date_req)}</span>
              </div>
              <div className="info-item">
                <label>Начало реализации:</label>
                <span>{formatDate(project.implem_start)}</span>
              </div>
              <div className="info-item">
                <label>Окончание реализации:</label>
                <span>{formatDate(project.implem_end)}</span>
              </div>
            </div>
          </div>
        </div>

        <div className="project-description">
          <div className="info-section">
            <h3>Описание проекта</h3>
            <div className="description-content">
              {project.description ? (
                <p>{project.description}</p>
              ) : (
                <p className="no-data">Описание проекта не указано</p>
              )}
            </div>
          </div>

          <div className="info-section">
            <h3>Цели проекта</h3>
            <div className="description-content">
              {project.goal ? (
                <p>{project.goal}</p>
              ) : (
                <p className="no-data">Цели проекта не указаны</p>
              )}
            </div>
          </div>

          <div className="info-section">
            <h3>Задачи проекта</h3>
            <div className="description-content">
              {project.tasks ? (
                <p>{project.tasks}</p>
              ) : (
                <p className="no-data">Задачи проекта не указаны</p>
              )}
            </div>
          </div>

          <div className="info-section">
            <h3>Социальная значимость</h3>
            <div className="description-content">
              {project.soc_signif ? (
                <p>{project.soc_signif}</p>
              ) : (
                <p className="no-data">Социальная значимость не указана</p>
              )}
            </div>
          </div>

          <div className="info-section">
            <h3>География проекта</h3>
            <div className="description-content">
              {project.pj_geo ? (
                <p>{project.pj_geo}</p>
              ) : (
                <p className="no-data">География проекта не указана</p>
              )}
            </div>
          </div>

          <div className="info-section">
            <h3>Целевые группы</h3>
            <div className="description-content">
              {project.target_groups ? (
                <p>{project.target_groups}</p>
              ) : (
                <p className="no-data">Целевые группы не указаны</p>
              )}
            </div>
          </div>
        </div>

        <div className="project-contact">
          <div className="info-section">
            <h3>Контактная информация</h3>
            <div className="info-grid">
              <div className="info-item">
                <label>Адрес:</label>
                <span>{project.address || 'Не указано'}</span>
              </div>
              <div className="info-item">
                <label>Веб-сайт:</label>
                {project.web_site ? (
                  <a href={project.web_site} target="_blank" rel="noopener noreferrer">
                    {project.web_site}
                  </a>
                ) : (
                  <span>Не указано</span>
                )}
              </div>
              <div className="info-item">
                <label>Страница заявки (внешняя):</label>
                {project.link ? (
                  <a href={project.link} target="_blank" rel="noopener noreferrer">
                    Открыть в новом окне
                  </a>
                ) : (
                  <span>Не указано</span>
                )}
              </div>
              <div className="info-item">
                <label>ИНН:</label>
                <span>{project.inn || 'Не указано'}</span>
              </div>
              <div className="info-item">
                <label>ОГРН:</label>
                <span>{project.ogrn || 'Не указано'}</span>
              </div>
              <div className="info-item">
                <label>Номер заявки:</label>
                <span>{project.req_num || 'Не указано'}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProjectDetail;
