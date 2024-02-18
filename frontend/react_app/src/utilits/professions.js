import api from './api'

export const getAllProfessions = async () => {
  const res = await api.get('/all_professions')
  return res.data
}

export const getProfessionById = async (id) => {
  const res = await api.get(`/profession/${id}`)
  return res.data
}

export const addProfession = async (payload) => {
  const res = await api.post('/add_profession', payload)
  return res.data
}

export const updateProfession = async (id, payload) => {
  const res = await api.put(`/update_profession/${id}`, payload)
  return res.data
}

export const deleteProfession = async (id) => {
  await api.delete(`/delete_profession/${id}`)
}