import streamlit as st
import yfinance as yf
import requests
import feedparser
from datetime import datetime, timedelta
from urllib.parse import quote
import random
import pytz

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
        min-height: 130px; /* Altura mínima para uniformidade */
        display: flex;
        flex-direction: column;
        justify-content: space-between;
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

# --- CARTEIRA BRASILEIRA ---
CARTEIRA_BR = {
    "PRIO3.SA": (267, 42.38), "ALUP11.SA": (159, 28.79), "BBAS3.SA": (236, 27.24),
    "MOVI3.SA": (290, 6.82), "AGRO3.SA": (135, 24.98), "VALE3.SA": (25, 61.38),
    "VAMO3.SA": (226, 6.75), "BBSE3.SA": (19, 33.30), "FESA4.SA": (95, 8.14),
    "SLCE3.SA": (31, 18.00), "TTEN3.SA": (17, 14.61), "JALL3.SA": (43, 4.65),
    "AMOB3.SA": (3, 0.00), "GARE11.SA": (142, 9.10), "KNCR11.SA": (9, 103.30),
}

# --- CARTEIRA AMERICANA ---
CARTEIRA_US = {
    "VOO": (0.89425, 475.26), "QQQ": (0.54245, 456.28), "TSLA": (0.52762, 205.26),
    "VNQ": (2.73961, 82.48), "OKLO": (2.0, 9.75), "VT": (1.0785, 112.68),
    "VTI": (0.43415, 264.89), "SLYV": (1.42787, 80.54), "GOOGL": (0.32828, 174.61),
    "IWD": (0.34465, 174.09), "DIA": (0.1373, 400.58), "DVY": (0.46175, 121.34),
    "META": (0.08487, 541.77), "BLK": (0.04487, 891.02), "DE": (0.10018, 399.28),
    "NVDA": (0.2276, 87.79), "CAT": (0.07084, 352.91), "AMD": (0.19059, 157.41),
    "NUE": (0.14525, 172.12), "COP": (0.24956, 120.21), "DTE": (0.12989, 115.48),
    "MSFT": (0.02586, 409.90), "GLD": (0.08304, 240.85), "NXE": (3.32257, 7.52),
    "XOM": (0.33901, 117.99), "SPY": (0.0546, 549.27), "JNJ": (0.13323, 150.12),
    "MPC": (0.14027, 178.23), "AMZN": (0.05482, 182.42), "DUK": (0.09776, 102.29),
    "NEE": (0.13274, 75.34), "DVN": (0.26214, 38.15), "JPM": (0.02529, 197.71),
    "MAGS": (0.09928, 54.19), "INTR": (0.77762, 6.43),
}

# --- FUNÇÕES COM CACHE (PERFORMANCE) ---

@st.cache_data(ttl=900)
def get_weather(lat, lon):
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat, "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m,precipitation",
            "timezone": "America/Sao_Paulo"
        }
        response = requests.get(url, params=params, timeout=5)
        data = response.json().get("current", {})
        code = data.get("weather_code", 0)
        weather_map = {
            0: ("☀️", "Limpo"), 1: ("🌤️", "Parcial"), 2: ("⛅", "Nublado"), 3: ("☁️", "Nublado"),
            51: ("🌦️", "Chuvisco"), 61: ("🌧️", "Chuva"), 80: ("🌦️", "Pancadas"), 95: ("⛈️", "Tempestade")
        }
        icon, descricao = weather_map.get(code, ("☁️", "Nublado"))
        return {
            "temp": data.get("temperature_2m", "--"),
            "wind": data.get("wind_speed_10m", "--"),
            "humidity": data.get("relative_humidity_2m", "--"),
            "icon": icon, "descricao": descricao,
            "precipitacao": data.get("precipitation", 0)
        }
    except:
        return {"temp": "--", "wind": "--", "humidity": "--", "icon": "❓", "descricao": "Erro", "precipitacao": 0}

@st.cache_data(ttl=900)
def get_stock_data(ticker):
    try:
        hist = yf.Ticker(ticker).history(period="2d")
        if len(hist) >= 1:
            atual = hist['Close'].iloc[-1]
            ant = hist['Close'].iloc[-2] if len(hist) > 1 else atual
            return atual, ((atual - ant) / ant) * 100
        return 0.0, 0.0
    except: return 0.0, 0.0

