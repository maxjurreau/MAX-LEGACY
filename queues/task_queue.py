"""
Task queue abstraction for background tasks.
Same structure as event_queue; separated for clarity.
"""

from .event_queue import EventQueue

class TaskQueue(EventQueue):
    pass
