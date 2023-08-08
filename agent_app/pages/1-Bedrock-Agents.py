import streamlit as st
from PIL import Image
import os

st.subheader("What are Bedrock Agents")

st.write("Bedrock Agent is a fully managed capability that enables developers to configure foundation models in a few clicks and complete actions (for example, processing insurance claims and making travel reservations) based on organization data and user input. Agents orchestrate interactions between foundation models, data sources, software applications, and user conversations, and automatically call APIs to take actions. Developers can easily integrate the agents and accelerate delivery of generative AI applications saving weeks of development effort")

st.subheader("How Agents work")

st.write("Agents use a foundataion model to perform the orchestration.  You can select one of the available foundational model from Amazon Bedrock")
st.write("Action groups are created for each Agent. Agents, based on the instruction, reasons and acts using one of the Action group")
st.write("Actions for each action group is coded in a Lambda function")

agents = Image.open('/Users/thandavm/work/strategic_accounts/ai_summit/gen_ai_app/pages/images/model_list.png')
st.image(agents)

st.markdown("---")
st.write("© Bedrock Agents")    