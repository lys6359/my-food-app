import streamlit as st

# 1. 設定網頁標題與圖標
st.set_page_config(page_title="AI 網頁點餐系統", page_icon="🍱")

st.title("🍱 我的視覺進階版點餐系統")
st.write("歡迎光臨！請參考下方精美圖片，選擇您想點的餐點與客製化選項喔！")

# 2. 定義菜單、價格與高清食物圖片網址
menu = {
    "滷肉飯 🍚": {
        "price": 45,
        "image": "https://unsplash.com"
    },
    "炸雞排 🍗": {
        "price": 85,
        "image": "https://unsplash.com"
    },
    "珍珠奶茶 🧋": {
        "price": 60,
        "image": "https://unsplash.com"
    },
    "黃金薯條 🍟": {
        "price": 50,
        "image": "https://unsplash.com"
    }
}

# 初始化購物車（如果不存在的話）
if "cart" not in st.session_state:
    st.session_state.cart = []

# 3. 建立兩欄網頁排版
col1, col2 = st.columns(2)

with col1:
    st.subheader("【 🍱 今日菜單 】")
    
    # 遍歷每樣食物並顯示圖片與價格
    for food, info in menu.items():
        st.markdown(f"### {food} — `${info['price']}元`")
        
        # 🌟 核心修改：使用 st.image 顯示高清食物圖片
        # width=300 可以控制圖片寬度，讓排版更整齊；caption 可以幫圖片加小字幕
        st.image(info["image"], width=300, caption=f"熱騰騰的{food}")
        
        # 如果是飲料（珍珠奶茶），就顯示冰塊和甜度的下拉選單
        if "珍珠奶茶" in food:
            ice = st.selectbox("🧊 選擇冰塊", ["正常冰", "少冰", "微冰", "去冰"], key="ice_select")
            sugar = st.selectbox("🍬 選擇甜度", ["正常甜", "少糖(7分)", "半糖(5分)", "微糖(3分)", "無糖"], key="sugar_select")
            button_label = f"➕ 點購 {food} ({ice}/{sugar})"
            note = f" ({ice}/{sugar})"
        else:
            # 普通餐點可以選擇辣度
            spicy = st.selectbox("🌶️ 辣度選擇", ["不辣", "微辣", "中辣", "大辣"], key=f"spicy_{food}")
            button_label = f"➕ 點購 {food} ({spicy})"
            note = f" ({spicy})"
            
        # 點擊按鈕時將食物與客製化選項存入購物車
        if st.button(button_label, key=f"btn_{food}"):
            full_name = f"{food}{note}"
            st.session_state.cart.append((full_name, info["price"]))
            st.toast(f"已將 {full_name} 加入購物車！")
        st.write("---") # 分隔線

with col2:
    st.subheader("【 🛒 您的購物車 】")
    if not st.session_state.cart:
        st.write("購物車目前是空的喔！")
        total = 0
    else:
        total = 0
        # 顯示購物車明細並提供刪除按鈕
        for index, (food_info, price) in enumerate(st.session_state.cart):
            item_col1, item_col2 = st.columns(2)
            with item_col1:
                st.write(f"- **{food_info}**：${price}元")
            with item_col2:
                if st.button("❌", key=f"del_{index}"):
                    st.session_state.cart.pop(index)
                    st.rerun()
            
            total += price
        
        st.write("---")
        
        # 折扣碼輸入框
        coupon = st.text_input("🏷️ 輸入折扣碼 (提示: VIP90 )")
        if coupon == "VIP90":
            discount = int(total * 0.1)
            final_total = total - discount
            st.info(f"🎉 成功套用 9 折折扣碼！已為您折抵 ${discount} 元")
        else:
            if coupon != "":
                st.error("❌ 折扣碼無效，請重新輸入！")
            final_total = total
            
        st.markdown(f"### 💰 總金額：**${final_total} 元**")
        
        # 結帳與清空按鈕
        if st.button("🏁 確認結帳", type="primary"):
            st.success(f"🎉 點餐成功！請至櫃檯支付 ${final_total} 元，餐點製作中！")
            
        if st.button("🗑️ 清空購物車"):
            st.session_state.cart = []
            st.rerun()
