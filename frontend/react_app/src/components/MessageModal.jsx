import React from 'react';
import styles from './modal.module.css'; // Импортируем стили

const MessageModal = ({ open, message, type, onClose }) => {
  if (!open) return null; // Если окно не открыто, ничего не рендерим

  // Функция для определения типа модального окна (цвет фона)
  const getModalClass = () => {
    switch (type) {
      case 'success':
        return styles['modal-success'];
      case 'error':
        return styles['modal-error'];
      case 'warning':
        return styles['modal-warning'];
      case 'info':
        return styles['modal-info'];
      default:
        return '';
    }
  };

  // Заменяем \n на <br /> для обработки новых строк
  const formattedMessage = message.split('\n').map((str, index, array) => (
    <>
      {str}
      {index < array.length - 1 && <br />}
    </>
  ));

  return (
    <div className={styles['modal-overlay']} onClick={onClose}>
      <div
        className={`${styles['modal-content']} ${getModalClass()}`}
        onClick={(e) => e.stopPropagation()}
      >
        <h2>
          {type === 'success'
            ? 'Успех!'
            : type === 'error'
            ? 'Ошибка'
            : type === 'warning'
            ? 'Предупреждение'
            : 'Информация'}
        </h2>
        <p>{formattedMessage}</p>
        <button className={styles['modal-close']} onClick={onClose}>
          Закрыть
        </button>
      </div>
    </div>
  );
};

export default MessageModal;