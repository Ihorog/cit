'use client'

import { useState, useRef, useEffect } from 'react'
import styles from './ChatInterface.module.css'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

interface ChatInterfaceProps {
  apiEndpoint?: string
}

export default function ChatInterface({
  apiEndpoint = process.env.NEXT_PUBLIC_CIT_API_URL || 'http://127.0.0.1:8790/chat'
}: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputText, setInputText] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isListening, setIsListening] = useState(false)
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const messagesEndRef = useRef<HTMLDivElement>(null)
  const recognitionRef = useRef<any>(null)
  const synthesisRef = useRef<SpeechSynthesisUtterance | null>(null)

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Initialize Speech Recognition
  useEffect(() => {
    if (typeof window !== 'undefined' && 'webkitSpeechRecognition' in window) {
      const SpeechRecognition = (window as any).webkitSpeechRecognition
      recognitionRef.current = new SpeechRecognition()
      recognitionRef.current.continuous = false
      recognitionRef.current.interimResults = false
      recognitionRef.current.lang = 'uk-UA'

      recognitionRef.current.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript
        setInputText(transcript)
        setIsListening(false)
      }

      recognitionRef.current.onerror = () => {
        setIsListening(false)
        setError('Помилка розпізнавання мови')
      }

      recognitionRef.current.onend = () => {
        setIsListening(false)
      }
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop()
      }
    }
  }, [])

  const toggleListening = () => {
    if (!recognitionRef.current) {
      setError('Розпізнавання мови не підтримується у вашому браузері')
      return
    }

    if (isListening) {
      recognitionRef.current.stop()
      setIsListening(false)
    } else {
      setError(null)
      recognitionRef.current.start()
      setIsListening(true)
    }
  }

  const speakText = (text: string) => {
    if (!('speechSynthesis' in window)) {
      setError('Синтез мови не підтримується у вашому браузері')
      return
    }

    // Stop current speech if any
    window.speechSynthesis.cancel()

    const utterance = new SpeechSynthesisUtterance(text)
    utterance.lang = 'uk-UA'
    utterance.rate = 0.9
    utterance.pitch = 1

    utterance.onstart = () => setIsSpeaking(true)
    utterance.onend = () => setIsSpeaking(false)
    utterance.onerror = () => {
      setIsSpeaking(false)
      setError('Помилка синтезу мови')
    }

    synthesisRef.current = utterance
    window.speechSynthesis.speak(utterance)
  }

  const stopSpeaking = () => {
    window.speechSynthesis.cancel()
    setIsSpeaking(false)
  }

  const sendMessage = async () => {
    const trimmedText = inputText.trim()
    if (!trimmedText || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: trimmedText,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputText('')
    setIsLoading(true)
    setError(null)

    try {
      const response = await fetch(apiEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: trimmedText })
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.reply || data.error || 'Немає відповіді',
        timestamp: new Date()
      }

      setMessages(prev => [...prev, assistantMessage])

      // Auto-speak assistant response
      if (data.reply && !data.error) {
        speakText(data.reply)
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Невідома помилка'
      setError(`Помилка з'єднання: ${errorMessage}`)

      const errorMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `❌ Помилка: ${errorMessage}`,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMsg])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const clearChat = () => {
    setMessages([])
    setError(null)
    stopSpeaking()
  }

  return (
    <div className={styles.chatContainer}>
      {/* Header */}
      <div className={styles.chatHeader}>
        <h2 className={styles.chatTitle}>Казкар</h2>
        {messages.length > 0 && (
          <button
            onClick={clearChat}
            className={styles.clearButton}
            aria-label="Очистити чат"
          >
            🗑️
          </button>
        )}
      </div>

      {/* Error Banner */}
      {error && (
        <div className={styles.errorBanner}>
          {error}
          <button onClick={() => setError(null)} className={styles.errorClose}>✕</button>
        </div>
      )}

      {/* Messages Area */}
      <div className={styles.messagesArea}>
        {messages.length === 0 ? (
          <div className={styles.emptyState}>
            <div className={styles.emptyIcon}>💬</div>
            <p>Напиши або натисни на мікрофон</p>
            <p className={styles.emptyHint}>Поставте питання Ci</p>
          </div>
        ) : (
          messages.map(msg => (
            <div
              key={msg.id}
              className={`${styles.message} ${styles[msg.role]}`}
            >
              <div className={styles.messageContent}>
                {msg.content}
              </div>
              <div className={styles.messageTime}>
                {msg.timestamp.toLocaleTimeString('uk-UA', {
                  hour: '2-digit',
                  minute: '2-digit'
                })}
              </div>
              {msg.role === 'assistant' && (
                <button
                  onClick={() => speakText(msg.content)}
                  className={styles.speakButton}
                  aria-label="Озвучити відповідь"
                >
                  {isSpeaking ? '🔊' : '🔉'}
                </button>
              )}
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className={styles.inputArea}>
        <div className={styles.inputWrapper}>
          <textarea
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Напиши повідомлення..."
            className={styles.textInput}
            rows={1}
            disabled={isLoading}
          />

          <div className={styles.inputActions}>
            {/* Voice Input Button */}
            <button
              onClick={toggleListening}
              className={`${styles.actionButton} ${isListening ? styles.listening : ''}`}
              aria-label={isListening ? 'Зупинити запис' : 'Голосовий ввід'}
              disabled={isLoading}
            >
              {isListening ? '🎙️' : '🎤'}
            </button>

            {/* Stop Speaking Button */}
            {isSpeaking && (
              <button
                onClick={stopSpeaking}
                className={styles.actionButton}
                aria-label="Зупинити відтворення"
              >
                ⏸️
              </button>
            )}

            {/* Send Button */}
            <button
              onClick={sendMessage}
              className={`${styles.sendButton} ${isLoading ? styles.loading : ''}`}
              disabled={isLoading || !inputText.trim()}
              aria-label="Відправити"
            >
              {isLoading ? '⏳' : '📤'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
