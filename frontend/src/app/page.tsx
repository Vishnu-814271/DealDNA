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

export default function HomePage() {
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

  // Derived stats
  const openDeals = deals.filter((d) => d.stage !== 'WON' && d.stage !== 'LOST');
  const totalPipelineValue = openDeals.reduce((acc, d) => acc + Number(d.value || 0), 0);

  const worldCount = memories.filter((m) => m.type === 'World').length;
  const expCount = memories.filter((m) => m.type === 'Experience').length;
  const obsCount = memories.filter((m) => m.type === 'Observation').length;
  const totalMemories = memories.length;

  // Find the highest-value open deal as the "featured" deal
  const featuredDeal = openDeals.length > 0
    ? openDeals.reduce((best, d) => (Number(d.value) > Number(best.value) ? d : best), openDeals[0])
    : null;

  // Win rate from historical data
  const wonDeals = deals.filter((d) => d.stage === 'WON');
  const closedDeals = deals.filter((d) => d.stage === 'WON' || d.stage === 'LOST');
  const winRate = closedDeals.length > 0 ? Math.round((wonDeals.length / closedDeals.length) * 100) : 0;

  const kpiCards = [
    {
      title: 'Pipeline Monitored',
      value: isLoading ? '—' : `${openDeals.length} Opportunities`,
      subtitle: 'Connected to persistent memory',
    },
    {
      title: 'Top Opportunity',
      value: isLoading ? '—' : featuredDeal ? formatCurrency(Number(featuredDeal.value)) : '$0',
      subtitle: isLoading ? '...' : featuredDeal ? `${featuredDeal.company?.name || featuredDeal.name}` : 'No open deals',
    },
    {
      title: 'Hindsight Memory',
      value: isLoading ? '—' : `${totalMemories} Retained`,
      subtitle: `World ${worldCount} · Experience ${expCount} · Observation ${obsCount}`,
    },
    {
      title: 'Historical Win Rate',
      value: isLoading ? '—' : closedDeals.length > 0 ? `${winRate}%` : 'N/A',
      subtitle: isLoading ? '...' : closedDeals.length > 0 ? `${wonDeals.length} won / ${closedDeals.length} closed` : 'No closed deals yet',
    },
  ];

  return (
    <div>
      <section className="section">
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '0.4rem' }}>
          <h1 className="page-title" style={{ display: 'inline-flex', alignItems: 'center', margin: 0 }}>
            DealDNA <span className="dealdna-brand-ai" style={{ fontSize: '0.95rem', marginLeft: '0.5rem', padding: '0.2rem 0.6rem' }}>AI</span>
          </h1>
        </div>
        <p className="page-subtitle" style={{ fontSize: '1.05rem', color: 'var(--primary)', fontWeight: 600 }}>
          The Revenue Memory Engine
        </p>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.92rem', maxWidth: '680px', marginTop: '0.5rem', lineHeight: 1.6 }}>
          Persistent deal memory and historical learning loop. DealDNA records customer interactions, recalls verified stakeholder facts, and recommends evidence-backed next-best actions without relying on transient prompt context.
        </p>

        <div className="kpi-grid">
          {kpiCards.map((item) => (
            <Card key={item.title} title={item.title} value={item.value} subtitle={item.subtitle} tone="blue" />
          ))}
        </div>
      </section>

      <section className="hero">
        {/* Featured deal card — driven by API data */}
        <Card
          title={
            isLoading
              ? 'Loading...'
              : featuredDeal
              ? `${featuredDeal.company?.name || featuredDeal.name}`
              : 'No Active Deals'
          }
          subtitle={
            isLoading
              ? ''
              : featuredDeal
              ? `${featuredDeal.id} · ${featuredDeal.stage} · ${featuredDeal.probability}% probability`
              : 'Create a deal to get started'
          }
        >
          {!isLoading && featuredDeal && (
            <>
              <ul className="feature-list">
                <li>
                  <span style={{ fontWeight: 500, color: 'var(--text-secondary)' }}>Deal Value</span>
                  <span className="status info">{formatCurrency(Number(featuredDeal.value))}</span>
                </li>
                <li>
                  <span style={{ fontWeight: 500, color: 'var(--text-secondary)' }}>Stage</span>
                  <span className="status info">{featuredDeal.stage}</span>
                </li>
                <li>
                  <span style={{ fontWeight: 500, color: 'var(--text-secondary)' }}>Win Probability</span>
                  <span className="status success">{featuredDeal.probability}%</span>
                </li>
              </ul>
              <div style={{ marginTop: '1.5rem' }}>
                <Link href={`/deals/${featuredDeal.id}`} className="button primary" style={{ display: 'inline-block' }}>
                  Launch Deal Workspace →
                </Link>
              </div>
            </>
          )}
          {!isLoading && !featuredDeal && (
            <div style={{ marginTop: '1rem' }}>
              <Link href="/deals" className="button primary" style={{ display: 'inline-block' }}>
                Go to Deal Pipeline →
              </Link>
            </div>
          )}
        </Card>

        <Card title="Revenue Intelligence Workspaces" subtitle="Direct access to memory-powered workflows">
          <ul className="summary-list">
            <li>
              <span>Executive Dashboard</span>
              <Link href="/dashboard" className="inline-pill">Open</Link>
            </li>
            <li>
              <span>Deal Pipeline</span>
              <Link href="/deals" className="inline-pill">Open</Link>
            </li>
            <li>
              <span>Memory Explorer (Hindsight)</span>
              <Link href="/memory" className="inline-pill">Open</Link>
            </li>
            <li>
              <span>AI Revenue Assistant</span>
              <Link href="/assistant" className="inline-pill">Open</Link>
            </li>
          </ul>
        </Card>
      </section>
    </div>
  );
}
