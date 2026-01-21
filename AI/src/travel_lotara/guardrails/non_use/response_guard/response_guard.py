class FinalResponseSchema:
    required_sections = [
        "day_by_day_itinerary",
        "logistics_summary",
        "tradeoffs"
    ]

    def validate(self, response: dict):
        for section in self.required_sections:
            if section not in response:
                raise ValueError(f"Missing section: {section}")