@st.cache_data(ttl=900)
def get_dolar():
    try:
        hist = yf.Ticker("USDBRL=X").history(period="1d")
        return hist['Close'].iloc[-1] if len(hist) >= 1 else 6.0
    except: return 6.0

@st.cache_data(ttl=900)
def calcular_variacao_carteira_br():
    var_total, pat_atual, custo_total = 0.0, 0.0, 0.0
    for ticker, (qtd, pm) in CARTEIRA_BR.items():
        try:
            p, v = get_stock_data(ticker) # simplificado para usar cache individual
            # Recalculo manual rápido apenas para totais
            hist = yf.Ticker(ticker).history(period="2d")
            if len(hist) >= 1:
                pa = hist['Close'].iloc[-1]
                pant = hist['Close'].iloc[-2] if len(hist) > 1 else pa
                var_total += (pa - pant) * qtd
                pat_atual += pa * qtd
                custo_total += pm * qtd
        except: continue
    return var_total, pat_atual, pat_atual - custo_total

@st.cache_data(ttl=900)
def calcular_variacao_carteira_us():
    var_total, pat_atual, custo_total = 0.0, 0.0, 0.0
    for ticker, (qtd, pm) in CARTEIRA_US.items():
        try:
            hist = yf.Ticker(ticker).history(period="2d")
            if len(hist) >= 1:
                pa = hist['Close'].iloc[-1]
                pant = hist['Close'].iloc[-2] if len(hist) > 1 else pa
                var_total += (pa - pant) * qtd
                pat_atual += pa * qtd
                custo_total += pm * qtd
        except: continue
    return var_total, pat_atual, pat_atual - custo_total

@st.cache_data(ttl=1800)
def get_news(query):
    try:
        url = f"https://news.google.com/rss/search?q={quote(query)}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
        return feedparser.parse(url).entries[:4]
    except: return []

@st.cache_data(ttl=1800)
def get_stock_news(query):
    try:
        url = f"https://news.google.com/rss/search?q={quote(query)}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
        entries = feedparser.parse(url).entries
        return entries[0] if entries else None
    except: return None

# --- LÓGICA DO DASHBOARD ---

fuso_brasilia = pytz.timezone('America/Sao_Paulo')
agora = datetime.now(fuso_brasilia)

# Header com 4 colunas: Hora | Notícia Variada 1 | Notícia Variada 2 | Notícia Ação
col_hora, col_div1, col_div2, col_news = st.columns(4)

dia_semana = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"][agora.weekday()]

# 1. Coluna HORA
with col_hora:
    st.markdown(f"""
    <div class="card bg-gradient-dark" style="text-align: center;">
        <div class="card-title" style="justify-content: center;">📅 {dia_semana}, {agora.strftime("%d/%m")}</div>
        <div class="card-value" style="font-size: 2.2rem;">{agora.strftime("%H:%M")}</div>
        <div class="card-subtitle">Quirinópolis-GO</div>
    </div>
    """, unsafe_allow_html=True)

# --- NOTÍCIAS VARIADAS (Substituindo Tasks) ---
# Lista de tópicos para sortear e garantir variedade no refresh
TOPICOS_VARIADOS = [
    {"emoji": "🌍", "tema": "Mundo", "query": "notícias internacionais mundo", "cor": "bg-gradient-blue"},
    {"emoji": "🚀", "tema": "Inovação", "query": "tecnologia inovação futuro", "cor": "bg-gradient-purple"},
    {"emoji": "🧬", "tema": "Ciência", "query": "ciência descobertas espaciais", "cor": "bg-gradient-teal"},
    {"emoji": "🎮", "tema": "Games", "query": "lançamentos games jogos pc console", "cor": "bg-gradient-red"},
    {"emoji": "🎬", "tema": "Cinema", "query": "novidades cinema filmes séries", "cor": "bg-gradient-orange"},
    {"emoji": "🚗", "tema": "Auto", "query": "lançamentos automotivos carros", "cor": "bg-gradient-dark"},
    {"emoji": "💡", "tema": "Curiosidades", "query": "curiosidades ciência mundo", "cor": "bg-gradient-green"},
]

# Sorteia 2 tópicos diferentes da lista
topicos_escolhidos = random.sample(TOPICOS_VARIADOS, 2)

