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

# ★모바일 화면 밀림 및 버튼 늘어남 현상 완벽 해결 CSS★
st.markdown("""
    <style>
    /* 1. 모바일에서 화면이 작아져도 두 줄로 나뉘지 않게 강제 한 줄 유지 */
    [data-testid="stHorizontalBlock"] {
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
    }
    
    /* 2. 컬럼 기본 여백 0으로 초기화 */
    [data-testid="column"] {
        min-width: 0 !important;
        padding: 0px !important;
    }

    /* 3. 체크박스가 들어있는 컬럼(텍스트 영역)은 유연하게 최대한 넓게 차지 */
    [data-testid="column"]:has(.stCheckbox) {
        flex: 1 1 auto !important;
        width: 100% !important;
    }

    /* 4. 팝오버(설정버튼)가 들어있는 컬럼은 우측 끝 40px로 작게 고정 */
    [data-testid="column"]:has([data-testid="stPopover"]) {
        flex: 0 0 40px !important;
        width: 40px !important;
    }

    /* 5. 톱니바퀴 버튼을 배경 없는 투명하고 작은 아이콘처럼 디자인 */
    [data-testid="stPopover"] > button {
        padding: 0px !important;
        height: 35px !important;
        width: 100% !important;
        border: none !important;
        background: transparent !important;
        font-size: 1.2rem !important;
    }
    
    /* 6. 체크박스 텍스트 상하 위치 미세 조정 */
    .stCheckbox { margin-top: 5px !important; }
    </style>
""", unsafe_allow_html=True)

st.title("📝 이거 하자!")

# 카페 제거 및 카테고리 필터 세팅
CATEGORY_LIST = ["🍽️ 맛집", "🎬 영화", "🏖️ 여행", "🎯 액티비티"]
FILTER_LIST = ["전체"] + CATEGORY_LIST

# --- 1. 새로운 항목 추가 (평소엔 숨겨져 있는 화살표 확장형 폼) ---
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
# 가로로 정렬되는 버튼형 라디오 사용
st.session_state['current_filter'] = st.radio(
    "카테고리 필터", 
    FILTER_LIST, 
    horizontal=True, 
    label_visibility="collapsed"
)

st.subheader("📌 저장된 리스트")

# --- 3. 리스트 출력 및 수정/삭제 팝오버 메뉴 ---
try:
    response = supabase.table("date_ideas").select("*").order("created_at", desc=True).execute()
    ideas = response.data

    if not ideas:
        st.info("아직 저장된 데이트 리스트가 없습니다.")
    else:
        # 상단에서 선택한 버튼에 따라 리스트 필터링
        if st.session_state['current_filter'] != "전체":
            ideas = [idea for idea in ideas if idea['category'] == st.session_state['current_filter']]
            
        for idea in ideas:
            
            # [A] ⚙️ 설정에서 '수정'을 눌렀을 때 열리는 모드
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
            
            # [B] 일반 리스트 화면
            else:
                col1, col2 = st.columns([9, 1]) # 가로 비율 부여 (CSS가 모바일에서 이 비율을 강제로 유지시켜 줌)
                
                # 텍스트 및 체크박스 영역
                with col1:
                    title_text = f"~~[{idea['category']}] {idea['title']}~~" if idea['is_done'] else f"[{idea['category']}] {idea['title']}"
                    is_checked = st.checkbox(title_text, value=idea['is_done'], key=f"check_{idea['id']}")
                    if is_checked != idea['is_done']:
                        supabase.table("date_ideas").update({"is_done": is_checked}).eq("id", idea['id']).execute()
                        st.rerun()
                        
                # 우측 끝 설정(톱니바퀴) 버튼 영역
                with col2:
                    with st.popover("⚙️", use_container_width=False):
                        if st.button("✏️ 수정", key=f"edit_{idea['id']}", use_container_width=True):
                            st.session_state['edit_item_id'] = idea['id']
                            st.rerun()
                        if st.button("🗑️ 삭제", key=f"del_{idea['id']}", use_container_width=True):
                            supabase.table("date_ideas").delete().eq("id", idea['id']).execute()
                            st.rerun()
                        
                st.markdown("<hr style='margin: 0px 0px 10px 0px;'/>", unsafe_allow_html=True)

except Exception as e:
    st.error(f"데이터베이스 연결 에러: {e}")
