import streamlit as st

# Setting page title and header
st.set_page_config(page_title="Bedrock Agents at work", page_icon=":robot_face:")

st.markdown(""" <style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style> """, unsafe_allow_html=True)

input_data = st.text_area("Input Data", key="input_data", placeholder= "Enter your query...")
btn_action = st.button("Action")