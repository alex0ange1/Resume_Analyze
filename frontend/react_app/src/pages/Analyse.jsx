import { useState } from 'react'
import {
  Container,
  Paper,
  Typography,
  Box,
  TextField,
  Button,
} from '@mui/material'
import FileUpload from '../components/FileUpload'
import { logout } from '../utilits/auth'
import { useNavigate } from 'react-router-dom'

const Analyse = () => {
  const navigate = useNavigate()
  const [professionName, setProfessionName] = useState('')

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const professionOk = professionName.trim().length > 0

  return (
    <Box
      sx={{
        minHeight: 'calc(100vh - 64px)',
        background: '#F6F8FB',
        py: 4,
      }}
    >
      <Container maxWidth="md">
        <Paper elevation={2} sx={{ p: 3, borderRadius: 2 }}>
          <Typography variant="h5" sx={{ color: 'primary.main', fontWeight: 700 }}>
            Анализ соответствия навыков
          </Typography>

          <TextField
            fullWidth
            label="Название профессии"
            placeholder="Например: ml-developer"
            value={professionName}
            onChange={(e) => setProfessionName(e.target.value)}
          />

          <Box sx={{ mt: 3 }}>
            <Typography sx={{ mb: 1 }}>Загрузите резюме для анализа</Typography>
            <FileUpload professionName={professionName} disabled={!professionOk} />
          </Box>
        </Paper>

        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
          <Button variant="contained" onClick={handleLogout}>
            Выйти из аккаунта
          </Button>
        </Box>
      </Container>
    </Box>
  )
}

export default Analyse
