import type {
  AnalyzePayload,
  SimilarityResult,
  DetectabilityResult,
  EmotionsResult,
  FactualResult,
  FullAnalysisResult,
  ToneResult
} from './types'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

function summarizePayload(payload: AnalyzePayload) {
  return {
    aiTextLength: payload.ai_text.length,
    humanizedTextLength: payload.humanized_text.length,
    numQuestions: payload.num_questions
  }
}

async function postJson<TResponse>(path: string, payload: AnalyzePayload): Promise<TResponse> {
  const url = `${API_BASE_URL}${path}`
  const startedAt = performance.now()

  console.log(`[analysis] -> ${path}`, {
    url,
    payload: summarizePayload(payload)
  })

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })

    const data = await response.json()
    const durationMs = Math.round(performance.now() - startedAt)

    if (!response.ok) {
      const errorMessage = data?.error || `Request failed for ${path}`
      console.error(`[analysis] x ${path}`, {
        status: response.status,
        durationMs,
        error: errorMessage,
        response: data
      })
      throw new Error(errorMessage)
    }

    console.log(`[analysis] <- ${path}`, {
      status: response.status,
      durationMs,
      result: data
    })

    return data as TResponse
  } catch (error) {
    const durationMs = Math.round(performance.now() - startedAt)
    console.error(`[analysis] ! ${path}`, {
      durationMs,
      error
    })
    throw error
  }
}

export async function analyzeSimilarity(payload: AnalyzePayload): Promise<SimilarityResult> {
  return postJson<SimilarityResult>('/similarity', payload)
}

export async function analyzeDetectability(payload: AnalyzePayload): Promise<DetectabilityResult> {
  return postJson<DetectabilityResult>('/detectability', payload)
}

export async function analyzeEmotions(payload: AnalyzePayload): Promise<EmotionsResult> {
  return postJson<EmotionsResult>('/emotions', payload)
}

export async function analyzeTone(payload: AnalyzePayload): Promise<ToneResult> {
  return postJson<ToneResult>('/tone', payload)
}

export async function analyzeFactual(payload: AnalyzePayload): Promise<FactualResult> {
  return postJson<FactualResult>('/factual', payload)
}

export async function runFullAnalysis(payload: AnalyzePayload): Promise<FullAnalysisResult> {
  console.log('[analysis] Starting full analysis', summarizePayload(payload))

  const [similarity, detectability, emotions, tone, factual] = await Promise.all([
    analyzeSimilarity(payload),
    analyzeDetectability(payload),
    analyzeEmotions(payload),
    analyzeTone(payload),
    analyzeFactual(payload)
  ])

  const mergedResult = {
    similarity,
    detectability,
    emotions,
    tone,
    factual
  }

  console.log('[analysis] Full analysis completed', mergedResult)

  return mergedResult
}
