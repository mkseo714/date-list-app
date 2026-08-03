import streamlit as st
from supabase import create_client

# Supabase API 연결 세팅
url = "https://qhskfxzfoghxncytwsep.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFoc2tmeHpmb2doeG5jeXR3c2VwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODU3NjE3NTAsImV4cCI6MjEwMTMzNzc1MH0.oUo8yh0BA0KGMxjztuvMkpLCFBkIVKaQHYX0m0pZM5s"
supabase = create_client(url, key)

# 모바일 화면에 맞게 꽉 차게 설정
st.set_page_config(page_title="우리의 데이트 리스트", layout="centered")

st.title("📝 다음에 우리 이거 하자!")

# 새로운 데이트 항목 추가 UI
with st.form("new_idea_form", clear_on_submit=True):
    category = st.selectbox("카테고리", ["🍽️ 맛집", "🎬 영화", "☕ 카페", "🏖️ 여행"])
    title = st.text_input("어디갈까? / 뭘할까?")
    submitted = st.form_submit_button("추가하기")
    
    # 추가하기 버튼을 눌렀을 때 API 통신(Insert)
    if submitted and title:
        supabase.table("date_ideas").insert({"title": title, "category": category, "is_done": False}).execute()
        st.success("추가 완료!")
        st.rerun() # 화면 새로고침

# 저장된 데이트 리스트 불러오기 API 통신(Select)
st.divider()
st.subheader("📌 저장된 리스트")

response = supabase.table("date_ideas").select("*").order("created_at", desc=True).execute()
ideas = response.data

# 체크박스 형태로 리스트 출력
for idea in ideas:
    # 이미 완료된 항목은 취소선 처리
    if idea['is_done']:
        st.write(f"~~[{idea['category']}] {idea['title']}~~")
    else:
        # 체크박스 클릭 시 DB 업데이트 (Update)
        if st.checkbox(f"[{idea['category']}] {idea['title']}", key=idea['id']):
            supabase.table("date_ideas").update({"is_done": True}).eq("id", idea['id']).execute()
            st.rerun()