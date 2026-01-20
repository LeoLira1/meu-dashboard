import streamlit as st
import yfinance as yf
import requests
import feedparser
from datetime import datetime, timedelta
from urllib.parse import quote
import random
import os.path
import pickle

# --- BIBLIOTECAS GOOGLE TASKS ---
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Configuração da página
st.set_page_config(
    page_title="Dashboard Pessoal",
    page_icon="🤖",
    layout="wide"
)

# --- CSS APRIMORADO ---
st.markdown("""
<style>
    .main-header { font-size: 2.5rem; font-weight: 700; color: #333; }
    .update-time { color: #666; font-size: 0.9rem; margin-bottom: 1.5rem; }
    
    /* Cards Gerais */
    .card {
        border-radius: 16px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    .card:hover { transform: translateY(-2px); }
    
    /* Cores dos Cards */
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
    
    /* Tarefas */
    .task-row {
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 8px;
        border-left: 4px solid #4A00E0;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    /* Variação de Ações */
    .stock-badge {
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 0.8rem;
        margin-left: 10px;
    }
    .stock-badge-positive { background: rgba(17, 153, 142, 0.8); }
    .stock-badge-negative { background: rgba(255, 81, 47, 0.8); }
    
    /* Notícias */
    .news-card {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 0.8rem;
        border-left: 5px solid #1A2980;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .news-card a { color: #333; text-decoration: none; font-weight: 500; }
    .news-card a:hover { color: #1A2980; }
    
    .section-header { font-size: 1.4rem; font-weight: 600; margin: 2rem 0 1rem 0; color: #444; border-bottom: 2px solid #eee; padding-bottom: 0.5rem; }
</style>
""", unsafe_allow_html=True)

# --- CARTEIRA BRASILEIRA (ticker: qtd, pm) ---
CARTEIRA_BR = {
    "PRIO3.SA": (267, 42.38),
    "ALUP11.SA": (159, 28.79),
    "BBAS3.SA": (236, 27.24),
    "MOVI3.SA": (290, 6.82),
    "AGRO3.SA": (135, 24.98),
    "VALE3.SA": (25, 61.38),
    "VAMO3.SA": (226, 6.75),
    "BBSE3.SA": (19, 33.30),
    "FESA4.SA": (95, 8.14),
    "SLCE3.SA": (31, 18.00),
    "TTEN3.SA": (17, 14.61),
    "JALL3.SA": (43, 4.65),
    "AMOB3.SA": (3, 0.00),
    "GARE11.SA": (142, 9.10),
    "KNCR11.SA": (9, 103.30),
}

# --- CARTEIRA AMERICANA (ticker: qtd, pm em USD) ---
CARTEIRA_US = {
    "VOO": (0.89425, 475.26),
    "QQQ": (0.54245, 456.28),
    "TSLA": (0.52762, 205.26),
    "VNQ": (2.73961, 82.48),
    "OKLO": (2.0, 9.75),
    "VT": (1.0785, 112.68),
    "VTI": (0.43415, 264.89),
    "SLYV": (1.42787, 80.54),
    "GOOGL": (0.32828, 174.61),
    "IWD": (0.34465, 174.09),
    "DIA": (0.1373, 400.58),
    "DVY": (0.46175, 121.34),
    "META": (0.08487, 541.77),
    "BLK": (0.04487, 891.02),
    "DE": (0.10018, 399.28),
    "NVDA": (0.2276, 87.79),
    "CAT": (0.07084, 352.91),
    "AMD": (0.19059, 157.41),
    "NUE": (0.14525, 172.12),
    "COP": (0.24956, 120.21),
    "DTE": (0.12989, 115.48),
    "MSFT": (0.02586, 409.90),
    "GLD": (0.08304, 240.85),
    "NXE": (3.32257, 7.52),
    "XOM": (0.33901, 117.99),
    "SPY": (0.0546, 549.27),
    "JNJ": (0.13323, 150.12),
    "MPC": (0.14027, 178.23),
    "AMZN": (0.05482, 182.42),
    "DUK": (0.09776, 102.29),
    "NEE": (0.13274, 75.34),
    "DVN": (0.26214, 38.15),
    "JPM": (0.02529, 197.71),
    "MAGS": (0.09928, 54.19),
    "INTR": (0.77762, 6.43),
}

# --- FUNÇÕES GOOGLE TASKS ---
SCOPES = ['https://www.googleapis.com/auth/tasks']

