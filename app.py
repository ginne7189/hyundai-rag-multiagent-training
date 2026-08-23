import streamlit as st

from coursekit.day1_rag import RAGSystem

st.set_page_config(page_title="RAG + Multi-Agent", layout="wide")
st.title("현대자동차 RAG + Multi-Agent 실습")
question = st.text_input("질문", "회생제동 단계는 어떻게 조절하나요?")
if st.button("실행"):
    result = RAGSystem().ask(question)
    st.subheader("답변")
    st.write(result.answer)
    st.subheader("출처")
    st.json([citation.model_dump() for citation in result.citations])
    st.subheader("Trace")
    st.code("\n".join(result.trace))

