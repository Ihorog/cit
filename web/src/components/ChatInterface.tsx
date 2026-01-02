'use client'

import { useState, useRef, useEffect } from 'react'
import styles from './ChatInterface.module.css'

interface Message {
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

interface ChatInterfaceProps {
  apiEndpoint?: string
}

export default function ChatInterface({ apiEndpoint = 'http://127.0.0.1:8790' }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isRecording, setIsRecording] = useState(false)
  const [healthStatus, setHealthStatus] = useState<{ ok: boolean; model?: string } | null>(null)
  const logRef = useRef<HTMLDivElement>(null)
  const recognitionRef = useRef<any>(null)

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight
    }
  }, [messages])

  // Health check polling
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await fetch(`${apiEndpoint}/health`)
        if (response.ok) {
          const data = await response.json()
          setHealthStatus({ ok: true, model: data.model })
        } else {
          setHealthStatus({ ok: false })
        }
      } catch (error) {
        setHealthStatus({ ok: false })
      }
    }

    checkHealth()
    const interval = setInterval(checkHealth, 4000)
    return () => clearInterval(interval)
  }, [apiEndpoint])

  // Initialize speech recognition
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
      if (SpeechRecognition) {
        recognitionRef.current = new SpeechRecognition()
        recognitionRef.current.lang = 'uk-UA'
        recognitionRef.current.continuous = false
        recognitionRef.current.interimResults = false

        recognitionRef.current.onresult = (event: any) => {
          const transcript = event.results[0][0].transcript
          setInput(transcript)
          setIsRecording(false)
        }

        recognitionRef.current.onerror = (event: any) => {
          console.error('Speech recognition error:', event.error)
          setIsRecording(false)
        }

        recognitionRef.current.onend = () => {
          setIsRecording(false)
        }
      }
    }
  }, [])

  const sendMessage = async () => {
    const text = input.trim()
    if (!text || isLoading) return

    const userMessage: Message = {
      role: 'user',
      content: text,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      const response = await fetch(`${apiEndpoint}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: text })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      const assistantMessage: Message = {
        role: 'assistant',
        content: data.reply || 'No response',
        timestamp: new Date()
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      const errorMessage: Message = {
        role: 'assistant',
        content: `Помилка: ${error instanceof Error ? error.message : 'Невідома помилка'}`,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const startRecording = () => {
    if (recognitionRef.current && !isRecording) {
      setIsRecording(true)
      try {
        recognitionRef.current.start()
      } catch (error) {
        console.error('Failed to start recording:', error)
        setIsRecording(false)
      }
    }
  }

  const speakText = (text: string) => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel()
      const utterance = new SpeechSynthesisUtterance(text)
      utterance.lang = 'uk-UA'
      window.speechSynthesis.speak(utterance)
    }
  }

  const speakLastMessage = () => {
    const lastAssistantMessage = [...messages].reverse().find(m => m.role === 'assistant')
    if (lastAssistantMessage) {
      speakText(lastAssistantMessage.content)
    }
  }

  return (
    <div className={styles.chatContainer}>
      {/* Status Bar */}
      <div className={styles.statusBar}>
        <div className={styles.healthBadge}>
          <span className={`${styles.statusDot} ${healthStatus?.ok ? styles.statusOnline : styles.statusOffline}`} />
          <span className={styles.statusText}>
            {healthStatus?.ok ? `Онлайн ${healthStatus.model ? `• ${healthStatus.model}` : ''}` : 'Офлайн'}
          </span>
        </div>
      </div>

      {/* Chat Log */}
      <div className={styles.chatLog} ref={logRef}>
        {messages.length === 0 && (
          <div className={styles.welcomeMessage}>
            <h3>👋 Привіт!</h3>
            <p>Напиши повідомлення або натисни 🎙️ для голосового введення</p>
          </div>
        )}
        {messages.map((msg, idx) => (
          <div key={idx} className={`${styles.message} ${msg.role === 'user' ? styles.userMessage : styles.aiMessage}`}>
            <div className={styles.messageContent}>{msg.content}</div>
          </div>
        ))}
        {isLoading && (
          <div className={`${styles.message} ${styles.aiMessage} ${styles.loadingMessage}`}>
            <div className={styles.messageContent}>
              <span className={styles.loadingDots}>
                <span>●</span><span>●</span><span>●</span>
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Input Bar */}
      <div className={styles.inputBar}>
        <textarea
          className={styles.messageInput}
          placeholder="Напиши або натисни 🎙️..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyPress}
          disabled={isLoading}
          rows={1}
        />
        <div className={styles.buttonGroup}>
          <button
            className={`${styles.button} ${styles.micButton}`}
            onClick={startRecording}
            disabled={isRecording || isLoading}
            title="Голосове введення (uk-UA)"
          >
            {isRecording ? '🔴' : '🎙️'}
          </button>
          <button
            className={`${styles.button} ${styles.ttsButton}`}
            onClick={speakLastMessage}
            disabled={messages.length === 0 || isLoading}
            title="Прослухати останню відповідь"
          >
            🔊
          </button>
          <button
            className={`${styles.button} ${styles.sendButton}`}
            onClick={sendMessage}
            disabled={!input.trim() || isLoading}
          >
            Надіслати
          </button>
        </div>
      </div>
    </div>
  )
}
