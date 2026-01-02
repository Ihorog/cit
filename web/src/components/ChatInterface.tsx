'use client'

import { useState, useRef, useEffect } from 'react'
import styles from './ChatInterface.module.css'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
}

interface ChatInterfaceProps {
  apiUrl?: string
}

export default function ChatInterface({ 
  apiUrl = process.env.NEXT_PUBLIC_CIT_API_URL || 'http://127.0.0.1:8790' 
}: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [healthStatus, setHealthStatus] = useState<'ok' | 'error' | 'unknown'>('unknown')
  const logRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  // Health check
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await fetch(`${apiUrl}/health`)
        if (response.ok) {
          setHealthStatus('ok')
        } else {
          setHealthStatus('error')
        }
      } catch (error) {
        setHealthStatus('error')
      }
    }

    checkHealth()
    const interval = setInterval(checkHealth, 10000) // 10 seconds
    return () => clearInterval(interval)
  }, [apiUrl])

  // Auto-scroll to bottom
  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight
    }
  }, [messages])

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return

    const userMessage = input.trim()
    const messageId = `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    setInput('')
    setMessages(prev => [...prev, { id: messageId, role: 'user', content: userMessage }])
    setIsLoading(true)

    try {
      const response = await fetch(`${apiUrl}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userMessage }),
      })

      if (!response.ok) {
        throw new Error(`Помилка сервера: ${response.status}`)
      }

      const data = await response.json()
      
      // Validate response structure
      if (typeof data !== 'object' || data === null) {
        throw new Error('Невірний формат відповіді від сервера')
      }

      const replyId = `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
      
      if (data.error) {
        setMessages(prev => [...prev, { 
          id: replyId,
          role: 'assistant', 
          content: `Помилка: ${data.error}` 
        }])
      } else if (data.reply && typeof data.reply === 'string') {
        setMessages(prev => [...prev, { 
          id: replyId,
          role: 'assistant', 
          content: data.reply 
        }])
      } else {
        throw new Error('Відповідь не містить очікуваних даних')
      }
    } catch (error) {
      const errorId = `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
      let errorMessage = 'Помилка з\'єднання. '
      
      if (error instanceof Error) {
        if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
          errorMessage += 'Перевірте підключення до інтернету або запустіть CIT сервер.'
        } else {
          errorMessage += error.message
        }
      } else {
        errorMessage += 'Невідома помилка. Спробуйте ще раз.'
      }
      
      setMessages(prev => [...prev, { 
        id: errorId,
        role: 'assistant', 
        content: errorMessage
      }])
    } finally {
      setIsLoading(false)
      textareaRef.current?.focus()
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const getHealthBadge = () => {
    switch (healthStatus) {
      case 'ok':
        return <span className={styles.healthOk}>● online</span>
      case 'error':
        return <span className={styles.healthError}>● offline</span>
      default:
        return <span className={styles.healthUnknown}>● перевірка...</span>
    }
  }

  return (
    <div className={styles.chatContainer}>
      <div className={styles.header}>
        <h2 className={styles.title}>Казкар</h2>
        <div className={styles.badge}>{getHealthBadge()}</div>
      </div>
      
      <div className={styles.chat}>
        <div ref={logRef} className={styles.log}>
          {messages.length === 0 && (
            <div className={styles.welcome}>
              <p>Напиши щось або натисни Enter...</p>
            </div>
          )}
          {messages.map((msg) => (
            <div 
              key={msg.id} 
              className={`${styles.message} ${msg.role === 'user' ? styles.userMessage : styles.aiMessage}`}
            >
              {msg.content}
            </div>
          ))}
          {isLoading && (
            <div className={`${styles.message} ${styles.aiMessage} ${styles.loading}`}>
              <span className={styles.dots}>●●●</span>
            </div>
          )}
        </div>
        
        <div className={styles.inputBar}>
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Напиши або натисни Enter..."
            rows={2}
            disabled={isLoading}
            className={styles.textarea}
          />
          <button
            onClick={sendMessage}
            disabled={isLoading || !input.trim()}
            className={styles.sendButton}
          >
            {isLoading ? '...' : 'Надіслати'}
          </button>
        </div>
      </div>
    </div>
  )
}
