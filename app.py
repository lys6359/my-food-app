import streamlit as st
import urllib.parse

# 1. 網頁基本設定
st.set_page_config(page_title="MY AI 網頁點餐系統", page_icon="🍔", layout="wide")

# 利用 CSS 注入，將背景改成高級明亮黃與深灰色調
st.markdown("""
    <style>
    .stApp {
        background-color: #FBBF24; /* 鮮豔的高級明亮黃底色 */
        color: #1F2937 !important;
    }
    h1 {
        color: #000000 !important;
        font-weight: 800 !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    [data-testid="stContainer"] {
        background-color: #1F2937 !important; /* 深灰色卡片背景 */
        border-radius: 16px !important;
        padding: 20px !important;
        border: none !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06) !important;
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
        width: 100% !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🍔 我的馬來西亞在地點餐系統")
st.write("歡迎光臨！請在下方選擇您的餐點。結帳後將引導至 WhatsApp 發送訂單給老闆喔！")

# 🌟 馬來西亞專屬設定
CURRENCY = "RM"
MY_PHONE_NUMBER = "60109456359"

# 讓客人選擇用餐方式
dining_type = st.radio("🥡 請選擇您的用餐方式：", ["內用 🍽️", "外帶 🛍️"], horizontal=True)

# 2. 定義菜單與價格
menu = {
    "特級牛肉漢堡 🍔": 18.00,
    "招牌炸雞排 🍗": 15.00,
    "珍珠奶茶 🧋": 9.50,
    "黃金薯條 🍟": 7.00
}

if "cart" not in st.session_state:
    st.session_state.cart = []

# 3. 建立兩欄網頁排版
col1, col2 = st.columns(2)

with col1:
    st.subheader("【 🍱 今日菜單 】")
    for food, price in menu.items():
        with st.container():
            st.markdown(f"### {food}")
            st.markdown(f"💰 價格：**{CURRENCY} {price:.2f}**")
            
            if "珍珠奶茶" in food:
                ice = st.selectbox("🧊 選擇冰塊", ["正常冰", "少冰", "微冰", "去冰"], key="ice_select")
                sugar = st.selectbox("🍬 選擇甜度", ["正常甜", "少糖(7分)", "半糖(5分)", "微糖(3分)", "無糖"], key="sugar_select")
                button_label = f"➕ 點購 {food} ({ice}/{sugar})"
                note = f" ({ice}/{sugar})"
            else:
                spicy = st.selectbox("🌶️ 辣度選擇", ["不辣", "微辣", "中辣", "大辣"], key=f"spicy_{food}")
                button_label = f"➕ 點購 {food} ({spicy})"
                note = f" ({spicy})"
                
            if st.button(button_label, key=f"btn_{food}"):
                st.session_state.cart.append((food + note, price))
                st.toast(f"已加入購物車！")

with col2:
    st.subheader("【 🛒 您的購物車 】")
    st.markdown(f"✨ 目前選擇：**{dining_type}**")
    
    if not st.session_state.cart:
        st.write("購物車目前是空的喔！")
        total = 0
    else:
        total = 0
        for index, (food_info, price) in enumerate(st.session_state.cart):
            item_col1, item_col2 = st.columns(2)
            with item_col1:
                st.write(f"- **{food_info}**：{CURRENCY} {price:.2f}")
            with item_col2:
                if st.button("❌", key=f"del_{index}"):
                    st.session_state.cart.pop(index)
                    st.rerun()
            total += price
        
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
        
        # 讓顧客手動勾選付款方式
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
            
            # 🌟 【終極修復】：將原本的 "qr.png" 換成你剛剛複製的 GitHub 圖片網址
            # 請把你剛才複製的圖片網址，替換掉下面雙引號裡的這串網址
            YOUR_QR_IMAGE_URL = "https://githubusercontent.com"
            
            # 透過網址讀取圖片，寬度設為 220 剛剛好，並且絕對不會因為本地找不到檔案而報錯！
            st.image(YOUR_QR_IMAGE_URL, width=220, caption="請截圖或直接用銀行 App 掃描此 DuitNow QR 轉賬")
            
            st.info("💡 提示：轉賬完成後，請點擊下方按鈕發送訂單，並在 WhatsApp 附上「付款收據截圖」給老闆喔！🙏")
            payment_closing_text = f"老闆，我已經完成 DuitNow 轉賬 {CURRENCY} {final_total:.2f}，附圖是我的付款收據，請查收接單，謝謝！🙏"
            is_button_disabled = False 
        else:
            st.info("💡 提示：請在下單後，於現場取餐/用餐時向櫃檯支付現金。")
            payment_closing_text = f"老闆，我選擇【到店支付現金】，請先幫我準備餐點，我抵達時再付款，謝謝！🙏"
            is_button_disabled = False 
        
        # 組合 WhatsApp 文字訊息
        whatsapp_text = f"🚨 【收到新訂單】 🚨\n\n"
        whatsapp_text += f"📌 用餐方式：{dining_type}\n"
        whatsapp_text += f"💳 付款方式：{pay_method}\n"
        whatsapp_text += f"-------------------------\n"
        for food_info, price in st.session_state.cart:
            whatsapp_text += f"▪️ {food_info} - {CURRENCY} {price:.2f}\n"
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
            st.session_state.cart = []
            st.rerun()
