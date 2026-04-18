# RAG Hygiene Dashboard

**Last Updated:** 2026-04-18  
**Owner:** Platform Team / AI Infra

## Overview

This dashboard monitors the health of our Retrieval-Augmented Generation (RAG) system. We track embedding drift and content staleness to ensure retrieval quality degrades gracefully over time.

---

## Metric: Embedding Drift

**Definition:** Cosine similarity between recent query embeddings and the centroid of document embeddings over time.

**Why it matters:** High drift indicates the query distribution has shifted from the document corpus, leading to poor retrieval relevance.

**Calculation (pgvector SQL):**
```sql
WITH recent_queries AS (
  SELECT embedding
  FROM query_logs
  WHERE created_at > NOW() - INTERVAL '7 days'
  LIMIT 1000
),
doc_centroid AS (
  SELECT AVG(embedding) as centroid
  FROM document_embeddings
)
SELECT 1 - (AVG(cosine_similarity(r.embedding, d.centroid))) as embedding_drift
FROM recent_queries r
CROSS JOIN doc_centroid d;
```

**Expected Range:** 0.0 (perfect alignment) to 1.0 (complete drift)

---

## Metric: Staleness

**Definition:** Days since last update for Top 10 most retrieved chunks.

**Why it matters:** Stale content leads to outdated or incorrect responses, especially for rapidly evolving domains.

**Calculation:**
```sql
SELECT
  chunk_id,
  EXTRACT(EPOCH FROM (NOW() - last_updated)) / 86400 as days_stale,
  retrieval_count
FROM document_chunks
WHERE retrieval_count > 0
ORDER BY retrieval_count DESC
LIMIT 10;
```

**Expected Range:** < 30 days for active content

---

## Alerting Thresholds

- **Warning:** Embedding drift > 15%
- **Critical:** Embedding drift > 25%
- **Info:** Any chunk > 90 days stale

**Alert Channels:** #ai-infra Slack, PagerDuty (critical only)

---

## Remediation Steps

### For Embedding Drift Alerts

1. **Investigate query patterns:** Review recent query logs for new topics or terminology shifts
2. **Update document corpus:** Add recent documentation or examples
3. **Re-index embeddings:** Trigger manual re-index of the knowledge base

### Manual Re-index Process

```bash
# From the ai-platform repository root
cd infra/rag-indexer

# Update configuration if needed
vim config/rag-indexer.yaml

# Run the indexer
python -m rag_indexer.main --full-reindex --validate

# Verify metrics improve
curl http://rag-monitor:9090/metrics | grep embedding_drift
```

**Expected Outcome:** Drift should reduce by 10-20% within 24 hours of re-indexing.

**Rollback:** If re-indexing causes issues, revert to previous embedding snapshot:
```bash
python -m rag_indexer.main --rollback-to $(cat .last_good_embedding_sha)
```