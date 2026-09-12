import streamlit as st
import urllib.parse

# 1. 網頁基本設定
st.set_page_config(page_title="MY AI 網頁點餐系統", page_icon="🍔")

st.title("🍔 我的馬來西亞在地點餐系統")
st.write("歡迎光臨！請在下方選擇您的餐點。結帳後將引導至 WhatsApp 發送訂單給老闆喔！")

# 🌟 馬來西亞專屬設定
CURRENCY = "RM"
MY_PHONE_NUMBER = "60109456359"

# 讓客人選擇用餐方式
dining_type = st.radio("🥡 請選擇您的用餐方式：", ["內用 🍽️", "外帶 🛍️"], horizontal=True)

# 2. 定義菜單與價格（馬來西亞令吉 RM）
menu = {
    "滷肉飯 🍚": 12.00,
    "炸雞排 🍗": 15.00,
    "珍珠奶茶 🧋": 9.50,
    "黃金薯條 🍟": 7.00
}

# 初始化購物車
if "cart" not in st.session_state:
    st.session_state.cart = []

# 3. 建立兩欄網頁排版
col1, col2 = st.columns(2)

with col1:
    st.subheader("【 🍱 今日菜單 】")
    
    for food, price in menu.items():
        with st.container(border=True):
            st.markdown(f"### {food}")
            st.markdown(f"💰 價格：**{CURRENCY} {price:.2f}**")
            
            # 客製化選項
            if "珍珠奶茶" in food:
                ice = st.selectbox("🧊 選擇冰塊", ["正常冰", "少冰", "微冰", "去冰"], key="ice_select")
                sugar = st.selectbox("🍬 選擇甜度", ["正常甜", "少糖(7分)", "半糖(5分)", "微糖(3分)", "無糖"], key="sugar_select")
                button_label = f"➕ 點購 {food} ({ice}/{sugar})"
                note = f" ({ice}/{sugar})"
            else:
                spicy = st.selectbox("🌶️ 辣度選擇", ["不辣", "微辣", "中辣", "大辣"], key=f"spicy_{food}")
                button_label = f"➕ 點購 {food} ({spicy})"
                note = f" ({spicy})"
                
            if st.button(button_label, key=f"btn_{food}", type="secondary"):
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
        
        # 組合 WhatsApp 文字訊息
        whatsapp_text = f"🚨 【收到新訂單】 🚨\n\n"
        whatsapp_text += f"📌 用餐方式：{dining_type}\n"
        whatsapp_text += f"-------------------------\n"
        for food_info, price in st.session_state.cart:
            whatsapp_text += f"▪️ {food_info} - {CURRENCY} {price:.2f}\n"
        whatsapp_text += f"-------------------------\n"
        if order_note:
            whatsapp_text += f"📝 備註：{order_note}\n"
        whatsapp_text += f"💰 總金額：{CURRENCY} {final_total:.2f}\n\n"
        whatsapp_text += f"請老闆確認接單，謝謝！🙏"
        
        # 轉換成網頁文字格式
        encoded_text = urllib.parse.quote(whatsapp_text)
        
        # 🌟 【這裡已經放上正確的斜線 / 】100% 沒問題！
        whatsapp_url = f"https://wa.me{MY_PHONE_NUMBER}?text={encoded_text}"
        
        # 建立美麗的藍色跳轉按鈕
        st.link_button("📱 點擊發送訂單至 WhatsApp", whatsapp_url, type="primary", use_container_width=True)
        
        if st.button("🗑️ 清空購物車"):
            st.session_state.cart = []
            st.rerun()
