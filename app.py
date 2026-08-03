import streamlit as st
from supabase import create_client

# Supabase API 연결 세팅
url = "https://qhskfxzfoghxncytwsep.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFoc2tmeHpmb2doeG5jeXR3c2VwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODU3NjE3NTAsImV4cCI6MjEwMTMzNzc1MH0.oUo8yh0BA0KGMxjztuvMkpLCFBkIVKaQHYX0m0pZM5s"
supabase = create_client(url, key)

# 모바일 화면에 맞게 꽉 차게 설정
st.set_page_config(page_title="우리의 데이트 리스트", layout="centered")

st.title("📝 이거 하자!")

# 사용할 카테고리 목록 지정
CATEGORY_LIST = ["🍽️ 맛집", "🎬 영화", "☕ 카페", "🏖️ 여행", "🎯 액티비티"]

# --- 1. 새로운 데이트 항목 추가 UI ---
with st.form("new_idea_form", clear_on_submit=True):
    category = st.selectbox("카테고리", CATEGORY_LIST)
    title = st.text_input("어디갈까? / 뭘할까?")
    submitted = st.form_submit_button("추가하기")
    
    if submitted and title:
        supabase.table("date_ideas").insert({"title": title, "category": category, "is_done": False}).execute()
        st.success("추가 완료!")
        st.rerun()

st.divider()
st.subheader("📌 저장된 리스트")

# --- 2. 리스트 출력 및 수정/삭제 기능 ---
try:
    response = supabase.table("date_ideas").select("*").order("created_at", desc=True).execute()
    ideas = response.data

    if not ideas:
        st.info("아직 저장된 데이트 리스트가 없습니다. 위에서 추가해 보세요!")
    else:
        for idea in ideas:
            # 완료 여부에 따라 취소선 처리
            title_text = f"~~[{idea['category']}] {idea['title']}~~" if idea['is_done'] else f"[{idea['category']}] {idea['title']}"
            
            # 모바일 화면을 고려해 가로를 8:2 비율로 나눔 (체크박스 영역 / 삭제 버튼 영역)
            col1, col2 = st.columns([8, 2])
            
            with col1:
                # [체크박스 기능] 상태가 다를 때만 DB 업데이트 (체크/해제 모두 가능)
                is_checked = st.checkbox(title_text, value=idea['is_done'], key=f"check_{idea['id']}")
                if is_checked != idea['is_done']:
                    supabase.table("date_ideas").update({"is_done": is_checked}).eq("id", idea['id']).execute()
                    st.rerun()

            with col2:
                # [삭제 기능] 휴지통 버튼
                if st.button("🗑️", key=f"del_{idea['id']}"):
                    supabase.table("date_ideas").delete().eq("id", idea['id']).execute()
                    st.rerun()
            
            # [수정 기능] 클릭하면 아래로 펼쳐지는 메뉴(Expander) 사용
            with st.expander("✏️ 내용 수정하기"):
                # 기존에 선택했던 카테고리를 기본값으로 띄워주기 위한 로직
                try:
                    default_index = CATEGORY_LIST.index(idea['category'])
                except ValueError:
                    default_index = 0
                    
                with st.form(f"edit_form_{idea['id']}"):
                    edit_category = st.selectbox("카테고리 변경", CATEGORY_LIST, index=default_index)
                    edit_title = st.text_input("내용 변경", value=idea['title'])
                    edit_submit = st.form_submit_button("저장")
                    
                    if edit_submit:
                        supabase.table("date_ideas").update({
                            "title": edit_title, 
                            "category": edit_category
                        }).eq("id", idea['id']).execute()
                        st.rerun()
            
            # 각 항목 사이에 얇은 구분선 추가 (시각적 분리)
            st.markdown("<hr style='margin: 0px; margin-bottom: 15px;'/>", unsafe_allow_html=True)

except Exception as e:
    st.error(f"데이터베이스 연결 에러: {e}")
