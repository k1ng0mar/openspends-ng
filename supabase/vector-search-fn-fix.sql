-- Run this in Supabase SQL Editor to fix the vector search function:

DROP FUNCTION IF EXISTS match_projects(vector, float, int);

CREATE OR REPLACE FUNCTION match_projects(
  query_embedding vector,
  match_threshold float DEFAULT 0.5,
  match_count int DEFAULT 10
)
RETURNS TABLE (
  id bigint,
  title text,
  contractor text,
  status text,
  budget_allocated double precision,
  latitude double precision,
  longitude double precision,
  similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT 
    p.id::bigint,
    p.title::text,
    p.contractor::text,
    p.status::text,
    p.budget_allocated::double precision,
    p.latitude::double precision,
    p.longitude::double precision,
    (1 - (p.embedding <=> query_embedding))::float as similarity
  FROM projects p
  WHERE p.embedding IS NOT NULL
    AND (1 - (p.embedding <=> query_embedding)) > match_threshold
  ORDER BY p.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;
