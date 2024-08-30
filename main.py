import streamlit as st

# Set up page configuration
st.set_page_config(page_title="Welcome Page", page_icon="🌐", layout="wide")

# Main app logic
def main():
    st.title("Welcome 🤖")
    st.write("Welcome to the application! Feel free to explore.")

# Run the app
if __name__ == "__main__":
    main()

