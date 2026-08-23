import streamlit as st

from coursekit.day1_rag import RAGSystem
from coursekit.day2_graph import AdaptiveRAG
from coursekit.day3_agent import AgentHarness
from coursekit.day4_multiagent import SearchAndVerifySystem
from coursekit.day5_system import OperationalSystem

st.set_page_config(page_title="RAG + Multi-Agent", layout="wide")
st.title("현대자동차 RAG + Multi-Agent 실습")
day = st.sidebar.selectbox("실행 단계", ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5"])
question = st.text_input("질문", "회생제동 단계는 어떻게 조절하나요?")
if st.button("실행"):
    systems = {
        "Day 1": lambda: RAGSystem().ask(question),
        "Day 2": lambda: AdaptiveRAG().ask(question),
        "Day 3": lambda: AgentHarness().run(question),
        "Day 4": lambda: SearchAndVerifySystem().run(question),
        "Day 5": lambda: OperationalSystem().run(question),
    }
    result = systems[day]()
    st.subheader("답변")
    st.write(result.answer)
    st.subheader("전체 결과")
    st.json(result.model_dump())
    st.subheader("Trace")
    st.code("\n".join(result.trace))

if day == "Day 5" and st.sidebar.button("전체 평가 실행"):
    st.sidebar.json(OperationalSystem().evaluate().model_dump())

