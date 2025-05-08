import streamlit as st
import pandas as pd

@st.cache_data
def load_data():
    df = pd.read_csv("bangkok_traffy_mock_modified1.csv", index_col=0)
    return df

df = load_data()

problem_types = ['น้ำท่วม', 'ร้องเรียน', 'ความสะอาด', 'ท่อระบายน้ำ', 'ถนน', 'คลอง',
       'ทางเท้า', 'เสียงรบกวน', 'สะพาน', 'สายไฟ', 'กีดขวาง', 'แสงสว่าง',
       'สัตว์จรจัด', 'ต้นไม้', 'ความปลอดภัย', 'จราจร', 'การเดินทาง',
       'เสนอแนะ', 'คนจรจัด', 'ห้องน้ำ', 'ป้ายจราจร', 'สอบถาม', 'ป้าย',
       'PM2.5']

@st.dialog("Select the problems")
def choose_problems():
    col1, col2, col3 = st.columns(3)
    with col1:
        problems1 = [st.checkbox(i, key=i) for i in problem_types[:8]]

    with col2:
        problems2 = [st.checkbox(i, key=i) for i in problem_types[8:16]]

    with col3:
        problems3 = [st.checkbox(i, key=i) for i in problem_types[16:]]
    problems = problems1 + problems2 + problems3
    if st.button("Select"):
        st.session_state.problems = problems
        st.rerun()


if st.button("Select problems"):
    choose_problems()
if "problems" in st.session_state:
    problems = st.session_state.problems
    chosen_type = set()
    for i in range(len(problems)):
        if problems[i]:
            chosen_type.add(problem_types[i])
    chosen_type

