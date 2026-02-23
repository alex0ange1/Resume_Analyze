import { Outlet, useLocation, useNavigate } from 'react-router-dom'
import { AppBar, Toolbar, Button, Box, Container } from '@mui/material'
import { logout } from '../utilits/auth'

const MainLayout = () => {
  const navigate = useNavigate()
  const location = useLocation()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const isActive = (path) => location.pathname === path

  return (
    <>
      <AppBar position="static" elevation={2}>
        <Toolbar disableGutters>
          <Container
            maxWidth="md"
            sx={{
              display: 'flex',
              alignItems: 'center',
              width: '100%',
              minHeight: 64,
            }}
          >
            <Box sx={{ flex: 1, display: 'flex', justifyContent: 'center', gap: 1 }}>
              <Button
                color="inherit"
                onClick={() => navigate('/competences')}
                sx={{ border: isActive('/competences') ? '2px solid rgba(255,255,255,0.6)' : '2px solid transparent' }}
              >
                Компетенции
              </Button>
              <Button
                color="inherit"
                onClick={() => navigate('/professions')}
                sx={{ border: isActive('/professions') ? '2px solid rgba(255,255,255,0.6)' : '2px solid transparent' }}
              >
                Профессии
              </Button>
              <Button
                color="inherit"
                onClick={() => navigate('/analyse')}
                sx={{ border: isActive('/analyse') ? '2px solid rgba(255,255,255,0.6)' : '2px solid transparent' }}
              >
                Анализ
              </Button>
            </Box>

            <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
              <Button color="inherit" onClick={handleLogout}>
                Выйти
              </Button>
            </Box>
          </Container>
        </Toolbar>
      </AppBar>

      <Outlet />
    </>
  )
}

export default MainLayout