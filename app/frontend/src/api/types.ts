export type AnalyzePayload = {
  ai_text: string
  humanized_text: string
  num_questions?: number
}

export type ApiError = {
  error: string
}

export type SimilarityResult = {
  similarity: {
    tfidf: number | null
    sbert: number | null
    nemotron: number | null
  }
  difference: {
    tfidf: number | null
    sbert: number | null
    nemotron: number | null
  }
  nemotron_error?: string
}

export type DetectabilityResult = {
  ai: Record<string, unknown>
  humanized: Record<string, unknown>
}

export type EmotionsResult = {
  ai: Array<Record<string, unknown>>
  humanized: Array<Record<string, unknown>>
}

export type ToneResult = {
  ai: Record<string, unknown>
  humanized: Record<string, unknown>
  delta_formality: number
}

export type FactualResult = {
  forward: Record<string, unknown>
  reversed: Record<string, unknown>
}

export type FullAnalysisResult = {
  similarity: SimilarityResult
  detectability: DetectabilityResult
  emotions: EmotionsResult
  tone: ToneResult
  factual: FactualResult
}
