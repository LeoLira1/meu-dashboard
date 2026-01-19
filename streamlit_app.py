import streamlit as st
import yfinance as yf
import requests
import feedparser
from datetime import datetime, timedelta
import random

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
    
    .card-title { font-size: 0.9rem; opacity: 0.9; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem; }
    .card-value { font-size: 1.8rem; font-weight: 700; margin-bottom: 0.2rem; }
    .card-subtitle { font-size: 0.8rem; opacity: 0.9; font-weight: 500; }
    
    /* Variação de Ações (Badge flutuante para contraste) */
    .stock-badge {
        background: rgba(255,255,255,0.2);
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 0.8rem;
        margin-left: 10px;
    }
    
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

# --- FUNÇÕES COM CACHE (PERFORMANCE) ---

@st.cache_data(ttl=3600) # Atualiza a cada 1 hora
def get_weather(lat, lon):
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current_weather": True,
            "timezone": "America/Sao_Paulo"
        }
        response = requests.get(url, params=params, timeout=5)
        data = response.json().get("current_weather", {})
        
        # Mapeamento simples de códigos WMO para Emojis
        code = data.get("weathercode", 0)
        icon = "☀️"
        if code in [1, 2, 3]: icon = "⛅"
        elif code in [45, 48]: icon = "🌫️"
        elif code in [51, 53, 55, 61, 63, 65]: icon = "🌧️"
        elif code >= 80: icon = "⛈️"
        
        return {
            "temp": data.get("temperature", "--"),
            "wind": data.get("windspeed", "--"),
            "icon": icon
        }
    except:
        return {"temp": "--", "wind": "--", "icon": "❓"}

@st.cache_data(ttl=900) # Atualiza a cada 15 min
def get_stock_data(ticker):
    try:
        acao = yf.Ticker(ticker)
        # Tenta pegar info rápida, se falhar pega histórico
        hist = acao.history(period="2d")
        if len(hist) >= 1:
            atual = hist['Close'].iloc[-1]
            anterior = hist['Close'].iloc[-2] if len(hist) > 1 else atual
            var = ((atual - anterior) / anterior) * 100
            return atual, var
        return 0.0, 0.0
    except:
        return 0.0, 0.0

@st.cache_data(ttl=1800) # Atualiza a cada 30 min
def get_news(query):
    try:
        # Codificando URL para evitar erros com acentos
        url = f"https://news.google.com/rss/search?q={query}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
        feed = feedparser.parse(url)
        return feed.entries[:4]
    except:
        return []

# --- LÓGICA DO DASHBOARD ---

# Header
st.markdown(f'<div class="main-header">Painel do Dia</div>', unsafe_allow_html=True)
st.markdown(f'<div class="update-time">Atualizado: {datetime.now().strftime("%d/%m %H:%M")} • Quirinópolis-GO</div>', unsafe_allow_html=True)

# 1. RESUMO PESSOAL (Novo!)
st.markdown('<div class="section-header">💪 Status & Metas</div>', unsafe_allow_html=True)
col_p1, col_p2, col_p3 = st.columns(3)

# Lógica do Treino
agora = datetime.now()
hora_treino = agora.replace(hour=20, minute=0, second=0, microsecond=0)
if agora.hour >= 21:
    msg_treino = "Treino Concluído? ✅"
    cor_treino = "bg-gradient-green"
elif agora.hour >= 20:
    msg_treino = "HORA DE ESMAGAR! 🔥"
    cor_treino = "bg-gradient-red"
else:
    delta = hora_treino - agora
    horas = delta.seconds // 3600
    minutos = (delta.seconds % 3600) // 60
    msg_treino = f"Faltam {horas}h {minutos}m"
    cor_treino = "bg-gradient-dark"

with col_p1:
    st.markdown(f"""
    <div class="card {cor_treino}">
        <div class="card-title">🏋️ Próximo Treino (20h)</div>
        <div class="card-value" style="font-size: 1.5rem">{msg_treino}</div>
    </div>
    """, unsafe_allow_html=True)

