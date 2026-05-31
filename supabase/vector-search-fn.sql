-- Add this SQL function to Supabase SQL Editor and run it:

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
  budget_allocated numeric,
  latitude double precision,
  longitude double precision,
  similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT 
    p.id,
    p.title,
    p.contractor,
    p.status,
    p.budget_allocated,
    p.latitude,
    p.longitude,
    1 - (p.embedding <=> query_embedding) as similarity
  FROM projects p
  WHERE p.embedding IS NOT NULL
    AND 1 - (p.embedding <=> query_embedding) > match_threshold
  ORDER BY p.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;
