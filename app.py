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
if 'show_form' not in st.session_state:
    st.session_state['show_form'] = False
if 'show_success' not in st.session_state:
    st.session_state['show_success'] = False

# ★CSS: 상단 영역(타이틀~필터) 고정(Sticky) 및 간격 압축★
st.markdown("""
    <style>
    .block-container {
        padding-top: 1rem !important;
        padding-left: 1.2rem !important;
        padding-right: 1.2rem !important;
        max-width: 100% !important;
        overflow-x: hidden !important; 
    }

    /* 🌟 상단 핵심 영역을 화면 상단에 고정하는 시각적 트릭 */
    .sticky-header {
        position: sticky;
        top: 0;
        z-index: 999;
        background-color: #FFFFFF; /* 라이트 모드 배경색 (화면 겹침 방지) */
        padding-top: 5px;
        padding-bottom: 5px;
        margin-bottom: 10px;
    }

    hr {
        margin-top: 4px !important;
        margin-bottom: 4px !important;
    }
    h3 {
        padding-top: 0px !important;
        padding-bottom: 3px !important;
        margin-top: 0px !important;
        margin-bottom: 5px !important;
    }
    h1 {
        padding-bottom: 2px !important;
        font-size: 1.8rem !important;
    }

    .stCheckbox { 
        margin-top: 0px !important; 
        margin-bottom: 0px !important;
        padding-top: 0px !important;
        padding-bottom: 0px !important;
    }
    
    .stCheckbox > div {
        min-height: 24px !important;
    }

    [data-testid="stHorizontalBlock"]:has(.stCheckbox) {
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
        width: 100% !important;
        gap: 0px !important; 
    }
    
    [data-testid="column"]:has(.stCheckbox) {
        min-width: 0 !important;
        padding: 0px !important;
        flex: 1 1 auto !important;
        width: calc(100% - 40px) !important; 
    }

    [data-testid="column"]:has([data-testid="stPopover"]) {
        min-width: 0 !important;
        padding: 0px !important;
        flex: 0 0 35px !important;
        width: 35px !important;
        margin-right: 5px !important; 
        display: flex;
        justify-content: flex-end;
    }

    [data-testid="stPopover"] > button {
        padding: 0px !important;
        height: 30px !important;
        width: 30px !important; 
        border: none !important;
        background: transparent !important;
        font-size: 1.3rem !important; 
        color: #888 !important; 
    }
    </style>
""", unsafe_allow_html=True)

CATEGORY_LIST = ["🍽️ 맛집", "🎬 영화", "🏖️ 여행", "🎯 액티비티"]
FILTER_LIST = ["전체"] + CATEGORY_LIST

# --- 🌟 [고정 영역 시작] 타이틀, 추가 버튼, 필터 버튼을 하나의 틀로 묶음 ---
st.markdown('<div class="sticky-header">', unsafe_allow_html=True)

st.title("📝 다음에 우리 여기 가자!")

# 성공 메시지
if st.session_state['show_success']:
    st.success("데이트 목록에 추가되었어요! 🥰")
    st.session_state['show_success'] = False 

# 새로운 항목 추가
if not st.session_state['show_form']:
    if st.button("➕ 새로운 데이트 추가하기", use_container_width=True):
        st.session_state['show_form'] = True
        st.rerun()
else:
    with st.container(border=True):
        with st.form("new_idea_form", clear_on_submit=True):
            category = st.selectbox("카테고리", CATEGORY_LIST)
            title = st.text_input("내용", placeholder="어디갈까? / 뭘할까?")
            
            submitted = st.form_submit_button("✅ 추가하기", use_container_width=True)
            if submitted and title:
                supabase.table("date_ideas").insert({"title": title, "category": category, "is_done": False}).execute()
                st.session_state['show_success'] = True
                st.session_state['show_form'] = False
                st.rerun()
        
        if st.button("닫기 🔺", use_container_width=True):
            st.session_state['show_form'] = False
            st.rerun()

st.divider()

# 카테고리 필터 버튼
st.session_state['current_filter'] = st.radio(
    "카테고리 필터", 
    FILTER_LIST, 
    horizontal=True, 
    label_visibility="collapsed"
)

st.markdown('</div>', unsafe_allow_html=True)
# --- [고정 영역 끝] ---

st.subheader("📌 저장된 리스트")

# --- 3. 리스트 출력 및 메뉴 (여기는 스크롤 가능) ---
try:
    response = supabase.table("date_ideas").select("*").order("created_at", desc=True).execute()
    ideas = response.data

    if not ideas:
        st.info("아직 저장된 데이트 리스트가 없습니다.")
    else:
        if st.session_state['current_filter'] != "전체":
            ideas = [idea for idea in ideas if idea['category'] == st.session_state['current_filter']]
            
        for idea in ideas:
            
            # [A] 수정 모드
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
                col1, col2 = st.columns([9, 1]) 
                
                with col1:
                    title_text = f"~~[{idea['category']}] {idea['title']}~~" if idea['is_done'] else f"[{idea['category']}] {idea['title']}"
                    is_checked = st.checkbox(title_text, value=idea['is_done'], key=f"check_{idea['id']}")
                    if is_checked != idea['is_done']:
                        supabase.table("date_ideas").update({"is_done": is_checked}).eq("id", idea['id']).execute()
                        st.rerun()
                        
                with col2:
                    with st.popover("☰", use_container_width=False):
                        if st.button("✏️ 수정", key=f"edit_{idea['id']}", use_container_width=True):
                            st.session_state['edit_item_id'] = idea['id']
                            st.rerun()
                        if st.button("🗑️ 삭제", key=f"del_{idea['id']}", use_container_width=True):
                            supabase.table("date_ideas").delete().eq("id", idea['id']).execute()
                            st.rerun()
                        
                st.markdown("<hr style='margin: 4px 0px 4px 0px;'/>", unsafe_allow_html=True)

except Exception as e:
    st.error(f"데이터베이스 연결 에러: {e}")
