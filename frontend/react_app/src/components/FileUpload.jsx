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
  Switch,
  FormControlLabel,
} from '@mui/material'
import DeleteIcon from '@mui/icons-material/Delete'
import { jsPDF } from 'jspdf'
import MessageModal from './MessageModal'
import Loader from './Loader'
import { upload_files, get_resumes, get_analyze_resumes } from '../utilits/analyze'

const FileUpload = ({ professionId, disabled }) => {
  const [files, setFiles] = useState([])
  const [report, setReport] = useState(null)
  const [isDetailed, setIsDetailed] = useState(false)
  const [loading, setLoading] = useState(false)

  const [open, setOpen] = useState(false)
  const [message, setMessage] = useState('')
  const [type, setType] = useState('')

  const canPickFiles = useMemo(() => !disabled && !!professionId, [disabled, professionId])
  const canAnalyze = useMemo(() => canPickFiles && files.length > 0, [canPickFiles, files.length])

  useEffect(() => {
    setFiles([])
    setReport(null)
    setIsDetailed(false)
  }, [professionId])

  const handleOpen = (msg, t) => {
    setMessage(msg)
    setType(t)
    setOpen(true)
  }

  const handleClose = () => setOpen(false)

  const handleFileChange = (event) => {
    const selectedFiles = Array.from(event.target.files || [])
    const valid = selectedFiles.filter(
      (f) =>
        f.type === 'application/pdf' ||
        f.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )

    if (selectedFiles.length === 0) return

    if (valid.length === 0) {
      handleOpen('Пожалуйста, выберите файлы форматов PDF или DOCX', 'warning')
      event.target.value = ''
      return
    }

    setFiles((prev) => [...prev, ...valid])
    setReport(null)
    event.target.value = ''
  }

  const handleRemoveFile = (index) => {
    setFiles((prev) => prev.filter((_, i) => i !== index))
    setReport(null)
  }

  const normalizeAnalysisArray = (response) => {
    if (Array.isArray(response)) return response

    if (response && typeof response === 'object') {
      const keys = ['resumes', 'data', 'results', 'items', 'analysis']
      for (const k of keys) {
        if (Array.isArray(response[k])) return response[k]
      }
    }

    return null
  }

  const buildReport = (resumes, analysisRaw) => {
    const analyzed = normalizeAnalysisArray(analysisRaw)

    const summary = `Отчет по следующим резюме: ${resumes.map((r) => r.last_name || 'Unknown').join(', ')}`

    let detailed = 'ПОДРОБНЫЙ ОТЧЕТ ПО РЕЗЮМЕ\n\n'

    if (Array.isArray(analyzed) && analyzed.length > 0) {
      analyzed.forEach((ra, idx) => {
        detailed += `Резюме №${idx + 1}\n`
        detailed += `Персональные данные: ${(ra.last_name || '') + ' ' + (ra.first_name || '') + ' ' + (ra.middle_name || '')}\n`
        detailed += `Процент соответствия: ${ra.match_percentage ?? 0}%\n`

        const mismatched = ra.mismatched_competencies || ra.missing_competencies

        if (Array.isArray(mismatched) && mismatched.length > 0) {
          detailed += 'Недостающие компетенции:\n'
          mismatched.forEach((c) => {
            if (typeof c === 'string') detailed += `- ${c}\n`
            else detailed += `- ${c?.name ?? 'Unknown'}\n`
          })
        } else {
          detailed += 'Все необходимые компетенции присутствуют\n'
        }

        detailed += '\n--------------------------------------------------\n\n'
      })
    } else {
      detailed += 'Формат данных анализа:\n'
      detailed += JSON.stringify(analysisRaw, null, 2)
      detailed += '\n\nНе удалось обработать данные в стандартном формате.'
    }

    return { summary, detailed }
  }

  const handleAnalyze = async () => {
    if (!professionId) {
      handleOpen('Сначала выберите профессию', 'warning')
      return
    }
    if (files.length === 0) {
      handleOpen('Пожалуйста, выберите файлы для анализа', 'warning')
      return
    }

    try {
      setLoading(true)
      setReport(null)

      const uploaded = await upload_files(files, professionId)

      const resumeIds = uploaded?.resume_ids || uploaded?.resumeIds
      if (!Array.isArray(resumeIds) || resumeIds.length === 0) {
        throw new Error('Бэкенд не вернул resume_ids после загрузки файлов')
      }

      const resumesResp = await get_resumes(resumeIds)
      const resumes = resumesResp?.resumes || resumesResp || []

      const analysisResp = await get_analyze_resumes(professionId, resumeIds)

      const newReport = buildReport(Array.isArray(resumes) ? resumes : [], analysisResp)
      setReport(newReport)
    } catch (e) {
      const msg = e?.response?.data?.detail || e?.message || 'Произошла ошибка при анализе'
      handleOpen(String(msg), 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleDownloadPDF = () => {
    if (!report) return

    const text = isDetailed ? report.detailed : report.summary

    const doc = new jsPDF()
    const margin = 10
    let y = margin

    const lines = doc.splitTextToSize(text, 180)
    lines.forEach((line) => {
      if (y + 8 > doc.internal.pageSize.height - margin) {
        doc.addPage()
        y = margin
      }
      doc.text(line, margin, y)
      y += 8
    })

    doc.save('report.pdf')
  }

  return (
    <>
      <MessageModal open={open} message={message} type={type} onClose={handleClose} />

      {loading && <Loader message="Анализируем... Пожалуйста, подождите." />}

      <Box>
        <Box sx={{ mb: 2 }}>
          <Button
            variant="contained"
            component="label"
            disabled={!canPickFiles}
            sx={{
              textTransform: 'none',
              opacity: canPickFiles ? 1 : 0.6,
            }}
          >
            Выбрать файлы
            <input type="file" hidden accept=".pdf,.docx" multiple onChange={handleFileChange} />
          </Button>

          {!professionId && (
            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.8 }}>
              Сначала выберите профессию
            </Typography>
          )}
        </Box>

        {files.length > 0 && (
          <>
            <Paper variant="outlined" sx={{ p: 1.5, mb: 2 }}>
              <Typography variant="subtitle2" sx={{ mb: 1 }}>
                Загруженные файлы ({files.length}):
              </Typography>

              <List dense>
                {files.map((file, index) => (
                  <ListItem
                    key={`${file.name}-${index}`}
                    secondaryAction={
                      <IconButton edge="end" onClick={() => handleRemoveFile(index)}>
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    }
                  >
                    <ListItemText
                      primary={file.name}
                      secondary={file.type.includes('pdf') ? 'PDF' : 'DOCX'}
                    />
                  </ListItem>
                ))}
              </List>
            </Paper>

            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
              <Button variant="contained" onClick={handleAnalyze} disabled={!canAnalyze}>
                Запустить анализ
              </Button>
            </Box>
          </>
        )}

        {report && (
          <Box sx={{ mt: 3, p: 2, bgcolor: 'background.default', borderRadius: 2 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Результаты анализа
            </Typography>

            <FormControlLabel
              control={
                <Switch checked={isDetailed} onChange={() => setIsDetailed((v) => !v)} />
              }
              label={isDetailed ? 'Подробный отчет' : 'Краткий отчет'}
              sx={{ mb: 1 }}
            />

            <Divider sx={{ mb: 2 }} />

            <Paper variant="outlined" sx={{ p: 2, bgcolor: '#fff', whiteSpace: 'pre-line' }}>
              <Typography variant="body2">
                {isDetailed ? report.detailed : report.summary}
              </Typography>
            </Paper>

            <Box sx={{ mt: 2 }}>
              <Button variant="contained" onClick={handleDownloadPDF}>
                Скачать отчет в PDF
              </Button>
            </Box>
          </Box>
        )}
      </Box>
    </>
  )
}

export default FileUpload