import logging
from datetime import datetime, timedelta
from typing import List, Union

from linebot import LineBotApi
from linebot.models import (
    BoxComponent,
    BubbleContainer,
    ButtonComponent,
    ButtonsTemplate,
    CarouselContainer,
    DatetimePickerTemplateAction,
    FlexSendMessage,
    ImageComponent,
    MessageAction,
    SeparatorComponent,
    TemplateSendMessage,
    TextComponent,
    TextSendMessage,
)

from src.bot import constants
from src.core.session.order_session_store import OrderSessionStore
from src.repos.member_repo import GoogleSheetMemberRepository
from src.repos.order_repo import GoogleSheetOrderRepository
from src.repos.product_repo import GoogleSheetProductRepository
from src.services.member_service import MemberService
from src.services.order_service import OrderService

order_session = OrderSessionStore()

member_repo = GoogleSheetMemberRepository()
member_service = MemberService(member_repo)

order_repo = GoogleSheetOrderRepository()
order_service = OrderService(order_repo)

product_repo = GoogleSheetProductRepository()


def handle_waiting_recipient(line_id: str, text: str) -> TextSendMessage:
    order_session.set_field(line_id, "recipient", text)
    order_session.set_field(line_id, "step", "waiting_address")
    return TextSendMessage(text="請輸入收件人地址")


def handle_waiting_address(line_id: str, text: str) -> FlexSendMessage:
    order_session.set_field(line_id, "address", text)
    order_session.set_field(line_id, "step", "confirm_address")

    return FlexSendMessage(
        alt_text="地址確認",
        contents=BubbleContainer(
            body=BoxComponent(
                layout="vertical",
                contents=[
                    TextComponent(text="收件地址確認", weight="bold", size="lg"),
                    SeparatorComponent(margin="md"),
                    TextComponent(
                        text=f"地址：{text}", wrap=True, margin="md", weight="bold"
                    ),
                    TextComponent(
                        text="請確認您的收件地址是否正確", margin="md", size="sm", color="#888888"
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
                        action=MessageAction(label="錯誤", text="錯誤"),
                    ),
                ],
            ),
        ),
    )


def handle_confirm_address(
    line_id: str, text: str
) -> FlexSendMessage | TextSendMessage:
    if text == "正確":
        order_session.set_field(line_id, "step", "waiting_orders")
        # 直接呼叫 handle_waiting_orders，讓使用者馬上看到分類字卡
        return handle_waiting_orders(line_id, text="")

    elif text == "錯誤":
        order_session.set_field(line_id, "step", "waiting_address")
        return TextSendMessage(text="請重新輸入正確的收件地址")

    return TextSendMessage(text="請點選【正確】來確認地址，或點選【錯誤】來重新修正")


def handle_waiting_orders(line_id: str, text: str) -> FlexSendMessage:
    products = product_repo.get_all()
    categories = sorted({p.category for p in products if p.category})  # 去除 None 與重複

    # 存分類到 session，後續使用
    order_session.set_field(line_id, "step", "waiting_category")

    # 為每個分類建立按鈕
    buttons = [
        ButtonComponent(
            action=MessageAction(label=category, text=f"分類：{category}"),
            style="primary",
            margin="sm",
        )
        for category in categories
    ]

    # 建立 Flex 訊息
    category_bubble = BubbleContainer(
        body=BoxComponent(
            layout="vertical",
            contents=[
                TextComponent(text="請選擇您要訂購的商品類別", weight="bold", size="md"),
                SeparatorComponent(margin="md"),
                *buttons,
            ],
        )
    )

    return FlexSendMessage(alt_text="選擇商品類別", contents=category_bubble)


# def handle_selected_category(
#     line_id: str, text: str
# ) -> Union[TextSendMessage, List[FlexSendMessage]]:
#     if not text.startswith("分類："):
#         return TextSendMessage(text="請從列表中選擇商品分類")

#     selected_category = text.replace("分類：", "").strip()
#     order_session.set_field(line_id, "step", "waiting_product")
#     order_session.set_field(line_id, "current_category", selected_category)

#     products = [p for p in product_repo.get_all() if p.category == selected_category]

#     if not products:
#         return TextSendMessage(text=f"⚠️『{selected_category}』目前無可訂購商品，請選擇其他分類")

