import { useEffect, useRef } from 'react'
import Message from './Message'
import TypingIndicator from './TypingIndicator'
import styles from './ChatWindow.module.css'

const QUICK_CATEGORIES = [
  { icon: '🍔', label: 'Cheapest Burger', query: 'What is the cheapest burger at KFC, Zorko, or Limra Garden?' },
  { icon: '🍕', label: 'Pizza Combos', query: "What pizza combos under ₹300 are available at Domino's or Pizza Hut in Vellore?" },
  { icon: '🥟', label: 'Momos & Pure Veg', query: 'Show me momo options at Wow! Momo and veg specials at Kailash Parbat.' },
  { icon: '🥞', label: 'Shakes & Pancakes', query: "What thick milkshakes & pancakes are served at Frozen Bottle and Uncle Peter's Pancakes?" },
]

export default function ChatWindow({ messages, isLoading, onSend }) {
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  const isInitialState = messages.length <= 1

  return (
    <div className={styles.window}>
      <div className={styles.inner}>
        {messages.map(msg => (
          <Message key={msg.id} message={msg} />
        ))}

        {isInitialState && (
          <div className={styles.heroSection}>
            <p className={styles.heroSubtitle}>Explore menus, prices, and food details across top Vellore restaurants:</p>
            <div className={styles.heroGrid}>
              {QUICK_CATEGORIES.map((cat, idx) => (
                <button
                  key={idx}
                  className={styles.heroCard}
                  onClick={() => onSend && onSend(cat.query)}
                >
                  <span className={styles.heroIcon}>{cat.icon}</span>
                  <div className={styles.heroText}>
                    <span className={styles.heroTitle}>{cat.label}</span>
                    <span className={styles.heroPrompt}>{cat.query}</span>
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}

        {isLoading && <TypingIndicator />}
        <div ref={bottomRef} />
      </div>
    </div>
  )
}

