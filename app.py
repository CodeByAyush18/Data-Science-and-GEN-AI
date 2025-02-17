import streamlit as st
from code_review import review_code  # Import Gemini AI function

# Streamlit App Title
st.title("AI Code Reviewer (Gemini AI)")

# User Input for Python Code
code = st.text_area("Paste your Python code here:", height=200)

if st.button("Review Code"):
    if code.strip():
        response = review_code(code)
        st.subheader("Review Feedback")
        #st.subheader("Updated Code")
        st.write(response)
    else:
        st.warning("Please enter some Python code.")

