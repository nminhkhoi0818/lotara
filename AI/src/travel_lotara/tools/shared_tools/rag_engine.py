"""
RAG Engine

Provides retrieval over curated travel knowledge with strict freshness metadata.
Uses simple in-memory search for demo (can be upgraded to vector DB).
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any, Iterable

from pydantic import BaseModel, Field, field_validator


class RAGDocument(BaseModel):
    """A retrieved document with freshness metadata."""
    source: str
    last_updated: date
    ttl_days: int = Field(ge=1, le=365)
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("last_updated", mode="before")
    @classmethod
    def _parse_last_updated(cls, value: Any) -> date:
        if isinstance(value, date):
            return value
        return datetime.strptime(str(value), "%Y-%m-%d").date()

    def is_fresh(self) -> bool:
        return date.today() <= self.last_updated + timedelta(days=self.ttl_days)


class RAGQuery(BaseModel):
    """Structured query for RAG retrieval."""
    query: str
    top_k: int = Field(default=5, ge=1, le=20)
    filters: dict[str, Any] = Field(default_factory=dict)


class RAGEngine:
    """
    Simple RAG engine with in-memory knowledge base.
    
    For production: Replace with vector database (Pinecone, Weaviate, etc.)
    """
    
    def __init__(self):
        self._knowledge_base = self._load_knowledge_base()
    
    def _load_knowledge_base(self) -> list[RAGDocument]:
        """Load curated travel knowledge."""
        today = date.today()
        
        return [
            # Tokyo
            RAGDocument(
                source="Tokyo Food Guide 2026",
                last_updated=today - timedelta(days=15),
                ttl_days=90,
                content="Tsukiji Outer Market remains the best place for fresh sushi and street food in Tokyo. Open 5am-2pm daily except Sundays. Must-try: tuna sashimi, tamago, and fresh uni. Average cost: $30-50 per person.",
                metadata={"destination": "Tokyo", "category": "food"}
            ),
            RAGDocument(
                source="Tokyo Temples & Shrines",
                last_updated=today - timedelta(days=30),
                ttl_days=180,
                content="Senso-ji Temple in Asakusa is Tokyo's oldest temple (founded 628 AD). Free entry. Best visited early morning (6-8am) or evening (5-7pm) to avoid crowds. Don't miss Nakamise shopping street leading to the temple.",
                metadata={"destination": "Tokyo", "category": "culture"}
            ),
            RAGDocument(
                source="Tokyo Transportation Guide",
                last_updated=today - timedelta(days=10),
                ttl_days=60,
                content="Suica or Pasmo card essential for metro/train travel. Tokyo Metro covers most tourist areas. Day pass: ¥600 ($5). Trains stop running around midnight. Taxi expensive ($15 minimum).",
                metadata={"destination": "Tokyo", "category": "transport"}
            ),
            RAGDocument(
                source="Tokyo Budget Tips 2026",
                last_updated=today - timedelta(days=5),
                ttl_days=30,
                content="Budget travelers can eat well for $25-35/day using convenience stores, ramen shops, and food halls. Mid-range: $80-120/day. Convenience store breakfasts are surprisingly good and cost $3-5.",
                metadata={"destination": "Tokyo", "category": "budget"}
            ),
            
            # Paris
            RAGDocument(
                source="Paris Museums 2026",
                last_updated=today - timedelta(days=20),
                ttl_days=90,
                content="Louvre Museum tickets €17 online, €15 at venue. Free first Sunday of month (crowds!). Paris Museum Pass (€62 for 2 days) worthwhile if visiting 3+ museums. Book Louvre tickets 2-3 days ahead.",
                metadata={"destination": "Paris", "category": "culture"}
            ),
            RAGDocument(
                source="Paris Food Scene",
                last_updated=today - timedelta(days=25),
                ttl_days=90,
                content="Best authentic bistros in Saint-Germain-des-Prés and Le Marais. Avoid tourist traps near Eiffel Tower. Dinner reservations essential for popular spots. Budget: €15-25 for lunch menu, €35-60 for dinner.",
                metadata={"destination": "Paris", "category": "food"}
            ),
            RAGDocument(
                source="Paris Metro Guide",
                last_updated=today - timedelta(days=12),
                ttl_days=60,
                content="Paris Metro Navigo Easy card recommended over single tickets. Day pass €8. Be alert for pickpockets on lines 1, 2, and 4. Stations close around 1am (2am weekends).",
                metadata={"destination": "Paris", "category": "transport"}
            ),
            
            # Bali
            RAGDocument(
                source="Bali Safety & Travel Tips",
                last_updated=today - timedelta(days=8),
                ttl_days=90,
                content="Ubud ideal for culture and nature (rice terraces, temples, yoga). Seminyak for beaches and nightlife. Uluwatu for surfing. Rent scooter $5/day but traffic chaotic. Grab app works well for car transport.",
                metadata={"destination": "Bali", "category": "general"}
            ),
            RAGDocument(
                source="Bali Temple Etiquette",
                last_updated=today - timedelta(days=45),
                ttl_days=180,
                content="Sarongs required at temples (usually provided for rent). Remove shoes. Women on period not permitted in some temples. Donations expected (Rp 20,000-50,000 / $1.50-3). Dress modestly.",
                metadata={"destination": "Bali", "category": "culture"}
            ),
            RAGDocument(
                source="Bali Food & Prices 2026",
                last_updated=today - timedelta(days=10),
                ttl_days=30,
                content="Local warungs: $2-4 per meal. Western restaurants in Seminyak/Ubud: $8-15. Street food safe if cooked fresh. Try: nasi goreng, mie goreng, satay, babi guling. Bottled water essential.",
                metadata={"destination": "Bali", "category": "food"}
            ),
            
            # General Travel Tips
            RAGDocument(
                source="Visa Requirements 2026",
                last_updated=today - timedelta(days=3),
                ttl_days=30,
                content="US citizens: Japan visa-free 90 days, France (Schengen) visa-free 90 days, Indonesia visa-free 30 days (extendable to 60). Check passport validity (6 months minimum for most countries).",
                metadata={"category": "visas"}
            ),
            RAGDocument(
                source="Travel Insurance Recommendations",
                last_updated=today - timedelta(days=7),
                ttl_days=60,
                content="World Nomads and SafetyWing popular for travelers. Coverage: medical ($50k+), evacuation, trip cancellation, lost baggage. Cost: $40-80 per week depending on age and destination. Book before trip.",
                metadata={"category": "insurance"}
            ),
            RAGDocument(
                source="Best Time to Book Flights",
                last_updated=today - timedelta(days=14),
                ttl_days=45,
                content="International flights: book 2-3 months ahead for best prices. Tuesday/Wednesday often cheapest to book and fly. Use Google Flights price calendar. Avoid peak seasons (July-August, Dec-Jan) for savings.",
                metadata={"category": "flights"}
            ),
        ]
    
    async def retrieve(self, query: RAGQuery) -> list[RAGDocument]:
        """
        Retrieve documents matching query.
        
        Uses simple keyword matching for demo.
        For production: Use vector embeddings and semantic search.
        """
        query_lower = query.query.lower()
        scored_docs = []
        
        for doc in self._knowledge_base:
            # Skip stale documents
            if not doc.is_fresh():
                continue
            
            # Apply filters
            if query.filters:
                match = True
                for key, value in query.filters.items():
                    if doc.metadata.get(key) != value:
                        match = False
                        break
                if not match:
                    continue
            
            # Simple relevance scoring (count keyword matches)
            content_lower = doc.content.lower()
            source_lower = doc.source.lower()
            
            score = 0
            for word in query_lower.split():
                if len(word) > 3:  # Skip short words
                    if word in content_lower:
                        score += 2
                    if word in source_lower:
                        score += 1
            
            if score > 0:
                scored_docs.append((score, doc))
        
        # Sort by score and return top_k
        scored_docs.sort(reverse=True, key=lambda x: x[0])
        return [doc for _, doc in scored_docs[:query.top_k]]

    async def validate_freshness(self, documents: Iterable[RAGDocument]) -> bool:
        """Ensure all documents are fresh."""
        return all(doc.is_fresh() for doc in documents)

