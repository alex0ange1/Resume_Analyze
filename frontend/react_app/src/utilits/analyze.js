import apiClient from './api';

export const upload_files = async (files, professionId) => {
    try {
      const formData = new FormData();
  
      // Если пришёл один файл — делаем его массивом
      const filesArray = Array.isArray(files) ? files : [files];
  
      filesArray.forEach(file => {
        formData.append('files', file); // ключ 'files' — должен соответствовать тому, как сервер ожидает
      });
  
      const response = await apiClient.post(`/analyze_files/${professionId}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
  
      return response.data;
    } catch (error) {
      console.error("Ошибка при загрузке файлов резюме:", error);
      throw error;
    }
  };
  

export const get_resumes = async (ids) => {
    try {
      const response = await apiClient.post('/get_resumes_by_ids', ids);
      return response.data;
    } catch (error) {
      console.error("Ошибка при получении информации резюме:", error);
      throw error;
    }
  };


// Функция для получения анализа резюме по профессии
export const get_analyze_resumes = async (profession_id, resumeIdsArray) => {
  try {
    const response = await apiClient.post(
      `/get_analyze_resumes_for_profession/${profession_id}`,
      resumeIdsArray // <-- тело запроса
    );

    return response.data;
  } catch (error) {
    console.error('Ошибка при получении анализа резюме:', error);
    console.error('Детали ошибки:', error.response ? error.response.data : 'Нет данных');
    throw error;
  }
};
