"use client";

import React, { useEffect, useState } from 'react';
import Link from 'next/link';

import { fetchJson, postJson } from '@/lib/api/client';
import { AgentChatResponse, Deal } from '@/types';

export default function AssistantPage() {
  const [deals, setDeals] = useState<Deal[]>([]);
  const [selectedDealId, setSelectedDealId] = useState<string>('DEAL-1007');
  const [messages, setMessages] = useState<Array<{ sender: 'user' | 'agent'; text: string; data?: AgentChatResponse }>>([
    {
      sender: 'agent',
      text: 'Welcome to DealDNA Revenue Intelligence. Select a deal to inspect persistent memories, request strategic next actions, or discover historical win/loss patterns.',
    },
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isSending, setIsSending] = useState(false);

  useEffect(() => {
    fetchJson<Deal[]>('/deals')
      .then((data) => {
        setDeals(data);
        if (data.length > 0 && !data.some((d) => d.id === selectedDealId)) {
          setSelectedDealId(data[0].id);
        }
      })
      .catch(() => {});
  }, []);

  const handleSendMessage = async (textToSend?: string) => {
    const query = textToSend || inputMessage;
    if (!query.trim() || isSending || !selectedDealId) return;

    setMessages((prev) => [...prev, { sender: 'user', text: query }]);
    setInputMessage('');
    setIsSending(true);

    try {
      const response = await postJson<AgentChatResponse>('/agent/chat', {
        deal_id: selectedDealId,
        message: query,
      });

      setMessages((prev) => [...prev, { sender: 'agent', text: response.answer, data: response }]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        { sender: 'agent', text: `Agent Error: ${err.message || 'Request failed'}` },
      ]);
    } finally {
      setIsSending(false);
    }
  };

  const selectedDeal = deals.find((d) => d.id === selectedDealId);

  return (
    <div style={{ maxWidth: '1040px', margin: '0 auto' }}>
      <section className="section" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1 className="page-title">DealDNA Intelligence Agent</h1>
          <p className="page-subtitle">
            Ground-truth conversational reasoning backed by Hindsight memory and structured sales state.
          </p>
        </div>

        {/* Deal Selector */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
          <label style={{ fontSize: '0.78rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>Active Deal:</label>
          <select
            value={selectedDealId}
            onChange={(e) => setSelectedDealId(e.target.value)}
            style={{
              padding: '0.55rem 0.85rem',
              background: '#ffffff',
              color: 'var(--text)',
              border: '1px solid var(--border)',
              fontSize: '0.88rem',
              borderRadius: 'var(--radius)',
            }}
          >
            {deals.map((d) => (
              <option key={d.id} value={d.id}>
                {d.company?.name || d.name} ({d.id})
              </option>
            ))}
          </select>
          {selectedDealId && (
            <Link href={`/deals/${selectedDealId}`} className="button" style={{ fontSize: '0.78rem', padding: '0.5rem 0.9rem' }}>
              Workspace ↗
            </Link>
          )}
        </div>
      </section>

      {/* Suggested Queries */}
      <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginBottom: '1rem' }}>
        {[
          `Who are the key decision makers and CFO requirements?`,
          `What are the pricing details and objections?`,
          `What should I do next to progress this deal?`,
          `Why did we lose the Cyberdyne deal?`,
          `Find similar historical deals and outcomes`,
          `Give me a concise executive summary`,
        ].map((q) => (
          <button
            key={q}
            onClick={() => handleSendMessage(q)}
            style={{
              background: '#f8fafc',
              border: '1px solid var(--border)',
              color: 'var(--text-secondary)',
              padding: '0.35rem 0.85rem',
              fontSize: '0.8rem',
              cursor: 'pointer',
              borderRadius: 'var(--radius)',
              transition: 'all 0.15s ease',
            }}
            onMouseEnter={(e) => {
              (e.currentTarget as HTMLButtonElement).style.background = '#eff6ff';
              (e.currentTarget as HTMLButtonElement).style.color = 'var(--primary)';
              (e.currentTarget as HTMLButtonElement).style.borderColor = 'var(--primary-border)';
            }}
            onMouseLeave={(e) => {
              (e.currentTarget as HTMLButtonElement).style.background = '#f8fafc';
              (e.currentTarget as HTMLButtonElement).style.color = 'var(--text-secondary)';
              (e.currentTarget as HTMLButtonElement).style.borderColor = 'var(--border)';
            }}
          >
            {q}
          </button>
        ))}
      </div>

      {/* Chat Messages Container */}
      <div
        className="card"
        style={{
          minHeight: '440px',
          maxHeight: '600px',
          overflowY: 'auto',
          display: 'flex',
          flexDirection: 'column',
          gap: '1rem',
          background: '#f8fafc',
          border: '1px solid var(--border)',
          marginBottom: '1.25rem',
        }}
      >
        {messages.map((msg, i) => (
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
                fontSize: '0.72rem',
                color: 'var(--text-muted)',
                marginBottom: '0.2rem',
                textTransform: 'uppercase',
                letterSpacing: '0.08em',
                textAlign: msg.sender === 'user' ? 'right' : 'left',
              }}
            >
              {msg.sender === 'user' ? 'Sales Representative' : 'DealDNA Agent'}
            </div>
            <div
              style={{
                padding: '0.9rem 1.15rem',
                background: msg.sender === 'user' ? '#eff6ff' : '#ffffff',
                border: msg.sender === 'user'
                  ? '1px solid var(--primary-border)'
                  : '1px solid var(--border)',
                borderRadius: 'var(--radius)',
                lineHeight: 1.55,
                fontSize: '0.9rem',
                whiteSpace: 'pre-wrap',
                color: 'var(--text)',
                boxShadow: 'var(--shadow-sm)',
              }}
            >
              {msg.text}

              {msg.data && (
                <div style={{ marginTop: '0.75rem', paddingTop: '0.75rem', borderTop: '1px solid var(--border)' }}>
                  <div style={{ display: 'flex', gap: '0.45rem', alignItems: 'center', flexWrap: 'wrap' }}>
                    <span
                      style={{
                        fontSize: '0.72rem',
                        padding: '0.2rem 0.5rem',
                        background: 'var(--info-soft)',
                        color: 'var(--info)',
                        border: '1px solid var(--info-border)',
                        borderRadius: '999px',
                        fontWeight: 600,
                      }}
                    >
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
                      <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', fontWeight: 600 }}>
                        Supporting Evidence:
                      </span>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem', marginTop: '0.25rem' }}>
                        {msg.data.evidence.map((ev, evIdx) => (
                          <div
                            key={evIdx}
                            style={{
                              fontSize: '0.76rem',
                              background: 'var(--primary-soft)',
                              padding: '0.35rem 0.55rem',
                              borderLeft: '2px solid var(--primary)',
                              color: 'var(--text-secondary)',
                              borderRadius: '0 var(--radius-sm) var(--radius-sm) 0',
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
        {isSending && (
          <div style={{ color: 'var(--text-muted)', fontStyle: 'italic', fontSize: '0.85rem' }}>
            DealDNA is accessing Hindsight memory...
          </div>
        )}
      </div>

      {/* Input */}
      <div style={{ display: 'flex', gap: '0.5rem' }}>
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
          placeholder={`Ask about ${selectedDeal?.company?.name || 'the selected deal'}, next actions, or patterns...`}
          style={{
            flex: 1,
            padding: '0.75rem 1rem',
            border: '1px solid var(--border)',
            background: '#ffffff',
            color: 'var(--text)',
            fontSize: '0.9rem',
            borderRadius: 'var(--radius)',
          }}
        />
        <button
          onClick={() => handleSendMessage()}
          disabled={isSending}
          className="button primary"
          style={{ padding: '0.75rem 1.6rem', cursor: 'pointer' }}
        >
          {isSending ? 'Thinking...' : 'Ask Agent'}
        </button>
      </div>
    </div>
  );
}
