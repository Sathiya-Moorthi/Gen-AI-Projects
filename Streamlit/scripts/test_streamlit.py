import streamlit as st

st.title("My first Streamlit app!")

name  = st.text_input("Enter your name:")

st.write(f"Hello, {name}!")

if st.button("Click me"):
    if name:
        st.balloons()
        st.success(f"Welcome to Streamlit, {name}!")
    else:
        st.info("Please enter your name above to see a special message.")
