import streamlit as st
import yfinance as yf
import requests
import feedparser
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="Meu Dashboard",
    page_icon="📊",
    layout="wide"
)

# CSS customizado para visual de cards
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .update-time {
        color: #888;
        font-size: 0.9rem;
        margin-bottom: 1.5rem;
    }
    .card {
        border-radius: 16px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .card-red {
        background: linear-gradient(135deg, #FF6B6B 0%, #FF8E8E 100%);
    }
    .card-blue {
        background: linear-gradient(135deg, #4FACFE 0%, #00F2FE 100%);
    }
    .card-green {
        background: linear-gradient(135deg, #43E97B 0%, #38F9D7 100%);
    }
    .card-purple {
        background: linear-gradient(135deg, #FA709A 0%, #FEE140 100%);
    }
    .card-dark {
        background: linear-gradient(135deg, #2C3E50 0%, #4CA1AF 100%);
    }
    .card-orange {
        background: linear-gradient(135deg, #F093FB 0%, #F5576C 100%);
    }
    .card-title {
        font-size: 0.9rem;
        opacity: 0.9;
        margin-bottom: 0.3rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .card-value {
        font-size: 2rem;
        font-weight: 700;
    }
    .card-subtitle {
        font-size: 0.8rem;
        opacity: 0.8;
    }
    .card-small-value {
        font-size: 1.3rem;
        font-weight: 600;
    }
    .news-card {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.5rem;
        border-left: 4px solid #FF6B6B;
    }
    .news-card a {
        color: #333;
        text-decoration: none;
        font-size: 0.9rem;
    }
    .news-card a:hover {
        color: #FF6B6B;
    }
    .section-title {
        font-size: 1.3rem;
        font-weight: 600;
        margin: 1.5rem 0 1rem 0;
        color: #333;
    }
    .stock-positive {
        color: #00C853;
        font-size: 0.85rem;
    }
    .stock-negative {
        color: #FF5252;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">📊 Meu Dashboard</div>', unsafe_allow_html=True)
st.markdown(f'<div class="update-time">Atualizado em: {datetime.now().strftime("%d/%m/%Y %H:%M")}</div>', unsafe_allow_html=True)

# === PRIMEIRA LINHA: CLIMA ===
st.markdown('<div class="section-title">🌤️ Clima</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

# Buscar clima de Quirinópolis
try:
    clima_quiri = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": -18.4486,
            "longitude": -50.4519,
            "current_weather": True,
            "timezone": "America/Sao_Paulo"
        },
        timeout=10
    ).json().get("current_weather", {})
except:
    clima_quiri = {}

# Buscar clima de Coruripe
try:
    clima_coruripe = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": -10.1264,
            "longitude": -36.1756,
            "current_weather": True,
            "timezone": "America/Sao_Paulo"
        },
        timeout=10
    ).json().get("current_weather", {})
except:
    clima_coruripe = {}

with col1:
    st.markdown(f"""
    <div class="card card-blue">
        <div class="card-title">🌡️ Quirinópolis</div>
        <div class="card-value">{clima_quiri.get('temperature', '?')}°C</div>
        <div class="card-subtitle">💨 {clima_quiri.get('windspeed', '?')} km/h</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="card card-green">
        <div class="card-title">🌡️ Coruripe</div>
        <div class="card-value">{clima_coruripe.get('temperature', '?')}°C</div>
        <div class="card-subtitle">💨 {clima_coruripe.get('windspeed', '?')} km/h</div>
    </div>
    """, unsafe_allow_html=True)

# === AÇÕES ===
st.markdown('<div class="section-title">📈 Ações B3</div>', unsafe_allow_html=True)

tickers_info = {
    "PRIO3.SA": {"nome": "PRIO3", "cor": "card-red"},
    "PETR4.SA": {"nome": "PETR4", "cor": "card-dark"},
    "VALE3.SA": {"nome": "VALE3", "cor": "card-purple"},
    "ITUB4.SA": {"nome": "ITUB4", "cor": "card-orange"},
}

cols = st.columns(4)

for i, (ticker, info) in enumerate(tickers_info.items()):
    try:
        acao = yf.Ticker(ticker)
        hist = acao.history(period="5d")
        if len(hist) >= 2:
            preco_atual = hist['Close'].iloc[-1]
            preco_anterior = hist['Close'].iloc[-2]
            variacao = ((preco_atual - preco_anterior) / preco_anterior) * 100
            var_class = "stock-positive" if variacao >= 0 else "stock-negative"
            var_symbol = "↑" if variacao >= 0 else "↓"
            var_text = f'<div class="{var_class}">{var_symbol} {variacao:+.2f}%</div>'
            preco_text = f"R$ {preco_atual:.2f}"
        elif len(hist) == 1:
            preco_text = f"R$ {hist['Close'].iloc[-1]:.2f}"
            var_text = ""
        else:
            preco_text = "N/D"
            var_text = ""
    except:
        preco_text = "Erro"
        var_text = ""
    
    with cols[i]:
        st.markdown(f"""
        <div class="card {info['cor']}">
            <div class="card-title">💹 {info['nome']}</div>
            <div class="card-small-value">{preco_text}</div>
            {var_text}
        </div>
        """, unsafe_allow_html=True)

# === NOTÍCIAS ===
st.markdown('<div class="section-title">📰 Notícias</div>', unsafe_allow_html=True)

col_news1, col_news2 = st.columns(2)

with col_news1:
    st.markdown("**Coruripe - AL**")
    try:
        feed_coruripe = feedparser.parse(
            "https://news.google.com/rss/search?q=Coruripe+Alagoas&hl=pt-BR&gl=BR&ceid=BR:pt-419"
        )
        for entry in feed_coruripe.entries[:4]:
            st.markdown(f"""
            <div class="news-card">
                <a href="{entry.link}" target="_blank">{entry.title}</a>
            </div>
            """, unsafe_allow_html=True)
    except:
        st.warning("Não foi possível carregar")

with col_news2:
    st.markdown("**Quirinópolis - GO**")
    try:
        feed_quiri = feedparser.parse(
            "https://news.google.com/rss/search?q=Quirinópolis+Goiás&hl=pt-BR&gl=BR&ceid=BR:pt-419"
        )
        for entry in feed_quiri.entries[:4]:
            st.markdown(f"""
            <div class="news-card">
                <a href="{entry.link}" target="_blank">{entry.title}</a>
            </div>
            """, unsafe_allow_html=True)
    except:
        st.warning("Não foi possível carregar")

# Botão de atualização
st.markdown("<br>", unsafe_allow_html=True)
if st.button("🔄 Atualizar dados"):
    st.rerun()
