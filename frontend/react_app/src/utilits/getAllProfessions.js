import apiClient from './api';

export const get_all_prof = async () => {
  try {
    const response = await apiClient.get('/all_professions');
    return response.data;
  } catch (error) {
    console.error("Ошибка при получении списка профессий:", error);
    throw error;
  }
};