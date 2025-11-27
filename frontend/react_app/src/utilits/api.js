import axios from "axios";

// Создаем экземпляр клиента axios
const apiClient = axios.create({
    baseURL: '/api',
    headers: {
        'Content-Type': 'application/json',
    },
});

// Добавление токена в заголовки для авторизованных запросов
apiClient.interceptors.request.use(
    (config) => {
        // Получаем токен из localStorage
        const token = localStorage.getItem('token');
        if (token) {
            // Если токен существует, добавляем его в заголовки
            config.headers['Authorization'] = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        // В случае ошибки запроса возвращаем отклонение
        return Promise.reject(error);
    }
);

export default apiClient;