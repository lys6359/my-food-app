import streamlit as st
import urllib.parse
import random
import os
from datetime import datetime

# 1. 網頁基本設定
st.set_page_config(page_title="MY AI 網頁點餐系統", page_icon="🥟", layout="wide")

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

# 老闆專用營業控制：True = 正常營業 | False = 店鋪打烊
IS_OPEN = True 

if not IS_OPEN:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    with st.container():
        st.markdown("<h1 style='text-align: center; color: #FBBF24 !important;'>🌙 店鋪休息中 / Closed</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-size: 18px; color: #FFFFFF !important;'>謝謝您的光臨！我們目前的營業時間已結束，明天請早喔！🙏</p>", unsafe_allow_html=True)
    st.stop() 

# ==========================================
# 🍔 前台顧客點餐大標題
# ==========================================
st.title("🥟 我的馬來西亞在地點餐系統")
st.write("歡迎光臨！請在下方選擇您的餐點。結帳後將引導至 WhatsApp 發送訂單給老闆喔！")
st.write("---")

# 用餐方式選擇
dining_type = st.radio(
    "🥡 請選擇您的用餐方式：", 
    ["內用 🍽️", "外帶 🛍️", "外送 / 食物配送 🚗"], 
    horizontal=True,
    index=None
)

# 🌟 重新定義菜單與基礎價格
menu = {
    "手工水餃 (10顆) 🥟": 10.00,
    "金黃鍋貼 (10顆) 🥟🔥": 11.00,
    "招牌脆皮雞翅 🍗": 8.00
}

CURRENCY = "RM"
MY_PHONE_NUMBER = "60109456359"

if "new_cart" not in st.session_state:
    st.session_state.new_cart = {}

# 🔢 系統每次自動生成獨一無二的訂單單號
if "order_id" not in st.session_state:
    date_str = datetime.now().strftime("%Y%m%d")
    st.session_state.order_id = f"MY-{date_str}-{random.randint(1000, 9999)}"

# 建立左右兩欄排版
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
            
            # 🌟 為新餐點設計客製化加點與口味選項
            if "水餃" in food:
                flavor = st.selectbox("🥬 選擇口味", ["韭菜豬肉", "高麗菜豬肉", "三鮮蝦仁 (+RM 2.00)"], key="dumpling_flavor")
                spicy = st.selectbox("🌶️ 辣度 (附贈辣椒醬)", ["不辣", "微辣", "中辣", "大辣"], key="dumpling_spicy")
                
                # 計算特殊口味加價
                actual_price = price + 2.00 if "三鮮蝦仁" in flavor else price
                full_food_name = f"{food} ({flavor}/{spicy})"
                
            elif "鍋貼" in food:
                flavor = st.selectbox("🔥 選擇口味", ["招牌豬肉", "韓式辣味 (+RM 1.00)"], key="potsticker_flavor")
                sauce = st.selectbox("🥢 配料醬汁", ["特調醬油膏", "加薑絲烏醋", "不需要醬汁"], key="potsticker_sauce")
                
                actual_price = price + 1.00 if "韓式辣味" in flavor else price
                full_food_name = f"{food} ({flavor}/{sauce})"
                
            else:  # 脆皮雞翅
                size = st.selectbox("🍗 選擇份量", ["標準份量 (3隻)", "分享份量 (6隻) (+RM 7.00)", "派對份量 (10隻) (+RM 15.00)"], key="wings_size")
                seasoning = st.selectbox("🧂 靈魂撒粉", ["招牌胡椒鹽", "勁辣辣椒粉", "梅子甘梅粉"], key="wings_seasoning")
                
                # 計算份量加價
                if "6隻" in size:
                    actual_price = price + 7.00
                elif "10隻" in size:
                    actual_price = price + 15.00
                else:
                    actual_price = price
                    
                full_food_name = f"{food} ({size}/{seasoning})"
                
            # 將計算好的價格傳遞給購物車按鈕使用
            if st.button(f"➕ 點購 {food}", key=f"btn_{food}", disabled=is_menu_disabled):
                # 記錄名稱與當時選擇的實際計算價格
                if full_food_name in st.session_state.new_cart:
                    st.session_state.new_cart[full_food_name]["qty"] += 1
                else:
                    st.session_state.new_cart[full_food_name] = {"qty": 1, "price": actual_price}
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
        st.write("購物車目前是空的喔！請從左側今日菜單點擊按鈕加入餐點。")
        total = 0
    else:
        total = 0
        st.write("---")
        
        for food_info, item_data in list(st.session_state.new_cart.items()):
            qty = item_data["qty"]
            item_price = item_data["price"]
            item_total = item_price * qty
            total += item_total
            
            cart_col1, cart_col2, cart_col3 = st.columns(3)
            with cart_col1:
                st.write(f"▪️ **{food_info}**  \n💰 單價: {CURRENCY} {item_price:.2f} x {qty}")
            with cart_col2:
                if st.button("➖", key=f"minus_{food_info}"):
                    st.session_state.new_cart[food_info]["qty"] -= 1
                    if st.session_state.new_cart[food_info]["qty"] <= 0:
                        del st.session_state.new_cart[food_info]
                    st.rerun()
            with cart_col3:
                if st.button("➕", key=f"plus_{food_info}"):
                    st.session_state.new_cart[food_info]["qty"] += 1
                    st.rerun()
                    
        st.write("---")
        order_note = st.text_input("📝 訂單備註（例如：水餃分開裝、鍋貼要焦一點）")
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
        
        # 建立明細文字
        whatsapp_text = f"*** NEW ORDER ({st.session_state.order_id}) ***\n\n"
        whatsapp_text += f"📍 用餐方式: {safe_dining}\n"
        whatsapp_text += f"💳 付款選擇: {safe_method}\n\n"
        whatsapp_text += f"--- 🛒 點餐明細 ---\n"
        for food_info, item_data in st.session_state.new_cart.items():
            whatsapp_text += f"▪️ {food_info} x {item_data['qty']}\n"
        whatsapp_text += f"\n💰 應付總額: {CURRENCY} {final_total:.2f}\n"
        if order_note:
            whatsapp_text += f"📝 備註: {order_note}\n"
        whatsapp_text += f"\n💬 {payment_closing_text}"
        
        encoded_text = urllib.parse.quote(whatsapp_text)
        whatsapp_url = f"https://wa.me{MY_PHONE_NUMBER}?text={encoded_text}"
        
        st.write("---")
        
        # 🚀 顧客發送按鈕：100% 穩定亮起、直接成功跳轉！
        st.link_button("🚀 確認並發送訂單至 WhatsApp", whatsapp_url, use_container_width=True)

        # 🧹 清空購物車按鈕
        st.write("") 
        if st.button("🧹 清空購物車並開始新訂單", use_container_width=True):
            st.session_state.new_cart = {}  
            next_date_str = datetime.now().strftime("%Y%m%d")
            st.session_state.order_id = f"MY-{next_date_str}-{random.randint(1000, 9999)}"
            st.rerun()