#     bubbles = []
#     for product in products:
#         # ⬇️ 如果是希臘式濃縮優格，加兩個按鈕＋margin 控制距離
#         if selected_category == "希臘式濃縮優格":
#             footer_contents = [
#                 ButtonComponent(
#                     style="primary",
#                     action=MessageAction(
#                         label="加入自訂數量", text=f"加入自訂數量：{product.product_name}"
#                     ),
#                 ),
#                 ButtonComponent(
#                     style="primary",
#                     action=MessageAction(
#                         label="購買一盒（12入）", text=f"加入一盒：{product.product_name}"
#                     ),
#                     margin="sm",  # 👈 控制兩個按鈕之間的距離
#                 ),
#             ]
#         else:
#             footer_contents = [
#                 ButtonComponent(
#                     style="primary",
#                     action=MessageAction(
#                         label="加入自訂數量", text=f"加入自訂數量：{product.product_name}"
#                     ),
#                 )
#             ]

#         bubble = BubbleContainer(
#             body=BoxComponent(
#                 layout="vertical",
#                 contents=[
#                     TextComponent(text=product.product_name, weight="bold", size="lg"),
#                     TextComponent(text=f"價格：${product.price}", margin="md"),
#                     SeparatorComponent(margin="md"),
#                     TextComponent(
#                         text="點選下方加入訂購", size="sm", color="#888888", margin="md"
#                     ),
#                 ],
#             ),
#             footer=BoxComponent(
#                 layout="vertical",
#                 contents=footer_contents,
#             ),
#         )
#         bubbles.append(bubble)

#     carousel_message = FlexSendMessage(
#         alt_text=f"{selected_category} 商品選單",
#         contents=CarouselContainer(contents=bubbles),
#     )

#     confirm_message = FlexSendMessage(
#         alt_text="完成此分類選購？",
#         contents=BubbleContainer(
#             body=BoxComponent(
#                 layout="vertical",
#                 contents=[
#                     TextComponent(
#                         text=f"是否完成『{selected_category}』的選購？", weight="bold", size="md"
#                     ),
#                     TextComponent(
#                         text="您可以繼續選購商品，最後再點選「完成」來完成此分類選購",
#                         wrap=True,
#                         margin="md",
#                         size="sm",
#                         color="#888888",
#                     ),
#                 ],
#             ),
#             footer=BoxComponent(
#                 layout="horizontal",
#                 spacing="md",
#                 contents=[
#                     ButtonComponent(
#                         style="primary",
#                         color="#00C851",
#                         action=MessageAction(
#                             label="完成選購", text=f"完成：{selected_category}"
#                         ),
#                     ),
#                 ],
#             ),
#         ),
#     )

#     return [carousel_message, confirm_message]


def handle_selected_category(
    line_id: str, text: str
) -> Union[TextSendMessage, List[FlexSendMessage]]:
    if not text.startswith("分類："):
        return TextSendMessage(text="請從列表中選擇商品分類")

    selected_category = text.replace("分類：", "").strip()
    order_session.set_field(line_id, "step", "waiting_product")
    order_session.set_field(line_id, "current_category", selected_category)

    products = [p for p in product_repo.get_all() if p.category == selected_category]

    if not products:
        return TextSendMessage(text=f"⚠️『{selected_category}』目前無可訂購商品，請選擇其他分類")

    bubbles = []
    for product in products:
        product_name = product.product_name
        image_url = constants.URL.get(product_name)  # 取出圖片 URL（可能為 None）

        # 設定 footer 按鈕
        if selected_category == "希臘式濃縮優格":
            footer_contents = [
                ButtonComponent(
                    style="primary",
                    action=MessageAction(label="加入自訂數量", text=f"加入自訂數量：{product_name}"),
                ),
                ButtonComponent(
                    style="primary",
                    action=MessageAction(
                        label="購買一盒（12入）", text=f"加入一盒：{product_name}"
                    ),
                    margin="sm",
                ),
            ]
        else:
            footer_contents = [
                ButtonComponent(
                    style="primary",
                    action=MessageAction(label="加入自訂數量", text=f"加入自訂數量：{product_name}"),
                )
            ]

        # 建立 bubble
        bubble = BubbleContainer(
            hero=ImageComponent(
                url=image_url, size="md", aspect_ratio="1:1", aspect_mode="fit"
            )
            if image_url
            else None,
            body=BoxComponent(
                layout="vertical",
                contents=[
                    TextComponent(text=product_name, weight="bold", size="lg"),
                    TextComponent(text=f"價格：${product.price}", margin="md"),
                    SeparatorComponent(margin="md"),
                    TextComponent(
                        text="點選下方加入訂購", size="sm", color="#888888", margin="md"
                    ),
                ],
            ),
            footer=BoxComponent(
                layout="vertical",
                contents=footer_contents,
            ),
        )
        bubbles.append(bubble)

    carousel_message = FlexSendMessage(
        alt_text=f"{selected_category} 商品選單",
        contents=CarouselContainer(contents=bubbles),
    )

    confirm_message = FlexSendMessage(
        alt_text="完成此分類選購？",
        contents=BubbleContainer(
            body=BoxComponent(
                layout="vertical",
                contents=[
                    TextComponent(
                        text=f"是否完成『{selected_category}』的選購？", weight="bold", size="md"
                    ),
                    TextComponent(
                        text="您可以繼續選購商品，最後再點選「完成」來完成此分類選購",
                        wrap=True,
                        margin="md",
                        size="sm",
                        color="#888888",
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
                        action=MessageAction(
                            label="完成選購", text=f"完成：{selected_category}"
                        ),
                    ),
                ],
            ),
        ),
    )

    return [carousel_message, confirm_message]


