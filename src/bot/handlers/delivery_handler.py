from linebot.models import (
    BoxComponent,
    BubbleContainer,
    FlexSendMessage,
    SeparatorComponent,
    TextComponent,
)

from src.core.session.delivery_session_store import DeliverySessionStore
from src.repos.member_repo import GoogleSheetMemberRepository
from src.services.member_service import MemberService

delivery_session = DeliverySessionStore()
member_repo = GoogleSheetMemberRepository()
member_service = MemberService(member_repo)


def handle_check_quota(line_id: str):
    member = member_service.get_by_line_id(line_id)
    remain = member.remain_delivery
    balance = member.balance
    total_delivery_fee = member.total_delivery_fee

    # 計算需補繳金額（只顯示正的）
    need_to_pay = abs(balance) if balance < 0 else 0

    delivery_session.clear_session(line_id)

    return FlexSendMessage(
        alt_text="剩餘次數及餘額查詢",
        contents=BubbleContainer(
            body=BoxComponent(
                layout="vertical",
                contents=[
                    TextComponent(
                        text="剩餘次數及餘額查詢", weight="bold", size="lg", margin="md"
                    ),
                    SeparatorComponent(margin="md"),
                    TextComponent(
                        text=(f"剩餘配送次數：{remain} 次" if remain >= 0 else "剩餘配送次數：0 次"),
                        margin="md",
                    ),
                    TextComponent(
                        text=f"點數餘額：{balance if balance > 0 else 0} 點", margin="md"
                    ),
                    TextComponent(
                        text=(
                            f"需補繳訂單差額：${need_to_pay}"
                            if need_to_pay > 0
                            else "需補繳訂單差額：$0"
                        ),
                        margin="md",
                        color="#D32F2F" if need_to_pay > 0 else "#555555",
                    ),
                    TextComponent(
                        text=(
                            f"需繳交運費：${total_delivery_fee}"
                            if total_delivery_fee > 0
                            else "需繳交運費：$0"
                        ),
                        margin="md",
                        color="#D32F2F" if need_to_pay > 0 else "#555555",
                    ),
                ],
            )
        ),
    )
