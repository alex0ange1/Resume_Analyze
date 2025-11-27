import './App.css'
import { Route, Routes } from 'react-router-dom';

import Analyse from './pages/Analyse';
import Authorization from './pages/Authorization';

export default function App() {
    return (
        <Routes>
            {/* Главная страница анализа */}
            <Route path="/" element={<Analyse />} />

            {/* Страница логина */}
            <Route path="/login" element={<Authorization />} />

            {/* Страница анализа напрямую */}
            <Route path="/analyse" element={<Analyse />} />
        </Routes>
    )
}
