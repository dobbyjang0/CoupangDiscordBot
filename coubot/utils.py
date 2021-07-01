from discord_slash.model import ButtonStyle
from discord_slash.utils.manage_components import create_button, create_actionrow


def pon_buttons():

    buttons = [
        create_button(
            style=ButtonStyle.secondary,
            emoji="✅",
            custom_id="true_btn"
        ),
        create_button(
            style=ButtonStyle.secondary,
            emoji="❌",
            custom_id="false_btn"
        )
    ]

    return create_actionrow(*buttons)
