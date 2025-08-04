<<<<<<< HEAD
import streamlit as st

def login_page():
    st.set_page_config(page_title="Login", layout="centered")

    # Título centralizado
    st.markdown("<h1 style='text-align: center;'>controle de contratos - GERAD</h1>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # Campos de usuário e senha
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    # Botão azul com texto branco
    login = st.button("Entrar")

    # Verifica se clicou no botão
    if login:
        if usuario and senha:
            st.success("✅ Login bem-sucedido! (Vamos continuar no próximo passo)")
        else:
            st.error("❌ Por favor, preencha usuário e senha.")

# CHAMANDO A FUNÇÃO LOGIN
login_page()
=======
import streamlit as st

def login_page():
    st.set_page_config(page_title="Login", layout="centered")

    # Título centralizado
    st.markdown("<h1 style='text-align: center;'>controle de contratos - GERAD</h1>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # Campos de usuário e senha
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    # Botão azul com texto branco
    login = st.button("Entrar")

    # Verifica se clicou no botão
    if login:
        if usuario and senha:
            st.success("✅ Login bem-sucedido! (Vamos continuar no próximo passo)")
        else:
            st.error("❌ Por favor, preencha usuário e senha.")

# CHAMANDO A FUNÇÃO LOGIN
login_page()
>>>>>>> f3eb7a1bdbe7190c3d661e491ced16c0636d5015
