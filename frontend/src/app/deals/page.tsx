"use client";

import React, { useEffect, useState } from 'react';
import Link from 'next/link';

import { Card } from '@/components/ui/Card';
import { fetchJson, postJson } from '@/lib/api/client';
import { Deal } from '@/types';

function formatValue(value: number | string) {
  return `$${Number(value).toLocaleString('en-US', { maximumFractionDigits: 0 })}`;
}

function formatStage(stage: string) {
  return stage.toUpperCase();
}

export default function DealsPage() {
  const [deals, setDeals] = useState<Deal[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newName, setNewName] = useState('');
  const [newCompany, setNewCompany] = useState('');
  const [newValue, setNewValue] = useState('150000');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const loadDeals = () => {
    setIsLoading(true);
    fetchJson<Deal[]>('/deals')
      .then(setDeals)
      .catch((err) => setError(err.message || 'The deal service is unavailable. Ensure FastAPI is running.'))
      .finally(() => setIsLoading(false));
  };

  useEffect(() => {
    loadDeals();
  }, []);

  const handleCreateDeal = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newName.trim() || !newCompany.trim()) return;

    setIsSubmitting(true);
    try {
      const comp = await postJson<{ id: string }>('/companies', {
        name: newCompany,
        industry: 'Technology',
        size: 'Enterprise',
      });

      await postJson('/deals', {
        company_id: comp.id,
        name: newName,
        stage: 'NEW',
        value: parseFloat(newValue) || 100000,
        probability: 50,
      });

      setShowCreateModal(false);
      setNewName('');
      setNewCompany('');
      loadDeals();
    } catch (err: any) {
      alert(`Failed to create deal: ${err.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div>
      <section className="section" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 className="page-title">Active Deal Pipeline</h1>
          <p className="page-subtitle">Track deal progress, buying committees, and memory-driven next actions.</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="button primary"
          style={{ padding: '0.65rem 1.4rem', cursor: 'pointer' }}
        >
          + Create Deal
        </button>
      </section>

      <div className="table-wrap">
        {isLoading && <p className="page-subtitle" style={{ padding: '1.5rem' }}>Loading live deals...</p>}
        {error && <p className="page-subtitle" style={{ padding: '1.5rem', color: 'var(--danger)' }}>{error}</p>}
        {!isLoading && !error && (
          <table className="data-table">
            <thead>
              <tr>
                <th>Deal Name</th>
                <th>Company / Account</th>
                <th>Stage</th>
                <th>Value</th>
                <th>Win Probability</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {deals.map((deal) => (
                <tr key={deal.id}>
                  <td>
                    <Link
                      href={`/deals/${deal.id}`}
                      style={{ fontWeight: 600, color: 'var(--primary)', textDecoration: 'none' }}
                    >
                      {deal.name}
                    </Link>
                  </td>
                  <td>{deal.company?.name ?? 'Unassigned'}</td>
                  <td>
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
                      {formatStage(deal.stage)}
                    </span>
                  </td>
                  <td style={{ fontWeight: 600, color: '#0f172a' }}>{formatValue(deal.value)}</td>
                  <td>
                    <span className="status info">{deal.probability}%</span>
                  </td>
                  <td>
                    <Link
                      href={`/deals/${deal.id}`}
                      className="button"
                      style={{ fontSize: '0.78rem', padding: '0.4rem 0.85rem' }}
                    >
                      Open Workspace →
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <div className="card-grid" style={{ marginTop: '2rem' }}>
        {deals.slice(0, 3).map((deal) => (
          <Link key={deal.id} href={`/deals/${deal.id}`}>
            <Card
              title={deal.company?.name ?? deal.name}
              value={formatValue(deal.value)}
              subtitle={`${formatStage(deal.stage)} • ${deal.probability}% probability`}
              tone="blue"
            />
          </Link>
        ))}
      </div>

      {/* CREATE DEAL MODAL */}
      {showCreateModal && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(15, 23, 42, 0.45)',
            backdropFilter: 'blur(4px)',
            display: 'grid',
            placeItems: 'center',
            zIndex: 100,
            padding: '1rem',
          }}
        >
          <div className="card" style={{ width: '100%', maxWidth: '480px', background: '#ffffff', border: '1px solid var(--border)' }}>
            <h2 style={{ fontSize: '1.2rem', marginTop: 0, fontWeight: 700 }}>
              Create Opportunity
            </h2>
            <form onSubmit={handleCreateDeal} style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
              <div>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', display: 'block', marginBottom: '0.2rem', fontWeight: 600 }}>
                  Deal Name
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Acme Enterprise Expansion"
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
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
                  Company Name
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Acme Technologies"
                  value={newCompany}
                  onChange={(e) => setNewCompany(e.target.value)}
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
                  Estimated Contract Value ($)
                </label>
                <input
                  type="number"
                  required
                  value={newValue}
                  onChange={(e) => setNewValue(e.target.value)}
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
                  onClick={() => setShowCreateModal(false)}
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
                  disabled={isSubmitting}
                  className="button primary"
                  style={{ padding: '0.55rem 1.35rem', cursor: 'pointer' }}
                >
                  {isSubmitting ? 'Creating...' : 'Create Deal'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
