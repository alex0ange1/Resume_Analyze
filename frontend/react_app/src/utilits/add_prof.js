import apiClient from './api';

export const add_prof = async (name, competencies) => {
  try {
    const data = {
        name: name,
        competencies: {
          competencies: competencies
        }
      };

    const response = await apiClient.post('/professions', data);
    return response.data;
  } catch (error) {
    console.error("Ошибка при добавлении профессий:", error);
    throw error;
  }
};
