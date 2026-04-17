import { useEffect, useMemo, useState } from 'react'
import { useLocation, Link } from 'react-router-dom'
import { runFullAnalysis } from '../api/analysis'
import type { FullAnalysisResult } from '../api/types'
import {
  pageStyle,
  cardStyle,
  errorStyle,
  titleStyle,
  resultHeaderStyle,
  resultSubtitleStyle,
  resultOverviewGridStyle,
  resultStatCardStyle,
  resultStatTopRowStyle,
  resultStatTitleStyle,
  resultChipStyle,
  resultStatValueStyle,
  resultStatDescriptionStyle,
  progressTrackStyle,
  tabRowStyle,
  tabButtonBaseStyle,
  resultContentGridStyle,
  resultSectionCardStyle,
  resultSectionHeaderStyle,
  resultSectionTitleStyle,
  resultSectionDescriptionStyle,
  resultSectionBodyStyle,
  metricRowStyle,
  metricRowTopStyle,
  metricLabelWrapStyle,
  metricLabelStyle,
  metricValueStyle,
  metricDescriptionStyle,
  infoBoxStyle,
  infoBoxTitleStyle,
  infoBoxTextStyle,
  infoBoxStackStyle,
  emotionRowStyle,
  emotionRowTopStyle,
  emotionLabelStyle,
  emotionValueStyle,
} from '../helpers/styles'
import { PRIMARY, WHITE, GREY, BLACK } from '../helpers/colors'

type TabKey = 'semantic' | 'faithfulness' | 'detectability' | 'tone'

function clamp01(value: number) {
  return Math.max(0, Math.min(1, value))
}

function formatScore(value: number | null | undefined, digits = 2) {
  if (value === null || value === undefined || Number.isNaN(value)) return 'N/A'
  return value.toFixed(digits)
}

function formatPercentFrom01(value: number | null | undefined, digits = 1) {
  if (value === null || value === undefined || Number.isNaN(value)) return 'N/A'
  return `${(value * 100).toFixed(digits)}%`
}

function averageAvailable(values: Array<number | null | undefined>) {
  const valid = values.filter((v): v is number => v !== null && v !== undefined && !Number.isNaN(v))
  if (valid.length === 0) return null
  return valid.reduce((sum, v) => sum + v, 0) / valid.length
}

function getEmotionMap(items?: Array<{ label: string; score: number }>) {
  const map: Record<string, number> = {}
  for (const item of items || []) {
    map[item.label] = item.score
  }
  return map
}

function getTopEmotion(items?: Array<{ label: string; score: number }>) {
  if (!items || items.length === 0) return null
  return items[0]
}

function getTopEmotionDelta(
  ai?: Array<{ label: string; score: number }>,
  humanized?: Array<{ label: string; score: number }>
) {
  const aiTop = getTopEmotion(ai)
  if (!aiTop) return null

  const humanizedMap = getEmotionMap(humanized)
  const sameEmotionScore = humanizedMap[aiTop.label] ?? 0

  return Math.abs(aiTop.score - sameEmotionScore)
}

function ProgressBar({ value }: { value: number | null | undefined }) {
  const safeValue = value === null || value === undefined || Number.isNaN(value) ? 0 : clamp01(value)

  return (
    <div style={progressTrackStyle}>
      <div
        style={{
          width: `${safeValue * 100}%`,
          height: '100%',
          backgroundColor: PRIMARY,
          borderRadius: '999px',
          transition: 'width 0.25s ease',
        }}
      />
    </div>
  )
}

function StatCard({
  title,
  chip,
  value,
  description,
}: {
  title: string
  chip: string
  value: number | null
  description: string
}) {
  return (
    <div style={resultStatCardStyle}>
      <div style={resultStatTopRowStyle}>
        <h3 style={resultStatTitleStyle}>{title}</h3>
        <span style={resultChipStyle}>{chip}</span>
      </div>

      <div style={resultStatValueStyle}>{formatScore(value)}</div>
      <ProgressBar value={value} />
      <p style={resultStatDescriptionStyle}>{description}</p>
    </div>
  )
}

function TabButton({
  active,
  children,
  onClick,
}: {
  active: boolean
  children: React.ReactNode
  onClick: () => void
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      style={{
        ...tabButtonBaseStyle,
        backgroundColor: active ? PRIMARY : WHITE,
        color: active ? WHITE : BLACK,
        border: active ? `1px solid ${PRIMARY}` : `1px solid ${GREY}`,
      }}
    >
      {children}
    </button>
  )
}

