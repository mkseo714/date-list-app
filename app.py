import streamlit as st
from supabase import create_client

# Supabase API 연결 세팅
url = "https://qhskfxzfoghxncytwsep.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFoc2tmeHpmb2doeG5jeXR3c2VwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODU3NjE3NTAsImV4cCI6MjEwMTMzNzc1MH0.oUo8yh0BA0KGMxjztuvMkpLCFBkIVKaQHYX0m0pZM5s"
supabase = create_client(url, key)

st.set_page_config(page_title="우리의 데이트 리스트", layout="centered")

# 세션 상태 초기화
if 'edit_item_id' not in st.session_state:
    st.session_state['edit_item_id'] = None
if 'current_filter' not in st.session_state:
    st.session_state['current_filter'] = "전체"

# CSS 정리: 지저분했던 강제 여백 제거하고 심플하게 유지
st.markdown("""
    <style>
    /* 체크박스 위치 미세조정 */
    .stCheckbox { 
        margin-top: 5px !important; 
    }
    /* 팝오버(옵션) 버튼을 둥글고 작게 만들어 화면 밖으로 나가지 않게 함 */
    [data-testid="stPopover"] > button {
        padding: 0px !important;
        height: 35px !important;
        width: 100% !important;
        border-radius: 8px !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📝 이거 하자!")

# 카페 카테고리 삭제 및 필터 리스트 생성
CATEGORY_LIST = ["🍽️ 맛집", "🎬 영화", "🏖️ 여행", "🎯 액티비티"]
FILTER_LIST = ["전체"] + CATEGORY_LIST

# --- 1. 새로운 항목 추가 (숨겨진 확장 폼) ---
with st.expander("➕ 새로운 데이트 추가하기"):
    with st.form("new_idea_form", clear_on_submit=True):
        category = st.selectbox("카테고리", CATEGORY_LIST)
        title = st.text_input("내용", placeholder="어디갈까? / 뭘할까?")
        
        submitted = st.form_submit_button("추가하기", use_container_width=True)
        if submitted and title:
            supabase.table("date_ideas").insert({"title": title, "category": category, "is_done": False}).execute()
            st.success("추가 완료!")
            st.rerun()

st.divider()

# --- 2. 카테고리 필터 버튼 ---
# 모바일에서도 가로로 예쁘게 정렬되는 라디오 버튼 형태 사용
st.session_state['current_filter'] = st.radio(
    "카테고리 필터", 
    FILTER_LIST, 
    horizontal=True, 
    label_visibility="collapsed"
)

st.subheader("📌 저장된 리스트")

# --- 3. 리스트 출력 및 옵션 버튼 ---
try:
    response = supabase.table("date_ideas").select("*").order("created_at", desc=True).execute()
    ideas = response.data

    if not ideas:
        st.info("아직 저장된 데이트 리스트가 없습니다.")
    else:
        # 선택된 필터에 따라 리스트 걸러내기
        if st.session_state['current_filter'] != "전체":
            ideas = [idea for idea in ideas if idea['category'] == st.session_state['current_filter']]
            
        for idea in ideas:
            
            # [A] 수정 모드 (입력 폼)
            if st.session_state['edit_item_id'] == idea['id']:
                with st.container(border=True):
                    try:
                        default_idx = CATEGORY_LIST.index(idea['category'])
                    except ValueError:
                        default_idx = 0
                        
                    new_category = st.selectbox("카테고리수정", CATEGORY_LIST, index=default_idx, key=f"cat_{idea['id']}")
                    new_title = st.text_input("내용수정", value=idea['title'], key=f"title_{idea['id']}")
                    
                    btn_col1, btn_col2 = st.columns(2)
                    with btn_col1:
                        if st.button("💾 저장", key=f"save_{idea['id']}", use_container_width=True):
                            supabase.table("date_ideas").update({"title": new_title, "category": new_category}).eq("id", idea['id']).execute()
                            st.session_state['edit_item_id'] = None
                            st.rerun()
                    with btn_col2:
                        if st.button("❌ 취소", key=f"cancel_{idea['id']}", use_container_width=True):
                            st.session_state['edit_item_id'] = None
                            st.rerun()
            
            # [B] 일반 리스트 화면 (더보기 메뉴 활용으로 잘림 현상 완벽 해결)
            else:
                # 텍스트(8.5) vs 설정버튼(1.5) 비율
                col1, col2 = st.columns([8.5, 1.5])
                
                with col1:
                    title_text = f"~~[{idea['category']}] {idea['title']}~~" if idea['is_done'] else f"[{idea['category']}] {idea['title']}"
                    is_checked = st.checkbox(title_text, value=idea['is_done'], key=f"check_{idea['id']}")
                    if is_checked != idea['is_done']:
                        supabase.table("date_ideas").update({"is_done": is_checked}).eq("id", idea['id']).execute()
                        st.rerun()
                        
                with col2:
                    # 톱니바퀴 버튼을 누르면 아래로 수정/삭제 메뉴가 펼쳐짐
                    with st.popover("⚙️", use_container_width=True):
                        if st.button("✏️ 수정", key=f"edit_{idea['id']}", use_container_width=True):
                            st.session_state['edit_item_id'] = idea['id']
                            st.rerun()
                        if st.button("🗑️ 삭제", key=f"del_{idea['id']}", use_container_width=True):
                            supabase.table("date_ideas").delete().eq("id", idea['id']).execute()
                            st.rerun()
                        
                st.markdown("<hr style='margin: 0px 0px 10px 0px;'/>", unsafe_allow_html=True)

except Exception as e:
    st.error(f"데이터베이스 연결 에러: {e}")
