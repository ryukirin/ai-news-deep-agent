from dataclasses import dataclass

@dataclass(frozen=True)
class MemoryContext:
    user_id: str = "local-user"