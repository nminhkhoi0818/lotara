"""
Milvus Location Retrieval Tool
===============================
This tool retrieves location data from Milvus vector database based on user queries.
It provides Vietnam tourism location recommendations with full details including
destinations, hotels, activities, and ratings.

PERFORMANCE OPTIMIZATIONS:
- Async execution to avoid blocking
- LRU caching for embeddings and queries
- Singleton Milvus client connection
- Fast HNSW index for sub-second searches
"""

from typing import Dict, Any, List, Optional
import asyncio
from ..base_tool import BaseTool
from google.adk.tools import ToolContext, FunctionTool
from src.travel_lotara.tracking import trace_tool
from src.travel_lotara.config.logging_config import get_logger
import json

logger = get_logger(__name__)


class MilvusRetrievalTool(BaseTool):
    """Retrieves location recommendations from Milvus vector database."""
    
    name = "milvus_location_retrieval"
    description = "Retrieve Vietnam tourism location data from Milvus vector database based on user preferences and query"
    
    def run(self, query: str, top_k: int = 5, tool_context: Optional[ToolContext] = None) -> Dict[str, Any]:
        """
        Retrieve location data from Milvus (synchronous wrapper).
        
        Args:
            query: User query describing preferences, location, or interests
            top_k: Number of top locations to retrieve (default: 5)
            tool_context: Optional ADK tool context for state access
            
        Returns:
            Dict containing:
                - locations: List of location objects with full details
                - count: Number of locations returned
                - query: Original query used
        """
        # Check if we're in an async context
        try:
            loop = asyncio.get_running_loop()
            # We're in an async context - use run_in_executor to avoid blocking
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(self._run_sync, query, top_k, tool_context)
                return future.result(timeout=30)  # 30 second timeout
        except RuntimeError:
            # No running event loop - safe to use sync version
            return self._run_sync(query, top_k, tool_context)
        except Exception as e:
            # Log critical errors with full details
            logger.error(f"Milvus sync run failed: {type(e).__name__}: {str(e)}", exc_info=True)
            return {
                "locations": [],
                "count": 0,
                "query": query,
                "success": False,
                "error": f"{type(e).__name__}: {str(e)}"
            }
    
    def _run_sync(self, query: str, top_k: int = 5, tool_context: Optional[ToolContext] = None) -> Dict[str, Any]:
        """
        Synchronous implementation of location retrieval.
        
        This method uses the Milvus engine functions.
        """
        try:
            # Import the synchronous retrieval function from milvus_engine
            from .milvus_engine import recommend_locations
            
            # Get user profile context if available
            user_context = ""
            if tool_context and "user_profile" in tool_context.state:
                profile = tool_context.state["user_profile"]
                user_context = f"""
User Profile Context:
- Travel Style: {profile.get('travel_style', 'unknown')}
- Budget Range: {profile.get('budget_range', 'unknown')}
- Group Type: {profile.get('group_type', 'unknown')}
- Preferences: {json.dumps(profile.get('preferences', {}), ensure_ascii=False)}
"""
            
            # Combine query with user context
            full_query = f"{query}\n{user_context}" if user_context else query
            
            # Retrieve locations from Milvus (with caching)
            locations = recommend_locations(full_query, top_k=top_k)
            
            # Store in tool context state if available
            if tool_context:
                tool_context.state["milvus_retrieved_locations"] = locations
                tool_context.state["milvus_query"] = query
            
            result = {
                "locations": locations,
                "count": len(locations),
                "query": query,
                "success": True
            }
            
            return result
            
        except Exception as e:
            # Log critical errors with full details
            logger.error(f"Milvus retrieval failed: {type(e).__name__}: {str(e)}", exc_info=True)
            error_result = {
                "locations": [],
                "count": 0,
                "query": query,
                "success": False,
                "error": f"{type(e).__name__}: {str(e)}"
            }
            
            # Store error in context if available
            if tool_context:
                tool_context.state["milvus_error"] = str(e)
            
            return error_result


@trace_tool(name="milvus_location_retrieval", tags=["milvus", "retrieval", "locations"])
def retrieve_data_from_milvus(query: str, top_k: int = 5, tool_context: Optional[ToolContext] = None) -> Dict[str, Any]:
    """
    Retrieve location recommendations from Milvus cloud.
    
    Use this tool to get detailed Vietnam tourism location data based on user queries.
    Each location includes:
    - Location name, province, description, rating
    - Image (main location image URL)
    - Destinations (places to visit with budget, time, duration, and image_url for each place/cuisine)
    - Cuisine recommendations (restaurants with budget, duration, and image_url)
    - Hotels (with cost category, reviews, and image_url)
    - Activities list
    - Keywords for semantic understanding
    
    Args:
        query: Description of what the user is looking for (e.g., "beach destinations", 
               "cultural sites near Hanoi", "family-friendly activities")
        top_k: Number of locations to retrieve (default: 5, max recommended: 10)
        tool_context: Automatically provided by ADK framework
        
    Returns:
        Dictionary with retrieved locations and metadata
        
    Example:
        result = retrieve_data_from_milvus(
            query="relaxing beach destinations for families",
            top_k=3
        )
        locations = result["locations"]
    """
    tool = MilvusRetrievalTool()
    return tool.run(query=query, top_k=top_k, tool_context=tool_context)



# Create tool instance
milvus_retrieval_tool = FunctionTool(
    func=retrieve_data_from_milvus,
)


# Traced version for monitoring
@trace_tool("milvus_location_retrieval")
def milvus_location_retrieval(query: str, top_k: int = 5, tool_context: Optional[ToolContext] = None) -> Dict[str, Any]:
    """
    Traced wrapper for Milvus location retrieval.
    
    Args:
        query: Search query for locations
        top_k: Number of results to return
        tool_context: ADK tool context
        
    Returns:
        Dict with locations and metadata
    """
    tool = MilvusRetrievalTool()
    return tool.run(query, top_k, tool_context)
