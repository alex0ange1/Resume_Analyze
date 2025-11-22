import './App.css'
import { Route, Routes, Navigate } from 'react-router-dom';

import Analyse from './pages/Analyse';
import Authorization from './pages/Authorization';


export default function App() {
    const isAuthenticated = !!localStorage.getItem('token')
    
    return (
        <Routes>
            <Route path="/" element={isAuthenticated ? <Analyse /> : <Navigate to='/login' />} />
            <Route path="/login" element={<Authorization />} />
        </Routes>
    )
}