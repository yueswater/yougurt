from linebot.models import (
    BoxComponent,
    BubbleContainer,
    ButtonComponent,
    FlexSendMessage,
    TextComponent,
    URIAction,
)


def handle_contact_us() -> FlexSendMessage:
    bubble = BubbleContainer(
        body=BoxComponent(
            layout="vertical",
            contents=[
                TextComponent(
                    text="您好 👋 感謝您聯絡我們",
                    weight="bold",
                    size="md",
                ),
                TextComponent(text="請點擊下方按鈕聯絡品菓客服", color="#888888", margin="md"),
            ],
        ),
        footer=BoxComponent(
            layout="vertical",
            contents=[
                ButtonComponent(
                    action=URIAction(
                        label="聯絡品菓客服", uri="https://line.me/R/ti/p/@mew5489a"
                    ),
                    style="primary",
                )
            ],
        ),
    )
    return FlexSendMessage(alt_text="聯絡品菓客服", contents=bubble)