# Função auxiliar para renderizar o card
def render_news_card(column, topic_data):
    # Busca notícias
    news_items = get_news(topic_data["query"])
    
    with column:
        if news_items:
            # Pega uma notícia aleatória das 4 retornadas para variar ainda mais
            item = random.choice(news_items)
            titulo = item.title[:50] + "..." if len(item.title) > 50 else item.title
            
            st.markdown(f"""
            <a href="{item.link}" target="_blank" style="text-decoration: none;">
                <div class="card {topic_data['cor']}" style="cursor: pointer;">
                    <div class="card-title">{topic_data['emoji']} {topic_data['tema']}</div>
                    <div class="card-subtitle" style="font-size: 0.95rem; line-height: 1.3; font-weight: 600;">{titulo}</div>
                    <div class="card-subtitle" style="margin-top: 8px; opacity: 0.8; font-size: 0.75rem;">Clique para ler</div>
                </div>
            </a>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="card {topic_data['cor']}">
                <div class="card-title">{topic_data['emoji']} {topic_data['tema']}</div>
                <div class="card-subtitle">Atualizando...</div>
            </div>
            """, unsafe_allow_html=True)

# 2. e 3. Colunas NOTÍCIAS VARIADAS
render_news_card(col_div1, topicos_escolhidos[0])
render_news_card(col_div2, topicos_escolhidos[1])

# 4. Coluna NOTÍCIA AÇÃO (Mantido)
with col_news:
    acoes_news = ["PRIO3 petróleo", "VALE3 mineração", "BBAS3 banco", "AGRO3 agronegócio"]
    acao_escolhida = random.choice(acoes_news)
    noticia = get_stock_news(acao_escolhida)
    
    if noticia:
        titulo = noticia.title[:50] + "..." if len(noticia.title) > 50 else noticia.title
        st.markdown(f"""
        <a href="{noticia.link}" target="_blank" style="text-decoration: none;">
            <div class="card bg-gradient-red" style="cursor: pointer;">
                <div class="card-title">📰 {acao_escolhida.split()[0]}</div>
                <div class="card-subtitle" style="font-size: 0.95rem; line-height: 1.3; font-weight: 600;">{titulo}</div>
                <div class="card-subtitle" style="margin-top: 8px; opacity: 0.8; font-size: 0.75rem;">Info Mercado</div>
            </div>
        </a>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="card bg-gradient-red">
            <div class="card-title">📰 Mercado</div>
            <div class="card-subtitle">Sem notícias</div>
        </div>
        """, unsafe_allow_html=True)

# 1. FILMES & SÉRIES
st.markdown('<div class="section-header">🎬 Filmes & Séries</div>', unsafe_allow_html=True)
INDICACOES = [
    {"titulo": "Oppenheimer", "tipo": "Filme", "genero": "Histórico", "nota": "9.0", "onde": "Prime"},
    {"titulo": "Interestelar", "tipo": "Filme", "genero": "Sci-Fi", "nota": "8.7", "onde": "Prime"},
    {"titulo": "Severance", "tipo": "Série", "genero": "Sci-Fi", "nota": "8.7", "onde": "Apple TV+"},
    {"titulo": "The Bear", "tipo": "Série", "genero": "Drama", "nota": "8.6", "onde": "Star+"},
    {"titulo": "Shogun", "tipo": "Série", "genero": "Histórico", "nota": "8.7", "onde": "Disney+"},
    {"titulo": "Succession", "tipo": "Série", "genero": "Drama", "nota": "8.9", "onde": "Max"},
]
indicacoes_dia = random.sample(INDICACOES, 3)
col_f1, col_f2, col_f3 = st.columns(3)
cores_filmes = ["bg-gradient-purple", "bg-gradient-red", "bg-gradient-teal"]

for i, (col, ind) in enumerate(zip([col_f1, col_f2, col_f3], indicacoes_dia)):
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

@st.cache_data(ttl=900)
def get_ai_news(query):
    try: return feedparser.parse(f"https://news.google.com/rss/search?q={quote(query)}&hl=pt-BR&gl=BR&ceid=BR:pt-419").entries[0]
    except: return None

for col, emp in zip([cia1, cia2, cia3, cia4], EMPRESAS_IA):
    noticia = get_ai_news(emp["query"])
    with col:
        if noticia:
            tit = noticia.title[:50] + "..." if len(noticia.title)>50 else noticia.title
            st.markdown(f"""<a href="{noticia.link}" target="_blank" style="text-decoration:none">
            <div class="card {emp['cor']}" style="min-height:140px; cursor:pointer">
                <div class="card-title">{emp['emoji']} {emp["nome"]}</div>
                <div class="card-subtitle" style="line-height:1.2">{tit}</div>
            </div></a>""", unsafe_allow_html=True)
        else:
             st.markdown(f"""<div class="card {emp['cor']}" style="min-height:140px"><div class="card-title">{emp['emoji']} {emp["nome"]}</div><div class="card-subtitle">Sem news</div></div>""", unsafe_allow_html=True)

