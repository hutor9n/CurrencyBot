def get_total_pages(items, items_per_page: int) -> int:
    return (len(items) + items_per_page - 1) // items_per_page


def close_inline_keyboard(bot, message):
    try:
        bot.edit_message_reply_markup(
            chat_id=message.chat.id,
            message_id=message.message_id,
            reply_markup=None,
        )
    except Exception:
        pass


def safe_edit_message_text(bot, message, text: str, **kwargs) -> bool:
    try:
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text=text,
            **kwargs,
        )
        return True
    except Exception:
        return False


def safe_edit_message_reply_markup(bot, message, reply_markup) -> bool:
    try:
        bot.edit_message_reply_markup(
            chat_id=message.chat.id,
            message_id=message.message_id,
            reply_markup=reply_markup,
        )
        return True
    except Exception:
        return False
