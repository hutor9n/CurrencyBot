import unittest
from unittest.mock import MagicMock

from controllers.common import close_inline_keyboard, safe_edit_message_reply_markup, safe_edit_message_text


class ControllerCommonTests(unittest.TestCase):
    def test_close_inline_keyboard_removes_reply_markup(self):
        bot = MagicMock()
        message = MagicMock()
        message.chat.id = 123
        message.message_id = 456

        close_inline_keyboard(bot, message)

        bot.edit_message_reply_markup.assert_called_once_with(
            chat_id=123,
            message_id=456,
            reply_markup=None,
        )

    def test_close_inline_keyboard_swallows_errors(self):
        bot = MagicMock()
        bot.edit_message_reply_markup.side_effect = RuntimeError("boom")
        message = MagicMock()
        message.chat.id = 123
        message.message_id = 456

        close_inline_keyboard(bot, message)

        bot.edit_message_reply_markup.assert_called_once()

    def test_safe_edit_message_text_returns_true_on_success(self):
        bot = MagicMock()
        message = MagicMock()
        message.chat.id = 123
        message.message_id = 456

        result = safe_edit_message_text(bot, message, "updated", parse_mode="HTML")

        self.assertTrue(result)
        bot.edit_message_text.assert_called_once_with(
            chat_id=123,
            message_id=456,
            text="updated",
            parse_mode="HTML",
        )

    def test_safe_edit_message_reply_markup_returns_false_on_error(self):
        bot = MagicMock()
        bot.edit_message_reply_markup.side_effect = RuntimeError("boom")
        message = MagicMock()
        message.chat.id = 123
        message.message_id = 456

        result = safe_edit_message_reply_markup(bot, message, reply_markup=None)

        self.assertFalse(result)
        bot.edit_message_reply_markup.assert_called_once_with(
            chat_id=123,
            message_id=456,
            reply_markup=None,
        )


if __name__ == "__main__":
    unittest.main()