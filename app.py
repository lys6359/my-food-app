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

# 核心數據庫：兩頁面共享，但前台不執行複雜迴圈，徹底防止鎖死
if "backend_orders_db" not in st.session_state:
    st.session_state.backend_orders_db = []

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
            
            cart_col1, cart_col2, cart_col3 = st.columns([2, 1, 1])
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
                st.image("qr.jpg", width=220, caption="請截圖或銀行 App 掃描轉賬")
            payment_closing_text = f"老闆，我已經完成 DuitNow 轉賬 {CURRENCY} {final_total:.2f}，附圖是我的付款收據，請查收並核對單號 {st.session_state.order_id}，謝謝！"
        else:
            st.info("💡 提示：請在下單後，於現場取餐/用餐時向櫃檯支付現金。")
            payment_closing_text = f"老闆，我選擇【到店支付現金】，請先幫我準備單號 {st.session_state.order_id} 的餐點，我抵達時再付款，謝謝！"
        
        safe_dining = "Takeaway (外帶)"
        if dining_type and "外送" in dining_type:
            safe_dining = f"Delivery (外送地址: {delivery_address})"
        elif dining_type and "內用" in dining_type:
            safe_dining = f"Dine-in (桌號: {table_number})"
            
        safe_method = "DuitNow QR" if "DuitNow" in pay_method else "Cash"
        
        # 建立 WhatsApp 訊息文字
        whatsapp_text = f"*** NEW ORDER ({st.session_state.order_id}) ***\n\n"
        whatsapp_text += f"📍 用餐方式: {safe_dining}\n"
        whatsapp_text += f"💳 付款選擇: {safe_method}\n\n"
        whatsapp_text += f"--- 🛒 點餐明細 ---\n"
        for food_info, qty in st.session_state.new_cart.items():
            whatsapp_text += f"▪️ {food_info} x {qty}\n"
        whatsapp_text += f"\n💰 應付總額: {CURRENCY} {final_total:.2f}\n"
        if order_note:
            whatsapp_text += f"📝 備註: {order_note}\n"
        whatsapp_text += f"\n💬 {payment_closing_text}"
        
        encoded_text = urllib.parse.quote(whatsapp_text)
        whatsapp_url = f"https://wa.me/{MY_PHONE_NUMBER}?text={encoded_text}"
        
        # 🌟 幕後自動寫入後台數據庫，絕不干擾前端元件
        if not any(o['order_id'] == st.session_state.order_id for o in st.session_state.backend_orders_db):
            st.session_state.backend_orders_db.append({
                "order_id": st.session_state.order_id,
                "time": datetime.now().strftime("%H:%M:%S"),
                "dining_type": safe_dining,
                "pay_method": safe_method,
                "items": dict(st.session_state.new_cart),
                "total": f"{CURRENCY} {final_total:.2f}",
                "note": order_note
            })

        st.write("---")
        # 🚀 100% 絕對正常、永不消失的黃色大按鈕！
        st.link_button("🚀 確認並發送訂單至 WhatsApp", whatsapp_url, use_container_width=True)

        # 🧹 清空購物車按鈕
        st.write("") 
        if st.button("🧹 清空購物車並開始新訂單", use_container_width=True):
            st.session_state.new_cart = {}  
            next_date_str = datetime.now().strftime("%Y%m%d")
            st.session_state.order_id = f"MY-{next_date_str}-{random.randint(1000, 9999)}"
            st.rerun()
