"use client";

import React, { useEffect, useState } from 'react';
import Link from 'next/link';

import { fetchJson } from '@/lib/api/client';
import { MemoryItem } from '@/types';

export default function MemoryPage() {
  const [memories, setMemories] = useState<MemoryItem[]>([]);
  const [filterType, setFilterType] = useState<'ALL' | 'World' | 'Experience' | 'Observation'>('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchJson<MemoryItem[]>('/memory')
      .then(setMemories)
      .catch(() => {})
      .finally(() => setIsLoading(false));
  }, []);

  const filteredMemories = memories.filter((m) => {
    const matchesType = filterType === 'ALL' || m.type === filterType;
    const matchesSearch =
      !searchQuery ||
      m.statement.toLowerCase().includes(searchQuery.toLowerCase()) ||
      m.deal_id.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesType && matchesSearch;
  });

  const worldCount = memories.filter((m) => m.type === 'World').length;
  const expCount = memories.filter((m) => m.type === 'Experience').length;
  const obsCount = memories.filter((m) => m.type === 'Observation').length;

  const typeColor = (type: string) => {
    if (type === 'World') return { border: '#bfdbfe', label: '#1d4ed8', bg: '#eff6ff' };
    if (type === 'Experience') return { border: '#a7f3d0', label: '#047857', bg: '#ecfdf5' };
    return { border: '#fde68a', label: '#b45309', bg: '#fffbeb' };
  };

  return (
    <div>
      <section className="section">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <h1 className="page-title">Hindsight Memory Explorer</h1>
            <p className="page-subtitle">
              Organizational intelligence retained across customer accounts, interactions, and closed outcomes.
            </p>
          </div>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <span className="pill">World: {worldCount}</span>
            <span className="pill">Experience: {expCount}</span>
            <span className="pill">Observation: {obsCount}</span>
          </div>
        </div>

        {/* Filters */}
        <div style={{ display: 'flex', gap: '1rem', marginTop: '1.5rem', flexWrap: 'wrap' }}>
          <input
            type="text"
            placeholder="Search memory statements or deal IDs..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              flex: 1,
              minWidth: '240px',
              padding: '0.65rem 1rem',
              background: '#ffffff',
              border: '1px solid var(--border)',
              color: 'var(--text)',
            }}
          />
          <div style={{ display: 'flex', gap: '0.4rem' }}>
            {(['ALL', 'World', 'Experience', 'Observation'] as const).map((t) => (
              <button
                key={t}
                onClick={() => setFilterType(t)}
                style={{
                  padding: '0.55rem 1.1rem',
                  border: `1px solid ${filterType === t ? 'var(--primary-border)' : 'var(--border)'}`,
                  background: filterType === t ? 'var(--primary-soft)' : '#ffffff',
                  color: filterType === t ? 'var(--primary)' : 'var(--text-secondary)',
                  fontWeight: filterType === t ? 600 : 400,
                  cursor: 'pointer',
                  fontSize: '0.82rem',
                  letterSpacing: '0.04em',
                  borderRadius: 'var(--radius)',
                  transition: 'all 0.15s ease',
                }}
              >
                {t}
              </button>
            ))}
          </div>
        </div>
      </section>

      {isLoading ? (
        <p className="page-subtitle" style={{ padding: '1rem 0' }}>Loading memories from Hindsight engine...</p>
      ) : filteredMemories.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
          No memories match the selected filters.
        </div>
      ) : (
        <div className="card-grid" style={{ marginTop: '1.5rem' }}>
          {filteredMemories.map((m) => {
            const colors = typeColor(m.type);
            return (
              <div
                key={m.id}
                className="card"
                style={{
                  background: '#ffffff',
                  borderLeft: `4px solid ${colors.border}`,
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
                  <span
                    style={{
                      fontWeight: 600,
                      fontSize: '0.72rem',
                      padding: '0.2rem 0.55rem',
                      borderRadius: '999px',
                      background: colors.bg,
                      color: colors.label,
                      border: `1px solid ${colors.border}`,
                      textTransform: 'uppercase',
                      letterSpacing: '0.06em',
                    }}
                  >
                    {m.type} Memory
                  </span>
                  <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                    Confidence: {m.confidence}%
                  </span>
                </div>
                <p style={{ fontSize: '0.9rem', lineHeight: 1.55, margin: '0.65rem 0', color: 'var(--text-secondary)' }}>
                  {m.statement}
                </p>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '0.8rem', fontSize: '0.78rem' }}>
                  <Link href={`/deals/${m.deal_id}`} style={{ color: 'var(--primary)', textDecoration: 'underline' }}>
                    Deal: {m.deal_id}
                  </Link>
                  {m.source_interaction_id && (
                    <span style={{ color: 'var(--text-muted)' }}>Source: {m.source_interaction_id}</span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
