import streamlit as st
import urllib.parse
import random
import os

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

st.title("🍔 我的馬來西亞在地點餐系統")
st.write("歡迎光臨！請在下方選擇您的餐點。結帳後將引導至 WhatsApp 發送訂單給老闆喔！")

# 用餐方式新增「食物配送 🚗」，並且預設為 None (強制顧客先選擇)
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

# 馬來西亞專屬貨幣符號
CURRENCY = "RM"
MY_PHONE_NUMBER = "60109456359"

if "new_cart" not in st.session_state:
    st.session_state.new_cart = {}

if "order_id" not in st.session_state:
    st.session_state.order_id = f"MY-{random.randint(1000, 9999)}"

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
    
    # 根據不同的用餐方式，動態彈出地址或桌號輸入框
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
        
        # 用於記錄文字明細發送給老闆
        items_summary_text = ""
        
        for food_info, qty in list(st.session_state.new_cart.items()):
            item_price = 0.0
            for menu_key in menu:
                if menu_key in food_info:
                    item_price = menu[menu_key]
                    break
            item_total = item_price * qty
            total += item_total
            
            # 建立購物車格式字串
            items_summary_text += f"- {food_info} x{qty} ({CURRENCY} {item_total:.2f})\n"
            
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
        
        # 付款方式選擇
        pay_method = st.radio(
            "💳 請選擇您的付款方式：", 
            ["DuitNow 線上轉賬", "到店支付現金 / 拿食物時付款"],
            index=None
        )
        
        payment_closing_text = ""
        is_button_disabled = True 
        
        # 外送和地址的完整防呆邏輯
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
            st.markdown(f"""
                <div style="background-color: #1F2937; padding: 15px; border-radius: 12px; margin-bottom: 10px; color: #FFFFFF;">
                    <h4 style="color: #FBBF24; margin-top: 0px; margin-bottom: 8px;">💳 DuitNow 轉賬收款說明</h4>
                    <p style="margin: 0px; font-size: 15px;">請掃描下方 QR Code 或手動轉賬總金額至老闆賬號：</p>
                    <p style="margin: 5px 0px; font-size: 18px; font-weight: bold; color: #FBBF24;">📞 號碼：010-9456359</p>
                </div>
            """, unsafe_allow_html=True)
            
            # 檢查並顯示你的 qr.jpg
            if os.path.exists("qr.jpg"):
                st.image("qr.jpg", width=220, caption="請截圖或直接用銀行 App 掃描此 DuitNow QR 轉賬")
            else:
                st.warning("⚠️ 找不到 qr.jpg 圖片檔案，請確保它上傳在專案根目錄中。")
            
            # 【新增優化功能】：讓顧客可以直接上傳付款收據截圖存檔提示
            uploaded_receipt = st.file_uploader("📸 上傳您的付款收據截圖 (選填)", type=["jpg", "png", "jpeg"])
            if uploaded_receipt is not None:
                st.success("✅ 收據已成功載入！請點擊下方按鈕將訂單發送到 WhatsApp。")
            
            st.info("💡 提示：轉賬完成後，請點擊下方按鈕發送訂單，並在 WhatsApp 附上「付款收據截圖」給老闆喔！🙏")
            payment_closing_text = f"老闆，我已經完成 DuitNow 轉賬 {CURRENCY} {final_total:.2f}，附圖是我的付款收據，請查收並核對單號 {st.session_state.order_id}，謝謝！"
            is_button_disabled = False 
        else:
            st.info("💡 提示：請在下單後，於現場取餐/用餐時向櫃檯支付現金。")
            payment_closing_text = f"老闆，我選擇【到店支付現金】，請先幫我準備單號 {st.session_state.order_id} 的餐點，我抵達時再付款，謝謝！"
            is_button_disabled = False 
        
        # 轉換成乾淨、全文字、絕不碎單的格式
        safe_dining = "Takeaway"
        if dining_type == "內用 🍽️":
            safe_dining = f"Dine-in (Table: {table_number})"
        elif dining_type == "外送 / 食物配送 🚗":
            safe_dining = f"Delivery (Address: {delivery_address})"
            
        if pay_method is not None:
            safe_method = "DuitNow QR" if "DuitNow" in pay_method else "Cash"
        else:
            safe_method = "Not Selected"
        
        # 4. 建構發送至 WhatsApp 的大字串（絕不碎單）
        whatsapp_text = f"*** 🍔 NEW ORDER ({st.session_state.order_id}) ***\n\n"
        whatsapp_text += f"📅 訂單單號: {st.session_state.order_id}\n"
        whatsapp_text += f"🥡 用餐方式: {safe_dining}\n"
        whatsapp_text += f"💳 付款方式: {safe_method}\n"
        whatsapp_text += f"📝 訂單備註: {order_note if order_note else '無'}\n\n"
        whatsapp_text += f"【 🛒 點餐明細 】\n{items_summary_text}\n"
        whatsapp_text += f"💰 總計金額: {CURRENCY} {final_total:.2f}\n\n"
        whatsapp_text += f"💬 顧客留言: {payment_closing_text}"
        
        # URL 編碼轉化
        encoded_text = urllib.parse.quote(whatsapp_text)
        whatsapp_url = f"https://wa.me{MY_PHONE_NUMBER}?text={encoded_text}"
        
        # 5. 送出訂單按鈕
        st.write("---")
        if st.button("🚀 確認無誤，送出訂單到 WhatsApp", key="submit_order", disabled=is_button_disabled, use_container_width=True):
            # 清空購物車以防重複提交，並生成新單號
            st.session_state.new_cart = {}
            st.session_state.order_id = f"MY-{random.randint(1000, 9999)}"
            
            # JavaScript 自動跳轉至 WhatsApp
            js = f"window.open('{whatsapp_url}')"
            st.components.v1.html(f"<script>{js}</script>", height=0, width=0)
            st.success("🎉 訂單已生成！正在為您開啟 WhatsApp 連線老闆...")
            st.rerun()
