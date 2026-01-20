import streamlit as st
import yfinance as yf
import requests
import feedparser
from datetime import datetime
from urllib.parse import quote
import random
import pytz

# --- BIBLIOTECAS GOOGLE SHEETS ---
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Configuração da página
st.set_page_config(
    page_title="Dashboard Pessoal",
    page_icon="🤖",
    layout="wide"
)

# --- CSS APRIMORADO (Mantido igual) ---
st.markdown("""
<style>
    .main-header { font-size: 2.5rem; font-weight: 700; color: #333; }
    .update-time { color: #666; font-size: 0.9rem; margin-bottom: 1.5rem; }
    .card { border-radius: 16px; padding: 1.2rem; margin-bottom: 1rem; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: transform 0.2s; }
    .card:hover { transform: translateY(-2px); }
    .bg-gradient-red { background: linear-gradient(135deg, #FF512F 0%, #DD2476 100%); }
    .bg-gradient-blue { background: linear-gradient(135deg, #1A2980 0%, #26D0CE 100%); }
    .bg-gradient-green { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); }
    .bg-gradient-dark { background: linear-gradient(135deg, #232526 0%, #414345 100%); }
    .bg-gradient-purple { background: linear-gradient(135deg, #8E2DE2 0%, #4A00E0 100%); }
    .bg-gradient-orange { background: linear-gradient(135deg, #f12711 0%, #f5af19 100%); }
    .bg-gradient-gold { background: linear-gradient(135deg, #F7971E 0%, #FFD200 100%); }
    .bg-gradient-teal { background: linear-gradient(135deg, #0F2027 0%, #203A43 50%, #2C5364 100%); }
    .card-title { font-size: 0.9rem; opacity: 0.9; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem; }
    .card-value { font-size: 1.8rem; font-weight: 700; margin-bottom: 0.2rem; }
    .card-subtitle { font-size: 0.8rem; opacity: 0.9; font-weight: 500; }
    .stock-badge { padding: 2px 8px; border-radius: 10px; font-size: 0.8rem; margin-left: 10px; }
    .stock-badge-positive { background: rgba(17, 153, 142, 0.8); }
    .stock-badge-negative { background: rgba(255, 81, 47, 0.8); }
    .section-header { font-size: 1.4rem; font-weight: 600; margin: 2rem 0 1rem 0; color: #444; border-bottom: 2px solid #eee; padding-bottom: 0.5rem; }
</style>
""", unsafe_allow_html=True)

# --- DADOS E FUNÇÕES DE SUPORTE ---

# Carteiras (Mantidas)
CARTEIRA_BR = {
    "PRIO3.SA": (267, 42.38), "ALUP11.SA": (159, 28.79), "BBAS3.SA": (236, 27.24),
    "MOVI3.SA": (290, 6.82), "AGRO3.SA": (135, 24.98), "VALE3.SA": (25, 61.38),
    "VAMO3.SA": (226, 6.75), "BBSE3.SA": (19, 33.30), "FESA4.SA": (95, 8.14),
    "SLCE3.SA": (31, 18.00), "TTEN3.SA": (17, 14.61), "JALL3.SA": (43, 4.65),
    "GARE11.SA": (142, 9.10), "KNCR11.SA": (9, 103.30),
}
CARTEIRA_US = {
    "VOO": (0.89425, 475.26), "QQQ": (0.54245, 456.28), "VNQ": (2.73961, 82.48),
    "VT": (1.0785, 112.68), "TSLA": (0.52762, 205.26), "NVDA": (0.2276, 87.79),
}

# --- CONEXÃO GOOGLE SHEETS ---
def conectar_gsheets():
    """Conecta ao Google Sheets usando st.secrets"""
    try:
        # Define o escopo
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        
        # Carrega credenciais dos Segredos (secrets.toml)
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        
        client = gspread.authorize(creds)
        # Abre a planilha pelo nome
        sheet = client.open("Tarefas_Dashboard").sheet1 
        return sheet
    except Exception as e:
        return None

