import threading

# Thread-local storage for request entity context
_entity_context = threading.local()


def get_current_entity():
    """Get the current requesting entity from thread-local storage"""
    return getattr(_entity_context, "entity", None)


def set_current_entity(entity):
    """Set the current requesting entity in thread-local storage"""
    _entity_context.entity = entity


def clear_current_entity():
    """Clear the current requesting entity from thread-local storage"""
    if hasattr(_entity_context, "entity"):
        delattr(_entity_context, "entity")
