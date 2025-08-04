import streamlit as st
import controle_de_contratos

# === CONFIGURAÇÃO DO LAYOUT WIDE ===
if not st.session_state.get("page_config_applied"):
    st.set_page_config(page_title="Controle de Contratos", layout="wide", initial_sidebar_state="collapsed")
    st.session_state["page_config_applied"] = True

# === ESCONDER MENU, RODAPÉ E TOOLBAR DO STREAMLIT ===
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stToolbar"] {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# === CREDENCIAIS DE LOGIN ===
USUARIO = "setorgerad"
SENHA = "gerad2025@"

# === INICIALIZAÇÃO DA SESSÃO ===
if "logado" not in st.session_state:
    st.session_state["logado"] = False

# === FUNÇÃO DE LOGIN ===
def login_page():
    st.markdown("""
        <style>
            .login-title {
                text-align: center;
                font-size: 45px;
                font-weight: bold;
                color: #0a3d62;
                margin-top: 30px;
                margin-bottom: 20px;
            }
            .stTextInput, .stButton {
                max-width: 700px;
                margin-left: auto;
                margin-right: auto;
            }
            .stTextInput>div>div>input {
                padding: 12px;
                font-size: 16px;
                border-radius: 8px;
            }
            .stButton>button {
                width: 100%;
                padding: 12px;
                background-color: #1f6feb;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                margin-top: 10px;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='login-title'>Controle de Contratos - GERAD</div>", unsafe_allow_html=True)

    usuario = st.text_input("Digite seu usuário", key="login_usuario")
    senha = st.text_input("Digite sua senha", type="password", key="login_senha")
    login = st.button("Entrar", key="botao_entrar")

    if login:
        if usuario == USUARIO and senha == SENHA:
            st.session_state["logado"] = True
            st.rerun()
        else:
            st.error("❌ Usuário ou senha incorretos.")

# === RENDERIZAÇÃO ===
if not st.session_state["logado"]:
    login_page()
else:
    controle_de_contratos.main()
