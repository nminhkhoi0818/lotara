"""
Query Parser

Extracts structured travel intent from natural language using LLM.
Parses budget, destination, dates, interests, constraints from user queries.
"""

from __future__ import annotations

import json
import logging
import re
from datetime import date, datetime, timedelta
from typing import Any, Optional

from pydantic import BaseModel, Field

try:
    from google import genai
    from google.genai import types
except ImportError:
    raise ImportError(
        "Google Generative AI not installed. Install with: pip install google-generativeai"
    )

from travel_lotara.config.settings import Settings


logger = logging.getLogger(__name__)


class ParsedIntent(BaseModel):
    """Structured representation of user's travel intent."""
    
    # Core intent
    destination: str = ""
    origin: Optional[str] = None
    
    # Dates
    depart_date: Optional[str] = None  # ISO format YYYY-MM-DD
    return_date: Optional[str] = None
    
    # Budget
    budget_usd: Optional[float] = None
    budget_per_day_usd: Optional[float] = None
    
    # Preferences
    interests: list[str] = Field(default_factory=list)  # ["culture", "food", "nature"]
    travel_style: Optional[str] = None  # "budget", "mid-range", "luxury"
    
    # Constraints
    max_flight_hours: Optional[float] = None
    preferred_airlines: list[str] = Field(default_factory=list)
    dietary_restrictions: list[str] = Field(default_factory=list)
    
    # Metadata
    trip_duration_days: Optional[int] = None
    num_travelers: int = 1
    
    # Raw query for reference
    raw_query: str = ""
    
    # Confidence
    parse_confidence: float = 0.0  # How confident the parser is


