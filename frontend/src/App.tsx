import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './components/HomePage';
import ProjectDetail from './components/ProjectDetail';
import ProblemsSolutionsPage from './components/ProblemsSolutionsPage';
import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/project/:id" element={<ProjectDetail />} />
        <Route path="/project/by-grant/:grantId" element={<ProjectDetail />} />
        <Route path="/problems-solutions" element={<ProblemsSolutionsPage />} />
      </Routes>
    </Router>
  );
}

export default App;
