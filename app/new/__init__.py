"""app.new package initialiser

Exports the status router added in status_fastapi.py so the main app
can import it as `from app.new import status_router` and include it.
"""

from .status_fastapi import router as status_router

__all__ = ["status_router"]
