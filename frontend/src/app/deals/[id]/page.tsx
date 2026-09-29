"use client";

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';

import { fetchJson, postJson } from '@/lib/api/client';
import {
  AgentChatResponse,
  Deal,
  DealPattern,
  Interaction,
  MemoryItem,
} from '@/types';

export default function DealDetailPage() {
  const params = useParams();
  const dealId = params?.id as string;

  const [deal, setDeal] = useState<Deal | null>(null);
  const [timeline, setTimeline] = useState<Interaction[]>([]);
  const [memories, setMemories] = useState<MemoryItem[]>([]);
  const [patterns, setPatterns] = useState<DealPattern | null>(null);
  const [latestRecommendation, setLatestRecommendation] = useState<AgentChatResponse | null>(null);

  const [activeTab, setActiveTab] = useState<'timeline' | 'chat' | 'recommendation' | 'memory' | 'patterns'>('timeline');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Chat state
  const [chatMessages, setChatMessages] = useState<Array<{ sender: 'user' | 'agent'; text: string; data?: AgentChatResponse }>>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isSendingChat, setIsSendingChat] = useState(false);

  // Add interaction modal state
  const [showAddInteraction, setShowAddInteraction] = useState(false);
  const [newType, setNewType] = useState<'MEETING' | 'CALL' | 'EMAIL' | 'NOTE'>('MEETING');
  const [newParticipants, setNewParticipants] = useState('Raj Mehta, Anita Shah');
  const [newContent, setNewContent] = useState('');
  const [isSubmittingInteraction, setIsSubmittingInteraction] = useState(false);

  // Record outcome modal state
  const [showOutcomeModal, setShowOutcomeModal] = useState(false);
  const [outcomeStatus, setOutcomeStatus] = useState<'WON' | 'LOST' | 'STALLED'>('WON');
  const [outcomeReason, setOutcomeReason] = useState('');
  const [outcomeStrategy, setOutcomeStrategy] = useState('');
  const [isSubmittingOutcome, setIsSubmittingOutcome] = useState(false);

  const loadDealData = async () => {
    if (!dealId) return;
    try {
      setIsLoading(true);
      const [dealData, timelineData, memoriesData, patternData] = await Promise.all([
        fetchJson<Deal>(`/deals/${dealId}`),
        fetchJson<Interaction[]>(`/deals/${dealId}/timeline`),
        fetchJson<MemoryItem[]>(`/deals/${dealId}/memories`),
        fetchJson<DealPattern>(`/deals/${dealId}/patterns`),
      ]);
      setDeal(dealData);
      setTimeline(timelineData);
      setMemories(memoriesData);
      setPatterns(patternData);

      // Trigger initial strategic analysis
      try {
        const initialRec = await postJson<AgentChatResponse>(`/deals/${dealId}/analyze`, {});
        setLatestRecommendation(initialRec);
      } catch {
        // ignore initial rec failure
      }
    } catch (err: any) {
      setError(err?.message || 'Failed to load deal details');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadDealData();
  }, [dealId]);

  const handleSendMessage = async (customText?: string) => {
    const textToSend = customText || inputMessage;
    if (!textToSend.trim() || isSendingChat) return;

    setChatMessages((prev) => [...prev, { sender: 'user', text: textToSend }]);
    setInputMessage('');
    setIsSendingChat(true);

    try {
      const response = await postJson<AgentChatResponse>('/agent/chat', {
        deal_id: dealId,
        message: textToSend,
      });

      setChatMessages((prev) => [...prev, { sender: 'agent', text: response.answer, data: response }]);
      if (response.recommendation) {
        setLatestRecommendation(response);
      }
    } catch (err: any) {
      setChatMessages((prev) => [
        ...prev,
        { sender: 'agent', text: `Error from DealDNA agent: ${err.message || 'Request failed'}` },
      ]);
    } finally {
      setIsSendingChat(false);
    }
  };

  const handleAddInteraction = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newContent.trim()) return;

    setIsSubmittingInteraction(true);
    try {
      const participantsList = newParticipants
        .split(',')
        .map((p) => p.trim())
        .filter(Boolean);

      await postJson(`/deals/${dealId}/interactions`, {
        type: newType,
        participants: participantsList,
        content: newContent,
      });

      setNewContent('');
      setShowAddInteraction(false);
      await loadDealData();
      setActiveTab('timeline');
    } catch (err: any) {
      alert(`Failed to save interaction: ${err.message}`);
    } finally {
      setIsSubmittingInteraction(false);
    }
  };

  const handleRecordOutcome = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!outcomeReason.trim()) return;

    setIsSubmittingOutcome(true);
    try {
      await postJson(`/deals/${dealId}/outcome`, {
        status: outcomeStatus,
        reason: outcomeReason,
        strategy_used: outcomeStrategy,
      });

      setShowOutcomeModal(false);
      await loadDealData();
    } catch (err: any) {
      alert(`Failed to record outcome: ${err.message}`);
    } finally {
      setIsSubmittingOutcome(false);
    }
  };

  if (isLoading) {
    return (
      <div style={{ padding: '2rem' }}>
        <p className="page-subtitle">Loading deal intelligence workspace...</p>
      </div>
    );
  }

  if (error || !deal) {
    return (
      <div style={{ padding: '2rem' }}>
        <p className="status error">{error || 'Deal not found'}</p>
        <Link href="/deals" className="button" style={{ marginTop: '1rem', display: 'inline-block' }}>
          ← Back to Deals
        </Link>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: '1240px', margin: '0 auto' }}>
      {/* Top Breadcrumb & Status */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
        <Link href="/deals" style={{ color: 'var(--text-muted)', fontSize: '0.85rem', fontWeight: 500 }}>
          ← Back to Deal Pipeline
        </Link>
        <div style={{ display: 'flex', gap: '0.65rem' }}>
          <span className="pill" style={{ color: 'var(--text-secondary)' }}>
            Memory Bank: dealdna-hackathon-bank
          </span>
          <span className="status success">
            Hindsight Engine: Connected
          </span>
        </div>
      </div>

      {/* Deal Header Banner (Clean Lite Theme) */}
      <div className="card" style={{ marginBottom: '1.5rem', background: '#ffffff', border: '1px solid var(--border)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem', marginBottom: '0.4rem' }}>
              <h1 style={{ fontSize: '1.65rem', margin: 0, fontWeight: 700, color: '#0f172a', letterSpacing: '-0.02em' }}>
                {deal.name}
              </h1>
              <span
                className="status"
                style={{
                  background:
                    deal.stage === 'WON'
                      ? 'var(--success-soft)'
                      : deal.stage === 'LOST'
                      ? 'var(--danger-soft)'
                      : 'var(--info-soft)',
                  color:
                    deal.stage === 'WON'
                      ? 'var(--success)'
                      : deal.stage === 'LOST'
                      ? 'var(--danger)'
                      : 'var(--info)',
                  border: `1px solid ${
                    deal.stage === 'WON'
                      ? 'var(--success-border)'
                      : deal.stage === 'LOST'
                      ? 'var(--danger-border)'
                      : 'var(--info-border)'
                  }`,
                }}
              >
                {deal.stage}
              </span>
            </div>
            <p style={{ margin: '0 0 0.5rem 0', color: 'var(--text-muted)', fontSize: '0.9rem' }}>
              {deal.company?.name} • {deal.company?.industry} • {deal.company?.size}
            </p>
            <p style={{ margin: 0, fontSize: '0.88rem', color: 'var(--text-secondary)' }}>
              Primary Stakeholder: <span style={{ color: '#0f172a', fontWeight: 600 }}>{deal.primary_contact ? `${deal.primary_contact.name} (${deal.primary_contact.role})` : 'Anita Shah (CFO)'}</span>
            </p>
          </div>

          <div style={{ display: 'flex', gap: '1.75rem', alignItems: 'center' }}>
            <div>
              <div style={{ color: 'var(--text-muted)', fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', fontWeight: 600 }}>Value</div>
              <div style={{ fontSize: '1.45rem', fontWeight: 700, color: 'var(--success)' }}>
                ${Number(deal.value).toLocaleString('en-US')}
              </div>
            </div>
            <div>
              <div style={{ color: 'var(--text-muted)', fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', fontWeight: 600 }}>Win Probability</div>
              <div style={{ fontSize: '1.45rem', fontWeight: 700, color: 'var(--primary)' }}>{deal.probability}%</div>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.45rem' }}>
              <button
                onClick={() => setShowAddInteraction(true)}
                className="button primary"
                style={{ padding: '0.55rem 1.15rem', fontSize: '0.82rem', cursor: 'pointer' }}
              >
                + Ingest Interaction
              </button>
              <button
                onClick={() => setShowOutcomeModal(true)}
                className="button"
                style={{
                  padding: '0.5rem 1.15rem',
                  fontSize: '0.82rem',
                  cursor: 'pointer',
                }}
              >
                Record Outcome
              </button>
            </div>
          </div>
        </div>

        {deal.summary && (
          <div style={{ marginTop: '1rem', paddingTop: '0.9rem', borderTop: '1px solid var(--border)', color: 'var(--text-secondary)', fontSize: '0.88rem' }}>
            <span style={{ color: 'var(--text-muted)', fontWeight: 600 }}>Context Brief: </span>
            {deal.summary}
          </div>
        )}
      </div>

      {/* Workspace Navigation Tabs */}
      <div style={{ display: 'flex', gap: '0.35rem', borderBottom: '1px solid var(--border)', marginBottom: '1.5rem', overflowX: 'auto' }}>
        {[
          { key: 'timeline', label: `Timeline (${timeline.length})` },
          { key: 'chat', label: 'AI Agent Chat' },
          { key: 'recommendation', label: 'Next Best Action' },
          { key: 'memory', label: `Memory Explorer (${memories.length})` },
          { key: 'patterns', label: 'Historical Patterns' },
        ].map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key as any)}
            style={{
              padding: '0.75rem 1.25rem',
              background: activeTab === tab.key ? '#ffffff' : 'transparent',
              border: 'none',
              borderBottom: activeTab === tab.key ? '2px solid var(--primary)' : '2px solid transparent',
              color: activeTab === tab.key ? 'var(--primary)' : 'var(--text-muted)',
              fontWeight: activeTab === tab.key ? 700 : 500,
              cursor: 'pointer',
              fontSize: '0.9rem',
              whiteSpace: 'nowrap',
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* TAB 1: TIMELINE */}
      {activeTab === 'timeline' && (
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h2 style={{ fontSize: '1.15rem', margin: 0, fontWeight: 700, color: '#0f172a' }}>
              Customer Interaction Chronology
            </h2>
            <button
              onClick={() => setShowAddInteraction(true)}
              className="button primary"
              style={{ fontSize: '0.8rem', padding: '0.45rem 0.95rem' }}
            >
              + Ingest Interaction
            </button>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
            {timeline.length === 0 ? (
              <p style={{ color: 'var(--text-muted)' }}>No interactions recorded yet. Click '+ Ingest Interaction' to add one.</p>
            ) : (
              timeline.map((item) => (
                <div
                  key={item.id}
                  className="card"
                  style={{
                    background: '#ffffff',
                    borderLeft: `4px solid ${item.type === 'MEETING' ? 'var(--primary)' : item.type === 'CALL' ? 'var(--success)' : '#8b5cf6'}`,
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
                      <span className="inline-pill" style={{ fontWeight: 600 }}>{item.type}</span>
                      <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                        {new Date(item.occurred_at).toLocaleDateString()} at {new Date(item.occurred_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>
                    <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                      <span className="status success" style={{ fontSize: '0.72rem' }}>
                        HINDSIGHT: {item.memory_sync_status}
                      </span>
                      <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>ID: {item.id}</span>
                    </div>
                  </div>

                  <p style={{ fontSize: '0.92rem', margin: '0.5rem 0', lineHeight: 1.5, color: '#0f172a' }}>
                    {item.content}
                  </p>

                  {item.participants && item.participants.length > 0 && (
                    <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                      <strong>Participants: </strong> {item.participants.join(', ')}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* TAB 2: AI AGENT CHAT */}
      {activeTab === 'chat' && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '1rem' }}>
          {/* Quick Prompt Suggestions */}
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginBottom: '0.35rem' }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', alignSelf: 'center', fontWeight: 600 }}>
              Suggested:
            </span>
            {[
              'What do you know about Acme?',
              'What should I do next?',
              'Find similar deals and outcomes',
              'Summarize this deal',
            ].map((q) => (
              <button
                key={q}
                onClick={() => handleSendMessage(q)}
                style={{
                  background: '#ffffff',
                  border: '1px solid var(--border)',
                  color: 'var(--primary)',
                  padding: '0.35rem 0.85rem',
                  fontSize: '0.8rem',
                  borderRadius: '999px',
                  fontWeight: 500,
                  cursor: 'pointer',
                  boxShadow: 'var(--shadow-sm)',
                }}
              >
                {q}
              </button>
            ))}
          </div>

          {/* Chat Window (Clean Lite Theme) */}
          <div
            className="card"
            style={{
              minHeight: '420px',
              maxHeight: '560px',
              overflowY: 'auto',
              display: 'flex',
              flexDirection: 'column',
              gap: '1rem',
              background: '#f8fafc',
              border: '1px solid var(--border)',
            }}
          >
            {chatMessages.length === 0 && (
              <div style={{ textAlign: 'center', margin: 'auto', color: 'var(--text-muted)' }}>
                <div style={{ fontSize: '1.15rem', fontWeight: 700, color: '#0f172a', marginBottom: '0.4rem' }}>
                  DealDNA Revenue Intelligence Agent
                </div>
                <p style={{ maxWidth: '480px', margin: '0.4rem auto', fontSize: '0.88rem' }}>
                  Ask factual questions, request strategic next steps, or surface historical patterns. Every answer is grounded in Hindsight persistent memory.
                </p>
              </div>
            )}

            {chatMessages.map((msg, i) => (
              <div
                key={i}
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignSelf: msg.sender === 'user' ? 'flex-end' : 'flex-start',
                  maxWidth: '85%',
                }}
              >
                <div
                  style={{
                    fontSize: '0.74rem',
                    color: 'var(--text-muted)',
                    marginBottom: '0.2rem',
                    fontWeight: 600,
                    textAlign: msg.sender === 'user' ? 'right' : 'left',
                  }}
                >
                  {msg.sender === 'user' ? 'Sales Representative' : 'DealDNA Memory Agent'}
                </div>
                <div
                  style={{
                    padding: '0.95rem 1.25rem',
                    background: msg.sender === 'user' ? '#eff6ff' : '#ffffff',
                    border: msg.sender === 'user' ? '1px solid #bfdbfe' : '1px solid var(--border)',
                    borderRadius: 'var(--radius)',
                    lineHeight: 1.55,
                    fontSize: '0.9rem',
                    whiteSpace: 'pre-wrap',
                    color: '#0f172a',
                    boxShadow: 'var(--shadow-sm)',
                  }}
                >
                  {msg.text}

                  {/* Intent & Evidence Citations */}
                  {msg.data && (
                    <div style={{ marginTop: '0.75rem', paddingTop: '0.75rem', borderTop: '1px solid var(--border)' }}>
                      <div style={{ display: 'flex', gap: '0.45rem', alignItems: 'center', flexWrap: 'wrap' }}>
                        <span className="pill" style={{ fontSize: '0.72rem', background: '#f8fafc', color: 'var(--primary)' }}>
                          INTENT: {msg.data.intent}
                        </span>
                        {msg.data.confidence_label && (
                          <span className="status success" style={{ fontSize: '0.72rem' }}>
                            CONFIDENCE: {msg.data.confidence_label}
                          </span>
                        )}
                        <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                          Memories referenced: {msg.data.memory_count}
                        </span>
                      </div>

                      {msg.data.evidence && msg.data.evidence.length > 0 && (
                        <div style={{ marginTop: '0.5rem' }}>
                          <span style={{ fontSize: '0.74rem', color: 'var(--text-muted)', fontWeight: 600 }}>
                            Supporting Evidence:
                          </span>
                          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem', marginTop: '0.25rem' }}>
                            {msg.data.evidence.map((ev, evIdx) => (
                              <div
                                key={evIdx}
                                style={{
                                  fontSize: '0.78rem',
                                  background: '#f8fafc',
                                  padding: '0.35rem 0.55rem',
                                  borderLeft: '3px solid var(--primary)',
                                  color: 'var(--text-secondary)',
                                  borderRadius: '0 4px 4px 0',
                                }}
                              >
                                <strong>{ev.interaction_id || 'Memory'}:</strong> {ev.reason}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            ))}
            {isSendingChat && (
              <div style={{ color: 'var(--text-muted)', fontStyle: 'italic', fontSize: '0.85rem' }}>
                DealDNA is recalling memories and synthesizing strategy...
              </div>
            )}
          </div>

          {/* Chat Input */}
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
              placeholder="Ask anything about Acme, requested next steps, or similar won deals..."
              style={{
                flex: 1,
                padding: '0.75rem 1rem',
                border: '1px solid var(--border-subtle)',
                background: '#ffffff',
                color: '#0f172a',
                fontSize: '0.9rem',
              }}
            />
            <button
              onClick={() => handleSendMessage()}
              disabled={isSendingChat}
              className="button primary"
              style={{ padding: '0.75rem 1.6rem', cursor: 'pointer' }}
            >
              {isSendingChat ? 'Thinking...' : 'Send'}
            </button>
          </div>
        </div>
      )}

      {/* TAB 3: NEXT BEST ACTION (RECOMMENDATION ENGINE) */}
      {activeTab === 'recommendation' && (
        <div>
          {latestRecommendation ? (
            <div className="card" style={{ background: '#ffffff', border: '1px solid var(--border)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <h2 style={{ fontSize: '1.2rem', margin: 0, fontWeight: 700, color: '#0f172a' }}>
                  Recommended Next Best Action
                </h2>
                <span className="status success">
                  Evidence: {latestRecommendation.confidence_label}
                </span>
              </div>

              <div
                style={{
                  background: 'var(--primary-soft)',
                  border: '1px solid var(--primary-border)',
                  borderLeft: '4px solid var(--primary)',
                  padding: '1.1rem 1.25rem',
                  fontSize: '1.05rem',
                  fontWeight: 600,
                  color: '#1e3a8a',
                  lineHeight: 1.5,
                  borderRadius: 'var(--radius)',
                  marginBottom: '1rem',
                }}
              >
                {latestRecommendation.next_action || latestRecommendation.recommendation}
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
                <div className="card" style={{ background: '#f8fafc', boxShadow: 'none' }}>
                  <div className="card-label">Strategic Rationale</div>
                  <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', margin: '0.4rem 0', lineHeight: 1.5 }}>
                    {latestRecommendation.rationale}
                  </p>
                </div>
                <div className="card" style={{ background: '#f8fafc', boxShadow: 'none' }}>
                  <div className="card-label">Historical Pattern Observed</div>
                  <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', margin: '0.4rem 0', lineHeight: 1.5 }}>
                    {latestRecommendation.historical_pattern}
                  </p>
                </div>
              </div>

              {latestRecommendation.caveats && (
                <div style={{ marginBottom: '1.25rem', color: 'var(--warning)', fontSize: '0.85rem' }}>
                  <strong>Note: </strong>
                  {latestRecommendation.caveats}
                </div>
              )}

              {/* Explicit Evidence Links */}
              <div>
                <div className="card-label" style={{ marginBottom: '0.5rem' }}>Supporting Evidence Links</div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                  {latestRecommendation.evidence.map((ev, i) => (
                    <div
                      key={i}
                      style={{
                        padding: '0.65rem 0.95rem',
                        background: '#f8fafc',
                        border: '1px solid var(--border)',
                        borderRadius: 'var(--radius-sm)',
                        fontSize: '0.85rem',
                        display: 'flex',
                        justifyContent: 'space-between',
                      }}
                    >
                      <span style={{ color: 'var(--text-secondary)' }}>{ev.reason}</span>
                      {ev.interaction_id && (
                        <span style={{ color: 'var(--primary)', fontWeight: 600 }}>{ev.interaction_id}</span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <p style={{ color: 'var(--text-muted)' }}>No recommendation available yet. Ingest an interaction or run AI Analysis.</p>
          )}
        </div>
      )}

      {/* TAB 4: MEMORY EXPLORER */}
      {activeTab === 'memory' && (
        <div>
          <div style={{ marginBottom: '1rem' }}>
            <h2 style={{ fontSize: '1.2rem', margin: 0, fontWeight: 700, color: '#0f172a' }}>
              Hindsight Memory Explorer
            </h2>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', margin: '0.2rem 0' }}>
              Persistent long-term memories extracted by Hindsight: World Memory (Facts), Experience Memory (Events), and Observation Memory (Inferred Patterns).
            </p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '1rem' }}>
            {memories.map((m) => (
              <div
                key={m.id}
                className="card"
                style={{
                  background: '#ffffff',
                  borderLeft: `4px solid ${
                    m.type === 'World' ? 'var(--primary)' : m.type === 'Experience' ? 'var(--success)' : '#8b5cf6'
                  }`,
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
                  <span
                    className="status"
                    style={{
                      fontWeight: 600,
                      fontSize: '0.72rem',
                      background: m.type === 'World' ? 'var(--info-soft)' : m.type === 'Experience' ? 'var(--success-soft)' : '#f5f3ff',
                      color: m.type === 'World' ? 'var(--info)' : m.type === 'Experience' ? 'var(--success)' : '#7c3aed',
                      border: `1px solid ${m.type === 'World' ? 'var(--info-border)' : m.type === 'Experience' ? 'var(--success-border)' : '#ddd6fe'}`,
                    }}
                  >
                    {m.type} Memory
                  </span>
                  <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                    Confidence: {m.confidence}%
                  </span>
                </div>
                <p style={{ fontSize: '0.9rem', lineHeight: 1.45, margin: '0.5rem 0', color: '#0f172a' }}>
                  {m.statement}
                </p>
                {m.source_interaction_id && (
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    Source: <span style={{ color: 'var(--primary)', fontWeight: 500 }}>{m.source_interaction_id}</span>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TAB 5: HISTORICAL PATTERNS & SIMILAR DEALS */}
      {activeTab === 'patterns' && patterns && (
        <div>
          <div className="card" style={{ marginBottom: '1.5rem', background: '#ffffff' }}>
            <div className="card-label">Observed Pipeline Pattern</div>
            <p style={{ fontSize: '0.95rem', color: '#0f172a', lineHeight: 1.5, margin: '0.5rem 0' }}>
              {patterns.observed_pattern}
            </p>

            <div style={{ marginTop: '1rem' }}>
              <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '0.4rem' }}>
                Recommended Tactics:
              </div>
              <ul style={{ margin: 0, paddingLeft: '1.2rem', fontSize: '0.88rem', color: 'var(--text-secondary)' }}>
                {patterns.recommended_tactics.map((t, idx) => (
                  <li key={idx} style={{ marginBottom: '0.25rem' }}>{t}</li>
                ))}
              </ul>
            </div>
          </div>

          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#0f172a', marginBottom: '0.75rem' }}>
            Comparable Historical Deals
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '1rem' }}>
            {patterns.comparable_deals.map((comp) => (
              <div key={comp.deal_id} className="card" style={{ background: '#ffffff' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
                  <span style={{ fontWeight: 600, fontSize: '0.92rem' }}>{comp.deal_name}</span>
                  <span
                    className="status"
                    style={{
                      background: comp.outcome === 'WON' ? 'var(--success-soft)' : 'var(--danger-soft)',
                      color: comp.outcome === 'WON' ? 'var(--success)' : 'var(--danger)',
                      border: `1px solid ${comp.outcome === 'WON' ? 'var(--success-border)' : 'var(--danger-border)'}`,
                    }}
                  >
                    {comp.outcome}
                  </span>
                </div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.4rem' }}>
                  {comp.company_name} • ${Number(comp.value).toLocaleString('en-US')}
                </div>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', margin: 0 }}>
                  <strong>Strategy used:</strong> {comp.strategy_used || 'Standard'}
                </p>
                <div style={{ fontSize: '0.76rem', color: 'var(--text-muted)', marginTop: '0.4rem' }}>
                  {comp.similarity_reason}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* MODAL: ADD INTERACTION */}
      {showAddInteraction && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(15, 23, 42, 0.4)',
            backdropFilter: 'blur(4px)',
            display: 'grid',
            placeItems: 'center',
            zIndex: 100,
            padding: '1rem',
          }}
        >
          <div
            className="card"
            style={{
              width: '100%',
              maxWidth: '520px',
              background: '#ffffff',
              border: '1px solid var(--border)',
            }}
          >
            <h2 style={{ fontSize: '1.2rem', marginTop: 0, fontWeight: 700 }}>
              Ingest Customer Interaction
            </h2>
            <form onSubmit={handleAddInteraction} style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
              <div>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', display: 'block', marginBottom: '0.2rem', fontWeight: 600 }}>
                  Channel Type
                </label>
                <select
                  value={newType}
                  onChange={(e: any) => setNewType(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.6rem 0.85rem',
                    background: '#ffffff',
                    color: 'var(--text)',
                    border: '1px solid var(--border)',
                  }}
                >
                  <option value="MEETING">Meeting</option>
                  <option value="CALL">Call</option>
                  <option value="EMAIL">Email</option>
                  <option value="NOTE">Sales Note</option>
                </select>
              </div>

              <div>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', display: 'block', marginBottom: '0.2rem', fontWeight: 600 }}>
                  Participants (comma-separated)
                </label>
                <input
                  type="text"
                  value={newParticipants}
                  onChange={(e) => setNewParticipants(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.6rem 0.85rem',
                    background: '#ffffff',
                    color: 'var(--text)',
                    border: '1px solid var(--border)',
                  }}
                />
              </div>

              <div>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', display: 'block', marginBottom: '0.2rem', fontWeight: 600 }}>
                  Content / Call Transcript / Email Body
                </label>
                <textarea
                  rows={4}
                  required
                  placeholder="e.g. Anita Shah (CFO) reviewed the initial ROI proposal and requested a customized 3-year TCO comparison."
                  value={newContent}
                  onChange={(e) => setNewContent(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.6rem 0.85rem',
                    background: '#ffffff',
                    color: 'var(--text)',
                    border: '1px solid var(--border)',
                    fontFamily: 'inherit',
                  }}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem', marginTop: '0.75rem' }}>
                <button
                  type="button"
                  onClick={() => setShowAddInteraction(false)}
                  className="button"
                  style={{
                    padding: '0.55rem 1.15rem',
                    cursor: 'pointer',
                  }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmittingInteraction}
                  className="button primary"
                  style={{ padding: '0.55rem 1.35rem', cursor: 'pointer' }}
                >
                  {isSubmittingInteraction ? 'Saving...' : 'Retain to Memory'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL: RECORD OUTCOME */}
      {showOutcomeModal && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(15, 23, 42, 0.4)',
            backdropFilter: 'blur(4px)',
            display: 'grid',
            placeItems: 'center',
            zIndex: 100,
            padding: '1rem',
          }}
        >
          <div
            className="card"
            style={{
              width: '100%',
              maxWidth: '520px',
              background: '#ffffff',
              border: '1px solid var(--border)',
            }}
          >
            <h2 style={{ fontSize: '1.2rem', marginTop: 0, fontWeight: 700 }}>
              Record Deal Outcome
            </h2>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
              Capturing this outcome stores it in Hindsight Observation Memory so future similar deals learn from this result.
            </p>
            <form onSubmit={handleRecordOutcome} style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
              <div>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', display: 'block', marginBottom: '0.2rem', fontWeight: 600 }}>
                  Outcome Status
                </label>
                <select
                  value={outcomeStatus}
                  onChange={(e: any) => setOutcomeStatus(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.6rem 0.85rem',
                    background: '#ffffff',
                    color: 'var(--text)',
                    border: '1px solid var(--border)',
                  }}
                >
                  <option value="WON">WON</option>
                  <option value="LOST">LOST</option>
                  <option value="STALLED">STALLED</option>
                </select>
              </div>

              <div>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', display: 'block', marginBottom: '0.2rem', fontWeight: 600 }}>
                  Outcome Reason
                </label>
                <textarea
                  rows={2}
                  required
                  placeholder="e.g. Delivered 3-year TCO model and peer benchmark case study directly to CFO."
                  value={outcomeReason}
                  onChange={(e) => setOutcomeReason(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.6rem 0.85rem',
                    background: '#ffffff',
                    color: 'var(--text)',
                    border: '1px solid var(--border)',
                    fontFamily: 'inherit',
                  }}
                />
              </div>

              <div>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', display: 'block', marginBottom: '0.2rem', fontWeight: 600 }}>
                  Strategy Used
                </label>
                <input
                  type="text"
                  placeholder="e.g. Executive ROI walkthrough + customer case study"
                  value={outcomeStrategy}
                  onChange={(e) => setOutcomeStrategy(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.6rem 0.85rem',
                    background: '#ffffff',
                    color: 'var(--text)',
                    border: '1px solid var(--border)',
                  }}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem', marginTop: '0.75rem' }}>
                <button
                  type="button"
                  onClick={() => setShowOutcomeModal(false)}
                  className="button"
                  style={{
                    padding: '0.55rem 1.15rem',
                    cursor: 'pointer',
                  }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmittingOutcome}
                  className="button primary"
                  style={{ padding: '0.55rem 1.35rem', cursor: 'pointer' }}
                >
                  {isSubmittingOutcome ? 'Saving...' : 'Record Outcome & Learn'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