function SectionCard({
  title,
  description,
  badge,
  children,
}: {
  title: string
  description: string
  badge?: string
  children: React.ReactNode
}) {
  return (
    <div style={resultSectionCardStyle}>
      <div style={resultSectionHeaderStyle}>
        <div>
          <h3 style={resultSectionTitleStyle}>{title}</h3>
          <p style={resultSectionDescriptionStyle}>{description}</p>
        </div>
        {badge && <span style={resultChipStyle}>{badge}</span>}
      </div>
      <div style={resultSectionBodyStyle}>{children}</div>
    </div>
  )
}

function MetricRow({
  label,
  tag,
  value,
  description,
  displayRealValue = false,
}: {
  label: string
  tag?: string
  value: number | null | undefined
  description: string
  displayRealValue?: boolean
}) {
  return (
    <div style={metricRowStyle}>
      <div style={metricRowTopStyle}>
        <div style={metricLabelWrapStyle}>
          <span style={metricLabelStyle}>{label}</span>
          {tag && <span style={resultChipStyle}>{tag}</span>}
        </div>
        <span style={metricValueStyle}>{displayRealValue ? value : formatScore(value)}</span>
      </div>

      <ProgressBar value={value} />
      <p style={metricDescriptionStyle}>{description}</p>
    </div>
  )
}

function InfoBox({
  title,
  children,
}: {
  title: string
  children: React.ReactNode
}) {
  return (
    <div style={infoBoxStyle}>
      <h4 style={infoBoxTitleStyle}>{title}</h4>
      <div style={infoBoxTextStyle}>{children}</div>
    </div>
  )
}

function EmotionComparisonRow({
  label,
  aiScore,
  humanizedScore,
}: {
  label: string
  aiScore: number | null | undefined
  humanizedScore: number | null | undefined
}) {
  return (
    <div style={metricRowStyle}>
      <div style={metricRowTopStyle}>
        <div style={metricLabelWrapStyle}>
          <span style={metricLabelStyle} style={{ ...metricLabelStyle, textTransform: 'capitalize' }}>
            {label}
          </span>
          <span style={resultChipStyle}>Emotion</span>
        </div>
      </div>

      <div style={emotionRowStyle}>
        <div style={emotionRowTopStyle}>
          <span style={emotionLabelStyle}>AI text</span>
          <span style={emotionValueStyle}>{formatPercentFrom01(aiScore)}</span>
        </div>
        <ProgressBar value={aiScore} />
      </div>

      <div style={emotionRowStyle}>
        <div style={emotionRowTopStyle}>
          <span style={emotionLabelStyle}>Humanized text</span>
          <span style={emotionValueStyle}>{formatPercentFrom01(humanizedScore)}</span>
        </div>
        <ProgressBar value={humanizedScore} />
      </div>

      <p style={metricDescriptionStyle}>
        Delta: {formatScore(
          aiScore !== null && aiScore !== undefined && humanizedScore !== null && humanizedScore !== undefined
            ? Math.abs(aiScore - humanizedScore)
            : null,
          3
        )}
      </p>
    </div>
  )
}

