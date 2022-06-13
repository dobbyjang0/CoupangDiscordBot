from index import bot

__all__ = (
    'ready',
)


async def ready() -> None:
    print("--- Success Login ---")
    print(bot.user.name)
