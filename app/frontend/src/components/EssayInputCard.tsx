import { useState } from 'react'
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

type EssayInputCardProps = {
  onAnalyze?: (aiEssay: string, humanizedEssay: string) => void
}

function EssayInputCard({ onAnalyze }: EssayInputCardProps) {
  const [aiEssay, setAiEssay] = useState('')
  const [humanizedEssay, setHumanizedEssay] = useState('')

  const handlePaste = async (target: 'ai' | 'human') => {
    try {
      const text = await navigator.clipboard.readText()
      if (target === 'ai') {
        setAiEssay(text)
      } else {
        setHumanizedEssay(text)
      }
    } catch (err) {
      console.error('Failed to read clipboard contents: ', err)
    }
  }

  return (
    <section style={essayInputSectionStyle}>
      <div style={essayInputCardStyle}>
        <h2 style={essayInputTitleStyle}>Compare & Analyze Text</h2>

        <div style={essayInputRowStyle}>
          {/* AI Essay Column */}
          <div style={essayColumnStyle}>
            <label style={essayLabelStyle}>
              <span>AI-Generated Essay</span>
              <button style={essayPasteButtonStyle} onClick={() => handlePaste('ai')}>
                Paste
              </button>
            </label>
            <textarea
              placeholder="Enter or paste the original AI-generated text here..."
              value={aiEssay}
              onChange={(e) => setAiEssay(e.target.value)}
              style={essayTextareaStyle}
            />
          </div>

          {/* Humanized Essay Column */}
          <div style={essayColumnStyle}>
            <label style={essayLabelStyle}>
              <span>Humanized Essay</span>
              <button style={essayPasteButtonStyle} onClick={() => handlePaste('human')}>
                Paste
              </button>
            </label>
            <textarea
              placeholder="Enter or paste the edited, humanized version here..."
              value={humanizedEssay}
              onChange={(e) => setHumanizedEssay(e.target.value)}
              style={essayTextareaStyle}
            />
          </div>
        </div>

        <div style={essayInputFooterStyle}>
          <button
            onClick={() => onAnalyze?.(aiEssay, humanizedEssay)}
            style={essayAnalyzeButtonStyle}
            disabled={!aiEssay || !humanizedEssay}
          >
            Analyze
          </button>
        </div>
      </div>
    </section>
  )
}

export default EssayInputCard