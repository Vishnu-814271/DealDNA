export type Company = {
  id: string;
  name: string;
  industry: string;
  size: string;
};

export type Contact = {
  id: string;
  company_id: string;
  name: string;
  role: string;
  email: string;
  phone?: string;
};

export type DealOutcome = {
  id: string;
  deal_id: string;
  status: 'WON' | 'LOST' | 'STALLED';
  reason: string;
  strategy_used?: string;
  closed_at?: string;
};

export type Deal = {
  id: string;
  company_id: string;
  primary_contact_id?: string;
  owner_id?: string;
  name: string;
  stage: 'NEW' | 'QUALIFICATION' | 'DISCOVERY' | 'EVALUATION' | 'NEGOTIATION' | 'STALLED' | 'WON' | 'LOST';
  value: number | string;
  currency: string;
  status: string;
  probability: number;
  expected_close_date?: string;
  summary?: string;
  created_at?: string;
  company?: Company;
  primary_contact?: Contact;
  outcomes?: DealOutcome[];
};

export type Interaction = {
  id: string;
  deal_id: string;
  type: 'MEETING' | 'CALL' | 'EMAIL' | 'NOTE';
  occurred_at: string;
  participants: string[];
  content: string;
  summary?: string;
  hindsight_document_id?: string;
  memory_sync_status: string;
};

export type EvidenceItem = {
  interaction_id?: string;
  reason: string;
};

export type AgentChatResponse = {
  answer: string;
  recommendation?: string;
  confidence_label?: 'supported' | 'limited_evidence' | 'insufficient_evidence';
  rationale?: string;
  historical_pattern?: string;
  next_action?: string;
  caveats?: string;
  evidence: EvidenceItem[];
  memory_count: number;
  intent: 'FACTUAL' | 'SUMMARY' | 'STRATEGY' | 'PATTERN';
  latency_ms: number;
};

export type MemoryItem = {
  id: string;
  deal_id: string;
  type: 'World' | 'Experience' | 'Observation';
  statement: string;
  source_interaction_id?: string;
  confidence: number;
  created_at?: string;
};

export type HistoricalDealMatch = {
  deal_id: string;
  deal_name: string;
  company_name: string;
  outcome: string;
  similarity_reason: string;
  strategy_used?: string;
  value: number;
};

export type DealPattern = {
  deal_id: string;
  observed_pattern: string;
  confidence_label: string;
  comparable_deals: HistoricalDealMatch[];
  recommended_tactics: string[];
};
