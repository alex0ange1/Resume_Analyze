import api from './api'

export const getAllCompetences = async () => {
  const res = await api.get('/competencies')
  return res.data
}

export const addCompetence = async (name) => {
  const res = await api.post('/competencies', { name })
  return res.data
}

export const updateCompetence = async (id, name) => {
  const res = await api.put(`/competencies/${id}`, { name })
  return res.data
}

export const deleteCompetence = async (id) => {
  await api.delete(`/competencies/${id}`)
}