with col_p2:
    # Dados mockados baseados no seu histórico recente (Ideal conectar a um banco de dados real depois)
    st.markdown("""
    <div class="card bg-gradient-purple">
        <div class="card-title">🍗 Proteína (Meta: 200g)</div>
        <div class="card-value" style="font-size: 1.5rem">167g / 200g</div>
        <div class="card-subtitle">Faltam 33g hoje</div>
    </div>
    """, unsafe_allow_html=True)

with col_p3:
    # Easter Egg Anime
    quotes = [
        "A dor é momentânea, a desistência dura para sempre. (One Piece)",
        "Eu não vou morrer, parceiro. (One Piece)",
        "Erga-se! (Solo Leveling)",
        "O tempo não espera por ninguém. (Sousou no Frieren)"
    ]
    st.markdown(f"""
    <div class="card bg-gradient-orange">
        <div class="card-title">⚔️ Anime Quote</div>
        <div class="card-subtitle" style="font-style: italic">"{random.choice(quotes)}"</div>
    </div>
    """, unsafe_allow_html=True)


# 2. CLIMA
st.markdown('<div class="section-header">🌤️ Clima na Região</div>', unsafe_allow_html=True)
c1, c2 = st.columns(2)

# Quirinópolis (Atual)
w_quiri = get_weather(-18.4486, -50.4519)
# Coruripe (Interesse)
w_coru = get_weather(-10.1264, -36.1756)

with c1:
    st.markdown(f"""
    <div class="card bg-gradient-blue">
        <div class="card-title">📍 Quirinópolis - GO</div>
        <div class="card-value">{w_quiri['icon']} {w_quiri['temp']}°C</div>
        <div class="card-subtitle">Vento: {w_quiri['wind']} km/h</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="card bg-gradient-green">
        <div class="card-title">🌊 Coruripe - AL</div>
        <div class="card-value">{w_coru['icon']} {w_coru['temp']}°C</div>
        <div class="card-subtitle">Vento: {w_coru['wind']} km/h</div>
    </div>
    """, unsafe_allow_html=True)

# 3. AÇÕES
st.markdown('<div class="section-header">📈 Mercado Financeiro</div>', unsafe_allow_html=True)
stocks = {
    "PRIO3": "PRIO3.SA",
    "PETR4": "PETR4.SA",
    "VALE3": "VALE3.SA",
    "ITUB4": "ITUB4.SA"
}

cols_s = st.columns(4)
for i, (name, ticker) in enumerate(stocks.items()):
    price, var = get_stock_data(ticker)
    symbol = "▲" if var >= 0 else "▼"
    # Badge cor neutra para garantir leitura
    
    with cols_s[i]:
        st.markdown(f"""
        <div class="card bg-gradient-dark">
            <div class="card-title">{name} <span class="stock-badge">{symbol} {var:.1f}%</span></div>
            <div class="card-value">R$ {price:.2f}</div>
        </div>
        """, unsafe_allow_html=True)

# 4. NOTÍCIAS
st.markdown('<div class="section-header">📰 Giro de Notícias</div>', unsafe_allow_html=True)
n1, n2 = st.columns(2)

with n1:
    st.markdown("**🌴 Coruripe & Região**")
    news_al = get_news("Coruripe Alagoas")
    if news_al:
        for item in news_al:
            st.markdown(f'<div class="news-card"><a href="{item.link}" target="_blank">{item.title}</a></div>', unsafe_allow_html=True)
    else:
        st.info("Sem notícias recentes.")

with n2:
    st.markdown("**📍 Quirinópolis & Goiás**")
    news_go = get_news("Quirinópolis Goiás")
    if news_go:
        for item in news_go:
            st.markdown(f'<div class="news-card"><a href="{item.link}" target="_blank">{item.title}</a></div>', unsafe_allow_html=True)
    else:
        st.info("Sem notícias recentes.")

if st.button("🔄 Atualizar Tudo"):
    st.cache_data.clear()
    st.rerun()