function ResultCard() {
  const location = useLocation()
  const aiEssay = location.state?.aiEssay?.trim() || ''
  const humanizedEssay = location.state?.humanizedEssay?.trim() || ''
  const numQuestions = location.state?.numQuestions ?? 10

  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [results, setResults] = useState<FullAnalysisResult | null>(null)
  const [activeTab, setActiveTab] = useState<TabKey>('semantic')

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
          num_questions: numQuestions,
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

  const derived = useMemo(() => {
    if (!results) return null

    const semanticAverage = averageAvailable([
      results.similarity?.similarity?.tfidf,
      results.similarity?.similarity?.sbert,
      results.similarity?.similarity?.nemotron,
    ])

    const faithfulnessAverage = averageAvailable([
      results.factual?.forward?.score,
      results.factual?.reversed?.score,
    ])

    const aiDetectabilityZeroGPT =
      results.detectability?.ai?.zerogpt?.fake_percentage !== undefined
        ? results.detectability.ai.zerogpt.fake_percentage / 100
        : null

    const humanizedDetectabilityZeroGPT =
      results.detectability?.humanized?.zerogpt?.fake_percentage !== undefined
        ? results.detectability.humanized.zerogpt.fake_percentage / 100
        : null

    const aiDetectabilitySapling = results.detectability?.ai?.sapling?.score ?? null
    const humanizedDetectabilitySapling = results.detectability?.humanized?.sapling?.score ?? null

    const detectabilityDeltaZeroGPT =
      aiDetectabilityZeroGPT !== null && humanizedDetectabilityZeroGPT !== null
        ? aiDetectabilityZeroGPT - humanizedDetectabilityZeroGPT
        : null

    const detectabilityDeltaSapling =
      aiDetectabilitySapling !== null && humanizedDetectabilitySapling !== null
        ? aiDetectabilitySapling - humanizedDetectabilitySapling
        : null
      
    const detectabilityDelta = averageAvailable([detectabilityDeltaZeroGPT, detectabilityDeltaSapling])
    
    const formalityDelta =
      results.tone?.delta_formality !== null && results.tone?.delta_formality !== undefined
        ? results.tone.delta_formality
        : null

    const topAiEmotion = getTopEmotion(results.emotions?.ai)
    const topHumanizedEmotion = getTopEmotion(results.emotions?.humanized)
    const topEmotionDelta = getTopEmotionDelta(results.emotions?.ai, results.emotions?.humanized)

    const formalityPreservation =
      formalityDelta !== null ? Math.max(0, 1 - Math.abs(formalityDelta)) : null

    const emotionPreservation =
      topEmotionDelta !== null ? Math.max(0, 1 - topEmotionDelta) : null

    const tonePreservation = averageAvailable([formalityPreservation, emotionPreservation])

    const aiEmotionMap = getEmotionMap(results.emotions?.ai)
    const humanizedEmotionMap = getEmotionMap(results.emotions?.humanized)
    const emotionLabels = Array.from(
      new Set([
        ...Object.keys(aiEmotionMap),
        ...Object.keys(humanizedEmotionMap),
      ])
    )

    return {
      semanticAverage,
      faithfulnessAverage,
      detectabilityDelta,
      formalityDelta,
      topAiEmotion,
      topHumanizedEmotion,
      topEmotionDelta,
      tonePreservation,
      aiEmotionMap,
      humanizedEmotionMap,
      emotionLabels,
    }
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
      <div style={{ ...cardStyle, maxWidth: '1200px', margin: '0 auto' }}>
        <div style={resultHeaderStyle}>
          <h2 style={titleStyle}>Analysis Overview</h2>
          <p style={resultSubtitleStyle}>
            Scores are reported on a 0–1 scale unless stated otherwise. Higher semantic and
            faithfulness scores are better. Tone and detectability describe stylistic and detector changes, respectively.
          </p>
        </div>

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

        {!isLoading && !error && results && derived && (
          <>
            <div style={resultOverviewGridStyle}>
              <StatCard
                title="Semantic"
                chip="Average"
                value={derived.semanticAverage}
                description="Average of TF-IDF, SBERT, and Nemotron similarity scores."
              />

              <StatCard
                title="Faithfulness"
                chip="QA / factual"
                value={derived.faithfulnessAverage}
                description="Average of forward and reversed factual consistency when available."
              />

              <StatCard
                title="Tone & Sentiment"
                chip="Combined"
                value={derived.tonePreservation}
                description="How well formality and emotional tone were preserved after humanization."
              />

              <StatCard
                title="Detectability"
                chip="Detectors"
                value={derived.detectabilityDelta}
                description="How much the humanizer reduced AI detectability."
              />
            </div>

            <div style={tabRowStyle}>
              <TabButton active={activeTab === 'semantic'} onClick={() => setActiveTab('semantic')}>
                Semantic
              </TabButton>
              <TabButton active={activeTab === 'faithfulness'} onClick={() => setActiveTab('faithfulness')}>
                Faithfulness
              </TabButton>
              <TabButton active={activeTab === 'tone'} onClick={() => setActiveTab('tone')}>
                Tone & Sentiment
              </TabButton>
              <TabButton active={activeTab === 'detectability'} onClick={() => setActiveTab('detectability')}>
                Detectability
              </TabButton>
            </div>

            {activeTab === 'semantic' && (
              <div style={resultContentGridStyle}>
                <SectionCard
                  title="Semantic Preservation Effects"
                  description="Measures how much meaning stays the same after rewriting."
                  badge="0–1"
                >
                  <MetricRow
                    label="TF-IDF similarity"
                    tag="Word-level"
                    value={results.similarity?.similarity?.tfidf}
                    description="Captures lexical overlap and vocabulary similarity."
                  />
                  <MetricRow
                    label="SBERT similarity"
                    tag="Sentence-level"
                    value={results.similarity?.similarity?.sbert}
                    description="Better reflects semantic meaning beyond exact word overlap."
                  />
                  <MetricRow
                    label="Nemotron similarity"
                    tag="Document-level"
                    value={results.similarity?.similarity?.nemotron}
                    description="Long-document semantic comparison across the full essay."
                  />
                </SectionCard>

                <div style={infoBoxStackStyle}>
                  <InfoBox title="Score interpretation">
                    <div>
                      <strong>TF-IDF</strong>
                      <ul style={{ margin: '0 0 0.5rem 0', paddingLeft: '1.1rem' }}>
                        <li>&gt;0.73: Strong semantic retention</li>
                        <li>0.57-0.74: Moderate drift</li>
                        <li>&lt;0.57: Substantial drift</li>
                      </ul>
                      <strong>SBERT</strong>
                      <ul style={{ margin: '0 0 0.5rem 0', paddingLeft: '1.1rem' }}>
                        <li>&gt;0.91: Strong semantic retention</li>
                        <li>0.84-0.91: Moderate drift</li>
                        <li>&lt;0.84: Substantial drift</li>
                      </ul>
                      <strong>Nemotron</strong>
                      <ul style={{ margin: 0, paddingLeft: '1.1rem' }}>
                        <li>&gt;0.96: Strong semantic retention</li>
                        <li>0.90-0.96: Moderate drift</li>
                        <li>&lt;0.90: Substantial drift</li>
                      </ul>
                    </div>
                  </InfoBox>

                  <InfoBox title="Differences">
                    <p><strong>TF-IDF difference:</strong> {formatScore(results.similarity?.difference?.tfidf, 3)}</p>
                    <p><strong>SBERT difference:</strong> {formatScore(results.similarity?.difference?.sbert, 3)}</p>
                    <p style={{ marginBottom: 0 }}>
                      <strong>Nemotron difference:</strong> {formatScore(results.similarity?.difference?.nemotron, 3)}
                    </p>
                  </InfoBox>
                </div>
              </div>
            )}

            {activeTab === 'faithfulness' && (
              <div style={resultContentGridStyle}>
                <SectionCard
                  title="Faithfulness"
                  description="Shows factual consistency without mixing it with detector outputs."
                  badge="0–1"
                >
                  <MetricRow
                    label="Forward factual score"
                    tag="Source → rewritten"
                    value={results.factual?.forward?.score}
                    description={
                      results.factual?.forward?.error || 'Checks whether original facts are preserved in the rewritten text.'
                    }
                  />

                  <MetricRow
                    label="Reversed factual score"
                    tag="Rewritten → source"
                    value={results.factual?.reversed?.score}
                    description={
                      results.factual?.reversed?.error || 'Checks whether rewritten claims are supported by the original text.'
                    }
                  />
                </SectionCard>

                <div style={infoBoxStackStyle}>
                  <InfoBox title="Score interpretation">
                    <ul style={{ margin: 0, paddingLeft: '1.1rem' }}>
                      <li>&gt;0.95: High factual consistency</li>
                      <li>&lt;0.85: Small factual consistency</li>
                    </ul>
                  </InfoBox>

                  <InfoBox title="Quick note">
                    <p style={{ marginTop: 0 }}>
                      Faithfulness is different from detectability.
                    </p>
                    <p style={{ marginBottom: 0 }}>
                      A text can preserve facts well but still be highly detectable as AI-generated.
                    </p>
                  </InfoBox>
                </div>
              </div>
            )}

            {activeTab === 'detectability' && (
              <div style={resultContentGridStyle}>
                <SectionCard
                  title="Detectability"
                  description="Compares available detector outputs for both the original AI text and the humanized text."
                >
                  <MetricRow
                    label="Sapling"
                    tag="AI text"
                    value={results.detectability?.ai?.sapling?.score ??  null}
                    description={results.detectability?.ai?.sapling?.error || 'AI probability for the original AI text from Sapling.'}
                  />

                  <MetricRow
                    label="Sapling"
                    tag="Humanized text"
                    value={results.detectability?.humanized?.sapling?.score ?? null}
                    description={results.detectability?.humanized?.sapling?.error || 'AI probability for the humanized text from Sapling.'}
                  />

                  <MetricRow
                    label="ZeroGPT"
                    tag="AI text"
                    value={
                      results.detectability?.ai?.zerogpt?.fake_percentage !== undefined
                        ? results.detectability.ai.zerogpt.fake_percentage / 100
                        : null
                    }
                    description={results.detectability?.ai?.zerogpt?.error ||"AI probability for the original AI text from ZeroGPT."}
                  />

                  <MetricRow
                    label="ZeroGPT"
                    tag="Humanized text"
                    value={
                      results.detectability?.humanized?.zerogpt?.fake_percentage !== undefined
                        ? results.detectability.humanized.zerogpt.fake_percentage / 100
                        : null
                    }
                    description={results.detectability?.humanized?.zerogpt?.error || "AI probability for the humanized text from ZeroGPT."}
                  />
                </SectionCard>

                <div style={infoBoxStackStyle}>
                  <InfoBox title="Score interpretation">
                    <div>
                      <strong>ZeroGPT</strong>
                      <ul style={{ margin: '0 0 0.5rem 0', paddingLeft: '1.1rem' }}>
                        <li>&gt;85.2: High AI confidence</li>
                        <li>&lt;42.5: Low AI confidence</li>
                      </ul>
                      <strong>Sapling</strong>
                      <ul style={{ margin: 0, paddingLeft: '1.1rem' }}>
                        <li>&gt;27.9: High AI confidence</li>
                        <li>&lt;2.1: Low AI confidence</li>
                      </ul>
                    </div>
                  </InfoBox>

                  <InfoBox title="About AI Detectors">
                    <p style={{ marginTop: 0 }}>
                      These tools analyze text for patterns commonly found in AI-generated content.
                    </p>
                    <p style={{ marginBottom: 0 }}>
                      Scores indicate the detector's confidence that a text was written by AI, not a definitive judgment.
                    </p>
                  </InfoBox>
                </div>
              </div>
            )}

            {activeTab === 'tone' && (
              <div style={resultContentGridStyle}>
                <SectionCard
                  title="Tone & Sentiment Shifts"
                  description="Shows formality change and emotion-level differences."
                >
                  <MetricRow
                    label="Formality shift"
                    tag="Absolute delta"
                    value={derived.formalityDelta}
                    description="Absolute change in overall formality between the two texts."
                    displayRealValue={true}
                  />

                  <MetricRow
                    label="Original formality"
                    tag="AI text"
                    value={results.tone?.ai?.formal}
                    description="Estimated formal writing score of the original AI text."
                  />

                  <MetricRow
                    label="Humanized formality"
                    tag="Humanized text"
                    value={results.tone?.humanized?.formal}
                    description="Estimated formal writing score of the humanized text."
                  />

                  <MetricRow
                    label="Top emotion change"
                    tag="Delta"
                    value={derived.topEmotionDelta}
                    description="Change in the original top emotion's score after rewriting."
                  />

                  {derived.emotionLabels.map((label) => (
                    <EmotionComparisonRow
                      key={label}
                      label={label}
                      aiScore={derived.aiEmotionMap[label]}
                      humanizedScore={derived.humanizedEmotionMap[label]}
                    />
                  ))}
                </SectionCard>

                <div style={infoBoxStackStyle}>
                  <InfoBox title="Top emotions">
                    <p>
                      <strong>AI text:</strong>{' '}
                      {derived.topAiEmotion
                        ? `${derived.topAiEmotion.label} (${formatPercentFrom01(derived.topAiEmotion.score)})`
                        : 'N/A'}
                    </p>
                    <p style={{ marginBottom: 0 }}>
                      <strong>Humanized text:</strong>{' '}
                      {derived.topHumanizedEmotion
                        ? `${derived.topHumanizedEmotion.label} (${formatPercentFrom01(derived.topHumanizedEmotion.score)})`
                        : 'N/A'}
                    </p>
                  </InfoBox>

                  <InfoBox title="Why this matters">
                    <p style={{ marginTop: 0 }}>
                      Formality captures style change.
                    </p>
                    <p style={{ marginBottom: 0 }}>
                      Emotion scores show whether the emotional framing became stronger, weaker, or changed direction.
                    </p>
                  </InfoBox>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}

export default ResultCard