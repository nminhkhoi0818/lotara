"""
Python client example for consuming real-time progress events from Lotara API.

This demonstrates how to use SSE (Server-Sent Events) to get live updates
while the AI agents are generating an itinerary.
"""

import requests
import json
import time
from typing import Callable, Optional


class LotaraStreamClient:
    """
    Client for streaming real-time progress from Lotara Travel API.
    
    Usage:
        client = LotaraStreamClient(base_url="https://your-service.zeabur.app")
        
        def on_progress(event):
            print(f"[{event['type']}] {event['message']} - {event['progress']}%")
        
        result = client.generate_itinerary_stream(
            destination="Tokyo, Japan",
            days="medium",
            budget="medium",
            on_progress=on_progress
        )
        
        print(f"Final itinerary: {result['itinerary']['trip_name']}")
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize streaming client.
        
        Args:
            base_url: Base URL of the Lotara API
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = 300  # 5 minutes
    
    def generate_itinerary_stream(
        self,
        destination: str,
        days: str = "medium",
        budget: str = "medium",
        travel_style: str = "adventure",
        companions: str = "solo",
        interests: Optional[list] = None,
        user_id: Optional[str] = None,
        on_progress: Optional[Callable] = None,
        on_error: Optional[Callable] = None,
        on_complete: Optional[Callable] = None,
    ) -> dict:
        """
        Generate itinerary with real-time progress streaming.
        
        Args:
            destination: Destination city/country
            days: Duration (short/medium/long)
            budget: Budget level (low/medium/high)
            travel_style: Travel style preference
            companions: Who you're traveling with
            interests: List of interests
            user_id: Optional user ID
            on_progress: Callback for progress events (receives event dict)
            on_error: Callback for error events (receives error dict)
            on_complete: Callback for completion (receives final result dict)
        
        Returns:
            Final itinerary result dictionary
        
        Raises:
            requests.exceptions.RequestException: For network errors
            ValueError: For API errors
        """
        url = f"{self.base_url}/api/itinerary/generate-stream"
        
        # Prepare request payload
        payload = {
            "userId": user_id or f"client_{int(time.time())}",
            "destination": destination,
            "duration": days,
            "budget": budget,
            "travelStyle": travel_style,
            "companions": companions,
            "interests": interests or [travel_style]
        }
        
        print(f"🚀 Starting itinerary generation for {destination}...")
        print(f"📡 Streaming progress from: {url}")
        
        # Start streaming request
        response = requests.post(
            url,
            json=payload,
            headers={
                "Content-Type": "application/json",
                "Accept": "text/event-stream"
            },
            stream=True,
            timeout=self.timeout
        )
        
        if response.status_code != 200:
            error_msg = f"API returned status {response.status_code}: {response.text}"
            if on_error:
                on_error({"error": error_msg})
            raise ValueError(error_msg)
        
        # Parse SSE stream
        final_result = None
        current_event = None
        
        for line in response.iter_lines(decode_unicode=True):
            if not line:
                continue
            
            # Parse SSE format
            if line.startswith('event: '):
                current_event = line[7:].strip()
            elif line.startswith('data: '):
                data_str = line[6:].strip()
                
                try:
                    data = json.loads(data_str)
                    
                    # Handle different event types
                    if current_event == 'progress':
                        if on_progress:
                            on_progress(data)
                    
                    elif current_event == 'done':
                        final_result = data
                        if on_complete:
                            on_complete(data)
                        print(f"\n✅ Itinerary generation complete!")
                        break
                    
                    elif current_event == 'error':
                        if on_error:
                            on_error(data)
                        error_msg = data.get('error', 'Unknown error')
                        raise ValueError(f"API error: {error_msg}")
                    
                    elif current_event == 'cache_hit':
                        print(f"⚡ Cache hit! {data.get('message', 'Retrieved from cache')}")
                    
                    elif current_event in ['validation_failed', 'error_retry']:
                        print(f"⚠️  {data.get('message', 'Warning')}")
                        if on_progress:
                            on_progress(data)
                
                except json.JSONDecodeError as e:
                    print(f"⚠️  Failed to parse event data: {e}")
                    continue
        
        if final_result is None:
            raise ValueError("Stream ended without receiving final result")
        
        return final_result


def main():
    """Example usage of the streaming client"""
    
    # Initialize client
    client = LotaraStreamClient(
        base_url="http://localhost:8000"  # Change to your Zeabur URL
    )
    
    # Progress callback with visual indicators
    def on_progress(event):
        event_type = event.get('type', 'unknown')
        message = event.get('message', '')
        progress = event.get('progress', 0)
        
        # Add emoji based on event type
        emoji = {
            'started': '🎬',
            'agent_started': '🤖',
            'tool_call': '🔍',
            'tool_result': '✅',
            'model_call': '💭',
            'validation': '🔎',
            'completed': '✅',
            'warning': '⚠️',
            'error': '❌'
        }.get(event_type, '📝')
        
        # Print progress bar
        bar_length = 30
        filled = int(bar_length * progress / 100)
        bar = '█' * filled + '░' * (bar_length - filled)
        
        print(f"\r{emoji} [{bar}] {progress:3d}% | {message}", end='', flush=True)
        
        # Print details for important events
        if event_type in ['agent_started', 'tool_call', 'model_call']:
            print()  # New line for important events
    
    def on_error(error):
        print(f"\n❌ Error occurred: {error}")
    
    def on_complete(result):
        print(f"\n🎉 Success! Generated: {result['itinerary']['trip_name']}")
    
    # Generate itinerary with streaming
    try:
        result = client.generate_itinerary_stream(
            destination="Bangkok, Thailand",
            days="medium",
            budget="medium",
            travel_style="cultural",
            companions="couple",
            on_progress=on_progress,
            on_error=on_error,
            on_complete=on_complete
        )
        
        # Display summary
        itinerary = result['itinerary']
        print(f"\n{'='*60}")
        print(f"Trip Name: {itinerary['trip_name']}")
        print(f"Destination: {itinerary['destination']}")
        print(f"Duration: {itinerary['total_days']} days")
        print(f"Budget: {itinerary['average_budget_spend_per_day']}/day")
        print(f"Rating: ⭐ {itinerary['average_ratings']}/5")
        print(f"{'='*60}")
        
        print(f"\nDay-by-day summary:")
        for day in itinerary.get('trip_overview', []):
            print(f"  Day {day['trip_number']}: {day['summary']}")
        
        # Save to file
        output_file = f"itinerary_{int(time.time())}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Full itinerary saved to: {output_file}")
    
    except ValueError as e:
        print(f"\n❌ Failed to generate itinerary: {e}")
    except KeyboardInterrupt:
        print(f"\n\n⚠️  Interrupted by user")


if __name__ == "__main__":
    main()
