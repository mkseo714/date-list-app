import streamlit as st
from supabase import create_client

# Supabase API 연결 세팅
url = "https://qhskfxzfoghxncytwsep.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFoc2tmeHpmb2doeG5jeXR3c2VwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODU3NjE3NTAsImV4cCI6MjEwMTMzNzc1MH0.oUo8yh0BA0KGMxjztuvMkpLCFBkIVKaQHYX0m0pZM5s"
supabase = create_client(url, key)

st.set_page_config(page_title="우리의 데이트 리스트", layout="centered")

if 'edit_item_id' not in st.session_state:
    st.session_state['edit_item_id'] = None

# ★CSS 수정: 화면 밖으로 나가는 현상 완벽 방지★
st.markdown("""
    <style>
    /* 1. 컬럼들을 가로 한 줄로 묶되, 아이템 사이의 간격을 줄여서 화면 밖으로 밀려나는 것을 막음 */
    [data-testid="stHorizontalBlock"] {
        flex-wrap: nowrap !important;
        align-items: center !important; 
        gap: 5px !important; 
        width: 100% !important;
    }
    
    /* 2. 텍스트가 아무리 길어도 화면 밖으로 나가지 않고 안에서 줄어들게 만듦 */
    [data-testid="column"] {
        min-width: 0 !important; 
        flex-shrink: 1 !important;
    }

    /* 3. 버튼이 좁은 영역 안에 쏙 들어가도록 가로 100% 사용 설정 */
    .stButton > button { 
        padding: 0px 5px !important; 
        height: 35px !important; 
        min-height: 35px !important;
        width: 100% !important;
    }
    
    /* 4. 체크박스 높이 조절 */
    .stCheckbox { 
        margin-top: 5px !important; 
    }
    </style>
""", unsafe_allow_html=True)

st.title("📝 이거 하자!")
CATEGORY_LIST = ["🍽️ 맛집", "🎬 영화", "☕ 카페", "🏖️ 여행", "🎯 액티비티"]

# --- 1. 새로운 항목 추가 (위아래 배치 원복) ---
with st.form("new_idea_form", clear_on_submit=True):
    category = st.selectbox("카테고리", CATEGORY_LIST)
    title = st.text_input("내용", placeholder="어디갈까? / 뭘할까?")
    
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
            
            # [A] 수정 모드 (입력하기 편하게 위아래 배치로 변경)
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
            
            # [B] 일반 리스트 화면 (버튼이 잘리지 않도록 비율을 7 : 1.5 : 1.5 로 조정)
            else:
                col1, col2, col3 = st.columns([7, 1.5, 1.5])
                
                with col1:
                    title_text = f"~~[{idea['category']}] {idea['title']}~~" if idea['is_done'] else f"[{idea['category']}] {idea['title']}"
                    is_checked = st.checkbox(title_text, value=idea['is_done'], key=f"check_{idea['id']}")
                    if is_checked != idea['is_done']:
                        supabase.table("date_ideas").update({"is_done": is_checked}).eq("id", idea['id']).execute()
                        st.rerun()
                        
                with col2:
                    if st.button("✏️", key=f"edit_{idea['id']}", help="수정"):
                        st.session_state['edit_item_id'] = idea['id']
                        st.rerun()
                        
                with col3:
                    if st.button("🗑️", key=f"del_{idea['id']}", help="삭제"):
                        supabase.table("date_ideas").delete().eq("id", idea['id']).execute()
                        st.rerun()
                        
                st.markdown("<hr style='margin: 5px 0px 10px 0px;'/>", unsafe_allow_html=True)

except Exception as e:
    st.error(f"데이터베이스 연결 에러: {e}")
