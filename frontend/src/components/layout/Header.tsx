"use client";

import React, { useEffect, useState } from 'react';
import Link from 'next/link';

import { fetchJson } from '@/lib/api/client';
import { Deal } from '@/types';

export function Header() {
  const [topDeal, setTopDeal] = useState<Deal | null>(null);

  useEffect(() => {
    fetchJson<Deal[]>('/deals')
      .then((deals) => {
        // Pick the highest-value open deal as the quick-access link
        const openDeals = deals.filter((d) => d.stage !== 'WON' && d.stage !== 'LOST');
        if (openDeals.length > 0) {
          const best = openDeals.reduce((a, b) => (Number(a.value) > Number(b.value) ? a : b), openDeals[0]);
          setTopDeal(best);
        } else if (deals.length > 0) {
          setTopDeal(deals[0]);
        }
      })
      .catch(() => {});
  }, []);

  return (
    <header className="header">
      <Link href="/" className="brand" style={{ textDecoration: 'none' }}>
        <div style={{ display: 'flex', flexDirection: 'column' }}>
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <span className="dealdna-brand-text">DealDNA</span>
            <span className="dealdna-brand-ai">AI</span>
          </div>
          <span className="dealdna-tagline">
            The Revenue Memory Engine
          </span>
        </div>
      </Link>

      <div className="header-actions">
        {topDeal && (
          <Link
            href={`/deals/${topDeal.id}`}
            className="primary-button"
            style={{ textDecoration: 'none', display: 'inline-block' }}
          >
            {topDeal.company?.name || topDeal.name} →
          </Link>
        )}
      </div>
    </header>
  );
}
