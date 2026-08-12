class HealthService:

    @staticmethod
    def get_health_status() -> dict:
        return {
            "status": "healthy",
            "service": "Marketing AI Agent",
        }