def get_tasks_service():
    """Autentica e retorna o serviço do Google Tasks"""
    creds = None
    if os.path.exists('token.json'):
        try:
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        except:
            os.remove('token.json')
            creds = None
            
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if os.path.exists('client_secret.json'):
                try:
                    flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
                    creds = flow.run_local_server(port=0)
                except Exception as e:
                    st.error(f"Erro na autenticação: {e}")
                    return None
            else:
                return None
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('tasks', 'v1', credentials=creds)

# --- FUNÇÕES COM CACHE (PERFORMANCE) ---

@st.cache_data(ttl=900)
def get_weather(lat, lon):
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m,precipitation",
            "timezone": "America/Sao_Paulo"
        }
        response = requests.get(url, params=params, timeout=5)
        data = response.json().get("current", {})
        
        code = data.get("weather_code", 0)
        weather_map = {
            0: ("☀️", "Céu limpo"), 1: ("🌤️", "Parcialmente limpo"), 2: ("⛅", "Parcialmente nublado"),
            3: ("☁️", "Nublado"), 45: ("🌫️", "Neblina"), 48: ("🌫️", "Neblina/geada"),
            51: ("🌦️", "Chuvisco leve"), 53: ("🌦️", "Chuvisco"), 55: ("🌧️", "Chuvisco forte"),
            61: ("🌧️", "Chuva leve"), 63: ("🌧️", "Chuva moderada"), 65: ("🌧️", "Chuva forte"),
            80: ("🌦️", "Pancadas leves"), 81: ("🌧️", "Pancadas"), 82: ("⛈️", "Pancadas fortes"),
            95: ("⛈️", "Tempestade"), 96: ("⛈️", "Tempestade/granizo"), 99: ("⛈️", "Tempestade severa"),
        }
        icon, descricao = weather_map.get(code, ("☁️", "Nublado"))
        
        return {
            "temp": data.get("temperature_2m", "--"),
            "wind": data.get("wind_speed_10m", "--"),
            "humidity": data.get("relative_humidity_2m", "--"),
            "icon": icon,
            "descricao": descricao,
            "precipitacao": data.get("precipitation", 0)
        }
    except:
        return {"temp": "--", "wind": "--", "humidity": "--", "icon": "❓", "descricao": "Erro", "precipitacao": 0}

@st.cache_data(ttl=900)
def get_stock_data(ticker):
    try:
        acao = yf.Ticker(ticker)
        hist = acao.history(period="2d")
        if len(hist) >= 1:
            atual = hist['Close'].iloc[-1]
            anterior = hist['Close'].iloc[-2] if len(hist) > 1 else atual
            var = ((atual - anterior) / anterior) * 100
            return atual, var
        return 0.0, 0.0
    except:
        return 0.0, 0.0

@st.cache_data(ttl=900)
def get_dolar():
    try:
        ticker = yf.Ticker("USDBRL=X")
        hist = ticker.history(period="1d")
        if len(hist) >= 1:
            return hist['Close'].iloc[-1]
        return 6.0
    except:
        return 6.0

@st.cache_data(ttl=900)
def calcular_variacao_carteira_br():
    variacao_total = 0.0
    patrimonio_atual = 0.0
    custo_total = 0.0
    for ticker, (qtd, pm) in CARTEIRA_BR.items():
        try:
            acao = yf.Ticker(ticker)
            hist = acao.history(period="2d")
            if len(hist) >= 1:
                preco_atual = hist['Close'].iloc[-1]
                preco_anterior = hist['Close'].iloc[-2] if len(hist) > 1 else preco_atual
                variacao_total += (preco_atual - preco_anterior) * qtd
                patrimonio_atual += preco_atual * qtd
                custo_total += pm * qtd
        except: continue
    return variacao_total, patrimonio_atual, patrimonio_atual - custo_total

@st.cache_data(ttl=900)
def calcular_variacao_carteira_us():
    variacao_total = 0.0
    patrimonio_atual = 0.0
    custo_total = 0.0
    for ticker, (qtd, pm) in CARTEIRA_US.items():
        try:
            acao = yf.Ticker(ticker)
            hist = acao.history(period="2d")
            if len(hist) >= 1:
                preco_atual = hist['Close'].iloc[-1]
                preco_anterior = hist['Close'].iloc[-2] if len(hist) > 1 else preco_atual
                variacao_total += (preco_atual - preco_anterior) * qtd
                patrimonio_atual += preco_atual * qtd
                custo_total += pm * qtd
        except: continue
    return variacao_total, patrimonio_atual, patrimonio_atual - custo_total

