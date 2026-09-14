import streamlit as st
import urllib.parse
import random

# 1. 網頁基本設定
st.set_page_config(page_title="MY AI 網頁點餐系統", page_icon="🍔", layout="wide")

# ==========================================
# 🌟 老闆專用控制台 (功能 C)
# ==========================================
# True  = 正常營業
# False = 店鋪打烊 (網頁會自動變成打烊海報，鎖死點餐)
IS_OPEN = True 

# 🌟 馬來西亞商家核心設定
CURRENCY = "RM"
MY_PHONE_NUMBER = "60109456359"

# ==========================================
# 網頁高級外觀 CSS 注入 (黑黃潮牌美式風格)
# ==========================================
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

# ==========================================
# 🌙 判定是否打烊 (功能 C)
# ==========================================
if not IS_OPEN:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    with st.container():
        st.markdown("<h1 style='text-align: center; color: #FBBF24 !important;'>🌙 店鋪休息中 / Closed</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-size: 18px; color: #FFFFFF !important;'>謝謝您的光臨！我們目前的營業時間已結束，明天請早喔！🙏</p>", unsafe_allow_html=True)
    st.stop() # 強制停止網頁後續的點餐代碼執行

# ==========================================
# 正常營業狀態下的點餐介面
# ==========================================
st.title("🍔 我的馬來西亞在地點餐系統")
st.write("歡迎光臨！請在下方選擇您的餐點。結帳後將引導至 WhatsApp 發送訂單給老闆喔！")

# 讓客人選擇用餐方式
dining_type = st.radio("🥡 請選擇您的用餐方式：", ["內用 🍽️", "外帶 🛍️"], horizontal=True)

# 定義菜單與價格
menu = {
    "特級牛肉漢堡 🍔": 18.00,
    "招牌炸雞排 🍗": 15.00,
    "珍珠奶茶 🧋": 9.50,
    "黃金薯條 🍟": 7.00
}

# 初始化高級購物車（功能 B：改用字典格式儲存 "商品名": 數量）
if "new_cart" not in st.session_state:
    st.session_state.new_cart = {}

# 初始化自動單號（功能 A：每位顧客進網頁自動生成唯一單號）
if "order_id" not in st.session_state:
    st.session_state.order_id = f"MY-{random.randint(1000, 9999)}"

# 3. 建立兩欄網頁排版
col1, col2 = st.columns(2)

with col1:
    st.subheader("【 🍱 今日菜單 】")
    for food, price in menu.items():
        with st.container():
            st.markdown(f"### {food}")
            st.markdown(f"💰 價格：**{CURRENCY} {price:.2f}**")
            
            # 客製化選單
            if "珍珠奶茶" in food:
                ice = st.selectbox("🧊 選擇冰塊", ["正常冰", "少冰", "微冰", "去冰"], key="ice_select")
                sugar = st.selectbox("🍬 選擇甜度", ["正常甜", "少糖(7分)", "半糖(5分)", "微糖(3分)", "無糖"], key="sugar_select")
                full_food_name = f"{food} ({ice}/{sugar})"
            else:
                spicy = st.selectbox("🌶️ 辣度選擇", ["不辣", "微辣", "中辣", "大辣"], key=f"spicy_{food}")
                full_food_name = f"{food} ({spicy})"
                
            if st.button(f"➕ 點購 {food}", key=f"btn_{food}"):
                # 功能 B：如果食物已在購物車就數量+1，沒有就建立1
                if full_food_name in st.session_state.new_cart:
                    st.session_state.new_cart[full_food_name] += 1
                else:
                    st.session_state.new_cart[full_food_name] = 1
                st.toast(f"已加入購物車！")
                st.rerun()

with col2:
    st.subheader("【 🛒 您的購物車 】")
    st.markdown(f"✨ 目前選擇：**{dining_type}** | 🔢 訂單單號：**{st.session_state.order_id}**") # 功能 A 顯示
    
    if not st.session_state.new_cart:
        st.write("購物車目前是空的喔！")
        total = 0
    else:
        total = 0
        st.write("---")
        
        # 功能 B：遍歷購物車，顯示合併後的數量與精細加減按鈕
        for food_info, qty in list(st.session_state.new_cart.items()):
            # 找出這款食物的基礎價格
            base_name = food_info.split(" (")[0]
            item_price = menu.get(base_name, 0.0)
            item_total = item_price * qty
            total += item_total
            
            # 建立三欄小排版：左邊品名數量，中間減，右邊加
            cart_col1, cart_col2, cart_col3 = st.columns([6, 1, 1])
            with cart_col1:
                st.write(f"▪️ **{food_info}** x {qty} = {CURRENCY} {item_total:.2f}")
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
        
        # 訂單備註與折扣碼
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
        
        if pay_method is None:
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
            
            # 使用正確的 Raw 網址加載您的 DuitNow QR
            RAW_QR_URL = "https://githubusercontent.com"
            st.image(RAW_QR_URL, width=220, caption="請截圖或直接用銀行 App 掃描此 DuitNow QR 轉賬")
            
            st.info("💡 提示：轉賬完成後，請點擊下方按鈕發送訂單，並在 WhatsApp 附上「付款收據截圖」給老闆喔！🙏")
            payment_closing_text = f"老闆，我已經完成 DuitNow 轉賬 {CURRENCY} {final_total:.2f}，附圖是我的付款收據，請查收並核對單號 {st.session_state.order_id}，謝謝！🙏"
            is_button_disabled = False 
        else:
            st.info("💡 提示：請在下單後，於現場取餐/用餐時向櫃檯支付現金。")
            payment_closing_text = f"老闆，我選擇【到店支付現金】，請先幫我準備單號 {st.session_state.order_id} 的餐點，我抵達時再付款，謝謝！🙏"
            is_button_disabled = False 
        
        # 🌟 組合 WhatsApp 文字訊息 (帶有自動單號功能 A)
        whatsapp_text = f"🚨 【收到新訂單】 🚨\n\n"
        whatsapp_text += f"🔢 訂單單號：{st.session_state.order_id}\n" # 功能 A 嵌入
        whatsapp_text += f"📌 用餐方式：{dining_type}\n"
        whatsapp_text += f"💳 付款方式：{pay_method}\n"
        whatsapp_text += f"-------------------------\n"
        # 功能 B：漂亮的格式化數量與小計明細
        for food_info, qty in st.session_state.new_cart.items():
            base_name = food_info.split(" (")[0]
            item_price = menu.get(base_name, 0.0)
            whatsapp_text += f"▪️ {food_info} x {qty} - {CURRENCY} {(item_price*qty):.2f}\n"
        whatsapp_text += f"-------------------------\n"
        if order_note:
            whatsapp_text += f"📝 備註：{order_note}\n"
        whatsapp_text += f"💰 總金額：{CURRENCY} {final_total:.2f}\n\n"
        whatsapp_text += payment_closing_text
        
        encoded_text = urllib.parse.quote(whatsapp_text)
        whatsapp_url = f"https://wa.me/{MY_PHONE_NUMBER}?text={encoded_text}"
        
        st.link_button(
            "📱 點擊發送訂單至 WhatsApp", 
            whatsapp_url, 
            type="primary", 
            use_container_width=True,
            disabled=is_button_disabled
        )
        
        if st.button("🗑️ 清空購物車"):
            st.session_state.new_cart = {}
            st.rerun()
