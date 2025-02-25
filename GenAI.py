import streamlit as st
import google.generativeai as ai
ai.configure(api_key="AIzaSyDIcrLpoMNI4iOuI3cBmas1qcfjfTXB7yM")
sys_prompt="""You are a helpful and interactive AI tutor for Mathematics
Students will ask you doubts related to various topics in Mathematics.You are expected
to reply in as much details as possible and if you could visualise them with the solution then it would make them understand the concept more easily
Make sure to take real life examples while explaining the concept.
In case if a student ask any question outside the Mathematics scope,
politely decline and tell them to ask the question from Mathematics domain only."""

model=ai.GenerativeModel(model_name="models/gemini-2.0-flash-exp",system_instruction=sys_prompt)

st.title("Maths Buddy")
user_prompt=st.text_input("Enter your query:",placeholder="Type your query here...")
btn_click=st.button("Generate Answer")
if btn_click==True:
  response=model.generate_content(user_prompt)
  st.write(response.text)