def handle_select_quantity(line_id: str, text: str) -> TextSendMessage:
    state = order_session.get_session(line_id)
    current_product = state.get("current_product")

    # 防止使用者未先點選商品就直接輸入數字
    if not current_product:
        return TextSendMessage(text="⚠️ 請先選擇要訂購的商品，再輸入數量")

    try:
        quantity = int(text)
        if not (1 <= quantity <= 99):
            raise ValueError("超出數量範圍")

        # 儲存到訂單暫存
        current_orders = state.get("orders", {})
        current_orders[current_product] = quantity
        order_session.set_field(line_id, "orders", current_orders)

        # 清除 current_product，避免錯誤重複輸入
        order_session.set_field(line_id, "current_product", None)

        return TextSendMessage(
            text=f"✅ 已將「{current_product}」{quantity}瓶加入訂購。\n\n您可以繼續選擇其他商品，或點擊上方按鈕【完成選購】來完成此類別選購。"
        )
    except Exception:
        return TextSendMessage(text="⚠️ 請輸入正確的數量（1～99）")


def handle_finish_category(
    line_id: str, text: str
) -> List[FlexSendMessage] | TextSendMessage:
    if not text.startswith("完成："):
        return TextSendMessage(text="請從選單中點選完成按鈕")

    text.replace("完成：", "").strip()

    # 取得已訂購項目
    state = order_session.get_session(line_id)
    orders = state.get("orders", {})

    if not orders:
        # 沒有訂購商品 → 回到商品類別選單
        order_session.set_field(line_id, "step", "waiting_orders")
        return [
            TextSendMessage(text="⚠️ 目前尚未有任何訂購商品，請先選擇商品進行訂購。"),
            handle_waiting_orders(line_id, ""),
        ]

    # 有商品 → 顯示結算與是否加購
    order_session.set_field(line_id, "step", "waiting_finish_category")

    product_list = product_repo.get_all()
    product_map = {p.product_name: p for p in product_list}

    product_lines = []
    total_price = 0
    for name, qty in orders.items():
        product = product_map.get(name)
        if product:
            subtotal = product.price * qty
            total_price += subtotal
            product_lines.append(
                TextComponent(
                    text=f"• {name} x {qty}瓶 = ${subtotal}",
                    size="md",
                    wrap=True,
                    margin="sm",
                )
            )

    summary_bubble = FlexSendMessage(
        alt_text="目前訂購清單",
        contents=BubbleContainer(
            body=BoxComponent(
                layout="vertical",
                contents=[
                    TextComponent(text="訂購商品總覽", weight="bold", size="lg"),
                    SeparatorComponent(margin="md"),
                    *product_lines,
                    SeparatorComponent(margin="md"),
                    TextComponent(
                        text=f"總計金額：${total_price}",
                        weight="bold",
                        size="md",
                        margin="md",
                    ),
                ],
            )
        ),
    )

    confirm_bubble = FlexSendMessage(
        alt_text="是否要繼續訂購其他類別商品？",
        contents=BubbleContainer(
            body=BoxComponent(
                layout="vertical",
                contents=[
                    TextComponent(text="加購其他商品", weight="bold", size="lg"),
                    TextComponent(text="是否還要訂購其他類別的商品？", margin="md"),
                ],
            ),
            footer=BoxComponent(
                layout="horizontal",
                spacing="md",
                contents=[
                    ButtonComponent(
                        style="primary",
                        action=MessageAction(label="完成商品選購", text="完成商品選購"),
                    ),
                    ButtonComponent(
                        style="secondary",
                        action=MessageAction(label="繼續選購", text="繼續選購"),
                    ),
                ],
            ),
        ),
    )

    return [summary_bubble, confirm_bubble]


