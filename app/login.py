from imports import st
from db import Database

def show_login():
    db_inst = Database()
    # db_inst.init_db()  # use só uma vez para criar tabelas

    aba = st.tabs(["Login", "Cadastro"])

    # LOGIN
    with aba[0]:
        st.title("Login")
        username = st.text_input("Login", key="login_username")
        password = st.text_input("Senha", type="password", key="login_password")
        
        if st.button("Entrar"):
            conn = db_inst.get_connection()
            cur = conn.cursor()
            sql = db_inst.opensql(filepath=db_inst.select_path, filename='user_autentication.sql')
            cur.execute(sql, (username, password))
            user = cur.fetchone()
            conn.close()

            if user:
                st.session_state["authenticated"] = True
                st.session_state["user_id"] = user[0]
                st.success("Login realizado com sucesso!")
            else:
                st.error("Usuário ou senha inválidos.")

    # CADASTRO
    with aba[1]:
        st.title("Cadastro")
        new_username = st.text_input("Novo login", key="register_username")
        new_password = st.text_input("Nova senha", type="password", key="register_password")
        confirm_password = st.text_input("Confirme a senha", type="password", key="register_confirm")

        if st.button("Cadastrar"):
            if not new_username or not new_password:
                st.error("Preencha todos os campos.")
            elif new_password != confirm_password:
                st.error("As senhas não coincidem.")
            else:
                try:
                    conn = db_inst.get_connection()
                    cur = conn.cursor()
                    cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
                                (new_username, new_password))
                    conn.commit()
                    conn.close()
                    st.success("Usuário cadastrado com sucesso!")
                except Exception as e:
                    st.error(f"Erro: {str(e)}")
