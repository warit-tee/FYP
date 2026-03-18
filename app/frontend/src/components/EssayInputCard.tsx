import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  essayInputSectionStyle,
  essayInputCardStyle,
  essayInputTitleStyle,
  essayInputRowStyle,
  essayColumnStyle,
  essayLabelStyle,
  essayTextareaStyle,
  essayInputFooterStyle,
  essayAnalyzeButtonStyle,
  essayPasteButtonStyle
} from '../helpers/styles'

function EssayInputCard() {
  const [aiEssay, setAiEssay] = useState('')
  const [humanizedEssay, setHumanizedEssay] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()

  const handlePaste = async (target: 'ai' | 'human') => {
    try {
      const text = await navigator.clipboard.readText()
      if (target === 'ai') setAiEssay(text)
      else setHumanizedEssay(text)
    } catch (err) {
      console.error('Failed to read clipboard contents: ', err)
    }
  }

  const handleAnalyze = async () => {
    setIsLoading(true)
    setError(null)

    try {
      const response = await fetch('/full-analysis', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ai_text: aiEssay,
          humanized_text: humanizedEssay
        })
      })

      const data = await response.json()
      if (!response.ok) {
        throw new Error(data.error || 'An unknown error occurred.')
      }

      // On success, navigate to the results page with the data
      navigate('/results', { state: { results: data } })
    } catch (err: any) {
      setError(err.message)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <section style={essayInputSectionStyle}>
      <div style={essayInputCardStyle}>
        <h2 style={essayInputTitleStyle}>Compare & Analyze Text</h2>

        <div style={essayInputRowStyle}>
          <div style={essayColumnStyle}>
            <label style={essayLabelStyle}>
              <span>AI-Generated Essay</span>
              <button style={essayPasteButtonStyle} onClick={() => handlePaste('ai')}>Paste</button>
            </label>
            <textarea
              placeholder="Enter or paste the original AI-generated text here..."
              value={aiEssay}
              onChange={(e) => setAiEssay(e.target.value)}
              style={essayTextareaStyle}
              disabled={isLoading}
            />
          </div>

          <div style={essayColumnStyle}>
            <label style={essayLabelStyle}>
              <span>Humanized Essay</span>
              <button style={essayPasteButtonStyle} onClick={() => handlePaste('human')}>Paste</button>
            </label>
            <textarea
              placeholder="Enter or paste the edited, humanized version here..."
              value={humanizedEssay}
              onChange={(e) => setHumanizedEssay(e.target.value)}
              style={essayTextareaStyle}
              disabled={isLoading}
            />
          </div>
        </div>

        <div style={essayInputFooterStyle}>
          {error && <p style={{ color: 'red', marginRight: 'auto' }}>Error: {error}</p>}
          <button
            onClick={handleAnalyze}
            style={essayAnalyzeButtonStyle}
            disabled={!aiEssay || !humanizedEssay || isLoading}
          >
            {isLoading ? 'Analyzing...' : 'Analyze'}
          </button>
        </div>
      </div> 
    </section>
  )
}

export default EssayInputCard