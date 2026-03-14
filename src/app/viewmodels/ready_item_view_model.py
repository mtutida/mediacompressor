from dataclasses import dataclass, field
from uuid import UUID, uuid4
from datetime import datetime

@dataclass(frozen=True)
class ReadyItemViewModel:
    """
    Presentation-layer ViewModel representing a READY state item.
    Identity is immutable and generated at creation time.
    No business logic.
    No threading.
    No engine interaction.
    """
    stable_id: UUID = field(default_factory=uuid4)
    source_path: str = ""
    output_path: str = ""
    preset_snapshot: object = None
    created_at: datetime = field(default_factory=datetime.utcnow)