class QueryParser:
    """
    LLM-based query parser for travel intent extraction.
    
    Uses Google Gemini to extract structured data from natural language.
    Falls back to regex-based extraction if LLM fails.
    """
    
    def __init__(self, settings: Optional[Settings] = None):
        """
        Initialize parser.
        
        Args:
            settings: Application settings (for API keys)
        """
        self.settings = settings or Settings()
        self._client: Optional[genai.Client] = None
    
    def _get_client(self) -> genai.Client:
        """Lazy load Gemini client."""
        if self._client is None:
            self._client = genai.Client(api_key=self.settings.google_api_key)
        return self._client
    
    async def parse(self, query: str) -> ParsedIntent:
        """
        Parse user query into structured intent.
        
        Args:
            query: Natural language query
            
        Returns:
            Structured travel intent
        """
        logger.info(f"Parsing query: {query[:100]}...")
        
        try:
            # Try LLM-based parsing first
            result = await self._parse_with_llm(query)
            result.raw_query = query
            
            # Fallback to regex for missing critical fields
            if not result.destination:
                result = self._parse_with_regex(query)
            
            logger.info(f"Parsed intent: destination={result.destination}, budget=${result.budget_usd}")
            return result
        
        except Exception as e:
            logger.error(f"LLM parsing failed: {e}, falling back to regex")
            return self._parse_with_regex(query)
    
    async def _parse_with_llm(self, query: str) -> ParsedIntent:
        """
        Parse query using Gemini LLM.
        
        Returns structured JSON matching ParsedIntent schema.
        """
        client = self._get_client()
        
        # Construct parsing prompt
        prompt = f"""Extract travel planning information from this query.

Query: "{query}"

Extract the following information and return ONLY a valid JSON object:

{{
  "destination": "primary destination city/country",
  "origin": "departure city if mentioned",
  "depart_date": "YYYY-MM-DD format if mentioned",
  "return_date": "YYYY-MM-DD format if mentioned",
  "budget_usd": numeric value if mentioned,
  "budget_per_day_usd": numeric value if mentioned,
  "interests": ["food", "culture", "nature", "adventure", "relaxation"],
  "travel_style": "budget" | "mid-range" | "luxury",
  "trip_duration_days": number of days if mentioned,
  "num_travelers": number of people,
  "parse_confidence": 0.0 to 1.0 (your confidence in this parse)
}}

Guidelines:
- If dates are relative (e.g., "next week"), convert to actual dates (today is {date.today()})
- Extract budget from phrases like "$3000 budget", "under $100/day", "cheap trip"
- Infer interests from context (e.g., "see temples" → ["culture"], "try local food" → ["food"])
- If travel style not explicit, infer from budget/context
- Set parse_confidence based on how explicit the query is
- Return ONLY the JSON object, no other text

JSON:"""

        # Call Gemini
        response = client.models.generate_content(
            model=self.settings.gemini_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.1,  # Low temperature for structured extraction
                max_output_tokens=500,
            ),
        )
        
        # Parse JSON from response
        text = response.text.strip()
        
        # Extract JSON if wrapped in markdown code blocks
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        
        # Parse JSON
        data = json.loads(text)
        
        # Create ParsedIntent
        return ParsedIntent(**data)
    
    def _parse_with_regex(self, query: str) -> ParsedIntent:
        """
        Fallback regex-based parser.
        
        Extracts basic information when LLM fails.
        """
        logger.info("Using regex fallback parser")
        
        result = ParsedIntent(raw_query=query, parse_confidence=0.5)
        
        # Extract destination (basic heuristic: proper nouns after "to", "in", "visit")
        dest_patterns = [
            r"(?:to|in|visit|going to|trip to)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
            r"^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+trip",
        ]
        for pattern in dest_patterns:
            match = re.search(pattern, query)
            if match:
                result.destination = match.group(1)
                break
        
        # Extract budget
        budget_patterns = [
            r"\$?(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:USD|dollars?|budget)",
            r"(?:budget|spend|max)\s*(?:of)?\s*\$?(\d+(?:,\d{3})*)",
            r"under\s*\$?(\d+)",
        ]
        for pattern in budget_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(",", "")
                result.budget_usd = float(amount_str)
                break
        
        # Extract per-day budget
        per_day_patterns = [
            r"\$?(\d+)\s*(?:per|/)?\s*day",
            r"(\d+)\s*(?:USD|dollars?)\s*(?:per|a)\s*day",
        ]
        for pattern in per_day_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                result.budget_per_day_usd = float(match.group(1))
                break
        
        # Extract interests (keyword matching)
        interest_keywords = {
            "food": ["food", "restaurant", "cuisine", "eat", "dining", "culinary"],
            "culture": ["temple", "museum", "cultural", "heritage", "history", "art"],
            "nature": ["nature", "hiking", "beach", "mountain", "park", "outdoor"],
            "adventure": ["adventure", "trek", "climb", "dive", "surf", "extreme"],
            "relaxation": ["relax", "spa", "resort", "peaceful", "quiet", "beach"],
            "nightlife": ["nightlife", "club", "bar", "party", "entertainment"],
        }
        
        query_lower = query.lower()
        for interest, keywords in interest_keywords.items():
            if any(kw in query_lower for kw in keywords):
                result.interests.append(interest)
        
        # Infer travel style from budget or keywords
        if result.budget_usd:
            if result.budget_usd < 1000:
                result.travel_style = "budget"
            elif result.budget_usd < 3000:
                result.travel_style = "mid-range"
            else:
                result.travel_style = "luxury"
        
        if any(word in query_lower for word in ["cheap", "budget", "backpack", "hostel"]):
            result.travel_style = "budget"
        elif any(word in query_lower for word in ["luxury", "premium", "5-star", "upscale"]):
            result.travel_style = "luxury"
        
        # Extract trip duration
        duration_patterns = [
            r"(\d+)\s*(?:day|night)s?",
            r"(\d+)d",
            r"for\s*(\d+)\s*(?:day|night)",
        ]
        for pattern in duration_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                result.trip_duration_days = int(match.group(1))
                break
        
        # Extract number of travelers
        traveler_patterns = [
            r"(\d+)\s*(?:people|person|traveler|pax)",
            r"group\s*of\s*(\d+)",
            r"(\d+)\s*of\s*us",
        ]
        for pattern in traveler_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                result.num_travelers = int(match.group(1))
                break
        
        return result


# Singleton instance
_parser_instance: Optional[QueryParser] = None


def get_query_parser() -> QueryParser:
    """Get singleton query parser instance."""
    global _parser_instance
    if _parser_instance is None:
        _parser_instance = QueryParser()
    return _parser_instance