@st.cache_data(ttl=1800)
def get_news(query):
    try:
        query_encoded = quote(query)
        url = f"https://news.google.com/rss/search?q={query_encoded}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
        feed = feedparser.parse(url)
        return feed.entries[:4]
    except: return []

@st.cache_data(ttl=900)
def get_ai_news(empresa, query):
    try:
        query_encoded = quote(query)
        url = f"https://news.google.com/rss/search?q={query_encoded}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
        feed = feedparser.parse(url)
        if feed.entries: return feed.entries[0]
        return None
    except: return None

# --- LÓGICA DO DASHBOARD ---

import pytz
fuso_brasilia = pytz.timezone('America/Sao_Paulo')
agora = datetime.now(fuso_brasilia)

col_hora, col_div1, col_div2, col_news = st.columns(4)
dia_semana = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"][agora.weekday()]

with col_hora:
    st.markdown(f"""
    <div class="card bg-gradient-dark" style="text-align: center;">
        <div class="card-title" style="justify-content: center;">📅 {dia_semana}, {agora.strftime("%d/%m")}</div>
        <div class="card-value" style="font-size: 2.2rem;">{agora.strftime("%H:%M")}</div>
        <div class="card-subtitle">Quirinópolis-GO</div>
    </div>
    """, unsafe_allow_html=True)

# Dividendos
DIVIDENDOS = [
    {"acao": "BBAS3", "tipo": "JCP", "valor": "R$ 0,47", "data": "31/01", "cor": "bg-gradient-blue"},
    {"acao": "VALE3", "tipo": "Dividendo", "valor": "R$ 2,09", "data": "12/03", "cor": "bg-gradient-green"},
    {"acao": "PRIO3", "tipo": "Dividendo", "valor": "R$ 1,23", "data": "15/02", "cor": "bg-gradient-teal"},
    {"acao": "BBSE3", "tipo": "Dividendo", "valor": "R$ 0,89", "data": "28/02", "cor": "bg-gradient-purple"},
    {"acao": "ITUB4", "tipo": "JCP", "valor": "R$ 0,32", "data": "01/02", "cor": "bg-gradient-orange"},
]
divs_mostrar = random.sample(DIVIDENDOS, 2)

with col_div1:
    div = divs_mostrar[0]
    st.markdown(f"""
    <div class="card {div['cor']}">
        <div class="card-title">💰 {div['acao']} • {div['tipo']}</div>
        <div class="card-value" style="font-size: 1.5rem;">{div['valor']}</div>
        <div class="card-subtitle">Data: {div['data']}</div>
    </div>
    """, unsafe_allow_html=True)

with col_div2:
    div = divs_mostrar[1]
    st.markdown(f"""
    <div class="card {div['cor']}">
        <div class="card-title">💰 {div['acao']} • {div['tipo']}</div>
        <div class="card-value" style="font-size: 1.5rem;">{div['valor']}</div>
        <div class="card-subtitle">Data: {div['data']}</div>
    </div>
    """, unsafe_allow_html=True)

with col_news:
    st.markdown(f"""
    <div class="card bg-gradient-red">
        <div class="card-title">📰 Info</div>
        <div class="card-subtitle">Painel Pessoal</div>
        <div class="card-subtitle" style="margin-top: 5px;">Atualizado: {agora.strftime("%H:%M")}</div>
    </div>
    """, unsafe_allow_html=True)

# --- 0. GOOGLE TASKS (NOVO) ---
st.markdown('<div class="section-header">📝 Minhas Tarefas (Google Tasks)</div>', unsafe_allow_html=True)

col_tasks_main, col_tasks_add = st.columns([2, 1])

# Inicializa serviço
service = get_tasks_service()

