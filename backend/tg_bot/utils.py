import random


async def generate_code():
    return str(random.randint(100000, 999999))


def escape_markdown_v2(text: str) -> str:
    """Экранирует специальные символы для MarkdownV2"""
    replace_chars = "_[]()~>#+-=|{}.!"
    return "".join("" if c in replace_chars else c for c in text)


def get_user_link(name: str, id: int):
    name = escape_markdown_v2(name)
    if not name:
        name = "Пользователь"
    return f"[{name}](tg://user?id={id})"
