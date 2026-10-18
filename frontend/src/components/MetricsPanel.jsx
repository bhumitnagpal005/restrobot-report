import { useState } from 'react'
import styles from './MetricsPanel.module.css'

function scoreColor(value) {
  if (value >= 0.8) return 'green'
  if (value >= 0.55) return 'yellow'
  return 'red'
}

function ScoreBar({ label, value }) {
  const color = scoreColor(value)
  const pct = Math.round(value * 100)
  return (
    <div className={styles.scoreRow}>
      <span className={styles.scoreLabel}>{label}</span>
      <div className={styles.barTrack}>
        <div className={`${styles.barFill} ${styles[color]}`} style={{ width: `${pct}%` }} />
      </div>
      <span className={`${styles.scorePct} ${styles[color]}`}>{pct}%</span>
    </div>
  )
}

function LatencyPill({ label, value }) {
  return (
    <div className={styles.pill}>
      <span className={styles.pillLabel}>{label}</span>
      <span className={styles.pillValue}>{value} ms</span>
    </div>
  )
}

export default function MetricsPanel({ metrics, exchangeId }) {
  const [open, setOpen] = useState(false)
  const [llmScores, setLlmScores] = useState(null)
  const [evaluating, setEvaluating] = useState(false)
  const [evalError, setEvalError] = useState(null)

  const { retrieval_confidence, latency } = metrics

  const handleEvaluate = async () => {
    setEvaluating(true)
    setEvalError(null)
    try {
      const res = await fetch('/api/evaluate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ exchange_id: exchangeId }),
      })
      if (!res.ok) throw new Error('Evaluation failed')
      const data = await res.json()
      setLlmScores(data)
    } catch (err) {
      setEvalError('Could not evaluate — try again.')
    } finally {
      setEvaluating(false)
    }
  }

  return (
    <div className={styles.wrapper}>
      <button className={styles.toggle} onClick={() => setOpen(o => !o)}>
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
          <polyline points={open ? "18 15 12 9 6 15" : "6 9 12 15 18 9"} />
        </svg>
        {open ? 'Hide' : 'View'} metrics
      </button>

      {open && (
        <div className={styles.panel}>

          {/* Always-available scores */}
          <p className={styles.section}>Retrieval</p>
          <ScoreBar label="Retrieval Confidence" value={retrieval_confidence} />

          {/* LLM-as-judge scores — loaded on demand */}
          <p className={styles.section}>Quality</p>
          {llmScores ? (
            <>
              <ScoreBar label="Faithfulness" value={llmScores.faithfulness} />
              <ScoreBar label="Answer Relevance" value={llmScores.answer_relevance} />
            </>
          ) : (
            <div className={styles.evaluateRow}>
              <p className={styles.evalHint}>
                Runs an LLM judge to score faithfulness and answer relevance.
                Uses 1 API call.
              </p>
              {evalError && <p className={styles.evalError}>{evalError}</p>}
              <button
                className={styles.evaluateBtn}
                onClick={handleEvaluate}
                disabled={evaluating}
              >
                {evaluating ? (
                  <span className={styles.spinner} />
                ) : (
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" />
                  </svg>
                )}
                {evaluating ? 'Evaluating…' : 'Evaluate response'}
              </button>
            </div>
          )}

          {/* Latency */}
          <p className={styles.section}>Latency</p>
          <div className={styles.pills}>
            <LatencyPill label="Retrieval" value={latency.retrieval_ms} />
            <LatencyPill label="Generation" value={latency.generation_ms} />
            <LatencyPill label="Total" value={latency.total_ms} />
          </div>
        </div>
      )}
    </div>
  )
}
