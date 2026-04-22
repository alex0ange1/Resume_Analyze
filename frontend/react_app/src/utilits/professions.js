import api from './api'

export const getAllProfessions = async () => {
  const res = await api.get('/professions')
  return res.data
}

export const getProfessionById = async (id) => {
  const res = await api.get(`/professions/${id}`)
  return res.data
}

export const addProfession = async (payload) => {
  const res = await api.post('/professions', payload)
  return res.data
}

export const updateProfession = async (id, payload) => {
  const res = await api.put(`/professions/${id}`, payload)
  return res.data
}

export const deleteProfession = async (id) => {
  await api.delete(`/professions/${id}`)
}
