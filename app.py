import streamlit as st
from supabase import create_client

# Supabase API 연결 세팅
url = "https://qhskfxzfoghxncytwsep.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFoc2tmeHpmb2doeG5jeXR3c2VwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODU3NjE3NTAsImV4cCI6MjEwMTMzNzc1MH0.oUo8yh0BA0KGMxjztuvMkpLCFBkIVKaQHYX0m0pZM5s"
supabase = create_client(url, key)

st.set_page_config(page_title="우리의 데이트 리스트", layout="centered")

# 수정 모드를 관리하기 위한 세션 상태 초기화
if 'edit_item_id' not in st.session_state:
    st.session_state['edit_item_id'] = None

# 모바일 UI 깔끔하게 다듬기 (버튼 크기 및 여백 최소화)
st.markdown("""
    <style>
    .stButton > button { padding: 0px 5px !important; height: 35px; }
    </style>
""", unsafe_allow_html=True)

st.title("📝 다음에 우리 여기 가자!")
CATEGORY_LIST = ["🍽️ 맛집", "🎬 영화", "☕ 카페", "🏖️ 여행", "🎯 액티비티"]

# --- 1. 새로운 항목 추가 ---
with st.form("new_idea_form", clear_on_submit=True):
    col1, col2 = st.columns([3, 7])
    with col1:
        category = st.selectbox("카테고리", CATEGORY_LIST, label_visibility="collapsed")
    with col2:
        title = st.text_input("내용", placeholder="어디갈까? / 뭘할까?", label_visibility="collapsed")
    
    submitted = st.form_submit_button("추가하기", use_container_width=True)
    if submitted and title:
        supabase.table("date_ideas").insert({"title": title, "category": category, "is_done": False}).execute()
        st.success("추가 완료!")
        st.rerun()

st.divider()
st.subheader("📌 저장된 리스트")

# --- 2. 리스트 출력 및 아이콘 배치 ---
try:
    response = supabase.table("date_ideas").select("*").order("created_at", desc=True).execute()
    ideas = response.data

    if not ideas:
        st.info("아직 저장된 데이트 리스트가 없습니다.")
    else:
        for idea in ideas:
            
            # [A] 수정 아이콘을 눌러 '수정 모드'가 된 항목의 화면
            if st.session_state['edit_item_id'] == idea['id']:
                with st.container(border=True):
                    # 기본 카테고리 인덱스 찾기
                    try:
                        default_idx = CATEGORY_LIST.index(idea['category'])
                    except ValueError:
                        default_idx = 0
                        
                    edit_col1, edit_col2 = st.columns([4, 6])
                    with edit_col1:
                        new_category = st.selectbox("카테고리수정", CATEGORY_LIST, index=default_idx, key=f"cat_{idea['id']}", label_visibility="collapsed")
                    with edit_col2:
                        new_title = st.text_input("내용수정", value=idea['title'], key=f"title_{idea['id']}", label_visibility="collapsed")
                    
                    btn_col1, btn_col2 = st.columns(2)
                    with btn_col1:
                        if st.button("💾 저장", key=f"save_{idea['id']}", use_container_width=True):
                            supabase.table("date_ideas").update({"title": new_title, "category": new_category}).eq("id", idea['id']).execute()
                            st.session_state['edit_item_id'] = None # 수정 모드 종료
                            st.rerun()
                    with btn_col2:
                        if st.button("❌ 취소", key=f"cancel_{idea['id']}", use_container_width=True):
                            st.session_state['edit_item_id'] = None # 수정 모드 종료
                            st.rerun()
            
            # [B] 평상시 '일반 모드' 화면 (우측에 작은 아이콘 배치)
            else:
                # 비율: 체크박스 글씨(7.5), 수정 아이콘(1.2), 삭제 아이콘(1.3)
                col1, col2, col3 = st.columns([7.5, 1.2, 1.3])
                
                with col1:
                    title_text = f"~~[{idea['category']}] {idea['title']}~~" if idea['is_done'] else f"[{idea['category']}] {idea['title']}"
                    is_checked = st.checkbox(title_text, value=idea['is_done'], key=f"check_{idea['id']}")
                    if is_checked != idea['is_done']:
                        supabase.table("date_ideas").update({"is_done": is_checked}).eq("id", idea['id']).execute()
                        st.rerun()
                        
                with col2:
                    if st.button("✏️", key=f"edit_{idea['id']}"):
                        # 클릭한 항목의 id를 세션에 저장하여 수정 모드로 전환
                        st.session_state['edit_item_id'] = idea['id']
                        st.rerun()
                        
                with col3:
                    if st.button("🗑️", key=f"del_{idea['id']}"):
                        supabase.table("date_ideas").delete().eq("id", idea['id']).execute()
                        st.rerun()
                        
                # 항목 간 얇은 구분선
                st.markdown("<hr style='margin: 5px 0px 10px 0px;'/>", unsafe_allow_html=True)

except Exception as e:
    st.error(f"데이터베이스 연결 에러: {e}")
