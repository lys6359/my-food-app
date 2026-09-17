import streamlit as st
import urllib.parse
import random
import os
from datetime import datetime

# 1. 網頁基本設定
st.set_page_config(page_title="MY AI 網頁點餐系統", page_icon="🍔", layout="wide")

# 利用 CSS 注入，將背景改成高級明亮黃與深灰色調
st.markdown("""
    <style>
    .stApp {
        background-color: #FBBF24; 
        color: #1F2937 !important;
    }
    h1, h2 {
        color: #000000 !important;
        font-weight: 800 !important;
    }
    [data-testid="stContainer"] {
        background-color: #1F2937 !important; 
        border-radius: 16px !important;
        padding: 20px !important;
        border: none !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
        margin-bottom: 15px !important;
    }
    [data-testid="stContainer"] .stMarkdown p, [data-testid="stContainer"] h3 {
        color: #FFFFFF !important;
    }
    [data-testid="stContainer"] button {
        background-color: #FBBF24 !important;
        color: #000000 !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        border: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# 老闆專用控制台：True = 正常營業 | False = 店鋪打烊
IS_OPEN = True 

if not IS_OPEN:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    with st.container():
        st.markdown("<h1 style='text-align: center; color: #FBBF24 !important;'>🌙 店鋪休息中 / Closed</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-size: 18px; color: #FFFFFF !important;'>謝謝您的光臨！我們目前的營業時間已結束，明天請早喔！🙏</p>", unsafe_allow_html=True)
    st.stop() 

# 初始化 Session State
if "new_cart" not in st.session_state:
    st.session_state.new_cart = {}

if "order_id" not in st.session_state:
    st.session_state.order_id = f"MY-{random.randint(1000, 9999)}"

# 🌟 初始化老闆後台的訂單歷史資料庫
if "order_history" not in st.session_state:
    st.session_state.order_history = []

# 🌟 側邊欄密碼驗證切換後台
st.sidebar.title("🛠️ 管理員選單")
admin_password = st.sidebar.text_input("🔑 輸入老闆登入密碼", type="password")
is_admin_mode = (admin_password == "boss6359")

if is_admin_mode:
    # ==================== 【📊 老闆後台管理面板】 ====================
    st.title("📊 老闆專屬後台管理面板 (Admin Dashboard)")
    st.sidebar.success("🔓 已成功登入老闆後台！")
    st.write("您可以在這裡即時查看顧客點單明細、核對金流與統計今日營業額。")
    
    if not st.session_state.order_history:
        st.info("📭 目前還沒有收到任何顧客的訂單喔！當顧客在前台點擊送出後，訂單會自動同步到這裡。")
    else:
        total_orders = len(st.session_state.order_history)
        sales_sum = sum(order["total_amount"] for order in st.session_state.order_history)
        
        stat_col1, stat_col2 = st.columns(2)
        with stat_col1:
            st.metric(label="📈 今日總訂單量", value=f"{total_orders} 單")
        with stat_col2:
            st.metric(label="💰 今日總營業額", value=f"RM {sales_sum:.2f}")
            
        st.write("---")
        st.subheader("📋 即時訂單明細列表")
        
        for i, order in enumerate(st.session_state.order_history):
            with st.expander(f"📋 單號：{order['id']} | 時間：{order['time']} | 狀態：【{order['status']}】", expanded=True):
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown(f"**🥡 用餐方式**：{order['dining_type']}")
                    st.markdown(f"**💳 付款方式**：{order['pay_method']}")
                    st.markdown(f"**💰 結帳總額**：RM {order['total_amount']:.2f}")
                    st.markdown(f"**📝 訂單備註**：{order['note']}")
                with col_b:
                    st.markdown(f"**🛒 點餐品項明細**：")
                    st.text(order['details'])
                    
                    new_status = st.selectbox(
                        "變更訂單狀態",
                        ["待核對金流", "製作中", "配送/取餐中", "已完成", "已取消"],
                        index=["待核對金流", "製作中", "配送/取餐中", "已完成", "已取消"].index(order['status']),
                        key=f"status_{order['id']}_{i}"
                    )
                    if new_status != order['status']:
                        st.session_state.order_history[i]['status'] = new_status
                        st.toast(f"單號 {order['id']} 狀態已更新為：{new_status}")
                        st.rerun()
else:
    # ==================== 【🛒 顧客點餐前台（完全回歸你原本的程式碼結構）】 ====================
    st.title("🍔 我的馬來西亞在地點餐系統")
    st.write("歡迎光臨！請在下方選擇您的餐點。結帳後將引導至 WhatsApp 發送訂單給老闆喔！")

    dining_type = st.radio(
        "🥡 請選擇您的用餐方式：", 
        ["內用 🍽️", "外帶 🛍️", "外送 / 食物配送 🚗"], 
        horizontal=True,
        index=None
    )

    menu = {
        "特級牛肉漢堡 🍔": 18.00,
        "招牌炸雞排 🍗": 15.00,
        "珍珠奶茶 🧋": 9.50,
        "黃金薯條 🍟": 7.00
    }

    CURRENCY = "RM"
    MY_PHONE_NUMBER = "60109456359"

    # 3. 建立兩欄網頁排版
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("【 🍱 今日菜單 】")
        
        if dining_type is None:
            st.error("⚠️ 請在網頁最上方先選擇您的「用餐方式」，才可以開始點餐喔！")
            is_menu_disabled = True
        else:
            is_menu_disabled = False

        for food, price in menu.items():
            with st.container():
                st.markdown(f"### {food}")
                st.markdown(f"💰 價格：**{CURRENCY} {price:.2f}**")
                
                if "珍珠奶茶" in food:
                    ice = st.selectbox("🧊 選擇冰塊", ["正常冰", "少冰", "微冰", "去冰"], key="ice_select")
                    sugar = st.selectbox("🍬 選擇甜度", ["正常甜", "少糖(7分)", "半糖(5分)", "微糖(3分)", "無糖"], key="sugar_select")
                    full_food_name = f"{food} ({ice}/{sugar})"
                else:
                    spicy = st.selectbox("🌶️ 辣度選擇", ["不辣", "微辣", "中辣", "大辣"], key=f"spicy_{food}")
                    full_food_name = f"{food} ({spicy})"
                    
                if st.button(f"➕ 點購 {food}", key=f"btn_{food}", disabled=is_menu_disabled):
                    if full_food_name in st.session_state.new_cart:
                        st.session_state.new_cart[full_food_name] += 1
                    else:
                        st.session_state.new_cart[full_food_name] = 1
                    st.toast(f"已加入購物車！")
                    st.rerun()

    with col2:
        st.subheader("【 🛒 您的購物車 】")
        
        display_type = dining_type if dining_type else "⚠️ 尚未選擇"
        st.markdown(f"✨ 目前選擇：**{display_type}** | 🔢 訂單單號：**{st.session_state.order_id}**") 
        
        delivery_address = ""
        table_number = ""
        
        if dining_type == "外送 / 食物配送 🚗":
            delivery_address = st.text_input("🏠 請輸入您的完整外送地址 (Delivery Address)：")
        elif dining_type == "內用 🍽️":
            table_number = st.text_input("🔢 請輸入您的桌號 (Table Number)：")
        
        if not st.session_state.new_cart:
            st.write("購物車目前是空的喔！")
            total = 0
        else:
            total = 0
            st.write("---")
            
            # 用於記錄要發送的純文字清單明細
            items_summary_text = ""
            
            for food_info, qty in list(st.session_state.new_cart.items()):
                item_price = 0.0
                for menu_key in menu:
                    if menu_key in food_info:
                        item_price = menu[menu_key]
                        break
                item_total = item_price * qty
                total += item_total
                
                items_summary_text += f"- {food_info} x {qty} ({CURRENCY} {item_total:.2f})\n"
                
                cart_col1, cart_col2, cart_col3 = st.columns(3)
                with cart_col1:
                    st.write(f"▪️ **{food_info}** x {qty}")
                with cart_col2:
                    if st.button("➖", key=f"minus_{food_info}"):
                        st.session_state.new_cart[food_info] -= 1
                        if st.session_state.new_cart[food_info] <= 0:
                            del st.session_state.new_cart[food_info]
                        st.rerun()
                with cart_col3:
                    if st.button("➕", key=f"plus_{food_info}"):
                        st.session_state.new_cart[food_info] += 1
                        st.rerun()
                        
            st.write("---")
            
            order_note = st.text_input("📝 訂單備註（例如：飯少、薯條不加鹽）")
            coupon = st.text_input("🏷️ 輸入折扣碼 (提示: VIP90 )")
            
            if coupon == "VIP90":
                discount = total * 0.1
                final_total = total - discount
                st.info(f"🎉 成功套用 9 折折扣碼！已折抵 {CURRENCY} {discount:.2f}")
            else:
                if coupon != "":
                    st.error("❌ 折扣碼無效！")
                final_total = total
                
            st.markdown(f"### 💰 總金額：**{CURRENCY} {final_total:.2f}**")
            st.write("---")
            
            pay_method = st.radio(
                "💳 請選擇您的付款方式：", 
                ["DuitNow 線上轉賬", "到店支付現金 / 拿食物時付款"],
                index=None
            )
            
            payment_closing_text = ""
            is_button_disabled = True 
            
            if dining_type == "外送 / 食物配送 🚗" and not delivery_address:
                st.error("⚠️ 您選擇了外送，請在上方購物車內填寫「完整外送地址」，才可以發送訂單喔！")
                is_button_disabled = True
            elif dining_type == "內用 🍽️" and not table_number:
                st.error("⚠️ 您選擇了內用，請在上方購物車內填寫「桌號」，才可以發送訂單喔！")
                is_button_disabled = True
            elif pay_method is None:
                st.error("⚠️ 請在上方選擇您的付款方式，才可以點擊按鈕發送訂單喔！")
                is_button_disabled = True
            elif pay_method == "DuitNow 線上轉賬":
                # 🔥 改用安全的標準元件，徹底防止引號引起的 SyntaxError
                st.warning("💳 DuitNow 轉賬收款說明\n\n請手動轉賬總金額至老闆賬號：\n📞 號碼：010-9456359")
                
                if os.path.exists("qr.jpg"):
                    st.image("qr.jpg", width=220, caption="請截圖或直接用銀行 App 掃描此 DuitNow QR 轉賬")
                
                st.info("💡 提示：轉賬完成後，請點擊下方按鈕發送訂單，並在 WhatsApp 附上「付款收據截圖」給老闆喔！🙏")
                payment_closing_text = f"老闆，我已經完成 DuitNow 轉賬 {CURRENCY} {final_total:.2f}，附圖是我的付款收據，請查收並核對單號 {st.session_state.order_id}，謝謝！"
