import { useEffect, useMemo, useState } from 'react'
import {
  Box,
  Typography,
  Button,
  Paper,
  List,
  ListItem,
  ListItemText,
  IconButton,
  Divider,
} from '@mui/material'
import DeleteIcon from '@mui/icons-material/Delete'
import MessageModal from './MessageModal'
import Loader from './Loader'
import { analyzeResume } from '../utilits/analyze'

const ACCEPT = '.pdf,.docx,.txt,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document,text/plain'

const isAllowedFile = (file) => {
  const name = (file.name || '').toLowerCase()
  if (name.endsWith('.pdf')) return file.type === 'application/pdf' || file.type === ''
  if (name.endsWith('.docx')) {
    return (
      file.type ===
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document' || file.type === ''
    )
  }
  if (name.endsWith('.txt')) return file.type === 'text/plain' || file.type === ''
  return false
}

const formatLevel = (level) => {
  const n = Number(level)
  if (Number.isFinite(n) && n >= 0 && n <= 3) {
    return `${n}/3`
  }
  return String(level)
}

const FileUpload = ({ professionName, disabled }) => {
  const [file, setFile] = useState(null)
  const [analysis, setAnalysis] = useState(null)
  const [loading, setLoading] = useState(false)

  const [open, setOpen] = useState(false)
  const [message, setMessage] = useState('')
  const [type, setType] = useState('')

  const trimmedProfession = (professionName || '').trim()
  const canPick = useMemo(() => !disabled && trimmedProfession.length > 0, [disabled, trimmedProfession])
  const canAnalyze = useMemo(() => canPick && !!file, [canPick, file])

  useEffect(() => {
    setFile(null)
    setAnalysis(null)
  }, [trimmedProfession])

  const handleOpen = (msg, t) => {
    setMessage(msg)
    setType(t)
    setOpen(true)
  }

  const handleClose = () => setOpen(false)

  const handleFileChange = (event) => {
    const selected = event.target.files?.[0]
    if (!selected) return

    if (!isAllowedFile(selected)) {
      handleOpen('Выберите файл в формате PDF, DOCX или TXT', 'warning')
      event.target.value = ''
      return
    }

    setFile(selected)
    setAnalysis(null)
    event.target.value = ''
  }

  const handleRemoveFile = () => {
    setFile(null)
    setAnalysis(null)
  }

  const handleAnalyze = async () => {
    if (!trimmedProfession) {
      handleOpen('Укажите название профессии', 'warning')
      return
    }
    if (!file) {
      handleOpen('Выберите файл резюме', 'warning')
      return
    }

    try {
      setLoading(true)
      setAnalysis(null)
      const data = await analyzeResume(file, trimmedProfession)
      setAnalysis(data)
    } catch (e) {
      const msg = e?.response?.data?.detail || e?.message || 'Ошибка при анализе'
      handleOpen(String(msg), 'error')
    } finally {
      setLoading(false)
    }
  }

  const matchPct =
    analysis && analysis.match_percent != null
      ? `${Number(analysis.match_percent).toFixed(1)}%`
      : null

  const finalLevels = analysis?.final_levels && typeof analysis.final_levels === 'object'
    ? Object.entries(analysis.final_levels)
    : []

  const missing = Array.isArray(analysis?.missing_skills) ? analysis.missing_skills : []

  return (
    <>
      <MessageModal open={open} message={message} type={type} onClose={handleClose} />

      {loading && <Loader message="Анализируем... Пожалуйста, подождите." />}

      <Box>
        <Box sx={{ mb: 2 }}>
          <Button
            variant="contained"
            component="label"
            disabled={!canPick}
            sx={{
              textTransform: 'none',
              opacity: canPick ? 1 : 0.6,
            }}
          >
            Выбрать файл
            <input type="file" hidden accept={ACCEPT} onChange={handleFileChange} />
          </Button>

          {!trimmedProfession && (
            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.8 }}>
              Сначала укажите профессию
            </Typography>
          )}
        </Box>

        {file && (
          <>
            <Paper variant="outlined" sx={{ p: 1.5, mb: 2 }}>
              <Typography variant="subtitle2" sx={{ mb: 1 }}>
                Загруженные файлы (1):
              </Typography>

              <List dense>
                <ListItem
                  secondaryAction={
                    <IconButton edge="end" onClick={handleRemoveFile} aria-label="Удалить файл">
                      <DeleteIcon fontSize="small" />
                    </IconButton>
                  }
                >
                  <ListItemText
                    primary={file.name}
                    secondary={
                      file.name.toLowerCase().endsWith('.pdf')
                        ? 'PDF'
                        : file.name.toLowerCase().endsWith('.txt')
                          ? 'TXT'
                          : 'DOCX'
                    }
                  />
                </ListItem>
              </List>
            </Paper>

            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
              <Button
                variant="contained"
                onClick={handleAnalyze}
                disabled={!canAnalyze}
                sx={{ textTransform: 'uppercase', fontWeight: 700, px: 3, py: 1.2 }}
              >
                Запустить анализ
              </Button>
            </Box>
          </>
        )}

        {analysis && (
          <Box sx={{ mt: 3, p: 2, bgcolor: 'background.default', borderRadius: 2 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Результаты анализа
            </Typography>

            <Divider sx={{ mb: 2 }} />

            <Paper variant="outlined" sx={{ p: 2.5, bgcolor: '#fff' }}>
              <Typography
                variant="subtitle1"
                sx={{ fontWeight: 700, letterSpacing: 0.5, mb: 2, textTransform: 'uppercase' }}
              >
                Подробный отчёт по резюме
              </Typography>

              <Typography variant="body2" sx={{ mb: 0.5 }}>
                <strong>Резюме:</strong> {file?.name ?? '—'}
              </Typography>
              <Typography variant="body2" sx={{ mb: 0.5 }}>
                <strong>Профессия:</strong> {analysis.profession ?? trimmedProfession}
              </Typography>
              {matchPct != null && (
                <Typography variant="body2" sx={{ mb: 2 }}>
                  <strong>Процент соответствия:</strong> {matchPct}
                </Typography>
              )}

              {finalLevels.length > 0 && (
                <>
                  <Typography variant="subtitle2" sx={{ mt: 2, mb: 1, fontWeight: 600 }}>
                    Оценка компетенций
                  </Typography>
                  <Box component="ul" sx={{ m: 0, pl: 2.5 }}>
                    {finalLevels.map(([skill, level]) => (
                      <Typography key={skill} component="li" variant="body2" sx={{ mb: 0.5 }}>
                        {skill}: {formatLevel(level)}
                      </Typography>
                    ))}
                  </Box>
                </>
              )}

              {missing.length > 0 && (
                <>
                  <Typography variant="subtitle2" sx={{ mt: 2, mb: 1, fontWeight: 600 }}>
                    Недостающие навыки
                  </Typography>
                  <Box component="ul" sx={{ m: 0, pl: 2.5 }}>
                    {missing.map((s, i) => (
                      <Typography key={`${s.name}-${i}`} component="li" variant="body2" sx={{ mb: 0.5 }}>
                        {s.name}: требуется уровень {s.required_level}, у кандидата {s.candidate_level}
                      </Typography>
                    ))}
                  </Box>
                </>
              )}

              {finalLevels.length === 0 && missing.length === 0 && (
                <Typography variant="body2" color="text.secondary">
                  Нет данных по компетенциям в ответе сервера.
                </Typography>
              )}
            </Paper>
          </Box>
        )}
      </Box>
    </>
  )
}

export default FileUpload
