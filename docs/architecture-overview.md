# DealDNA Architecture Overview

## Purpose

DealDNA is an AI-powered sales and revenue intelligence platform. It helps teams track deal progress, capture customer context, recall historical memory, and generate recommendations based on prior outcomes.

## Core principles

1. PostgreSQL stores structured business truth.
2. Hindsight memory stores long-term learning and recall.
3. The Agent Orchestrator builds context before calling an LLM.
4. Evidence is required for recommendations.
5. The frontend never talks directly to PostgreSQL or model providers.

## Layers

- Frontend: Next.js + React
- API: FastAPI
- Business logic: modules for deals, customers, memory, recommendations
- Data: PostgreSQL
- AI memory: Hindsight adapter
- LLM: provider abstraction layer

## Flow

User action -> Frontend -> FastAPI -> Domain services -> PostgreSQL -> outbox/worker -> memory + recommender -> LLM -> response

## Architecture choice

This project starts as a modular monolith so that service boundaries remain clean while keeping the MVP manageable.
