import { useState, useRef, useEffect } from 'react'
import styles from './InputBar.module.css'

const SUGGESTIONS = [
  "🍔 KFC & Zorko burgers",
  "🍕 Domino's & Pizza Hut combos under ₹300",
  "🌯 Limra Garden special rolls",
  "🥟 Wow! Momo varieties",
  "🍲 Saleem Punjabi Dhaba specials",
  "🥤 Frozen Bottle milkshakes & desserts",
  "🥞 Uncle Peter's Pancakes",
]

export default function InputBar({ onSend, disabled }) {
  const [value, setValue] = useState('')
  const textareaRef = useRef(null)

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`
    }
  }, [value])

  const submit = (textToSend) => {
    const trimmed = (textToSend || value).trim()
    if (!trimmed || disabled) return
    onSend(trimmed)
    setValue('')
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
    }
  }

  const handleKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      submit()
    }
  }

  return (
    <div className={styles.bar}>
      <div className={styles.suggestions}>
        {SUGGESTIONS.map((s, idx) => (
          <button
            key={idx}
            className={styles.chip}
            onClick={() => submit(s.replace(/^[^\w\s]+\s*/, ''))}
            disabled={disabled}
          >
            {s}
          </button>
        ))}
      </div>

      <div className={styles.inputWrapper}>
        <textarea
          ref={textareaRef}
          className={styles.input}
          placeholder="Ask about Vellore menus, prices, operating hours..."
          value={value}
          onChange={e => setValue(e.target.value)}
          onKeyDown={handleKey}
          disabled={disabled}
          rows={1}
        />
        <button
          className={styles.sendBtn}
          onClick={() => submit()}
          disabled={disabled || !value.trim()}
          aria-label="Send"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
            <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
          </svg>
        </button>
      </div>
      <div className={styles.metaRow}>
        <span className={styles.hint}>Press Enter to send · Shift+Enter for new line</span>
        {value.length > 0 && <span className={styles.charCount}>{value.length} chars</span>}
      </div>
    </div>
  )
}


