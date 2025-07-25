import logging

from linebot import LineBotApi
from linebot.models import (
    BoxComponent,
    BubbleContainer,
    ButtonComponent,
    FlexSendMessage,
    MessageAction,
    SeparatorComponent,
    TextComponent,
    TextSendMessage,
)

from src.bot import constants
from src.bot.utils.member_utils import validate_phone_format
from src.core.session.bind_session_store import BindSessionStore
from src.repos.member_repo import GoogleSheetMemberRepository
from src.services.member_service import MemberService

repo = GoogleSheetMemberRepository()
binding_session = BindSessionStore()
member_service = MemberService(repo)


def handle_waiting_name(line_id: str, name: str) -> TextSendMessage:
    binding_session.set_field(line_id, "name", name)
    binding_session.set_field(line_id, "step", "waiting_phone")
    return TextSendMessage(text="請輸入您的手機號碼\n例如：0912345678 或 0912-345-678")


@validate_phone_format
def handle_waiting_phone(line_id: str, phone: str) -> FlexSendMessage:
    binding_session.set_field(line_id, "phone", phone)
    binding_session.set_field(line_id, "step", "waiting_confirm")

    name = binding_session.get_session(line_id).get("name")

    return FlexSendMessage(
        alt_text="請確認您的綁定資訊",
        contents=BubbleContainer(
            body=BoxComponent(
                layout="vertical",
                contents=[
                    TextComponent(text="會員綁定資訊確認", weight="bold", size="lg"),
                    SeparatorComponent(margin="md"),
                    TextComponent(text=f"姓名：{name}", wrap=True, margin="md"),
                    TextComponent(text=f"電話：{phone}", wrap=True, margin="md"),
                    SeparatorComponent(margin="md"),
                    TextComponent(
                        text="請確認以上資訊是否正確：",
                        size="md",
                        color="#888888",
                        margin="sm",
                    ),
                ],
            ),
            footer=BoxComponent(
                layout="horizontal",
                spacing="md",
                contents=[
                    ButtonComponent(
                        style="primary",
                        color="#00C851",
                        action=MessageAction(label="正確", text="正確"),
                    ),
                    ButtonComponent(
                        style="primary",
                        color="#ff4444",
                        action=MessageAction(label="重新修正", text="重新修正"),
                    ),
                ],
            ),
        ),
    )


def handle_waiting_confirm(
    line_id: str, answer: str, line_bot_api: LineBotApi
) -> TextSendMessage:
    state = binding_session.get_session(line_id)

    if answer == "正確":
        name = state.get("name")
        phone = state.get("phone")

        try:
            profile = line_bot_api.get_profile(line_id)
            display_name = profile.display_name
        except Exception as e:
            logging.warning("無法取得使用者 LINE 資料：%s", str(e))
            return TextSendMessage(text="無法取得您的 LINE 名稱，請稍後再試")

        try:
            # Add member data
            _ = member_service.create_member(line_id, name, phone, display_name)

            # Clear binding_session storage
            binding_session.clear_session(line_id)
            logging.info("使用者 LINE 顯示名稱為：%s", display_name)
            return TextSendMessage(
                text=constants.Message.get("BIND_SUCESS", "").format(name=name)
            )
        except Exception:
            logging.exception("會員建立失敗")
            return TextSendMessage(text="資料儲存失敗，請稍後再試")
    elif answer == "重新修正":
        binding_session.start_session(line_id)
        return TextSendMessage(text="請重新輸入您的本名")
    else:
        return TextSendMessage(text="請輸入「是」或「否」來確認資訊是否正確")


def handle_binding_step(
    line_id: str, text: str, line_bot_api: LineBotApi
) -> TextSendMessage:
    step = binding_session.get_session(line_id).get("step")
    if step == "waiting_name":
        return handle_waiting_name(line_id, text)
    elif step == "waiting_phone":
        return handle_waiting_phone(line_id, text)
    elif step == "waiting_confirm":
        return handle_waiting_confirm(line_id, text, line_bot_api)
    else:
        binding_session.clear_session(line_id)
        return TextSendMessage(text="綁定流程異常，請輸入「綁定會員」重新開始")


def initiate_binding(line_id: str) -> TextSendMessage:
    binding_session.start_session(line_id)
    return TextSendMessage(text="請輸入您的本名")


def is_binding_session_active(line_id: str) -> bool:
    return binding_session.is_active(line_id)
