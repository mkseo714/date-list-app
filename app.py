import streamlit as st
import pandas as pd
import uuid
from streamlit_gsheets import GSheetsConnection

# --- 페이지 기본 설정 ---
st.set_page_config(page_title="우리의 데이트 리스트", layout="centered")

# --- 1. 구글 스프레드시트 DB 연결 ---
conn = st.connection("gsheets", type=GSheetsConnection)

# 데이터 불러오기
try:
    df = conn.read(worksheet="Sheet1", ttl=0)
    if df is None or df.empty or len(df.columns) == 0:
        df = pd.DataFrame(columns=["id", "title", "category", "is_done"])
    else:
        df['is_done'] = df['is_done'].astype(bool)
except Exception as e:
    st.error(f"구글 시트 연결 에러: {e}")
    df = pd.DataFrame(columns=["id", "title", "category", "is_done"])

# --- 세션 상태 초기화 ---
if 'edit_item_id' not in st.session_state:
    st.session_state['edit_item_id'] = None
if 'show_form' not in st.session_state:
    st.session_state['show_form'] = False
if 'show_success' not in st.session_state:
    st.session_state['show_success'] = False

# --- CSS 디자인 (모바일 최적화 및 심볼 버튼 투명화) ---
st.markdown("""
    <style>
    .block-container {
        padding-top: 1rem !important; padding-left: 1.2rem !important;
        padding-right: 1.2rem !important; max-width: 100% !important; overflow-x: hidden !important; 
    }
    hr { margin-top: 4px !important; margin-bottom: 4px !important; }
    h3 { padding-top: 0px !important; padding-bottom: 3px !important; margin-top: 0px !important; margin-bottom: 5px !important; }
    h1 { padding-bottom: 2px !important; font-size: 1.8rem !important; }
    
    .stCheckbox { margin-top: 0px !important; margin-bottom: 0px !important; padding-top: 0px !important; padding-bottom: 0px !important; }
    .stCheckbox > div { min-height: 24px !important; }
    
    /* 리스트 아이템 가로 정렬 강제 */
    [data-testid="stHorizontalBlock"]:has(.stCheckbox) { flex-direction: row !important; flex-wrap: nowrap !important; align-items: center !important; width: 100% !important; gap: 0px !important; }
    [data-testid="column"]:has(.stCheckbox) { min-width: 0 !important; padding: 0px !important; flex: 1 1 auto !important; width: calc(100% - 40px) !important; }
    
    /* 팝오버(수정/삭제) 메뉴 버튼 크기 */
    [data-testid="column"]:has([data-testid="stPopover"]) { min-width: 0 !important; padding: 0px !important; flex: 0 0 35px !important; width: 35px !important; margin-right: 5px !important; display: flex; justify-content: flex-end; }
    [data-testid="stPopover"] > button { padding: 0px !important; height: 30px !important; width: 30px !important; border: none !important; background: transparent !important; font-size: 1.3rem !important; color: #888 !important; }
    
    /* 🔥 [신규] 컨트롤 패널(토글+섞기심볼) 모바일 강제 한 줄 정렬 */
    [data-testid="stHorizontalBlock"]:has([data-testid="stToggle"]) { 
        flex-direction: row !important; 
        flex-wrap: nowrap !important; 
        align-items: center !important; 
    }
    
    /* 🔥 [신규] 섞기 버튼을 투명한 아이콘으로 만들고 가장 왼쪽으로 밀착 */
    [data-testid="stHorizontalBlock"]:has([data-testid="stToggle"]) div[data-testid="stButton"] > button {
        justify-content: flex-start !important;
        padding: 0px !important;
        border: none !important;
        background: transparent !important;
        font-size: 1.8rem !important;
        box-shadow: none !important;
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

# --- 2. 데이터 추가(Insert) 기능 ---
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
                new_row = pd.DataFrame([{"id": str(uuid.uuid4()), "title": title, "category": category, "is_done": False}])
                df = pd.concat([df, new_row], ignore_index=True)
                conn.update(worksheet="Sheet1", data=df)
                
                st.session_state['show_success'] = True
                st.session_state['show_form'] = False
                st.rerun()
        
        if st.button("닫기 🔺", use_container_width=True):
            st.session_state['show_form'] = False
            st.rerun()

st.divider()

# --- 컨트롤 패널 (토글 80%, 심볼 버튼 20% 비율 할당) ---
ctrl_col1, ctrl_col2 = st.columns([8, 2], vertical_alignment="center")
with ctrl_col1:
    hide_completed = st.toggle("👻 완료된 항목 숨기기", value=False)
with ctrl_col2:
    if st.button("🔀", help="리스트 순서 섞기", use_container_width=True):
        if not df.empty:
            df = df.sample(frac=1).reset_index(drop=True)
            conn.update(worksheet="Sheet1", data=df)
            st.rerun()

st.divider()

# --- 탭 메뉴 구조 ---
selected_tabs = st.tabs(TAB_LIST)

# --- 3. 데이터 조회 및 수정/삭제 기능 ---
if df.empty:
    st.info("아직 저장된 데이트 리스트가 없습니다.")
else:
    for i, tab_name in enumerate(TAB_LIST):
        with selected_tabs[i]:
            if tab_name == "전체":
                filtered_df = df
            else:
                filtered_df = df[df['category'] == tab_name]

            if hide_completed:
                filtered_df = filtered_df[filtered_df['is_done'] == False]

            if filtered_df.empty:
                if hide_completed:
                    st.info("아직 완료하지 않은 데이트가 없네요! 새로 추가해볼까요?")
                else:
                    st.info(f"'{tab_name}' 카테고리에 저장된 리스트가 없습니다.")
            else:
                st.subheader(f"📌 {tab_name} 리스트")
                
                for idx, row in filtered_df.iterrows():
                    item_id = str(row['id'])
                    item_category = row['category']
                    item_title = row['title']
                    item_is_done = bool(row['is_done'])

                    # [A] 수정 모드
                    if st.session_state['edit_item_id'] == item_id:
                        with st.container(border=True):
                            try:
                                default_idx = CATEGORY_LIST.index(item_category)
                            except ValueError:
                                default_idx = 0
                            
                            new_category = st.selectbox("카테고리수정", CATEGORY_LIST, index=default_idx, key=f"cat_{tab_name}_{item_id}")
                            new_title = st.text_input("내용수정", value=item_title, key=f"title_{tab_name}_{item_id}")
                            
                            btn_col1, btn_col2 = st.columns(2)
                            with btn_col1:
                                if st.button("💾 저장", key=f"save_{tab_name}_{item_id}", use_container_width=True):
                                    df.loc[df['id'] == item_id, ['title', 'category']] = [new_title, new_category]
                                    conn.update(worksheet="Sheet1", data=df)
                                    st.session_state['edit_item_id'] = None
                                    st.rerun()
                            with btn_col2:
                                if st.button("❌ 취소", key=f"cancel_{tab_name}_{item_id}", use_container_width=True):
                                    st.session_state['edit_item_id'] = None
                                    st.rerun()
                    
                    # [B] 일반 리스트 화면
                    else:
                        col1, col2 = st.columns([9, 1]) 
                        
                        with col1:
                            title_text = f"~~[{item_category}] {item_title}~~" if item_is_done else f"[{item_category}] {item_title}"
                            is_checked = st.checkbox(title_text, value=item_is_done, key=f"check_{tab_name}_{item_id}")
                            
                            if is_checked != item_is_done:
                                df.loc[df['id'] == item_id, 'is_done'] = is_checked
                                conn.update(worksheet="Sheet1", data=df)
                                st.rerun()
                                
                        with col2:
                            with st.popover("☰", use_container_width=False):
                                if st.button("✏️ 수정", key=f"edit_{tab_name}_{item_id}", use_container_width=True):
                                    st.session_state['edit_item_id'] = item_id
                                    st.rerun()
                                if st.button("🗑️ 삭제", key=f"del_{tab_name}_{item_id}", use_container_width=True):
                                    df = df[df['id'] != item_id]
                                    conn.update(worksheet="Sheet1", data=df)
                                    st.rerun()
                        
                        st.markdown("<hr style='margin: 4px 0px 4px 0px;'/>", unsafe_allow_html=True)