def handle_selected_date(line_id: str, date_str: str) -> FlexSendMessage:
    order_session.set_field(line_id, "desired_date", date_str)
    order_session.set_field(line_id, "step", "waiting_confirm")

    session = order_session.get_session(line_id)
    recipient = session.get("recipient", "")
    address = session.get("address", "")
    orders = session.get("orders", {})
    desired_date = session.get("desired_date", "")

    product_list = product_repo.get_all()
    product_map = {p.product_name: p for p in product_list}

    order_summary_components = [TextComponent(text="商品：", margin="md")]
    total_price = 0
    for name, qty in orders.items():
        product = product_map.get(name)
        if product:
            subtotal = product.price * qty
            total_price += subtotal
            order_summary_components.append(
                TextComponent(text=f"• {name} x {qty}瓶", wrap=True, margin="md")
            )

    return FlexSendMessage(
        alt_text="請確認訂單資訊",
        contents=BubbleContainer(
            body=BoxComponent(
                layout="vertical",
                contents=[
                    TextComponent(text="訂單確認", weight="bold", size="lg"),
                    SeparatorComponent(margin="md"),
                    TextComponent(text=f"收件人：{recipient}", wrap=True, margin="md"),
                    TextComponent(text=f"地址：{address}", wrap=True, margin="md"),
                    *order_summary_components,
                    TextComponent(
                        text=f"期望收貨日期：{desired_date}", wrap=True, margin="md"
                    ),
                    TextComponent(  # 🔽 額度扣除這一行
                        text=f"額度扣除：${total_price}",
                        wrap=True,
                        margin="md",
                        weight="bold",
                    ),
                    SeparatorComponent(margin="md"),
                    TextComponent(
                        text="請點選下方按鈕確認是否送出：", size="sm", color="#888888", margin="md"
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
                        action=MessageAction(label="是", text="是"),
                    ),
                    ButtonComponent(
                        style="primary",
                        color="#ff4444",
                        action=MessageAction(label="否", text="否"),
                    ),
                ],
            ),
        ),
    )


def handle_waiting_desired_date(line_id: str) -> TemplateSendMessage:
    order_session.set_field(line_id, "step", "waiting_confirm")

    return TemplateSendMessage(
        alt_text="請選擇期望收貨日期",
        template=ButtonsTemplate(
            title="請選擇期望收貨日期",
            text="點選下方按鈕選擇日期",
            actions=[
                DatetimePickerTemplateAction(
                    label="選擇日期",
                    data=f"action=select_date&line_id={line_id}",
                    mode="date",  # 也可以是 "time" 或 "datetime"
                    initial=(datetime.today() + timedelta(days=7)).strftime("%Y-%m-%d"),
                    min=(datetime.today() + timedelta(days=7)).strftime("%Y-%m-%d"),
                    max=(datetime.today() + timedelta(days=14)).strftime("%Y-%m-%d"),
                )
            ],
        ),
    )


