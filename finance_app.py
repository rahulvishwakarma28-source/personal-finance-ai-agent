
import streamlit as st
from finance_agent import build_finance_agent

st.set_page_config(page_title="Personal Finance AI Agent")

st.title("Personal Finance AI Agent")
st.write("Ask about loan EMI, monthly investments, budgets, or basic calculations.")

api_key = st.sidebar.text_input(
    "OpenAI API key",
    type="password"
)

st.sidebar.caption("The key is used for this session and is not saved to a file.")

with st.form("finance_question"):
    question = st.text_area(
        "Enter your question",
        placeholder="Calculate EMI for a ₹10 lakh loan at 8% interest for 20 years."
    )
    submitted = st.form_submit_button("Get answer")

if submitted:
    if not api_key.strip():
        st.warning("Enter your OpenAI API key in the sidebar.")
    elif not question.strip():
        st.warning("Enter a question.")
    else:
        try:
            with st.spinner("Working on your question..."):
                agent = build_finance_agent(api_key.strip())

                result = agent.invoke(
                    {"messages": [{"role": "user", "content": question}]},
                    config={"recursion_limit": 10}
                )

            tools_used = [
                message.name
                for message in result["messages"]
                if message.type == "tool"
            ]

            if tools_used:
                st.caption("Tools used: " + ", ".join(tools_used))

            st.markdown(result["messages"][-1].content)

        except Exception:
            st.error(
                "The request could not be completed. Check your API key, "
                "API balance, and internet connection."
            )

st.caption(
    "For educational calculations. Investment returns are estimates "
    "and are not guaranteed."
)
