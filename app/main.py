from imports import st
from login import show_login
from dashboard_home import dash

def main():
    if not st.session_state.get("authenticated", False):
        show_login()
    else:
        dash()

main()