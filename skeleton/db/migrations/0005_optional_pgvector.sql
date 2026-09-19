-- ============================================================================
-- 0005_optional_pgvector.sql — embeddings, only where pgvector exists.
-- Supabase ships pgvector; a bare local Postgres does not. This migration is
-- therefore guarded so the schema, the RLS suite and CI stay green either way.
-- ============================================================================

do $$
begin
  if exists (select 1 from pg_available_extensions where name = 'vector') then
    execute 'create extension if not exists vector';
    execute 'alter table knowledge_chunk add column if not exists embedding vector(1536)';
    execute 'create index if not exists idx_knowledge_chunk_embedding
               on knowledge_chunk using hnsw (embedding vector_cosine_ops)';
    raise notice 'pgvector present: embedding column and HNSW index added';
  else
    raise notice 'pgvector unavailable: skipping embedding column (Supabase enables it by default)';
  end if;
end $$;

-- Retrieval must always be tenant-scoped. When you add the similarity search,
-- put the org filter in the SQL, not in application code:
--
--   select c.id, c.content
--     from knowledge_chunk c
--    where c.organization_id = $1
--    order by c.embedding <=> $2
--    limit 8;
--
-- and assert in the context-assembly layer that every returned chunk's
-- organization_id equals the run's organization_id before it enters a prompt.