# --- FUNÇÕES COM CACHE ---
@st.cache_data(ttl=900)
def get_weather(lat, lon):
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {"latitude": lat, "longitude": lon, "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m,precipitation", "timezone": "America/Sao_Paulo"}
        data = requests.get(url, params=params, timeout=5).json().get("current", {})
        code = data.get("weather_code", 0)
        weather_map = {0: "☀️", 1: "🌤️", 2: "⛅", 3: "☁️", 45: "🌫️", 51: "🌦️", 61: "🌧️", 80: "⛈️", 95: "⛈️"}
        return {"temp": data.get("temperature_2m", "--"), "icon": weather_map.get(code, "☁️"), "descricao": "Atualizado", "wind": data.get("wind_speed_10m", "--")}
    except: return {"temp": "--", "icon": "❓", "descricao": "Erro", "wind": "--"}

@st.cache_data(ttl=900)
def get_stock_data(ticker):
    try:
        hist = yf.Ticker(ticker).history(period="2d")
        if len(hist) >= 1:
            atual = hist['Close'].iloc[-1]
            prev = hist['Close'].iloc[-2] if len(hist) > 1 else atual
            return atual, ((atual - prev) / prev) * 100
        return 0.0, 0.0
    except: return 0.0, 0.0

@st.cache_data(ttl=900)
def get_dolar():
    try: return yf.Ticker("USDBRL=X").history(period="1d")['Close'].iloc[-1]
    except: return 6.0

@st.cache_data(ttl=1800)
def get_news(query):
    try: return feedparser.parse(f"https://news.google.com/rss/search?q={quote(query)}&hl=pt-BR&gl=BR&ceid=BR:pt-419").entries[:4]
    except: return []

# --- INÍCIO DO DASHBOARD ---

fuso = pytz.timezone('America/Sao_Paulo')
agora = datetime.now(fuso)

# Cabeçalho
col_h, col_d1, col_d2, col_info = st.columns(4)
with col_h:
    st.markdown(f"""<div class="card bg-gradient-dark" style="text-align:center"><div class="card-title">📅 {agora.strftime("%d/%m")} • {agora.strftime("%H:%M")}</div><div class="card-subtitle">Quirinópolis-GO</div></div>""", unsafe_allow_html=True)

# Dividendos
divs = [
    {"a": "BBAS3", "t": "JCP", "v": "R$ 0,47", "d": "31/01", "c": "bg-gradient-blue"},
    {"a": "VALE3", "t": "Div", "v": "R$ 2,09", "d": "12/03", "c": "bg-gradient-green"},
    {"a": "PRIO3", "t": "Div", "v": "R$ 1,23", "d": "15/02", "c": "bg-gradient-teal"}
]
for i, col in enumerate([col_d1, col_d2]):
    d = divs[i]
    with col: st.markdown(f"""<div class="card {d['c']}"><div class="card-title">💰 {d['a']}</div><div class="card-value">{d['v']}</div><div class="card-subtitle">{d['t']} • {d['d']}</div></div>""", unsafe_allow_html=True)

with col_info:
    st.markdown(f"""<div class="card bg-gradient-red"><div class="card-title">📰 Info</div><div class="card-subtitle">Painel Pessoal</div><div class="card-subtitle">v2.1 Sheets</div></div>""", unsafe_allow_html=True)

# --- 0. TAREFAS VIA GOOGLE SHEETS (O CORAÇÃO DA OPÇÃO 2) ---
st.markdown('<div class="section-header">📝 Minhas Tarefas (Google Sheets)</div>', unsafe_allow_html=True)

sheet = conectar_gsheets()

col_tasks, col_add = st.columns([2, 1])

