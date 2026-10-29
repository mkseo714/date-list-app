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

            if filtered_df.empty:
                st.info(f"'{tab_name}' 카테고리에 저장된 리스트가 없습니다.")
            else:
                st.subheader(f"📌 {tab_name} 리스트")
                
                # 데이터프레임의 각 줄(row)을 순회하며 화면에 그리기
                for idx, row in filtered_df.iterrows():
                    item_id = row['id']
                    item_category = row['category']
                    item_title = row['title']
                    item_is_done = row['is_done']

                    # [A] 수정 모드 (key에 tab_name 추가)
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
                    
                    # [B] 일반 리스트 화면 (key에 tab_name 추가)
                    else:
                        col1, col2 = st.columns([9, 1]) 
                        
                        with col1:
                            title_text = f"~~[{item_category}] {item_title}~~" if item_is_done else f"[{item_category}] {item_title}"
                            
                            # 바로 여기서 에러가 났던 것입니다. 이름표(key)에 tab_name을 붙여 중복을 막았습니다.
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
