import { useState } from 'react'
import MetricsPanel from './MetricsPanel'
import styles from './Message.module.css'

function formatTime(ts) {
  if (!ts) return ''
  return new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

export default function Message({ message }) {
  const isUser = message.role === 'user'
  const isError = message.role === 'error'
  const [copied, setCopied] = useState(false)

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className={`${styles.row} ${isUser ? styles.rowUser : styles.rowBot}`}>
      {!isUser && (
        <div className={`${styles.avatar} ${styles.botAvatar}`}>
          <span>🤖</span>
        </div>
      )}
      <div className={`${styles.bubbleWrapper} ${isUser ? styles.wrapperUser : styles.wrapperBot}`}>
        <div className={`${styles.bubble} ${isUser ? styles.user : isError ? styles.error : styles.bot}`}>
          <div className={styles.content}>{message.content}</div>
          <div className={styles.footer}>
            <span className={styles.time}>{formatTime(message.timestamp)}</span>
            {!isUser && !isError && (
              <button className={styles.copyBtn} onClick={handleCopy} title="Copy response">
                {copied ? '✓ Copied' : 'Copy'}
              </button>
            )}
          </div>
        </div>
        {message.role === 'bot' && message.metrics && (
          <MetricsPanel metrics={message.metrics} exchangeId={message.exchangeId} />
        )}
      </div>
      {isUser && (
        <div className={`${styles.avatar} ${styles.userAvatar}`}>
          <span>👤</span>
        </div>
      )}
    </div>
  )
}

