# Example: Responding to a Drift Alert

**Last Updated:** 2026-04-18  
**Owner:** Platform Team / AI Infra

## Alert Details

- **PagerDuty alert:** `Critical: Embedding Drift at 27% (Threshold: 25%) for knowledge base 'internal-docs'`
- **Triggered:** 2026-04-18 09:12 UTC
- **Severity:** Critical
- **Affected system:** RAG retrieval for internal documentation search

---

## Initial Triage (5 min)

1. Check `#ai-infra` Slack for recent activity.
2. Confirm the alert timestamp and note any correlated incidents.
3. Findings: a spike in user questions about the newly released "MCP Toolset v2.0" which is not yet indexed in the vector database.

**Triage conclusion:** Drift is likely caused by new content being referenced by queries before it was added to the knowledge base.

---

## Investigation (10 min)

Run the embedding drift query to confirm and quantify the issue.

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

### Sample output

| embedding_drift |
|-----------------|
| 0.27 |

Run a focused query for the spike terms:

```sql
SELECT q.query_text, cosine_similarity(q.embedding, d.centroid) as similarity
FROM query_logs q
CROSS JOIN doc_centroid d
WHERE q.query_text ILIKE '%MCP%'
ORDER BY similarity ASC
LIMIT 20;
```

### Sample output

| query_text | similarity |
|---------------------------|------------|
| "How do I configure MCP Toolset v2.0" | 0.62 |
| "MCP Toolset v2.0 release notes" | 0.59 |

**Investigation conclusion:** New MCP Toolset content is under-indexed, causing a drift spike above the critical threshold.

---

## Remediation (30 min)

1. Locate the missing documentation files on the shared drive.
2. Add them to the ingestion pipeline input directory, e.g., `/mnt/docs-to-index/internal-docs/mcp-toolset-v2.0/`.
3. Trigger the manual re-index:

```bash
cd /repo/infra/rag-indexer
python -m rag_indexer.main --full-reindex --validate
```

4. Monitor the indexer logs for errors and completion status.
5. Confirm the new documents were processed and embeddings were stored.

**Key checkpoints:**
- New content appears in ingestion logs
- No validation failures in `--validate`
- Indexer finishes cleanly

---

## Verification (15 min)

Re-run the drift query after indexing completes.

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

### Sample output

| embedding_drift |
|-----------------|
| 0.11 |

**Verification conclusion:** Drift returned to 11%, which is below the warning threshold and back in healthy range.

---

## Post-Incident Action

- Create a Jira ticket to automate documentation source detection.
- Schedule weekly full re-indexes for the knowledge base.
- Add an alert rule for new content categories not seen in the current index.

**Suggested ticket summary:** "Automate knowledge base source discovery and weekly RAG full re-index for internal-docs."
