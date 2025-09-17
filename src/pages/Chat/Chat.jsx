import React, { useState, useRef, useEffect } from 'react';
import './Chat.scss';

const Chat = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: 'María González',
      content: '¡Hola! ¿Alguien ha terminado la tarea de Cálculo?',
      timestamp: '10:30 AM',
      isOwn: false,
      avatar: 'M'
    },
    {
      id: 2,
      sender: 'Tú',
      content: 'Sí, ya la terminé. ¿Necesitas ayuda con algún ejercicio?',
      timestamp: '10:32 AM',
      isOwn: true,
      avatar: 'T'
    },
    {
      id: 3,
      sender: 'Carlos Rodríguez',
      content: 'Yo también necesito ayuda con el ejercicio 5 😅',
      timestamp: '10:35 AM',
      isOwn: false,
      avatar: 'C'
    },
    {
      id: 4,
      sender: 'María González',
      content: '¡Perfecto! ¿Podríamos hacer una videollamada más tarde?',
      timestamp: '10:36 AM',
      isOwn: false,
      avatar: 'M'
    }
  ]);

  const [newMessage, setNewMessage] = useState('');
  const [activeUsers] = useState([
    { id: 1, name: 'María González', status: 'online', avatar: 'M' },
    { id: 2, name: 'Carlos Rodríguez', status: 'online', avatar: 'C' },
    { id: 3, name: 'Ana López', status: 'away', avatar: 'A' },
    { id: 4, name: 'Diego Martínez', status: 'offline', avatar: 'D' }
  ]);

  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = (e) => {
    e.preventDefault();
    if (newMessage.trim()) {
      const message = {
        id: messages.length + 1,
        sender: 'Tú',
        content: newMessage,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        isOwn: true,
        avatar: 'T'
      };
      setMessages([...messages, message]);
      setNewMessage('');
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-sidebar">
        <div className="sidebar-header">
          <h2>Usuarios Activos</h2>
        </div>
        
        <div className="users-list">
          {activeUsers.map(user => (
            <div key={user.id} className={`user-item ${user.status}`}>
              <div className="user-avatar">
                {user.avatar}
                <div className={`status-dot ${user.status}`}></div>
              </div>
              <div className="user-info">
                <span className="user-name">{user.name}</span>
                <span className="user-status">
                  {user.status === 'online' ? 'En línea' : 
                   user.status === 'away' ? 'Ausente' : 'Desconectado'}
                </span>
              </div>
            </div>
          ))}
        </div>

        <div className="chat-actions">
          <button className="action-btn video-call">
            📹 Videollamada
          </button>
          <button className="action-btn share-screen">
            🖥️ Compartir Pantalla
          </button>
          <button className="action-btn file-share">
            📎 Compartir Archivo
          </button>
        </div>
      </div>

      <div className="chat-main">
        <div className="chat-header">
          <h1>Chat Grupal - Cálculo I</h1>
          <div className="chat-info">
            <span className="online-count">{activeUsers.filter(u => u.status === 'online').length} usuarios en línea</span>
          </div>
        </div>

        <div className="messages-container">
          {messages.map(message => (
            <div key={message.id} className={`message ${message.isOwn ? 'own' : 'other'}`}>
              {!message.isOwn && (
                <div className="message-avatar">
                  {message.avatar}
                </div>
              )}
              
              <div className="message-content">
                {!message.isOwn && (
                  <div className="message-sender">{message.sender}</div>
                )}
                <div className="message-text">{message.content}</div>
                <div className="message-timestamp">{message.timestamp}</div>
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        <form className="message-input-container" onSubmit={handleSendMessage}>
          <div className="input-wrapper">
            <input
              type="text"
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              placeholder="Escribe tu mensaje..."
              className="message-input"
            />
            <button type="button" className="emoji-btn">😊</button>
            <button type="button" className="attach-btn">📎</button>
          </div>
          <button type="submit" className="send-btn" disabled={!newMessage.trim()}>
            ➤
          </button>
        </form>
      </div>
    </div>
  );
};

export default Chat;
