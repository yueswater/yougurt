import logging

from linebot.models import (
    BoxComponent,
    BubbleContainer,
    ButtonComponent,
    FlexSendMessage,
    ImageSendMessage,
    MessageAction,
    SeparatorComponent,
    TextComponent,
    TextSendMessage,
)

from src.core.session.purchase_session_store import PurchaseSessionStore
from src.repos.member_repo import GoogleSheetMemberRepository
from src.services.member_service import MemberService

repo = GoogleSheetMemberRepository()
purchase_session = PurchaseSessionStore()
member_service = MemberService(repo)

# Step 1: 使用者點選「年購方案」


def handle_annual_purchase_start(line_id: str):
    if not member_service.exists(line_id):
        return TextSendMessage(text="⚠️ 您尚未綁定會員，請先完成會員綁定後再使用年購方案功能。")

    purchase_session.start_session(line_id)
    purchase_session.set_field(line_id, "step", "waiting_bank_account")

    return [
        TextSendMessage(
            text="📢 請匯款至以下帳戶：\n\n台灣銀行（代碼 004）\n帳號：123-456-789-012\n戶名：優格好好"
        ),
        ImageSendMessage(
            original_content_url="https://example.com/bank_info.jpg",
            preview_image_url="https://example.com/bank_info.jpg",
        ),
        TextSendMessage(text="✅ 匯款完成後，請輸入您帳戶的末五碼："),
    ]


# Step 2: 使用者輸入末五碼


def handle_waiting_bank_account(line_id: str, text: str):
    if not (text.isdigit() and len(text) == 5):
        return TextSendMessage(text="❌ 請輸入正確的帳戶末五碼（5 位數字）")

    purchase_session.set_field(line_id, "bank_account", text)
    purchase_session.set_field(line_id, "step", "waiting_purchase_confirm")

    return FlexSendMessage(
        alt_text="請確認匯款末五碼",
        contents=BubbleContainer(
            body=BoxComponent(
                layout="vertical",
                contents=[
                    TextComponent(text="請確認您的匯款資訊", weight="bold", size="lg"),
                    SeparatorComponent(margin="md"),
                    TextComponent(text=f"您輸入的帳戶末五碼為：{text}", wrap=True, margin="md"),
                    TextComponent(text="是否正確？", margin="md"),
                ],
            ),
            footer=BoxComponent(
                layout="horizontal",
                contents=[
                    ButtonComponent(
                        style="primary",
                        color="#00C851",
                        action=MessageAction(label="是", text="是"),
                    ),
                    ButtonComponent(
                        style="secondary",
                        color="#ff4444",
                        action=MessageAction(label="否", text="否"),
                    ),
                ],
            ),
        ),
    )


# Step 3: 使用者點選「是」或「否」


def handle_waiting_purchase_confirm(line_id: str, answer: str):
    if answer == "是":
        bank_account = purchase_session.get_session(line_id).get("bank_account")
        try:
            member_service.update_fields_by_line_id(
                line_id=line_id, updates={"bank_account": bank_account}
            )
            purchase_session.clear_session(line_id)
            return TextSendMessage(text="✅ 年購方案已確認完成，感謝您的匯款！")
        except Exception:
            logging.exception("年購方案儲存失敗")
            return TextSendMessage(text="❌ 處理失敗，請稍後再試一次。")

    elif answer == "否":
        purchase_session.set_field(line_id, "step", "waiting_bank_account")
        return TextSendMessage(text="請重新輸入您帳戶的末五碼：")

    else:
        return TextSendMessage(text="請點選下方的「是」或「否」。")
