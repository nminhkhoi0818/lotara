destinations (
  id uuid,
  name text,
  country text,
  tags text[],
  budget_level text,
  best_seasons text[]
)

itineraries (
  id uuid,
  user_id uuid,
  content jsonb,
  status text
)

pretrip_cache (
  key text,
  value jsonb,
  updated_at timestamp
)
