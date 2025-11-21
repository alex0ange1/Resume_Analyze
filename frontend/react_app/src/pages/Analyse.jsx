import { useNavigate } from 'react-router-dom';
import { logout } from '../utilits/auth';
import FileUpload from '../components/FileUpload'
import { Box, Button } from '@mui/material';
import LogoutIcon from '@mui/icons-material/Logout';
import { useEffect, useState } from 'react';
import { add_prof } from '../utilits/add_prof';
import Loader from '../components/Loader';

const Analyse = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  const prof_list = [
    {
      "name": "Data Scientist",
      "competencies": {
        "competencies": [
          {
                "name": "Определения, история развития и главные тренды ИИ",
                "level": 1
            },
            {
                "name": "Процесс, стадии и методологии разработки решений на основе ИИ (Docker, Linux/Bash, Git)",
                "level": 2
            },
            {
                "name": "Статистические методы и первичный анализ данных",
                "level": 2
            },
            {
                "name": "Оценка качества работы методов ИИ",
                "level": 2
            },
            {
                "name": "Языки программирования и библиотеки (Python, C++)",
                "level": 1
            },
            {
                "name": "SQL базы данных (GreenPLum, Postgres, Oracle)",
                "level": 1
            },
            {
                "name": "NoSQL базы данных (Cassandra, MongoDB, ElasticSearch, Neo4J, Hbase)",
                "level": 1
            },
            {
                "name": "Hadoop, SPARK, Hive",
                "level": 1
            },
            {
                "name": "Качество и предобработка данных, подходы и инструменты",
                "level": 2
            },
            {
                "name": "Работа с распределенной кластерной системой",
                "level": 1
            },
            {
                "name": "Методы машинного обучения",
                "level": 2
            },
            {
                "name": "Рекомендательные системы",
                "level": 1
            },
            {
                "name": "Методы оптимизации",
                "level": 2
            },
            {
                "name": "Основы глубокого обучения",
                "level": 2
            },
            {
                "name": "Анализ изображений и видео",
                "level": 2
            },
            {
                "name": "Машинное обучение на больших данных",
                "level": 1
            },
            {
                "name": "Глубокое обучение для анализа естественного языка",
                "level": 2
            },
            {
                "name": "Обучение с подкреплением и глубокое обучение с подкреплением",
                "level": 1
            },
            {
                "name": "Глубокое обучение для анализа и генерации изображений, видео",
                "level": 2
            },
            {
                "name": "Анализ естественного языка",
                "level": 2
            },
            {
                "name": "Информационный поиск",
                "level": 1
            }
        ]
      }
    },
    {
      "name": "Data Engineer",
      "competencies": {
        "competencies": [
          {
                "name": "Определения, история развития и главные тренды ИИ",
                "level": 1
            },
            {
                "name": "Процесс, стадии и методологии разработки решений на основе ИИ (Docker, Linux/Bash, Git)",
                "level": 2
            },
            {
                "name": "Статистические методы и первичный анализ данных",
                "level": 1
            },
            {
                "name": "Оценка качества работы методов ИИ",
                "level": 1
            },
            {
                "name": "Языки программирования и библиотеки (Python, С++)",
                "level": 2
            },
            {
                "name": "Работа с распределенной кластерной системой",
                "level": 2
            },
            {
                "name": "Методы машинного обучения",
                "level": 2
            },
            {
                "name": "Методы оптимизации",
                "level": 1
            },
            {
                "name": "Основы глубокого обучения",
                "level": 2
            },
            {
                "name": "Анализ изображений и видео",
                "level": 1
            },
            {
                "name": "Машинное обучение на больших данных",
                "level": 2
            },
            {
                "name": "Массово параллельные вычисления для ускорения машинного обучения (GPU)",
                "level": 1
            },
            {
                "name": "Глубокое обучение для анализа естественного языка",
                "level": 2
            },
            {
                "name": "Потоковая обработка данных (data streaming, event processing)",
                "level": 2
            },
            {
                "name": "Глубокое обучение для анализа и генерации изображений, видео",
                "level": 2
            },
            {
                "name": "Анализ естественного языка",
                "level": 1
            },
            {
                "name": "Информационный поиск",
                "level": 1
            },
            {
                "name": "SQL базы данных (GreenPlum, Postgres, Oracle)",
                "level": 3
            },
            {
                "name": "NoSQL базы данных (Cassandra, MongoDB, ElasticSearch, Neo4J, Hbase)",
                "level": 3
            },
            {
                "name": "Массово параллельная обработка и анализ данных",
                "level": 2
            },
            {
                "name": "Hadoop, SPARK, Hive",
                "level": 2
            },
            {
                "name": "Качество и предобработка данных, подходы и инструменты",
                "level": 3
            }
        ]
      }
    },    
    {
      "name": "Technical analyst in AI",
      "competencies": {
        "competencies": [
          {
                "name": "Определения, история развития и главные тренды ИИ", 
                "level": 1
            },
            {
                "name": "Процесс, стадии и методологии разработки решений на основе ИИ (Docker, Linux/Bash, Git)",
                "level": 1
            },
            {
                "name": "Статистические методы и первичный анализ данных", 
                "level": 1
            },
            {
                "name": "Оценка качества работы методов ИИ", 
                "level": 1
            },
            {
                "name": "Языки программирования и библиотеки (Python, С++)",
                "level": 1
            },
            {
                "name": "Методы машинного обучения", 
                "level": 1
            },
            {
                "name": "Рекомендательные системы", 
                "level": 1
            },
            {
                "name": "Анализ изображений и видео", 
                "level": 1
            },
            {
                "name": "Анализ естественного языка",
                "level": 1
            },
            {
                "name": "Основы глубокого обучения",
                "level": 1
            },
            {
                "name": "Глубокое обучение для анализа и генерации изображений, видео", 
                "level": 1
            },
            {
                "name": "Глубокое обучение для анализа естественного языка", 
                "level": 1
            },
            {
                "name": "SQL базы данных (GreenPlum, Postgres, Oracle)",
                "level": 1
            },
            {
                "name": "NoSQL базы данных (Cassandra, MongoDB, ElasticSearch, Neo4J, Hbase)", 
                "level": 1
            },
            {
                "name": "Качество и предобработка данных, подходы и инструменты", 
                "level": 1
            }
        ]
      }
    },
    {
      "name": "Manager in AI",
      "competencies": {
        "competencies": [
          {
                "name": "Определения, история развития и главные тренды ИИ",
                "level": 1
            },
            {
                "name": "Процесс, стадии и методологии разработки решений на основе ИИ (Docker, Linux/Bash, Git)",
                "level": 1
            },
            {
                "name": "Оценка качества работы методов ИИ", 
                "level": 1
            },
            {
                "name": "Методы машинного обучения",
                "level": 1
            },
            {
                "name": "Анализ изображений и видео", 
                "level": 1
            },
            {
                "name": "Анализ естественного языка",
                "level": 1
            },
            {
                "name": "Основы глубокого обучения", 
                "level": 1
            },
            {
                "name": "Глубокое обучение для анализа и генерации изображений, видео", 
                "level": 1
            },
            {
                "name": "Глубокое обучение для анализа естественного языка", 
                "level": 1
            },
            {
                "name": "SQL базы данных (GreenPlum, Postgres, Oracle)", 
                "level": 1
            },
            {
                "name": "NoSQL базы данных (Cassandra, MongoDB, ElasticSearch, Neo4J, Hbase)", 
                "level": 1
            },
            {
                "name": "Качество и предобработка данных, подходы и инструменты", 
                "level": 1
            }
        ]
      }
    }
  ];
  useEffect(() => {
    const fetchData = async () => {
      try {
        await Promise.all(
          prof_list.map(prof =>
            add_prof(prof.name, prof.competencies.competencies) // Асинхронно выполняем все операции
          )
        );
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div>
      <FileUpload />
      
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3, mb: 2 }}>
        <Button
          variant="contained"
          color="primary"
          onClick={handleLogout}
          endIcon={<LogoutIcon />}
          sx={{ 
            borderRadius: '4px',
            px: 3,
            py: 1,
            bgcolor: '#0078C8',
            '&:hover': {
              bgcolor: '#00396F',
            }
          }}
        >
          Выйти из аккаунта
        </Button>
      </Box>
    </div>
  );
};

export default Analyse;
