import axios from "axios";

const apiClient = axios.create({
    baseURL: '/api',
    headers: {
        'Content-Type': 'application/json',
    },
});

apiClient.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers['Authorization'] = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

apiClient.interceptors.response.use(
    (r) => r,
    (error) => {
        const url = String(error.config?.url || '');
        const status = error.response?.status;
        const authFailed = status === 401 || status === 403;
        const loginRequest = url.includes('/token');
        if (authFailed && loginRequest) {
            return Promise.reject(error);
        }
        const noServer =
            !error.response ||
            (typeof status === 'number' && status >= 500 && status <= 599);
        if (authFailed || noServer) {
            if (!window.location.pathname.startsWith('/login')) {
                localStorage.removeItem('token');
                window.location.assign('/login');
            }
        }
        return Promise.reject(error);
    }
);

export default apiClient;