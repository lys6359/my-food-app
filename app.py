import streamlit as st
import urllib.parse
import random
import os
import pandas as pd  # 引入 pandas 用於處理訂單報表匯出
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
    h1, h2, h3 {
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

# 核心數據庫結構：儲存所有成功生成的歷史訂單（供老闆後台查閱、匯出）
if "backend_orders_db" not in st.session_state:
    st.session_state.backend_orders_db = []

# 老闆專用營業控制（預設營業）
IS_OPEN = True 

if not IS_OPEN:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    with st.container():
        st.markdown("<h1 style='text-align: center; color: #FBBF24 !important;'>🌙 店鋪休息中 / Closed</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-size: 18px; color: #FFFFFF !important;'>謝謝您的光臨！我們目前的營業時間已結束，明天請早喔！🙏</p>", unsafe_allow_html=True)
    st.stop() 

# ==========================================
# 🍔 頂部導覽列（包含標題與獨立的老闆後台彈窗）
# ==========================================
top_col1, top_col2 = st.columns([8, 2])
with top_col1:
    st.title("🍔 我的馬來西亞在地點餐系統")
    st.write("歡迎光臨！請在下方選擇您的餐點。結帳後將引導至 WhatsApp 發送訂單給老闆喔！")

with top_col2:
    # 🌟 使用獨立的 popover 元件，完全不影響主頁面渲染，100% 解決按鈕不見的問題
    with st.popover("⚙️ 店家管理中心"):
        admin_password = st.text_input("🔑 輸入管理員密碼：", type="password", key="admin_pwd_pop")
        if admin_password == "1234":
            st.success("🔓 登入成功")
            if not st.session_state.backend_orders_db:
                st.info("📭 目前尚無訂單紀錄。")
            else:
                st.write(f"📈 今日自動生成單號數量: **{len(st.session_state.backend_orders_db)}** 單")
                
                # 訂單資料轉換與匯出
                export_data = []
                for order in st.session_state.backend_orders_db:
                    items_text = ", ".join([f"{k}x{v}" for k, v in order['items'].items()])
                    export_data.append({
                        "訂單單號": order['order_id'],
                        "下單時間": order['time'],
                        "用餐方式": order['dining_type'],
                        "付款方式": order['pay_method'],
                        "點餐明細": items_text,
                        "應付總額": order['total'],
                        "客戶備註": order['note']
                    })
                df = pd.DataFrame(export_data)
                csv_buffer = df.to_csv(index=False).encode('utf-8-sig')
                
                st.download_button(
                    label="📥 下載今日訂單報表 (CSV)",
                    data=csv_buffer,
                    file_name=f"今日訂單報表_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                
                st.write("---")
                for order in st.session_state.backend_orders_db:
                    with st.expander(f"📋 單號：{order['order_id']}"):
                        st.write(f"**📍 用餐方式:** {order['dining_type']}")
                        st.write(f"**💳 付款方式:** {order['pay_method']}")
                        st.write(f"**💰 總金額:** {order['total']}")
                        st.write("**🛒 明細:**")
                        for item, qty in order['items'].items():
                            st.write(f"- {item} x {qty}")
                        if order['note']:
                            st.write(f"**📝 備註:** {order['note']}")

st.write("---") 

# ==========================================
# 🥡 用餐方式選擇
# ==========================================
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

# 自動生成唯一的訂單單號
if "order_id" not in st.session_state:
    date_str = datetime.now().strftime("%Y%m%d")
    st.session_state.order_id = f"MY-{date_str}-{random.randint(1000, 9999)}"

# 建立兩欄網頁排版
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
            ["DuitNow 線上轉賬", "到店支付現金 / 拿食物時付款"]
        )
        
        payment_closing_text = ""
        
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
            
            payment_closing_text = f"老闆，我已經完成 DuitNow 轉賬 {CURRENCY} {final_total:.2f}，附圖是我的付款收據，請查收並核對單號 {st.session_state.order_id}，謝謝！"
        else:
            st.info("💡 提示：請在下單後，於現場取餐/用餐時向櫃檯支付現金。")
            payment_closing_text = f"老闆，我選擇【到店支付現金】，請先幫我準備單號 {st.session_state.order_id} 的餐點，我抵達時再付款，謝謝！"
        
        # 文字格式化
        safe_dining = "Takeaway (外帶)"
        if dining_type and "外送" in dining_type:
            safe_dining = f"Delivery (外送地址: {delivery_address})"
        elif dining_type and "內用" in dining_type:
            safe_dining = f"Dine-in (桌號: {table_number})"
            
        safe_method = "DuitNow QR" if "DuitNow" in pay_method else "Cash"
        
        # 建立 WhatsApp 訊息文字
