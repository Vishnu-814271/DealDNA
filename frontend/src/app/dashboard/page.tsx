"use client";

import React, { useEffect, useState } from 'react';
import Link from 'next/link';

import { Card } from '@/components/ui/Card';
import { fetchJson } from '@/lib/api/client';
import { Deal, MemoryItem } from '@/types';

function formatCurrency(value: number): string {
  if (value >= 1_000_000) return `$${(value / 1_000_000).toFixed(1)}M`;
  if (value >= 1_000) return `$${(value / 1_000).toFixed(0)}k`;
  return `$${value.toLocaleString('en-US')}`;
}

export default function DashboardPage() {
  const [deals, setDeals] = useState<Deal[]>([]);
  const [memories, setMemories] = useState<MemoryItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetchJson<Deal[]>('/deals'),
      fetchJson<MemoryItem[]>('/memory'),
    ])
      .then(([dealsData, memoriesData]) => {
        setDeals(dealsData);
        setMemories(memoriesData);
      })
      .catch(() => {})
      .finally(() => setIsLoading(false));
  }, []);

  const openDeals = deals.filter((d) => d.stage !== 'WON' && d.stage !== 'LOST');
  const wonDeals = deals.filter((d) => d.stage === 'WON');
  const totalPipelineValue = openDeals.reduce((acc, d) => acc + Number(d.value || 0), 0);
  const totalWonValue = wonDeals.reduce((acc, d) => acc + Number(d.value || 0), 0);

  // Pick the highest-value open deal as the featured deal
  const featuredDeal = openDeals.length > 0
    ? openDeals.reduce((best, d) => (Number(d.value) > Number(best.value) ? d : best), openDeals[0])
    : null;

  const stats = [
    { label: 'Active Pipeline', value: formatCurrency(totalPipelineValue), tone: 'blue' },
    { label: 'Deals Won', value: formatCurrency(totalWonValue), tone: 'green' },
    { label: 'Hindsight Memories', value: String(memories.length), tone: 'amber' },
    { label: 'Attention Required', value: String(openDeals.length), tone: 'red' },
  ];

  return (
    <div>
      <section className="section">
        <h1 className="page-title">Executive Revenue Dashboard</h1>
        <p className="page-subtitle">Real-time pipeline intelligence powered by Hindsight persistent memory.</p>

        <div className="kpi-grid">
          {stats.map((stat) => (
            <Card key={stat.label} title={stat.label} value={isLoading ? '—' : stat.value} tone={stat.tone as any} />
          ))}
        </div>
      </section>

      {/* Featured Deal Banner — driven by live API data */}
      {featuredDeal && (
        <div
          className="card"
          style={{
            background: '#ffffff',
            border: '1px solid #bfdbfe',
            borderLeft: '4px solid var(--primary)',
            marginBottom: '2rem',
            padding: '1.4rem 1.75rem',
            boxShadow: 'var(--shadow)',
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', marginBottom: '0.35rem' }}>
                <span className="status info" style={{ fontSize: '0.72rem' }}>
                  TOP OPPORTUNITY
                </span>
                <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>{featuredDeal.id}</span>
              </div>
              <h2 style={{ fontSize: '1.35rem', margin: 0, fontWeight: 700, color: '#0f172a' }}>
                {featuredDeal.company?.name || featuredDeal.name}
              </h2>
              <p style={{ color: 'var(--text-muted)', margin: '0.35rem 0 0 0', fontSize: '0.88rem' }}>
                {featuredDeal.stage} · {formatCurrency(Number(featuredDeal.value))} · {featuredDeal.probability}% probability
              </p>
            </div>
            <Link
              href={`/deals/${featuredDeal.id}`}
              className="button primary"
              style={{ padding: '0.65rem 1.4rem', fontWeight: 600, display: 'inline-block' }}
            >
              Launch Deal Workspace →
            </Link>
          </div>
        </div>
      )}

      <section className="hero">
        <Card title="Active Opportunities" subtitle="Click any deal to inspect its Hindsight memory layer">
          {isLoading ? (
            <p style={{ color: 'var(--text-muted)' }}>Loading deals...</p>
          ) : deals.length === 0 ? (
            <p style={{ color: 'var(--text-muted)' }}>No deals found. Create one from the Deals page.</p>
          ) : (
            <ul className="timeline">
              {deals.map((item) => (
                <li key={item.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Link href={`/deals/${item.id}`} style={{ fontWeight: 600, color: 'var(--primary)' }}>
                    {item.company?.name || item.name}
                  </Link>
                  <div style={{ display: 'flex', gap: '0.85rem', alignItems: 'center' }}>
                    <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                      {formatCurrency(Number(item.value))}
                    </span>
                    <span
                      className="status"
                      style={{
                        background:
                          item.stage === 'WON'
                            ? 'var(--success-soft)'
                            : item.stage === 'LOST'
                            ? 'var(--danger-soft)'
                            : 'var(--info-soft)',
                        color:
                          item.stage === 'WON'
                            ? 'var(--success)'
                            : item.stage === 'LOST'
                            ? 'var(--danger)'
                            : 'var(--info)',
                        border: `1px solid ${
                          item.stage === 'WON'
                            ? 'var(--success-border)'
                            : item.stage === 'LOST'
                            ? 'var(--danger-border)'
                            : 'var(--info-border)'
                        }`,
                      }}
                    >
                      {item.stage}
                    </span>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </Card>

        <Card title="Memory Insights" subtitle="Derived from Hindsight memories retained across deals">
          {isLoading ? (
            <p style={{ color: 'var(--text-muted)' }}>Loading memories...</p>
          ) : memories.length === 0 ? (
            <p style={{ color: 'var(--text-muted)' }}>No memories recorded yet. Add interactions to build the memory layer.</p>
          ) : (
            <ul className="summary-list">
              {memories.slice(0, 5).map((m) => (
                <li key={m.id}>
                  <span>
                    <strong style={{ textTransform: 'capitalize' }}>{m.type}:</strong> {m.statement}
                  </span>
                  <span className="status info" style={{ fontSize: '0.72rem', whiteSpace: 'nowrap' }}>
                    {m.confidence}%
                  </span>
                </li>
              ))}
              {memories.length > 5 && (
                <li>
                  <Link href="/memory" style={{ color: 'var(--primary)', fontWeight: 600 }}>
                    View all {memories.length} memories →
                  </Link>
                </li>
              )}
            </ul>
          )}
        </Card>
      </section>
    </div>
  );
}