def handle_waiting_confirm(
    line_id: str, answer: str, line_bot_api: LineBotApi
) -> TextSendMessage:
    session = order_session.get_session(line_id)  # ✅ 一開始就要寫
    # ⛔ 若未選擇日期就點選「是」，提示並重新要求選擇日期
    if session.get("desired_date") is None:
        order_session.set_field(line_id, "step", "waiting_desired_date")
        return [
            TextSendMessage(text="⚠️ 尚未選擇期望收貨日期，請在下方重新選擇"),
            handle_waiting_desired_date(line_id),
        ]

    if answer == "是":
        try:
            session = order_session.get_session(line_id)
            recipient = session.get("recipient")
            address = session.get("address")
            orders = session.get("orders")

            desired_date = datetime.strptime(session.get("desired_date"), "%Y-%m-%d")

            name_to_pid, product_map = get_product_lookup()
            converted_orders = {}
            for name, qty in orders.items():
                pid = name_to_pid.get(name)
                if not pid:
                    raise ValueError(f"找不到商品名稱：{name}")
                converted_orders[pid] = qty

            # Create an order
            created_order = order_service.create_order(
                line_id=line_id,
                recipient=recipient,
                address=address,
                orders=converted_orders,
                payment_method="LINE",
                desired_date=desired_date,
                product_map=product_map,
            )

            order_session.clear_session(line_id)

            # 建立商品清單區塊
            product_lines = []
            for pid, qty in created_order.orders.items():
                product = product_map.get(pid)
                if product:
                    product_lines.append(
                        TextComponent(
                            text=f"• {product.product_name} x {qty}瓶",
                            size="md",
                            wrap=True,
                            margin="sm",  # 加入這一行
                        )
                    )

            # 訂單詳情 Bubble
            order_detail_bubble = BubbleContainer(
                body=BoxComponent(
                    layout="vertical",
                    contents=[
                        TextComponent(text="訂單詳情", weight="bold", size="lg"),
                        SeparatorComponent(margin="md"),
                        TextComponent(
                            text=f"訂單編號：{str(created_order.order_id)[:5]}",
                            wrap=True,
                            margin="md",
                        ),
                        TextComponent(
                            text=f"收件人姓名：{created_order.recipient}",
                            wrap=True,
                            margin="md",
                        ),
                        TextComponent(
                            text=f"地址：{created_order.address}", wrap=True, margin="md"
                        ),
                        TextComponent(text="配送內容：", margin="md"),
                        *product_lines,  # 若太擠可以考慮在 product_lines 中的每一項也加上 margin
                        TextComponent(
                            text=f"額度扣除：${created_order.order_fee}",
                            margin="md",
                            wrap=True,
                        ),
                        TextComponent(
                            text=f"訂購日期：{created_order.order_date.strftime('%Y-%m-%d')}",
                            margin="md",
                            wrap=True,
                        ),
                        TextComponent(
                            text=f"期望收貨日期：{created_order.desired_date.strftime('%Y-%m-%d')}",
                            margin="md",
                            wrap=True,
                        ),
                    ],
                )
            )

            return [
                TextSendMessage(text="訂單已建立成功！謝謝您的訂購。"),
                FlexSendMessage(alt_text="訂單詳情", contents=order_detail_bubble),
            ]

        except Exception:
            logging.exception("訂單建立失敗")
            return TextSendMessage(text="訂單建立失敗，請稍後再試")

    elif answer == "否":
        # 重新啟動 session，但只清除商品相關欄位，保留收件人與地址
        session = order_session.get_session(line_id)
        order_session.set_field(line_id, "orders", {})
        order_session.set_field(line_id, "step", "waiting_orders")
        order_session.set_field(line_id, "desired_date", None)

        return [
            TextSendMessage(text="請重新選擇訂購項目"),
            handle_waiting_orders(line_id, text=""),  # 直接跳回商品類別選單
        ]

    else:
        return TextSendMessage(text="請點選上方的【是】或【否】按鈕以完成確認")


def handle_order_step(
    line_id: str, text: str, line_bot_api: LineBotApi
) -> TextSendMessage | FlexSendMessage:
    step = order_session.get_session(line_id).get("step")

    print(f"[DEBUG] step: {step}, text: {text}")  # 可協助除錯

    if step == "waiting_recipient":
        return handle_waiting_recipient(line_id, text)
    elif step == "waiting_address":
        return handle_waiting_address(line_id, text)
    elif step == "confirm_address":
        return handle_confirm_address(line_id, text)
    elif step == "waiting_orders":
        return handle_waiting_orders(line_id, text)
    elif step == "waiting_category":
        return handle_selected_category(line_id, text)
    elif step == "waiting_product":
        if text.startswith("加入自訂數量："):
            current_product = text.replace("加入自訂數量：", "").strip()
            order_session.set_field(line_id, "current_product", current_product)
            return TextSendMessage(text=f"請輸入『{current_product}』的訂購數量（1～99）")
        elif text.startswith("加入一盒："):
            current_product = text.replace("加入一盒：", "").strip()
            order_session.set_field(line_id, "current_product", current_product)
            return handle_select_quantity(line_id, text="12")  # 直接使用 12 當作數量
        elif text.startswith("完成："):
            return handle_finish_category(line_id, text)
        else:
            return handle_select_quantity(line_id, text)
    elif step == "waiting_finish_category":
        if text == "完成商品選購":
            return handle_waiting_desired_date(line_id)
        elif text == "繼續選購":
            return handle_waiting_orders(line_id, "")
        else:
            return TextSendMessage(text="請點選【完成商品選購】來完成所有商品選購，或是點選【繼續選購】來繼續選購商品")
    elif step == "waiting_desired_date":
        return handle_waiting_desired_date(line_id)
    elif step == "waiting_confirm":
        return handle_waiting_confirm(line_id, text, line_bot_api)
    else:
        order_session.clear_session(line_id)
        return TextSendMessage(text="訂單流程異常，請輸入【預約訂購】重新開始")


def initiate_order(line_id: str) -> TextSendMessage:
    order_session.start_session(line_id)
    return TextSendMessage(text="請輸入收件人姓名")


def is_order_session_active(line_id: str) -> bool:
    return order_session.is_active(line_id)


def get_product_lookup():
    product_list = product_repo.get_all()
    name_to_pid = {p.product_name: p.product_id for p in product_list}
    product_map = {p.product_id: p for p in product_list}
    return name_to_pid, product_map
