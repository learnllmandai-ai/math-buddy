"""Session management helpers for MathBuddy."""


class SessionManager:
    """Simple session manager placeholder."""

    def __init__(self) -> None:
        self.session = {}

    def set(self, key: str, value: object) -> None:
        self.session[key] = value

    def get(self, key: str, default=None):
        return self.session.get(key, default)
