from imports import st


def dash():
    pages = {
        "Menu": [
            st.Page("dashboard_home.py", title="Dashboard"),
            st.Page("carteira.py", title="Carteira"),
            st.Page("proventos.py", title="Proventos"),
        ],
    }
    pg = st.navigation(pages)
    pg.run()
