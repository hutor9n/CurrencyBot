from handlers.start import register_start_handlers
from handlers.current_rates import register_current_rates_handlers
from handlers.converter import register_converter_handlers

def register_all_handlers():
    """Реєструє всі хендлери для команд та повідомлень."""
    register_start_handlers()
    register_current_rates_handlers()
    register_converter_handlers()
