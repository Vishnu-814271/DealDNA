import type { ReactNode } from 'react';

type CardProps = {
  title: string;
  value?: string;
  subtitle?: string;
  tone?: 'default' | 'blue' | 'green' | 'amber' | 'red';
  children?: ReactNode;
};

export function Card({ title, value, subtitle, tone = 'default', children }: CardProps) {
  return (
    <div className={`card tone-${tone === 'default' ? 'blue' : tone}`}>
      <div className="card-label">{title}</div>
      {value ? <div className="card-value">{value}</div> : null}
      {subtitle ? <div className="card-subtitle">{subtitle}</div> : null}
      {children}
    </div>
  );
}
