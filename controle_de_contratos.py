import streamlit as st

# ✅ Garante layout wide antes de qualquer renderização
if "page_config_applied" not in st.session_state:
    st.set_page_config(layout="wide")
    st.session_state["page_config_applied"] = True

import os
import pandas as pd
import sqlite3
from datetime import datetime as dt, date
from PIL import Image
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode


def main():
    hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stDeployButton {display: none;}
        body { margin-top: 0px; padding-top: 0px; }
        .stAppHeader { margin-top: 0px !important; }
        .stAppViewContainer { padding-top: 0px !important; }
        .stMainBlockContainer { padding-top: 0px !important; }
        .stAppHeader .stAppHeader { display: flex; justify-content: space-between; align-items: center; height: 60px; }
        .stAppHeader img { height: 40px; }
        .stButton > button { padding-left: 0; padding-right: 0; }
        .stTextInput, .stTextArea { width: 100%; max-width: 400px; }
        .stSelectbox, .stDateInput { width: 100%; max-width: 400px; }
        </style>
    """
    st.markdown(hide_menu_style, unsafe_allow_html=True)

    def carregar_dados():
        conn = sqlite3.connect('contratos.db')
        try:
            df = pd.read_sql_query("SELECT * FROM contratos", conn)
        except Exception:
            df = pd.DataFrame(columns=["data_assinatura", "data_vencimento", "nome_empresa", "numero_contrato",
                                       "categoria", "status", "objeto", "observacoes"])
        conn.close()
        df['data_assinatura'] = pd.to_datetime(df['data_assinatura'], errors='coerce')
        df['data_vencimento'] = pd.to_datetime(df['data_vencimento'], errors='coerce')
        if 'observacoes' not in df.columns:
            df['observacoes'] = ''
        df.fillna({'nome_empresa': '', 'numero_contrato': '', 'categoria': '', 'status': '', 'objeto': '', 'observacoes': ''}, inplace=True)
        return df

    if ('df_contratos' not in st.session_state) or st.session_state.get("recarregar_contratos", False):
        st.session_state.df_contratos = carregar_dados()
        st.session_state["recarregar_contratos"] = False

    col_vazio, col_sair = st.columns([9, 1])
    with col_sair:
        st.markdown("""
            <style>
            div.stButton > button {
                background-color: #e74c3c;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 8px;
                padding: 0.5em 1em;
            }
            </style>
        """, unsafe_allow_html=True)

        if st.button("Sair", key="btn_sair"):
            for key in list(st.session_state.keys()):
                if key != "page_config_applied":
                    del st.session_state[key]
            st.session_state["recarregar_contratos"] = True
            st.rerun()

    def salvar_dados(df):
        df['data_assinatura'] = pd.to_datetime(df['data_assinatura'], errors='coerce')
        df['data_vencimento'] = pd.to_datetime(df['data_vencimento'], errors='coerce')
        df['data_assinatura'] = df['data_assinatura'].dt.strftime('%Y-%m-%d')
        df['data_vencimento'] = df['data_vencimento'].dt.strftime('%Y-%m-%d')
        conn = sqlite3.connect('contratos.db')
        df.to_sql('contratos', conn, if_exists='replace', index=False)
        conn.close()

    def calcular_metricas(df):
        hoje = pd.Timestamp.today().normalize()
        df['data_vencimento'] = pd.to_datetime(df['data_vencimento'], errors='coerce')
        df['dif_dias'] = (df['data_vencimento'].dt.normalize() - hoje).dt.days

        def mensagem_dias(dias):
            if dias < 0:
                return f"Seu contrato está a {abs(dias)} dias vencido."
            elif dias > 0:
                return f"Seu contrato vence em {dias} dias."
            else:
                return "Seu contrato vence hoje."

        df["Dias de Atraso"] = df['dif_dias'].apply(mensagem_dias)

        def situacao_contrato(row):
            if row['dif_dias'] < 0:
                return '🔴 Contrato vencido'
            elif row['dif_dias'] <= 30:
                return '🟡 Contrato próximo do vencimento'
            else:
                return '🟢 Contrato em dia'

        df['Situação do Contrato'] = df.apply(situacao_contrato, axis=1)
        total = len(df)
        vencidos = len(df[df['dif_dias'] < 0])
        proximos = len(df[(df['dif_dias'] >= 0) & (df['dif_dias'] <= 30)])
        em_dia = total - vencidos - proximos
        df.drop(columns=['dif_dias'], inplace=True)
        return total, vencidos, em_dia, proximos, df

    def excluir_contrato(index):
        st.session_state.df_contratos = st.session_state.df_contratos.drop(index)
        st.session_state.df_contratos.reset_index(drop=True, inplace=True)
        salvar_dados(st.session_state.df_contratos)
        st.success("✅ Contrato excluído com sucesso!")

    total, vencidos, em_dia, proximos, st.session_state.df_contratos = calcular_metricas(st.session_state.df_contratos)

    logo_path = "logomarca.png"
    logo = Image.open(logo_path) if os.path.exists(logo_path) else None
    if not logo:
        st.error("⚠️ Logo não encontrada.")

    col_logo, col_titulo = st.columns([1, 6])
    with col_logo:
        if logo:
            st.image(logo, width=200)
    with col_titulo:
        st.markdown("<h1 style='font-size: 48px; text-align:center;'>Controle de Contratos</h1>", unsafe_allow_html=True)

    def dashboard_resumo(total, vencidos, em_dia, proximos):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"<div style='background:#1c1f26; padding:20px; border-radius:10px; text-align:center;'><h5 style='color:white;'>TOTAL DE CONTRATOS</h5><h2 style='color:white;'>{total}</h2></div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div style='background:#c40707; padding:20px; border-radius:10px; text-align:center;'><h5 style='color:white;'>CONTRATOS VENCIDOS</h5><h2 style='color:white;'>{vencidos}</h2></div>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<div style='background:#16a34a; padding:20px; border-radius:10px; text-align:center;'><h5 style='color:white;'>CONTRATOS EM DIA</h5><h2 style='color:white;'>{em_dia}</h2></div>", unsafe_allow_html=True)
        with col4:
            st.markdown(f"<div style='background:#facc15; padding:20px; border-radius:10px; text-align:center;'><h5 style='color:black;'>PRÓXIMOS DO VENCIMENTO</h5><h2 style='color:black;'>{proximos}</h2></div>", unsafe_allow_html=True)

    dashboard_resumo(total, vencidos, em_dia, proximos)
    st.markdown("<br>", unsafe_allow_html=True)

    col_esq, col_dir = st.columns([1, 5])
    with col_esq:
        st.markdown("<h3 style='font-size: 24px;'>Adicionar Novo Contrato</h3>", unsafe_allow_html=True)
        with st.form(key="form_contrato"):
            data_vencimento = st.date_input("Data de Vencimento", value=date.today())
            nome_empresa = st.text_input("Nome da Empresa")
            numero_contrato = st.number_input("Número do Contrato", step=1)
            categoria = st.text_input("Categoria")
            status = st.selectbox("Status", ["Ativo", "Inativo"])
            objeto = st.text_area("Objeto")
            observacoes = st.text_area("Observações")
            salvar = st.form_submit_button("Salvar Contrato")
            atualizar = st.form_submit_button("Atualizar Dashboard")

        if salvar:
            novo_contrato = pd.DataFrame([{
                "data_assinatura": pd.NaT,
                "data_vencimento": data_vencimento,
                "nome_empresa": nome_empresa,
                "numero_contrato": numero_contrato,
                "categoria": categoria,
                "status": status,
                "objeto": objeto,
                "observacoes": observacoes
            }])
            st.session_state.df_contratos = pd.concat([st.session_state.df_contratos, novo_contrato], ignore_index=True)
            salvar_dados(st.session_state.df_contratos)
            st.session_state.df_contratos = carregar_dados()
            total, vencidos, em_dia, proximos, st.session_state.df_contratos = calcular_metricas(st.session_state.df_contratos)

        if atualizar:
            total, vencidos, em_dia, proximos, st.session_state.df_contratos = calcular_metricas(st.session_state.df_contratos)
            st.success("✅ Dashboard atualizado com sucesso!")

    with col_dir:
        st.markdown("<h3 style='font-size: 24px;'>Relação de Contratos</h3>", unsafe_allow_html=True)

        situacoes = ["Todos"] + sorted(st.session_state.df_contratos["Situação do Contrato"].unique())
        filtro_situacao = st.selectbox("Filtrar por Situação", situacoes)

        df_filtrado = st.session_state.df_contratos.copy()
        if filtro_situacao != "Todos":
            df_filtrado = df_filtrado[df_filtrado["Situação do Contrato"] == filtro_situacao]

        df_filtrado['Data de Vencimento'] = pd.to_datetime(df_filtrado['data_vencimento'], errors='coerce').dt.strftime('%d/%m/%Y')

        df_exibir = df_filtrado[['Data de Vencimento', 'Dias de Atraso', 'nome_empresa', 'numero_contrato',
                                 'categoria', 'status', 'Situação do Contrato', 'objeto', 'observacoes']].copy()

        df_exibir.columns = ['Vencimento', 'Dias de Atraso', 'Empresa', 'Nº Contrato',
                             'Categoria', 'Status', 'Situação', 'Objeto', 'Observação']

        gb = GridOptionsBuilder.from_dataframe(df_exibir)
        gb.configure_default_column(editable=True, resizable=True, filter=False,
                                    cellStyle={'textAlign': 'center', 'whiteSpace': 'normal', 'overflow': 'hidden', 'textOverflow': 'ellipsis'})
        for col in ['Objeto', 'Observação']:
            gb.configure_column(col, tooltipField=col, cellStyle={'white-space': 'normal', 'word-wrap': 'break-word'})
        gb.configure_column("Dias de Atraso", flex=3, minWidth=250)
        gb.configure_column("Situação", flex=3, minWidth=250)
        for col in ['Vencimento', 'Empresa', 'Nº Contrato', 'Categoria', 'Status']:
            gb.configure_column(col, flex=1, minWidth=100)
        gb.configure_grid_options(domLayout='autoHeight', suppressMenu=True, enableBrowserTooltips=True, suppressHorizontalScroll=False)

        AgGrid(
            df_exibir,
            gridOptions=gb.build(),
            height=min(600, 40 * (len(df_exibir) + 1)),
            enable_enterprise_modules=False,
            theme='material',
            update_mode=GridUpdateMode.VALUE_CHANGED,
            allow_unsafe_jscode=True,
            fit_columns_on_grid_load=True,
            reload_data=True,
            key="aggrid"
        )

        contrato_selecionado = st.selectbox("Selecione o contrato a excluir", ["Selecione o contrato para excluir"] + list(df_filtrado['nome_empresa'].values))
        if contrato_selecionado != "Selecione o contrato para excluir":
            if st.button(f"🗑️ Excluir Contrato {contrato_selecionado}"):
                contrato_idx = df_filtrado[df_filtrado['nome_empresa'] == contrato_selecionado].index[0]
                excluir_contrato(contrato_idx)
                total, vencidos, em_dia, proximos, st.session_state.df_contratos = calcular_metricas(st.session_state.df_contratos)


if __name__ == "__main__":
    main()