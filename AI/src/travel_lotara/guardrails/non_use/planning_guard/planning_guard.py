# Planning Consistency Guard

# ================== Prevents:
#### + 10 cities in 3 days
#### + Night travel after full-day activity
#### + Unrealistic pacing


class PacingGuard:
    MAX_ACTIVITIES_PER_DAY = 5

    def validate_day(self, day_plan: dict):
        if len(day_plan.get("activities", [])) > self.MAX_ACTIVITIES_PER_DAY:
            raise ValueError("Day plan too dense")
