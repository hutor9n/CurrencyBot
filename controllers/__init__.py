from telebot import TeleBot
from controllers.start_controller import register_start_controllers
from controllers.rates_controller import register_rates_controllers
from controllers.converter_controller import register_converter_controllers

def register_all_controllers(bot: TeleBot):
    register_start_controllers(bot)
    register_rates_controllers(bot)
    register_converter_controllers(bot)
