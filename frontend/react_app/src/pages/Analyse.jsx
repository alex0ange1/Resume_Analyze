import { useNavigate } from 'react-router-dom'
import { logout } from '../utilits/auth'
import { Box, Button, Select, MenuItem, FormControl, InputLabel, CircularProgress, Alert, Typography, Paper } from '@mui/material'
import LogoutIcon from '@mui/icons-material/Logout'
import CloudUploadIcon from '@mui/icons-material/CloudUpload'
import { useState } from 'react'

const Analyse = () => {
	const navigate = useNavigate()
	const [file, setFile] = useState(null)
	const [profession, setProfession] = useState('')
	const [loading, setLoading] = useState(false)
	const [result, setResult] = useState(null)
	const [error, setError] = useState('')
	const [uploadedText, setUploadedText] = useState('')

	const professions = ['Data Scientist', 'Data Engineer', 'Technical analyst in AI', 'Manager in AI']

	const handleFileChange = e => {
		const selectedFile = e.target.files[0]
		setFile(selectedFile)
		setResult(null)
		setError('')
		setUploadedText('')
	}

	const handleAnalyze = async () => {
		if (!file) {
			setError('Выберите файл резюме')
			return
		}

		if (!profession) {
			setError('Выберите профессию для анализа')
			return
		}

		setLoading(true)
		setError('')
		setResult(null)

		try {
			// 1. Загружаем файл и получаем текст
			const formData = new FormData()
			formData.append('file', file)

			const token = localStorage.getItem('token')

			// Загрузка файла
			const uploadResponse = await fetch('http://localhost:8000/upload-resume', {
				method: 'POST',
				headers: {
					Authorization: `Bearer ${token}`,
				},
				body: formData,
			})

			if (!uploadResponse.ok) {
				const errorData = await uploadResponse.json()
				throw new Error(errorData.detail || 'Ошибка загрузки файла')
			}

			const uploadData = await uploadResponse.json()
			const resumeText = uploadData.text
			setUploadedText(resumeText)

			// 2. Отправляем текст на анализ
			const analyzeResponse = await fetch('http://localhost:8000/evaluate-resume', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					Authorization: `Bearer ${token}`,
				},
				body: JSON.stringify({
					resume_text: resumeText,
					profession: profession,
				}),
			})

			if (!analyzeResponse.ok) {
				const errorData = await analyzeResponse.json()
				throw new Error(errorData.detail || 'Ошибка анализа резюме')
			}

			const analyzeData = await analyzeResponse.json()
			setResult(analyzeData)
		} catch (err) {
			setError(err.message || 'Произошла ошибка при анализе')
			console.error('Ошибка:', err)
		} finally {
			setLoading(false)
		}
	}

	const handleLogout = () => {
		logout()
		navigate('/login')
	}

	return (
		<Box sx={{ maxWidth: 800, margin: 'auto', p: 3 }}>
			<Typography variant='h4' gutterBottom align='center'>
				Анализ резюме
			</Typography>

			<Paper elevation={3} sx={{ p: 3, mb: 3 }}>
				{/* Выбор файла */}
				<Box sx={{ mb: 3 }}>
					<Button variant='outlined' component='label' startIcon={<CloudUploadIcon />} sx={{ mr: 2 }}>
						Выберите файл резюме
						<input type='file' hidden onChange={handleFileChange} accept='.pdf,.doc,.docx,.txt' />
					</Button>
					{file && (
						<Typography variant='body2' sx={{ mt: 1 }}>
							📄 Выбран файл: <strong>{file.name}</strong> ({Math.round(file.size / 1024)} KB)
						</Typography>
					)}
				</Box>

				{/* Выбор профессии */}
				<FormControl fullWidth sx={{ mb: 3 }}>
					<InputLabel>Профессия для анализа</InputLabel>
					<Select value={profession} label='Профессия для анализа' onChange={e => setProfession(e.target.value)}>
						<MenuItem value=''>
							<em>Выберите профессию</em>
						</MenuItem>
						{professions.map(prof => (
							<MenuItem key={prof} value={prof}>
								{prof}
							</MenuItem>
						))}
					</Select>
				</FormControl>

				{/* Кнопка анализа */}
				<Button variant='contained' color='primary' onClick={handleAnalyze} disabled={!file || !profession || loading} fullWidth size='large'>
					{loading ? (
						<>
							<CircularProgress size={24} sx={{ mr: 1 }} />
							Анализируем...
						</>
					) : (
						'Проанализировать резюме'
					)}
				</Button>

				{/* Ошибки */}
				{error && (
					<Alert severity='error' sx={{ mt: 2 }}>
						{error}
					</Alert>
				)}
			</Paper>

			{/* Результаты */}
			{result && (
				<Paper elevation={3} sx={{ p: 3, mb: 3 }}>
					<Typography variant='h5' gutterBottom>
						📊 Результаты анализа
					</Typography>

					{/* Уровни компетенций */}
					<Typography variant='h6' gutterBottom>
						Уровни компетенций:
					</Typography>
					<Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
						{Object.entries(result.final_levels || {}).map(([skill, level]) => (
							<Paper
								key={skill}
								elevation={1}
								sx={{
									p: 1,
									minWidth: 120,
									textAlign: 'center',
									bgcolor: level === 3 ? '#4caf50' : level === 2 ? '#ff9800' : '#f44336',
									color: 'white',
								}}>
								<Typography variant='body2'>{skill}</Typography>
								<Typography variant='h6'>Уровень {level}</Typography>
							</Paper>
						))}
					</Box>

					{/* Общая оценка */}
					{result.evaluation && (
						<>
							<Typography variant='h6' gutterBottom>
								Общая оценка:
							</Typography>
							<Paper elevation={1} sx={{ p: 2, mb: 2 }}>
								<Typography>
									<strong>Совпадение:</strong> {result.evaluation.match_percentage || result.evaluation.score || 0}%
								</Typography>
								{result.evaluation.recommendations && (
									<>
										<Typography sx={{ mt: 1 }}>
											<strong>Рекомендации:</strong>
										</Typography>
										<ul>
											{result.evaluation.recommendations.map((rec, idx) => (
												<li key={idx}>{rec}</li>
											))}
										</ul>
									</>
								)}
							</Paper>
						</>
					)}

					{/* Отладочная информация */}
					<details>
						<summary>Подробная информация (для отладки)</summary>
						<pre style={{ background: '#f5f5f5', padding: '10px', borderRadius: '4px', overflow: 'auto' }}>{JSON.stringify(result, null, 2)}</pre>
					</details>
				</Paper>
			)}

			{/* Извлечённый текст (для отладки) */}
			{uploadedText && (
				<Paper elevation={2} sx={{ p: 2, mb: 3 }}>
					<Typography variant='h6' gutterBottom>
						Извлечённый текст:
					</Typography>
					<Box
						sx={{
							maxHeight: 200,
							overflow: 'auto',
							p: 1,
							bgcolor: '#f9f9f9',
							borderRadius: 1,
							fontSize: '0.9rem',
						}}>
						{uploadedText.length > 500 ? uploadedText.substring(0, 500) + '...' : uploadedText}
					</Box>
					<Typography variant='caption' color='text.secondary'>
						Показано {Math.min(uploadedText.length, 500)} из {uploadedText.length} символов
					</Typography>
				</Paper>
			)}

			{/* Кнопка выхода */}
			<Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
				<Button
					variant='contained'
					color='secondary'
					onClick={handleLogout}
					endIcon={<LogoutIcon />}
					sx={{
						borderRadius: '4px',
						px: 3,
						py: 1,
						bgcolor: '#0078C8',
						'&:hover': {
							bgcolor: '#00396F',
						},
					}}>
					Выйти из аккаунта
				</Button>
			</Box>
		</Box>
	)
}

export default Analyse