if sheet:
    # Ler dados
    try:
        dados = sheet.get_all_records() # Retorna lista de dicionários
        
        # Adicionar Tarefa
        with col_add:
            with st.form("add_sheet_task"):
                st.markdown("**Nova Tarefa**")
                nova_task = st.text_input("Descrição")
                if st.form_submit_button("Salvar na Planilha"):
                    if nova_task:
                        data_hoje = agora.strftime("%d/%m/%Y")
                        sheet.append_row([nova_task, "Pendente", data_hoje])
                        st.success("Salvo!")
                        st.rerun()

        # Listar Tarefas
        with col_tasks:
            if not dados:
                st.info("A planilha está vazia ou não conseguimos ler.")
            else:
                pendentes = [d for d in dados if d.get("Status") != "Concluído"]
                
                if not pendentes:
                    st.success("Tudo em dia! Nenhuma tarefa pendente.")
                else:
                    for i, row in enumerate(dados):
                        # Ajuste de índice: +2 porque sheets começa em 1 e tem header
                        row_num = i + 2 
                        if row.get("Status") != "Concluído":
                            c1, c2, c3 = st.columns([0.1, 0.7, 0.2])
                            with c1:
                                if st.button("✅", key=f"done_{i}"):
                                    sheet.update_cell(row_num, 2, "Concluído") # Atualiza coluna B (Status)
                                    st.rerun()
                            with c2:
                                st.write(f"**{row.get('Tarefa')}**")
                            with c3:
                                st.caption(f"{row.get('Data')}")
                                
    except Exception as e:
        st.error(f"Erro ao ler planilha: {e}")
        st.info("Verifique se a planilha 'Tarefas_Dashboard' existe e se o cabeçalho é: Tarefa | Status | Data")
else:
    st.warning("⚠️ Configure os 'Secrets' com a credencial de serviço do Google Cloud para conectar à planilha.")

# 1. CLIMA (Simplificado)
st.markdown('<div class="section-header">🌤️ Clima</div>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
wq = get_weather(-18.4486, -50.4519)
wc = get_weather(-10.1264, -36.1756)
with c1: st.markdown(f"""<div class="card bg-gradient-blue"><div class="card-title">📍 Quirinópolis</div><div class="card-value">{wq['icon']} {wq['temp']}°C</div><div class="card-subtitle">Vento: {wq['wind']} km/h</div></div>""", unsafe_allow_html=True)
with c2: st.markdown(f"""<div class="card bg-gradient-green"><div class="card-title">🌊 Coruripe</div><div class="card-value">{wc['icon']} {wc['temp']}°C</div><div class="card-subtitle">Vento: {wc['wind']} km/h</div></div>""", unsafe_allow_html=True)

# 2. IA & TECH & AÇÕES
st.markdown('<div class="section-header">🤖 Tech & 📈 Mercado</div>', unsafe_allow_html=True)
col_ia, col_mkt = st.columns(2)

with col_ia:
    news_ai = get_news("DeepSeek OpenAI Google Gemini")
    if news_ai:
        item = news_ai[0]
        st.markdown(f"""<a href="{item.link}" target="_blank" style="text-decoration:none"><div class="card bg-gradient-purple"><div class="card-title">🤖 IA Destaque</div><div class="card-subtitle">{item.title}</div></div></a>""", unsafe_allow_html=True)

with col_mkt:
    dolar = get_dolar()
    st.markdown(f"""<div class="card bg-gradient-gold"><div class="card-title">💵 Dólar</div><div class="card-value">R$ {dolar:.3f}</div></div>""", unsafe_allow_html=True)

# 3. CARTEIRA (Resumo)
v_br = sum([get_stock_data(t)[1] for t in list(CARTEIRA_BR.keys())[:5]]) / 5 # Média simples demo
st.markdown(f"**Variação média Carteira Top 5 BR:** {v_br:.2f}%")

if st.button("🔄 Atualizar"):
    st.cache_data.clear()
    st.rerun()
