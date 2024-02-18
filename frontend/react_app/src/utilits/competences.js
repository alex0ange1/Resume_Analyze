import api from './api'

export const getAllCompetences = async () => {
  const res = await api.get('/all_competencies')
  return res.data
}

export const addCompetence = async (name) => {
  const res = await api.post('/add_competence', { name })
  return res.data
}

export const updateCompetence = async (id, name) => {
  const res = await api.put(`/update_competence/${id}`, { name })
  return res.data
}

export const deleteCompetence = async (id) => {
  await api.delete(`/delete_competence/${id}`)
}