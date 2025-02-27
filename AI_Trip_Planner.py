import streamlit as st
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

# ✅ Load API Key from .env
load_dotenv()  # This loads the .env file

GOOGLE_API_KEY = os.getenv("AIzaSyAOfkoYXjQsvVx8arfiyJe33hHWopoAd4o")

if not GOOGLE_API_KEY:
    st.error("Google API key is missing! Ensure it's set in a .env file.")
    st.stop()

# ✅ Set the API key explicitly in the environment
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY  

# ✅ Initialize LangChain's Google GenAI Model
llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro")

st.title("🌍 AI Travel Planner")
st.write("Find the best travel options between two locations.")

source = st.text_input("Enter source location:")
destination = st.text_input("Enter destination:")

prompt_template = PromptTemplate(
    input_variables=["source", "destination"],
    template="Suggest the best travel options between {source} and {destination}, including flights, trains, buses, and taxis."
)

def get_travel_options(source, destination):
    """Fetch travel options using LangChain's Google GenAI."""
    try:
        prompt = prompt_template.format(source=source, destination=destination)
        response = llm.invoke(prompt)
        return response if response else "No travel data available."
    except Exception as e:
        return f"Error fetching travel options: {str(e)}"

if st.button("Find Travel Options"):
    if source and destination:
        with st.spinner("Fetching best travel routes..."):
            response = get_travel_options(source, destination)
            st.success("Travel recommendations fetched!")
            st.write(response)
    else:
        st.warning("Please enter both source and destination.")
