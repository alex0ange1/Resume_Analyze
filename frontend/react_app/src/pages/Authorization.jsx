import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { login, register } from '../utilits/auth'  // импортируем login и register функции
import styles from './Authorization.module.css';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import { 
    Container,
  Paper, 
  Typography,
  TextField,
  Button,
  Box,
  Divider,
  Link
  } from '@mui/material';
import MessageModal from '../components/MessageModal';

const Theme = createTheme({
  palette: {
    primary: {
      main: '#0078C8', // основной синий
    },
    secondary: {
      main: '#00396F', // темно-синий
    },
    background: {
      default: '#F6F8FB',
    },
  },
});


const Authorization = () => {
    const [mode, setMode] = useState('login') // 'login' | 'register'
    const [form, setForm] = useState({ email: '', password: '' })
    const navigate = useNavigate()
    const [open, setOpen] = useState(false);
    const [message, setMessage] = useState('');
    const [type, setType] = useState('');


    const toggleMode = () => {
        setMode(mode === 'login' ? 'register' : 'login')
    }

    const handleChange = (e) => {
        setForm({ ...form, [e.target.name]: e.target.value })
    }

    const handleOpen = (message, type) => {
      setMessage(message);
      setType(type);
      setOpen(true);
    };
  
    const handleClose = () => {
      setOpen(false);
    };

    const handleSubmit = async (e) => {
      e.preventDefault();
      
        try {
            if (mode === 'login') {
                const data = await login(form);
                localStorage.setItem('token', data.access_token);
                navigate('/');
            } else {
                await register(form)
                handleOpen('Регистрация прошла успешно!\nТеперь войдите.', 'success')
                setMode('login')
            }
        } catch (error) {
            const msg = 'Ошибка: ' + (error?.response?.data?.detail || error.message);
            handleOpen(msg, 'error')
        }
    }

    return (
    <ThemeProvider theme={Theme}>

      <MessageModal open={open} message={message} type={type} onClose={handleClose} />

      <Container maxWidth="sm" sx={{ py: 3, height: '100vh', display: 'flex', alignItems: 'center' }}>
        <Paper elevation={2} sx={{ p: 4, borderRadius: '8px', width: '400px' }}>
          
        {/* Блок с логотипом */}
          <Box sx={{display: 'flex', justifyContent: 'center', mb: 3}}>
            <img
            src="/logo.png"
            alt="Газпром нефть"
            style={{
              height: '100px',
              objectFit: 'contain'
            }}
            />
          </Box>
          
          <Typography 
            variant="h5" 
            sx={{ 
              mb: 2, 
              color: 'primary.main',
              fontWeight: 'bold',
              textAlign: 'center' 
            }}
          >
            {mode === 'login' ? 'Вход' : 'Регистрация'}
          </Typography>
          <Divider sx={{ mb: 3 }} />
          
          <Box component="form" onSubmit={handleSubmit} sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <TextField
              name="email"
              type="email"
              value={form.email}
              onChange={handleChange}
              label="Email"
              variant="outlined"
              fullWidth
              required
              sx={{ mb: 1 }}
            />
            <TextField
              name="password"
              type="password"
              value={form.password}
              onChange={handleChange}
              label="Пароль"
              variant="outlined"
              fullWidth
              required
              sx={{ mb: 3 }}
            />
            <Button 
              type="submit" 
              variant="contained" 
              color="primary" 
              fullWidth
              size="large"
              sx={{ mb: 2 }}
            >
              {mode === 'login' ? 'Войти' : 'Зарегистрироваться'}
            </Button>
          </Box>
          
          <Box sx={{ textAlign: 'center', mt: 2 }}>
            <Typography variant="body2" color="text.secondary">
              {mode === 'login' ? 'Нет аккаунта?' : 'Уже есть аккаунт?'}{' '}
              <Link 
                component="button"
                variant="body2"
                onClick={toggleMode}
                sx={{ 
                  textDecoration: 'none', 
                  fontWeight: 'medium',
                  cursor: 'pointer',
                  border: 'none',
                  background: 'none',
                  color: 'primary.main'
                }}
              >
                {mode === 'login' ? 'Зарегистрироваться' : 'Войти'}
              </Link>
            </Typography>
          </Box>
        </Paper>
      </Container>
    </ThemeProvider>
  );
};

export default Authorization