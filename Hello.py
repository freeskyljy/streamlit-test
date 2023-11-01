# Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import streamlit as st
import sqlite3
import datetime
import pandas as pd
import hashlib

st.title("Gold Daughter//Login")

# SQLite3 데이터베이스 연결
user_data_conn = sqlite3.connect('user_data.db')
user_data_cursor = user_data_conn.cursor()

# SQLite3 데이터베이스 연결 (카운트 데이터용)
count_data_conn = sqlite3.connect('count_data.db')
count_data_cursor = count_data_conn.cursor()

# SQLite3 로그 데이터베이스 연결
log_conn = sqlite3.connect('user_log.db')
log_cursor = log_conn.cursor()

username = st.text_input("아이디")
password = st.text_input("비밀번호", type="password")

login_button = st.button("로그인")
if login_button:
    user_data_cursor.execute("SELECT username, password FROM users WHERE username=?", (username,))
    user_data = user_data_cursor.fetchone()
    if user_data is not None and user_data[1] == hashlib.sha256(password.encode()).hexdigest():
        st.success("로그인 성공")
        st.session_state.logged_in = True
    else:
        st.error("로그인 실패, 잘못된 아이디 혹은 비번입니다.")
        st.session_state.logged_in = False

# 로그인한 사용자에게만 횟수 증가 버튼을 표시
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if st.session_state.logged_in:
    if st.button("횟수 증가"):
        count_data_cursor.execute("SELECT count FROM user_count WHERE username=?", (username,))
        count = count_data_cursor.fetchone()
        if count is not None:
            new_count = count[0] + 1
            count_data_cursor.execute("UPDATE user_count SET count = ? WHERE username = ?", (new_count, username))
            count_data_conn.commit()
            st.success("횟수가 증가했습니다!")

            # 사용자 로그 생성 및 기록
            timestamp = datetime.datetime.now()
            log_cursor.execute("INSERT INTO user_logs (username, count, timestamp) VALUES (?, ?, ?)", (username, new_count, timestamp))
            log_conn.commit()
            st.success("기록되었습니다!")

# 사용자 순위를 가져와 표와 그래프로 표시
count_data_cursor.execute("SELECT username, count FROM user_count ORDER BY count DESC")
user_rankings = count_data_cursor.fetchall()

st.title("횟수 순위 및 그래프")
st.table(user_rankings)

# 그래프로 사용자 카운트 순위를 시각화
df = pd.DataFrame(user_rankings, columns=["사용자", "카운트"])
st.bar_chart(df.set_index("사용자"))

user_data_conn.close()
count_data_conn.close()
log_conn.close()
