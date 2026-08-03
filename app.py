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
if 'show_form' not in st.session_state:
    st.session_state['show_form'] = False
if 'show_success' not in st.session_state:
    st.session_state['show_success'] = False

# ★CSS: 간격 압축 및 리스트 디자인 최적화★
st.markdown("""
    <style>
    .block-container {
        padding-top: 1rem !important;
        padding-left: 1.2rem !important;
        padding-right: 1.2rem !important;
        max-width: 100% !important;
        overflow-x: hidden !important; 
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

st.title("📝 우리 이거 하자!")

CATEGORY_LIST = ["🍽️ 맛집", "🎬 영화", "🏖️ 여행", "🎯 액티비티"]
TAB_LIST = ["전체"] + CATEGORY_LIST

# --- 성공 메시지 ---
if st.session_state['show_success']:
    st.success("데이트 목록에 추가되었어요! 🥰")
    st.session_state['show_success'] = False 

# --- 새로운 항목 추가 폼 ---
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

# --- 🌟 [탭 메뉴 구조 도입] 상단에 고정되는 네이티브 탭 인터페이스 ---
selected_tab = st.tabs(TAB_LIST)

# --- 데이터 불러오기 ---
try:
    response = supabase.table("date_ideas").select("*").order("created_at", desc=True).execute()
    ideas = response.data

    if not ideas:
        st.info("아직 저장된 데이트 리스트가 없습니다.")
    else:
        # 각 탭(전체, 맛집, 영화, 여행, 액티비티)별로 리스트 매핑
        for i, tab_name in enumerate(TAB_LIST):
            with selected_tab[i]:
                # 탭 이름에 맞춰 필터링
                if tab_name == "전체":
                    filtered_ideas = ideas
                else:
                    filtered_ideas = [idea for idea in ideas if idea['category'] == tab_name]

                if not filtered_ideas:
                    st.info(f"'{tab_name}' 카테고리에 저장된 리스트가 없습니다.")
                else:
                    st.subheader(f"📌 {tab_name} 리스트")
                    
                    for idea in filtered_ideas:
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
