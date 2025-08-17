import React, { useMemo } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Исправляем иконки маркеров Leaflet
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.8.0/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.8.0/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.8.0/images/marker-shadow.png',
});

interface Project {
  id: number;
  name: string;
  region: string;
  org: string;  // Изменено с organization на org
  winner: boolean;
  money_req_grant: number;
  year?: number;
  direction?: string;
  contest?: string;
  coordinates?: { lat: number; lng: number };
}

interface ProjectMapProps {
  projects: Project[];
}

// Координаты основных городов России
const CITY_COORDINATES: { [key: string]: [number, number] } = {
  'Москва': [55.7558, 37.6173],
  'Санкт-Петербург': [59.9311, 30.3609],
  'Новосибирск': [55.0084, 82.9357],
  'Екатеринбург': [56.8431, 60.6454],
  'Казань': [55.8304, 49.0661],
  'Нижний Новгород': [56.2965, 43.9361],
  'Челябинск': [55.1644, 61.4368],
  'Самара': [53.2001, 50.15],
  'Омск': [54.9885, 73.3242],
  'Ростов-на-Дону': [47.2357, 39.7015],
  'Уфа': [54.7388, 55.9721],
  'Красноярск': [56.0184, 92.8672],
  'Пермь': [58.0105, 56.2502],
  'Волгоград': [48.7080, 44.5133],
  'Воронеж': [51.6720, 39.1843],
  'Саратов': [51.5924, 46.0348],
  'Краснодар': [45.0355, 38.9753],
  'Тольятти': [53.5303, 49.3461],
  'Ижевск': [56.8527, 53.2118],
  'Ульяновск': [54.3142, 48.4031],
};

// Функция для получения координат по региону
const getCoordinatesForRegion = (region: string): [number, number] => {
  // Ищем точное совпадение
  if (CITY_COORDINATES[region]) {
    return CITY_COORDINATES[region];
  }
  
  // Ищем частичное совпадение
  for (const city in CITY_COORDINATES) {
    if (region.includes(city) || city.includes(region)) {
      return CITY_COORDINATES[city];
    }
  }
  
  // Если регион содержит "область", "край", "республика" - ищем по ключевым словам
  const regionWords = region.toLowerCase().split(' ');
  for (const word of regionWords) {
    for (const city in CITY_COORDINATES) {
      if (city.toLowerCase().includes(word) || word.includes(city.toLowerCase())) {
        return CITY_COORDINATES[city];
      }
    }
  }
  
  // По умолчанию - центр России
  return [55.7558, 37.6173]; // Москва
};

// Создаем иконки для разных типов проектов
const createIcon = (winner: boolean) => {
  return L.divIcon({
    html: winner ? '🏆' : '📍',
    className: 'custom-div-icon',
    iconSize: [30, 30],
    iconAnchor: [15, 15],
    popupAnchor: [0, -15]
  });
};

// Компонент для центрирования карты на маркерах
const MapController: React.FC<{ projects: Project[] }> = ({ projects }) => {
  const map = useMap();
  
  React.useEffect(() => {
    if (projects.length > 0) {
      // Получаем все координаты
      const coordinates = projects.map(project => {
        const coords = getCoordinatesForRegion(project.region);
        return coords;
      });
      
      if (coordinates.length > 0) {
        // Создаем bounds для всех точек
        const markers = coordinates.map(coord => L.marker(coord as [number, number]));
        const group = L.featureGroup(markers);
        map.fitBounds(group.getBounds().pad(0.1));
      }
    }
  }, [map, projects]);
  
  return null;
};

const ProjectMap: React.FC<ProjectMapProps> = ({ projects }) => {
  // Группируем проекты по координатам для избежания наложения маркеров
  const groupedProjects = useMemo(() => {
    const groups: { [key: string]: Project[] } = {};
    
    projects.forEach(project => {
      const coords = getCoordinatesForRegion(project.region);
      const key = `${coords[0]},${coords[1]}`;
      
      if (!groups[key]) {
        groups[key] = [];
      }
      groups[key].push(project);
    });
    
    return Object.entries(groups).map(([coordStr, projectsGroup]) => {
      const [lat, lng] = coordStr.split(',').map(Number);
      return {
        lat,
        lng,
        projects: projectsGroup
      };
    });
  }, [projects]);

  const formatMoney = (amount: number) => {
    return new Intl.NumberFormat('ru-RU').format(amount) + ' ₽';
  };

  return (
    <div style={{ height: '600px', width: '100%' }}>
      <MapContainer
        center={[61.5240, 105.3188]} // Центр России
        zoom={4}
        style={{ height: '100%', width: '100%' }}
        scrollWheelZoom={true}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        <MapController projects={projects} />
        
        {groupedProjects.map((group, index) => {
          // Добавляем небольшое смещение для множественных маркеров
          const offset = group.projects.length > 1 ? Math.random() * 0.01 - 0.005 : 0;
          const hasWinners = group.projects.some(p => p.winner);
          
          return (
            <Marker
              key={index}
              position={[group.lat + offset, group.lng + offset]}
              icon={createIcon(hasWinners)}
            >
              <Popup maxWidth={400} className="custom-popup">
                <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
                  <h3 style={{ margin: '0 0 10px 0', color: '#2d3748' }}>
                    📍 {group.projects[0].region}
                  </h3>
                  <p style={{ margin: '0 0 15px 0', color: '#4a5568', fontSize: '0.9em' }}>
                    <strong>{group.projects.length}</strong> проект{group.projects.length > 1 ? 'ов' : ''}
                    {hasWinners && ' • '}
                    {hasWinners && <span style={{ color: '#d69e2e' }}>🏆 Есть победители</span>}
                  </p>
                  
                  <div style={{ maxHeight: '200px', overflowY: 'auto' }}>
                    {group.projects.slice(0, 5).map((project) => (
                      <div
                        key={project.id}
                        style={{
                          borderBottom: '1px solid #e2e8f0',
                          paddingBottom: '8px',
                          marginBottom: '8px',
                          fontSize: '0.85em'
                        }}
                      >
                        <div style={{ fontWeight: 'bold', color: '#2d3748', marginBottom: '4px' }}>
                          {project.winner ? '🏆' : '📋'} {project.name.substring(0, 50)}
                          {project.name.length > 50 && '...'}
                        </div>
                        <div style={{ color: '#4a5568', fontSize: '0.9em' }}>
                          {project.org?.substring(0, 40)}
                          {project.org && project.org.length > 40 && '...'}
                        </div>
                        <div style={{ color: '#2d3748', fontWeight: '500', marginTop: '2px' }}>
                          {formatMoney(project.money_req_grant)}
                        </div>
                      </div>
                    ))}
                    {group.projects.length > 5 && (
                      <div style={{ 
                        textAlign: 'center', 
                        color: '#718096', 
                        fontSize: '0.8em',
                        marginTop: '8px'
                      }}>
                        ... и еще {group.projects.length - 5} проект{group.projects.length - 5 > 1 ? 'ов' : ''}
                      </div>
                    )}
                  </div>
                </div>
              </Popup>
            </Marker>
          );
        })}
      </MapContainer>
    </div>
  );
};

export default ProjectMap;
