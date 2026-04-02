import apiClient from './api'


export const analyzeResume = async (file, profession) => {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('profession', profession.trim())

  const response = await apiClient.post('/resumes/analyze', formData, {
    transformRequest: (data, headers) => {
      if (data instanceof FormData) {
        delete headers['Content-Type']
      }
      return data
    },
  })

  return response.data
}
