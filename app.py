import streamlit as st
import urllib.parse
import random
import os
from datetime import datetime

# 1. 網頁基本設定
st.set_page_config(page_title="MY AI 網頁點餐系統", page_icon="🍔", layout="wide")

# 利用 CSS 注入，將背景改成高級明亮黃與深灰色調，並優化側邊欄與表格樣式
st.markdown("""
    <style>
    .stApp {
        background-color: #FBBF24; 
        color: #1F2937 !important;
    }
    h1, h2, h3 {
        color: #000000 !important;
        font-weight: 800 !important;
    }
    /* 側邊欄老闆後台樣式優化 */
    [data-testid="stSidebar"] {
        background-color: #111827 !important;
        color: #FFFFFF !important;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #FBBF24 !important;
    }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label {
        color: #FFFFFF !important;
    }
    /* 顧客貨架與購物車 Container */
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

# 初始化全域模擬數據庫：儲存所有成功送出的訂單（供老闆後台查閱）
if "all_orders" not in st.session_state:
    st.session_state.all_orders = []

# ==========================================
# 🛠️ 老闆專用控制台 (側邊欄隱藏管理後台)
# ==========================================
with st.sidebar:
    st.title("👨‍🍳 老闆專屬後台面板")
    st.write("此面板僅供店家管理使用")
    
    # 控制店鋪營業狀態
    IS_OPEN = st.toggle("店鋪營業狀態 (Open/Closed)", value=True)
    
    st.write("---")
    st.subheader("📊 訂單實時監控中心")
    
    if not st.session_state.all_orders:
        st.info("📭 目前暫無新訂單。顧客點擊發送後此處將自動更新。")
    else:
        st.success(f"📈 今日已接收訂單量: {len(st.session_state.all_orders)} 單")
        
        # 遍歷所有生成的訂單單號並列表顯示
        for order in st.session_state.all_orders:
            with st.expander(f"📋 單號：{order['order_id']} ({order['time']})"):
                st.markdown(f"**用餐方式:** {order['dining_type']}")
                st.markdown(f"**付款方式:** {order['pay_method']}")
                st.markdown(f"**總金額:** {order['total']}")
                st.markdown("**餐點明細:**")
                for item, qty in order['items'].items():
                    st.write(f"- {item} x {qty}")
                if order['note']:
                    st.markdown(f"**備註:** {order['note']}")
                
                # 訂單狀態管理
                st.selectbox(
                    "更新訂單狀態", 
                    ["新訂單 🆕", "製作中 🍳", "配送/待取中 🛵", "已完成 ✅"], 
                    key=f"status_{order['order_id']}"
                )

# 營業中斷防禦邏輯
if not IS_OPEN:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    with st.container():
        st.markdown("<h1 style='text-align: center; color: #FBBF24 !important;'>🌙 店鋪休息中 / Closed</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-size: 18px; color: #FFFFFF !important;'>謝謝您的光臨！我們目前的營業時間已結束，明天請早喔！🙏</p>", unsafe_allow_html=True)
    st.stop() 

# ==========================================
# 🍔 前台顧客點餐系統
# ==========================================
st.title("🍔 我的馬來西亞在地點餐系統")
st.write("歡迎光臨！請在下方選擇您的餐點。結帳後將引導至 WhatsApp 發送訂單給老闆喔！")

# 用餐方式
dining_type = st.radio(
    "🥡 請選擇您的用餐方式：", 
    ["內用 🍽️", "外帶 🛍️", "外送 / 食物配送 🚗"], 
    horizontal=True,
    index=None
)

# 定義菜單與價格
menu = {
    "特級牛肉漢堡 🍔": 18.00,
    "招牌炸雞排 🍗": 15.00,
    "珍珠奶茶 🧋": 9.50,
    "黃金薯條 🍟": 7.00
}

CURRENCY = "RM"
MY_PHONE_NUMBER = "60109456359"

if "new_cart" not in st.session_state:
    st.session_state.new_cart = {}

# 自動生成唯一的訂單單號 (結合當前日期與隨機數，格式如：MY-20260917-1024)
if "order_id" not in st.session_state:
    date_str = datetime.now().strftime("%Y%m%d")
    st.session_state.order_id = f"MY-{date_str}-{random.randint(1000, 9999)}"

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
    st.markdown(f"✨ 目前選擇：**{display_type}** | 🔢 自動生成單號：**{st.session_state.order_id}**") 
    
    delivery_address = ""
    table_number = ""
    
    if dining_type == "外送 / 食物配送 🚗":
        delivery_address = st.text_input("🏠 請輸入您的完整外送地址 (Delivery Address):")
    elif dining_type == "內用 🍽️":
        table_number = st.text_input("🔢 請輸入您的桌號 (Table Number):")
    
    if not st.session_state.new_cart:
        st.write("購物車目前是空的喔！")
        total = 0
    else:
        total = 0
        st.write("---")
        
        for food_info, qty in list(st.session_state.new_cart.items()):
            item_price = 0.0
            for menu_key in menu:
                if menu_key in food_info:
                    item_price = menu[menu_key]
                    break
            item_total = item_price * qty
            total += item_total
            
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
            index=0  # 🌟 核心修正：預設選取第一個，防止 None 導致程式誤判
        )
        
        payment_closing_text = ""
        
        # 根據付款方式渲染 UI，但不去干涉按鈕的生死
        if pay_method == "DuitNow 線上轉賬":
            st.markdown("""
                <div style="background-color: #1F2937; padding: 15px; border-radius: 12px; margin-bottom: 10px; color: #FFFFFF;">
                    <h4 style="color: #FBBF24; margin-top: 0px; margin-bottom: 8px;">💳 DuitNow 轉賬收款說明</h4>
                    <p style="margin: 0px; font-size: 15px;">請掃描下方 QR Code 或手動轉賬總金額至老闆賬號：</p>
                    <p style="margin: 5px 0px; font-size: 18px; font-weight: bold; color: #FBBF24;">📞 號碼：010-9456359</p>
                </div>
            """, unsafe_allow_html=True)
            
            if os.path.exists("qr.jpg"):
                st.image("qr.jpg", width=220, caption="請截圖或直接用銀行 App 掃描此 DuitNow QR 轉賬")
            else:
                st.warning("⚠️ 找不到 qr.jpg 收款碼圖片，請老闆將圖片放置於同級目錄下。")
            
            st.info("💡 提示：轉賬完成後，請點擊下方按鈕發送訂單，並在 WhatsApp 附上「付款收據截圖」給老闆喔！🙏")
            payment_closing_text = f"老闆，我已經完成 DuitNow 轉賬 {CURRENCY} {final_total:.2f}，附圖是我的付款收據，請查收並核對單號 {st.session_state.order_id}，謝謝！"
        else:
            st.info("💡 提示：請在下單後，於現場取餐/用餐時向櫃檯支付現金。")
            payment_closing_text = f"老闆，我選擇【到店支付現金】，請先幫我準備單號 {st.session_state.order_id} 的餐點，我抵達時再付款，謝謝！"
        
        # 格式化文字
        safe_dining = "Takeaway (外帶)"
        if dining_type and "外送" in dining_type:
            safe_dining = f"Delivery (外送地址: {delivery_address})"
        elif dining_type and "內用" in dining_type:
            safe_dining = f"Dine-in (桌號: {table_number})"
            
        safe_method = "DuitNow QR" if pay_method and "DuitNow" in pay_method else "Cash"
        
        # 建立 WhatsApp 訊息文字
        whatsapp_text = f"*** NEW ORDER ({st.session_state.order_id}) ***\n\n"
        whatsapp_text += f"📍 用餐方式: {safe_dining}\n"
        whatsapp_text += f"💳 付款選擇: {safe_method}\n\n"
        whatsapp_text += f"--- 🛒 點餐明細 ---\n"
        
        for food_info, qty in st.session_state.new_cart.items():
            whatsapp_text += f"▪️ {food_info} x {qty}\n"
            
