import React from 'react';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>🎯 SocFinder</h1>
        <p>Интерактивная платформа анализа грантов</p>
        <p>Приложение успешно развернуто на сервере!</p>
        <div className="stats">
          <div className="stat-item">
            <strong>166,849</strong> проектов
          </div>
          <div className="stat-item">
            <strong>32,107</strong> победителей
          </div>
          <div className="stat-item">
            <strong>71+ млрд ₽</strong> грантов
          </div>
        </div>
      </header>
    </div>
  );
}

export default App;
