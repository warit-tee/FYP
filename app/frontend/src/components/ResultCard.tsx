import { useEffect, useMemo, useState } from 'react'
import { useLocation, Link } from 'react-router-dom'
import { runFullAnalysis } from '../api/analysis'
import type { FullAnalysisResult } from '../api/types'
import { pageStyle, cardStyle, errorStyle, titleStyle } from '../helpers/styles'
import { PRIMARY } from '../helpers/colors'

function ResultCard() {
  const location = useLocation()
  const aiEssay = location.state?.aiEssay?.trim() || ''
  const humanizedEssay = location.state?.humanizedEssay?.trim() || ''
  const numQuestions = location.state?.numQuestions ?? 10
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [results, setResults] = useState<FullAnalysisResult | null>(null)

  useEffect(() => {
    let mounted = true

    async function fetchResults() {
      if (!aiEssay || !humanizedEssay) {
        setIsLoading(false)
        return
      }

      setIsLoading(true)
      setError(null)

      try {
        const data = await runFullAnalysis({
          ai_text: aiEssay,
          humanized_text: humanizedEssay,
          num_questions: numQuestions
        })

        if (mounted) {
          setResults(data)
        }
      } catch (err: unknown) {
        if (mounted) {
          const message = err instanceof Error ? err.message : 'An unknown error occurred.'
          setError(message)
        }
      } finally {
        if (mounted) {
          setIsLoading(false)
        }
      }
    }

    fetchResults()

    return () => {
      mounted = false
    }
  }, [aiEssay, humanizedEssay, numQuestions])

  const fullAnalysisText = useMemo(() => {
    if (!results) {
      return ''
    }

    return JSON.stringify(results, null, 2)
  }, [results])

  if (!aiEssay || !humanizedEssay) {
    return (
      <div style={pageStyle}>
        <div style={{ ...cardStyle, maxWidth: '800px', margin: '0 auto' }}>
          <div style={errorStyle}>
            <h2>No Input Text Found</h2>
            <p>Please go back and analyze two texts to see the results.</p>
            <Link to="/input" style={{ color: PRIMARY, textDecoration: 'none', fontWeight: 600 }}>
              Go to Input Page
            </Link>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div style={pageStyle}>
      <div style={{ ...cardStyle, maxWidth: '1000px', margin: '0 auto' }}>
        <h2 style={titleStyle}>Full Analysis Text</h2>

        {isLoading && (
          <div className="loading-wrap" role="status" aria-live="polite">
            <div className="spinner" aria-hidden="true" />
            <p>Analyzing...</p>
          </div>
        )}

        {!isLoading && error && (
          <div style={errorStyle}>
            <p style={{ color: 'red' }}>Error: {error}</p>
            <Link to="/input" style={{ color: PRIMARY, textDecoration: 'none', fontWeight: 600 }}>
              Back to Input
            </Link>
          </div>
        )}

        {!isLoading && !error && (
          <pre className="analysis-text-output">{fullAnalysisText}</pre>
        )}
      </div>
    </div>
  )
}

export default ResultCard