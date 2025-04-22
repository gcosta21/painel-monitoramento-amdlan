import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# Configurações
st.set_page_config(page_title="Painel de Monitoramento - Amd Lan", layout="wide")
st.title("🔧 Painel de Monitoramento - Amd Lan")

# URL da API FastAPI hospedada no Render
API_URL = "https://monitoramento-amdlan-api.onrender.com/api/ultimos"

# Requisição dos dados
try:
    response = requests.get(API_URL)
    response.raise_for_status()
    dados = response.json()
    df = pd.DataFrame(dados)
except Exception as e:
    st.error(f"Erro ao obter dados da API: {e}")
    st.stop()

if df.empty:
    st.warning("Nenhum dado recebido ainda.")
    st.stop()

# Conversões
df["dataHoraEnvio"] = pd.to_datetime(df["dataHoraEnvio"])
df["dataHoraUltimoBackup"] = pd.to_datetime(df["dataHoraUltimoBackup"])
df["dataHoraUltimaValidacao"] = pd.to_datetime(df["dataHoraUltimaValidacao"])

# Lista de clientes
clientes = df["cliente"].unique()
cliente_selecionado = st.selectbox("Selecione um cliente", clientes)

# Filtrar dados por cliente
dados_cliente = df[df["cliente"] == cliente_selecionado].copy()
ultimo = dados_cliente.iloc[0]

# Visão geral
col1, col2, col3, col4 = st.columns(4)
col1.metric("🧠 CPU (%)", f"{ultimo['usoCPU']}%")
col2.metric("💾 RAM (%)", f"{ultimo['usoRAM']}%")
col3.metric("📊 Disco (%)", f"{ultimo['usoDisco']}%")
col4.metric("🌡️ Temp. CPU", f"{ultimo['temperaturaCPU']}°C")

col5, col6, col7 = st.columns(3)
col5.metric("🔁 Uptime (h)", f"{ultimo['uptimeHoras']}")
col6.metric("📦 Banco (MB)", f"{ultimo['tamanhoBancoMB']}")
col7.metric("🔥 Firebird", "Rodando" if ultimo["firebirdRodando"] else "Parado", delta_color="inverse")

st.divider()

# Backup e validação
col8, col9 = st.columns(2)
col8.metric("📅 Último Backup", ultimo["dataHoraUltimoBackup"].strftime("%d/%m %H:%M"))
col9.metric("✅ Última Validação", 
            ultimo["dataHoraUltimaValidacao"].strftime("%d/%m %H:%M"), 
            "Com Erro" if ultimo["validacaoComErro"] else "OK",
            delta_color="inverse" if ultimo["validacaoComErro"] else "normal")

# Histórico
st.subheader("📜 Histórico de registros")
st.dataframe(dados_cliente[[
    "dataHoraEnvio", "usoCPU", "usoRAM", "usoDisco", "temperaturaCPU",
    "firebirdRodando", "tamanhoBancoMB", "dataHoraUltimoBackup",
    "dataHoraUltimaValidacao", "validacaoComErro"
]].head(30), use_container_width=True)
