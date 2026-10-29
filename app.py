import streamlit as st
import pandas as pd
import uuid
import time
from streamlit_gsheets import GSheetsConnection

# --- 페이지 기본 설정 ---
st.set_page_config(page_title="우리의 데이트 리스트", layout="centered")

# --- 무한 루프 방지용 세션 상태 추가 ---
if 'last_update_time' not in st.session_state:
    st.session_state['last_update_time'] = 0
if 'local_df' not in st.session_state:
    st.session_state['local_df'] = pd.DataFrame()
if 'edit_item_id' not in st.session_state:
    st.session_state['edit_item_id'] = None
if 'show_form' not in st.session_state:
    st.session_state['show_form'] = False
if 'show_success' not in st.session_state:
    st.session_state['show_success'] = False

# --- 1. 구글 스프레드시트 DB 연결 ---
conn = st.connection("gsheets", type=GSheetsConnection)

# 🔥 [핵심 방어 코드] 저장 함수
def save_to_db(dataframe):
    save_df = dataframe.copy()
    save_df['is_done'] = save_df['is_done'].apply(lambda x: "TRUE" if x else "FALSE")
    conn.update(worksheet="Sheet1", data=save_df)
    st.cache_data.clear() 
    
    # 저장 직후 5초 동안은 느린 구글 서버 대신 '내 컴퓨터의 최신 기억'을 믿도록 저장해둡니다.
    st.session_state['local_df'] = dataframe.copy()
    st.session_state['last_update_time'] = time.time()

# --- 2. 데이터 불러오기 (철통 방어 로직 적용) ---
try:
    raw_df = conn.read(worksheet="Sheet1", ttl=5)
    
    # 🔥 내가 수정한 지 5초가 안 지났다면, 예전 데이터(raw_df)를 무시하고 최신 데이터(local_df)를 사용!
    if time.time() - st.session_state['last_update_time'] < 5 and not st.session_state['local_df'].empty:
        df = st.session_state['local_df'].copy()
    else:
        if raw_df is None or raw_df.empty or len(raw_df.columns) == 0:
            df = pd.DataFrame(columns=["id", "title", "category", "is_done"])
        else:
            df = raw_df.copy()
            if 'is_done' not in df.columns:
                df['is_done'] = False
            df['is_done'] = df['is_done'].apply(
                lambda x: True if str(x).strip().upper() in ['TRUE', '1', '1.0'] else False
            )
except Exception as e:
    st.error(f"⚠️ 구글 서버 지연으로 데이터를 불러오지 못했습니다. DB 보호를 위해 앱을 일시 정지합니다. 새로고침 해주세요. (에러: {e})")
    st.stop() 

# --- CSS 디자인 ---
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
    
    [data-testid="stHorizontalBlock"]:has(.stCheckbox) { flex-direction: row !important; flex-wrap: nowrap !important; align-items: center !important; width: 100% !important; gap: 0px !important; }
    [data-testid="column"]:has(.stCheckbox) { min-width: 0 !important; padding: 0px !important; flex: 1 1 auto !important; width: calc(100% - 40px) !important; }
    
    [data-testid="column"]:has([data-testid="stPopover"]) { min-width: 0 !important; padding: 0px !important; flex: 0 0 35px !important; width: 35px !important; margin-right: 5px !important; display: flex; justify-content: flex-end; }
    [data-testid="stPopover"] > button { padding: 0px !important; height: 30px !important; width: 30px !important; border: none !important; background: transparent !important; font-size: 1.3rem !important; color: #888 !important; }
    
    [data-testid="stHorizontalBlock"]:has([data-testid="stToggle"]) { 
        flex-direction: row !important; 
        flex-wrap: nowrap !important; 
        align-items: center !important; 
    }
    [data-testid="stHorizontalBlock"]:has([data-testid="stToggle"]) div[data-testid="stButton"] > button {
        border: none !important;
        background: transparent !important;
        font-size: 1.5rem !important;
        box-shadow: none !important;
        padding: 0px !important;
        margin-left: -15px !important; 
    }
    </style>
""", unsafe_allow_html=True)

st.title("📝 우리 이거 하자!")

CATEGORY_LIST = ["🍽️ 맛집", "🎬 영화", "🏖️ 여행", "🎯 액티비티"]
TAB_LIST = ["전체"] + CATEGORY_LIST

if st.session_state['show_success']:
    st.success("데이트 목록에 추가되었어요! 🥰")
    st.session_state['show_success'] = False 

# --- 3. 데이터 추가 기능 ---
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
                save_to_db(df) 
                st.session_state['show_success'] = True
                st.session_state['show_form'] = False
                st.rerun()
        if st.button("닫기 🔺", use_container_width=True):
            st.session_state['show_form'] = False
            st.rerun()

st.divider()

# --- 컨트롤 패널 ---
ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([4, 1, 5], vertical_alignment="center")
with ctrl_col1:
    hide_completed = st.toggle("👻 완료된 항목 숨기기", value=False)
with ctrl_col2:
    if st.button("🔀", help="리스트 순서 섞기"):
        if not df.empty:
            df = df.sample(frac=1).reset_index(drop=True)
            save_to_db(df)
            st.rerun()
with ctrl_col3:
    st.empty()

st.divider()

# --- 탭 메뉴 구조 및 리스트 출력 ---
selected_tabs = st.tabs(TAB_LIST)

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
                                    save_to_db(df) 
                                    st.session_state['edit_item_id'] = None
                                    st.rerun()
                            with btn_col2:
                                if st.button("❌ 취소", key=f"cancel_{tab_name}_{item_id}", use_container_width=True):
                                    st.session_state['edit_item_id'] = None
                                    st.rerun()
                    else:
                        col1, col2 = st.columns([9, 1]) 
                        with col1:
                            title_text = f"~~[{item_category}] {item_title}~~" if item_is_done else f"[{item_category}] {item_title}"
                            
                            is_checked = st.checkbox(title_text, value=item_is_done, key=f"check_{tab_name}_{item_id}")
                            
                            # 상태가 바뀌었을 때만 DB를 업데이트하고 다른 탭과 동기화
                            if is_checked != item_is_done:
                                df.loc[df['id'] == item_id, 'is_done'] = is_checked
                                
                                # 🔥 전체 탭과 카테고리 탭의 체크 상태를 강제로 일치시켜 루프 차단
                                for t in TAB_LIST:
                                    if f"check_{t}_{item_id}" in st.session_state:
                                        st.session_state[f"check_{t}_{item_id}"] = is_checked
                                        
                                save_to_db(df)
                                st.rerun()
                                
                        with col2:
                            with st.popover("☰", use_container_width=False):
                                if st.button("✏️ 수정", key=f"edit_{tab_name}_{item_id}", use_container_width=True):
                                    st.session_state['edit_item_id'] = item_id
                                    st.rerun()
                                if st.button("🗑️ 삭제", key=f"del_{tab_name}_{item_id}", use_container_width=True):
                                    df = df[df['id'] != item_id]
                                    save_to_db(df)
                                    st.rerun()
                        
                        st.markdown("<hr style='margin: 4px 0px 4px 0px;'/>", unsafe_allow_html=True)
