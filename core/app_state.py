"""Application state shared by the desktop controller and views."""

from dataclasses import dataclass


@dataclass
class AppState:
    """Mutable application state kept outside the Tkinter widget tree."""

    lang: str = "AR"
    current_cipher: str = "Caesar"
    current_theme_name: str = "Midnight"
    operations_count: int = 0
    crypto_busy: bool = False
    crypto_job_id: int = 0
    closing: bool = False
