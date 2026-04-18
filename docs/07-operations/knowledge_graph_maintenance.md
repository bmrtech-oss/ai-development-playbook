# Knowledge Graph & Database Maintenance

**Last Updated:** 2026-04-18

## Overview
Our Knowledge Graph (RDF/OWL) and Vector DB (pgvector) are the brains of our platform. They require specialized maintenance compared to standard relational databases.

## Schema Migrations
### Relational (PostgreSQL)
- Use `alembic` for Python-based migrations.
- **Zero-Downtime:** All migrations must be additive or non-breaking. Never drop columns without a 2-release deprecation cycle.

### Vector Data (pgvector)
- **Re-indexing:** Changing embedding models requires a full re-index. This must be done on a shadow table/collection before swapping.
- **HNSW Tuning:** Periodically monitor `m` and `ef_construction` parameters as the dataset grows to maintain search recall.

### Knowledge Graph (RDF/OWL)
- **Ontology Versioning:** Treat the ontology like code. Version it in the `schema/` directory.
- **Inference Performance:** Limit OWL reasoning to "Materialized Views" where possible. Avoid real-time reasoning on the full graph during request cycles.

## Data Quality & Consistency
- **Orphaned Nodes:** Weekly jobs to prune embeddings for files that no longer exist in the repository.
- **Ontology Alignment:** Ensure that `tree-sitter` tags align with the RDF classes (e.g., a `Function` in Python tree-sitter must map to `:CodeFunction` in our ontology).

## Backups & Recovery
- **Point-in-Time Recovery (PITR):** Enabled for PostgreSQL.
- **Vector Snapshots:** Daily snapshots of vector partitions.
- **KG Export:** Weekly TTL (Turtle) exports of the core ontology and instance data for disaster recovery.

## Health Metrics
- **Mean Search Latency:** Target < 200ms for vector search.
- **Triple Count:** Monitor the growth of the KG to predict storage needs.
- **Inference Time:** Monitor how long it takes to run the reasoning engine on new repository ingests.