if service:
    # Adicionar tarefa
    with col_tasks_add:
        with st.form("nova_tarefa"):
            st.markdown("**Nova Tarefa**")
            titulo_task = st.text_input("Título", placeholder="Ex: Comprar ração")
            submit_task = st.form_submit_button("Adicionar")
            if submit_task and titulo_task:
                try:
                    service.tasks().insert(tasklist='@default', body={'title': titulo_task}).execute()
                    st.success("Adicionada!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")

    # Listar tarefas
    with col_tasks_main:
        try:
            results = service.tasks().list(tasklist='@default', showCompleted=False, maxResults=10).execute()
            items = results.get('items', [])
            
            if not items:
                st.info("Nenhuma tarefa pendente! 🎉")
            else:
                for item in items:
                    c1, c2 = st.columns([0.1, 0.9])
                    with c1:
                        # Botão para concluir
                        if st.button("✅", key=item['id'], help="Concluir tarefa"):
                            # Marca como concluída (update status)
                            item['status'] = 'completed'
                            service.tasks().update(tasklist='@default', task=item['id'], body=item).execute()
                            st.rerun()
                    with c2:
                        st.markdown(f"<div style='padding-top: 5px; font-size: 1.1rem;'>{item['title']}</div>", unsafe_allow_html=True)
                        
        except Exception as e:
            st.error(f"Erro ao carregar tarefas: {e}")
else:
    st.warning("⚠️ Configure o arquivo 'client_secret.json' na pasta do projeto para ativar o Google Tasks.")


# 1. FILMES & SÉRIES
st.markdown('<div class="section-header">🎬 Filmes & Séries</div>', unsafe_allow_html=True)
INDICACOES = [
    {"titulo": "Oppenheimer", "tipo": "Filme", "genero": "Drama", "nota": "9.0", "onde": "Prime"},
    {"titulo": "Interestelar", "tipo": "Filme", "genero": "Sci-Fi", "nota": "8.7", "onde": "Prime"},
    {"titulo": "Ruptura (Severance)", "tipo": "Série", "genero": "Sci-Fi", "nota": "8.7", "onde": "Apple TV+"},
    {"titulo": "Silo", "tipo": "Série", "genero": "Sci-Fi", "nota": "8.1", "onde": "Apple TV+"},
    {"titulo": "Blade Runner 2049", "tipo": "Filme", "genero": "Sci-Fi", "nota": "8.0", "onde": "Netflix"},
    {"titulo": "Shogun", "tipo": "Série", "genero": "Drama", "nota": "8.7", "onde": "Disney+"},
]
# Seleção aleatória garantindo diversidade
indicacoes_dia = random.sample(INDICACOES, 3)
cf1, cf2, cf3 = st.columns(3)
cores_filmes = ["bg-gradient-purple", "bg-gradient-red", "bg-gradient-teal"]

for i, (col, ind) in enumerate(zip([cf1, cf2, cf3], indicacoes_dia)):
    emoji = "🎬" if ind["tipo"] == "Filme" else "📺"
    with col:
        st.markdown(f"""
        <div class="card {cores_filmes[i]}">
            <div class="card-title">{emoji} {ind["tipo"]} • ⭐ {ind["nota"]}</div>
            <div class="card-value" style="font-size: 1.3rem">{ind["titulo"]}</div>
            <div class="card-subtitle">{ind["genero"]} • {ind["onde"]}</div>
        </div>
        """, unsafe_allow_html=True)

# 2. IA & TECH
st.markdown('<div class="section-header">🤖 IA & Tech</div>', unsafe_allow_html=True)
EMPRESAS_IA = [
    {"nome": "OpenAI", "query": "OpenAI ChatGPT news", "emoji": "🟢", "cor": "bg-gradient-green"},
    {"nome": "Claude", "query": "Anthropic Claude AI", "emoji": "🟠", "cor": "bg-gradient-orange"},
    {"nome": "Gemini", "query": "Google Gemini AI updates", "emoji": "🔵", "cor": "bg-gradient-blue"},
    {"nome": "DeepSeek", "query": "DeepSeek AI China", "emoji": "🟣", "cor": "bg-gradient-purple"},
]
cia1, cia2, cia3, cia4 = st.columns(4)
for col, emp in zip([cia1, cia2, cia3, cia4], EMPRESAS_IA):
    noticia = get_ai_news(emp["nome"], emp["query"])
    with col:
        if noticia:
            tit = noticia.title[:50] + "..." if len(noticia.title)>50 else noticia.title
            st.markdown(f"""<a href="{noticia.link}" target="_blank" style="text-decoration:none">
            <div class="card {emp['cor']}" style="min-height:140px; cursor:pointer">
                <div class="card-title">{emp['emoji']} {emp["nome"]}</div>
                <div class="card-subtitle" style="line-height:1.2">{tit}</div>
            </div></a>""", unsafe_allow_html=True)
        else:
             st.markdown(f"""<div class="card {emp['cor']}" style="min-height:140px">
                <div class="card-title">{emp['emoji']} {emp["nome"]}</div>
                <div class="card-subtitle">Sem news</div>
            </div>""", unsafe_allow_html=True)

