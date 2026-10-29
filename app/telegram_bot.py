import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from app.workflow import run_support_workflow

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to Customer Support!\n"
        "Describe your issue, and I'll connect you with the right specialist."
    )


async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    customer_message = (update.message.text or "").strip()

    if not customer_message:
        await update.message.reply_text(
            "Please send a message describing your issue."
        )
        return

    # Reuse the previous billing issue when the customer sends details.
    pending_issue = context.user_data.get("pending_billing_issue")

    if pending_issue:
        message_to_process = (
            f"Previous customer issue: {pending_issue}\n"
            f"Customer's follow-up details: {customer_message}"
        )
    else:
        message_to_process = customer_message

    waiting_message = await update.message.reply_text(
        "⏳ Your request is being analyzed. Please wait..."
    )

    try:
        import asyncio

        response = await asyncio.to_thread(
            run_support_workflow,
            message_to_process,
        )

        await waiting_message.edit_text(response)

        # Keep the conversation context if more billing information is needed.
        response_lower = response.lower()
        needs_more_info = (
            "what email address" in response_lower
            or "approximate transaction date" in response_lower
            or "amount you were charged" in response_lower
        )

        if needs_more_info:
            context.user_data["pending_billing_issue"] = message_to_process
        else:
            context.user_data.pop("pending_billing_issue", None)

    except Exception as error:
        print(f"Telegram support error: {error!r}")

        await waiting_message.edit_text(
            "Sorry, we couldn't process your request right now. "
            "Please try again later."
        )


def main():
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN is missing from your .env file."
        )

    application = (
        Application.builder()
        .token(TELEGRAM_BOT_TOKEN)
        .build()
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    print("Telegram support bot is starting...")
    application.run_polling()


if __name__ == "__main__":
    main()