# 3. CLIMA
st.markdown('<div class="section-header">🌤️ Clima na Região</div>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
w_quiri = get_weather(-18.4486, -50.4519)
w_coru = get_weather(-10.1264, -36.1756)

with c1:
    p_txt = f" • 💧 {w_quiri['precipitacao']}mm" if w_quiri['precipitacao'] > 0 else ""
    st.markdown(f"""<div class="card bg-gradient-blue"><div class="card-title">📍 Quirinópolis - GO</div><div class="card-value">{w_quiri['icon']} {w_quiri['temp']}°C</div><div class="card-subtitle">{w_quiri['descricao']} • 💨 {w_quiri['wind']}km/h{p_txt}</div></div>""", unsafe_allow_html=True)

with c2:
    p_txt = f" • 💧 {w_coru['precipitacao']}mm" if w_coru['precipitacao'] > 0 else ""
    st.markdown(f"""<div class="card bg-gradient-green"><div class="card-title">🌊 Coruripe - AL</div><div class="card-value">{w_coru['icon']} {w_coru['temp']}°C</div><div class="card-subtitle">{w_coru['descricao']} • 💨 {w_coru['wind']}km/h{p_txt}</div></div>""", unsafe_allow_html=True)

# 4. AÇÕES
st.markdown('<div class="section-header">📈 Destaques Mercado</div>', unsafe_allow_html=True)
stocks = list(CARTEIRA_BR.keys())[:3] + ["USDBRL=X"]
cols_s = st.columns(4)
for i, ticker in enumerate(stocks):
    price, var = get_stock_data(ticker)
    bg = "stock-badge-positive" if var >= 0 else "stock-badge-negative"
    sym = "▲" if var >= 0 else "▼"
    name = ticker.split('.')[0]
    with cols_s[i]:
        st.markdown(f"""<div class="card bg-gradient-dark"><div class="card-title">{name} <span class="stock-badge {bg}">{sym} {var:.1f}%</span></div><div class="card-value">R$ {price:.2f}</div></div>""", unsafe_allow_html=True)

# 5. NOTÍCIAS LOCAIS
st.markdown('<div class="section-header">📰 Giro Local</div>', unsafe_allow_html=True)
n1, n2 = st.columns(2)
with n1:
    st.markdown("**🌴 Coruripe**")
    for item in get_news("Coruripe Alagoas"): st.markdown(f'<div class="news-card"><a href="{item.link}" target="_blank">{item.title}</a></div>', unsafe_allow_html=True)
with n2:
    st.markdown("**📍 Quirinópolis**")
    for item in get_news("Quirinópolis Goiás"): st.markdown(f'<div class="news-card"><a href="{item.link}" target="_blank">{item.title}</a></div>', unsafe_allow_html=True)

if st.button("🔄 Atualizar Dashboard"):
    st.cache_data.clear()
    st.rerun()

# 6. RODAPÉ FINANCEIRO
st.markdown('<div class="section-header">💰 Resumo Carteira</div>', unsafe_allow_html=True)
dolar = get_dolar()
v_br, p_br, l_br = calcular_variacao_carteira_br()
v_us, p_us, l_us = calcular_variacao_carteira_us()
total_lucro = l_br + (l_us * dolar)
total_patrim = p_br + (p_us * dolar)
cor_lucro = "bg-gradient-green" if total_lucro >= 0 else "bg-gradient-red"

cc1, cc2 = st.columns(2)
with cc1: st.markdown(f"""<div class="card bg-gradient-gold"><div class="card-title">💵 Dólar</div><div class="card-value">R$ {dolar:.3f}</div></div>""", unsafe_allow_html=True)
with cc2: st.markdown(f"""<div class="card {cor_lucro}"><div class="card-title">💎 Lucro Total</div><div class="card-value">R$ {total_lucro:,.2f}</div><div class="card-subtitle">Patrimônio: R$ {total_patrim:,.2f}</div></div>""", unsafe_allow_html=True)