# 3. CLIMA
st.markdown('<div class="section-header">🌤️ Clima na Região</div>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
w_quiri = get_weather(-18.4486, -50.4519) # Quirinópolis
w_coru = get_weather(-10.1264, -36.1756)  # Coruripe

with c1:
    p_txt = f" • 💧 {w_quiri['precipitacao']}mm" if w_quiri['precipitacao'] > 0 else ""
    st.markdown(f"""
    <div class="card bg-gradient-blue">
        <div class="card-title">📍 Quirinópolis - GO</div>
        <div class="card-value">{w_quiri['icon']} {w_quiri['temp']}°C</div>
        <div class="card-subtitle">{w_quiri['descricao']} • 💨 {w_quiri['wind']}km/h{p_txt}</div>
    </div>""", unsafe_allow_html=True)

with c2:
    p_txt = f" • 💧 {w_coru['precipitacao']}mm" if w_coru['precipitacao'] > 0 else ""
    st.markdown(f"""
    <div class="card bg-gradient-green">
        <div class="card-title">🌊 Coruripe - AL</div>
        <div class="card-value">{w_coru['icon']} {w_coru['temp']}°C</div>
        <div class="card-subtitle">{w_coru['descricao']} • 💨 {w_coru['wind']}km/h{p_txt}</div>
    </div>""", unsafe_allow_html=True)

# 4. AÇÕES FAVORITAS
st.markdown('<div class="section-header">📈 Ações em Destaque</div>', unsafe_allow_html=True)
stocks = list(CARTEIRA_BR.keys())[:3] + ["USDBRL=X"] # Simplificado para demo
cols_s = st.columns(4)
for i, ticker in enumerate(stocks):
    price, var = get_stock_data(ticker)
    bg = "stock-badge-positive" if var >= 0 else "stock-badge-negative"
    sym = "▲" if var >= 0 else "▼"
    with cols_s[i]:
        st.markdown(f"""
        <div class="card bg-gradient-dark">
            <div class="card-title">{ticker.split('.')[0]} <span class="stock-badge {bg}">{sym} {var:.1f}%</span></div>
            <div class="card-value">R$ {price:.2f}</div>
        </div>""", unsafe_allow_html=True)

# 5. NOTÍCIAS GERAIS
st.markdown('<div class="section-header">📰 Notícias Locais</div>', unsafe_allow_html=True)
n1, n2 = st.columns(2)
with n1:
    st.markdown("**🌴 Coruripe**")
    for item in get_news("Coruripe Alagoas"):
        st.markdown(f'- [{item.title}]({item.link})')
with n2:
    st.markdown("**📍 Quirinópolis**")
    for item in get_news("Quirinópolis Goiás"):
        st.markdown(f'- [{item.title}]({item.link})')

if st.button("🔄 Atualizar Tudo"):
    st.cache_data.clear()
    st.rerun()

# 6. CARTEIRA TOTAL
st.markdown('<div class="section-header">💰 Resumo Financeiro</div>', unsafe_allow_html=True)
dolar = get_dolar()
v_br, p_br, l_br = calcular_variacao_carteira_br()
v_us, p_us, l_us = calcular_variacao_carteira_us()

total_patrim = p_br + (p_us * dolar)
total_lucro = l_br + (l_us * dolar)
cor_lucro = "bg-gradient-green" if total_lucro >= 0 else "bg-gradient-red"

cc1, cc2 = st.columns(2)
with cc1:
    st.markdown(f"""<div class="card bg-gradient-gold"><div class="card-title">💵 Dólar</div><div class="card-value">R$ {dolar:.3f}</div></div>""", unsafe_allow_html=True)
with cc2:
    st.markdown(f"""<div class="card {cor_lucro}"><div class="card-title">💎 Lucro Total Estimado</div><div class="card-value">R$ {total_lucro:,.2f}</div><div class="card-subtitle">Patrimônio: R$ {total_patrim:,.2f}</div></div>""", unsafe_allow_html=True)
