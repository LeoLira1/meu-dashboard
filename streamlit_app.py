import streamlit as st
import yfinance as yf
import requests
import feedparser
from datetime import datetime, timedelta
from urllib.parse import quote
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
    .bg-gradient-gold { background: linear-gradient(135deg, #F7971E 0%, #FFD200 100%); }
    .bg-gradient-teal { background: linear-gradient(135deg, #0F2027 0%, #203A43 50%, #2C5364 100%); }
    
    .card-title { font-size: 0.9rem; opacity: 0.9; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem; }
    .card-value { font-size: 1.8rem; font-weight: 700; margin-bottom: 0.2rem; }
    .card-subtitle { font-size: 0.8rem; opacity: 0.9; font-weight: 500; }
    
    /* Variação de Ações (Badge flutuante para contraste) */
    .stock-badge {
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 0.8rem;
        margin-left: 10px;
    }
    .stock-badge-positive {
        background: rgba(17, 153, 142, 0.8);
    }
    .stock-badge-negative {
        background: rgba(255, 81, 47, 0.8);
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

# --- FUNÇÕES COM CACHE (PERFORMANCE) ---

@st.cache_data(ttl=900)  # Atualiza a cada 15 min para clima mais preciso
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
        
        # Mapeamento de códigos WMO para Emojis e descrição
        code = data.get("weather_code", 0)
        
        # Códigos WMO mais detalhados
        weather_map = {
            0: ("☀️", "Céu limpo"),
            1: ("🌤️", "Parcialmente limpo"),
            2: ("⛅", "Parcialmente nublado"),
            3: ("☁️", "Nublado"),
            45: ("🌫️", "Neblina"),
            48: ("🌫️", "Neblina com geada"),
            51: ("🌦️", "Chuvisco leve"),
            53: ("🌦️", "Chuvisco"),
            55: ("🌧️", "Chuvisco forte"),
            61: ("🌧️", "Chuva leve"),
            63: ("🌧️", "Chuva moderada"),
            65: ("🌧️", "Chuva forte"),
            66: ("🌧️", "Chuva congelante"),
            67: ("🌧️", "Chuva congelante forte"),
            71: ("🌨️", "Neve leve"),
            73: ("🌨️", "Neve"),
            75: ("❄️", "Neve forte"),
            80: ("🌦️", "Pancadas leves"),
            81: ("🌧️", "Pancadas"),
            82: ("⛈️", "Pancadas fortes"),
            85: ("🌨️", "Pancadas de neve"),
            86: ("❄️", "Nevasca"),
            95: ("⛈️", "Tempestade"),
            96: ("⛈️", "Tempestade com granizo"),
            99: ("⛈️", "Tempestade severa"),
        }
        
        icon, descricao = weather_map.get(code, ("❓", "Indisponível"))
        precipitacao = data.get("precipitation", 0)
        
        return {
            "temp": data.get("temperature_2m", "--"),
            "wind": data.get("wind_speed_10m", "--"),
            "humidity": data.get("relative_humidity_2m", "--"),
            "icon": icon,
            "descricao": descricao,
            "precipitacao": precipitacao
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
    """Retorna cotação do dólar"""
    try:
        ticker = yf.Ticker("USDBRL=X")
        hist = ticker.history(period="1d")
        if len(hist) >= 1:
            return hist['Close'].iloc[-1]
        return 6.0  # fallback
    except:
        return 6.0

@st.cache_data(ttl=900)
def calcular_variacao_carteira_br():
    """Calcula variação diária da carteira BR em R$"""
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
                
                # Variação do dia em R$
                variacao_dia = (preco_atual - preco_anterior) * qtd
                variacao_total += variacao_dia
                
                # Patrimônio atual
                patrimonio_atual += preco_atual * qtd
                custo_total += pm * qtd
        except:
            continue
    
    # Lucro/Prejuízo total vs PM
    lucro_total = patrimonio_atual - custo_total
    
    return variacao_total, patrimonio_atual, lucro_total

@st.cache_data(ttl=900)
def calcular_variacao_carteira_us():
    """Calcula variação diária da carteira US em US$"""
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
                
                variacao_dia = (preco_atual - preco_anterior) * qtd
                variacao_total += variacao_dia
                
                patrimonio_atual += preco_atual * qtd
                custo_total += pm * qtd
        except:
            continue
    
    lucro_total = patrimonio_atual - custo_total
    
    return variacao_total, patrimonio_atual, lucro_total

@st.cache_data(ttl=1800)
def get_news(query):
    try:
        query_encoded = quote(query)
        url = f"https://news.google.com/rss/search?q={query_encoded}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        feed = feedparser.parse(response.content)
        return feed.entries[:4]
        
    except requests.RequestException:
        try:
            query_encoded = quote(query)
            url = f"https://news.google.com/rss/search?q={query_encoded}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
            feed = feedparser.parse(
                url,
                agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            return feed.entries[:4]
        except:
            return []
    except:
        return []

# --- LÓGICA DO DASHBOARD ---

# Ajuste de fuso horário para Brasília
import pytz
fuso_brasilia = pytz.timezone('America/Sao_Paulo')
agora = datetime.now(fuso_brasilia)

# Header compacto com cards úteis
col_hora, col_div1, col_div2, col_news = st.columns(4)

# Card de Hora Atual
dia_semana = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"][agora.weekday()]

with col_hora:
    st.markdown(f"""
    <div class="card bg-gradient-dark" style="text-align: center;">
        <div class="card-title" style="justify-content: center;">📅 {dia_semana}, {agora.strftime("%d/%m")}</div>
        <div class="card-value" style="font-size: 2.2rem;">{agora.strftime("%H:%M")}</div>
        <div class="card-subtitle">Quirinópolis-GO</div>
    </div>
    """, unsafe_allow_html=True)

# Função para buscar notícias das ações
@st.cache_data(ttl=1800)
def get_stock_news(query):
    try:
        query_encoded = quote(query)
        url = f"https://news.google.com/rss/search?q={query_encoded}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        feed = feedparser.parse(response.content)
        if feed.entries:
            return feed.entries[0]
        return None
    except:
        return None

# Categorias de notícias para os cards
CATEGORIAS_NEWS = [
    {"nome": "Tecnologia", "query": "tecnologia inovação", "emoji": "💻", "cor": "bg-gradient-purple"},
    {"nome": "Ciência", "query": "ciência descoberta pesquisa", "emoji": "🔬", "cor": "bg-gradient-blue"},
    {"nome": "Espaço", "query": "NASA espaço astronomia", "emoji": "🚀", "cor": "bg-gradient-teal"},
    {"nome": "Economia", "query": "economia Brasil mercado", "emoji": "📊", "cor": "bg-gradient-green"},
    {"nome": "Mundo", "query": "internacional mundo notícias", "emoji": "🌍", "cor": "bg-gradient-orange"},
]

# Selecionar 2 categorias aleatórias para os cards
categorias_selecionadas = random.sample(CATEGORIAS_NEWS, 2)

# Card de Notícia 1
with col_div1:
    cat1 = categorias_selecionadas[0]
    noticia1 = get_stock_news(cat1["query"])
    
    if noticia1:
        titulo1 = noticia1.title[:45] + "..." if len(noticia1.title) > 45 else noticia1.title
        st.markdown(f"""
        <a href="{noticia1.link}" target="_blank" style="text-decoration: none;">
            <div class="card {cat1['cor']}" style="cursor: pointer;">
                <div class="card-title">{cat1['emoji']} {cat1['nome']}</div>
                <div class="card-subtitle" style="font-size: 0.9rem; line-height: 1.3;">{titulo1}</div>
                <div class="card-subtitle" style="margin-top: 5px; opacity: 0.7;">Clique para ler</div>
            </div>
        </a>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="card {cat1['cor']}">
            <div class="card-title">{cat1['emoji']} {cat1['nome']}</div>
            <div class="card-subtitle">Sem notícias no momento</div>
        </div>
        """, unsafe_allow_html=True)

# Card de Notícia 2
with col_div2:
    cat2 = categorias_selecionadas[1]
    noticia2 = get_stock_news(cat2["query"])
    
    if noticia2:
        titulo2 = noticia2.title[:45] + "..." if len(noticia2.title) > 45 else noticia2.title
        st.markdown(f"""
        <a href="{noticia2.link}" target="_blank" style="text-decoration: none;">
            <div class="card {cat2['cor']}" style="cursor: pointer;">
                <div class="card-title">{cat2['emoji']} {cat2['nome']}</div>
                <div class="card-subtitle" style="font-size: 0.9rem; line-height: 1.3;">{titulo2}</div>
                <div class="card-subtitle" style="margin-top: 5px; opacity: 0.7;">Clique para ler</div>
            </div>
        </a>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="card {cat2['cor']}">
            <div class="card-title">{cat2['emoji']} {cat2['nome']}</div>
            <div class="card-subtitle">Sem notícias no momento</div>
        </div>
        """, unsafe_allow_html=True)

# Notícia de uma ação da carteira
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
                <div class="card-subtitle" style="font-size: 0.9rem; line-height: 1.3;">{titulo}</div>
                <div class="card-subtitle" style="margin-top: 5px; opacity: 0.7;">Clique para ler</div>
            </div>
        </a>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="card bg-gradient-red">
            <div class="card-title">📰 Notícias</div>
            <div class="card-subtitle">Sem notícias no momento</div>
        </div>
        """, unsafe_allow_html=True)

# 1. FILMES & SÉRIES
st.markdown('<div class="section-header">🎬 Filmes & Séries</div>', unsafe_allow_html=True)

# Lista de indicações (filmes e séries com nota e gênero)
INDICACOES = [
    {"titulo": "Oppenheimer", "tipo": "Filme", "genero": "Drama/Histórico", "nota": "9.0", "onde": "Prime Video"},
    {"titulo": "Se7en", "tipo": "Filme", "genero": "Suspense/Crime", "nota": "8.6", "onde": "Netflix"},
    {"titulo": "Interestelar", "tipo": "Filme", "genero": "Ficção Científica", "nota": "8.7", "onde": "Prime Video"},
    {"titulo": "O Poço", "tipo": "Filme", "genero": "Terror/Suspense", "nota": "7.0", "onde": "Netflix"},
    {"titulo": "Clube da Luta", "tipo": "Filme", "genero": "Drama/Suspense", "nota": "8.8", "onde": "Star+"},
    {"titulo": "Parasita", "tipo": "Filme", "genero": "Suspense/Drama", "nota": "8.5", "onde": "Prime Video"},
    {"titulo": "A Origem", "tipo": "Filme", "genero": "Ficção Científica", "nota": "8.8", "onde": "HBO Max"},
    {"titulo": "O Jogo da Imitação", "tipo": "Filme", "genero": "Drama/Biografia", "nota": "8.0", "onde": "Netflix"},
    {"titulo": "Duna: Parte 2", "tipo": "Filme", "genero": "Ficção Científica", "nota": "8.8", "onde": "Max"},
    {"titulo": "Whiplash", "tipo": "Filme", "genero": "Drama/Musical", "nota": "8.5", "onde": "Prime Video"},
    {"titulo": "Breaking Bad", "tipo": "Série", "genero": "Drama/Crime", "nota": "9.5", "onde": "Netflix"},
    {"titulo": "Succession", "tipo": "Série", "genero": "Drama", "nota": "8.9", "onde": "Max"},
    {"titulo": "Dark", "tipo": "Série", "genero": "Ficção Científica", "nota": "8.7", "onde": "Netflix"},
    {"titulo": "Severance", "tipo": "Série", "genero": "Suspense/Ficção", "nota": "8.7", "onde": "Apple TV+"},
    {"titulo": "The Bear", "tipo": "Série", "genero": "Drama/Comédia", "nota": "8.6", "onde": "Star+"},
    {"titulo": "Shogun", "tipo": "Série", "genero": "Drama/Histórico", "nota": "8.7", "onde": "Star+"},
    {"titulo": "True Detective S1", "tipo": "Série", "genero": "Crime/Drama", "nota": "9.0", "onde": "Max"},
    {"titulo": "Chernobyl", "tipo": "Série", "genero": "Drama/Histórico", "nota": "9.4", "onde": "Max"},
    {"titulo": "The Last of Us", "tipo": "Série", "genero": "Drama/Ação", "nota": "8.8", "onde": "Max"},
    {"titulo": "Bem-vindos ao Derry", "tipo": "Série", "genero": "Terror", "nota": "8.1", "onde": "Max"},
]

# Selecionar 3 indicações aleatórias
indicacoes_dia = random.sample(INDICACOES, 3)

col_f1, col_f2, col_f3 = st.columns(3)

cores_filmes = ["bg-gradient-purple", "bg-gradient-red", "bg-gradient-teal"]

for i, (col, indicacao) in enumerate(zip([col_f1, col_f2, col_f3], indicacoes_dia)):
    emoji = "🎬" if indicacao["tipo"] == "Filme" else "📺"
    with col:
        st.markdown(f"""
        <div class="card {cores_filmes[i]}">
            <div class="card-title">{emoji} {indicacao["tipo"]} • ⭐ {indicacao["nota"]}</div>
            <div class="card-value" style="font-size: 1.3rem">{indicacao["titulo"]}</div>
            <div class="card-subtitle">{indicacao["genero"]} • {indicacao["onde"]}</div>
        </div>
        """, unsafe_allow_html=True)

# 2. IA & TECH
st.markdown('<div class="section-header">🤖 IA & Tech</div>', unsafe_allow_html=True)

@st.cache_data(ttl=900)  # Atualiza a cada 15 min
def get_ai_news(empresa, query):
    """Busca notícias de empresas de IA"""
    try:
        query_encoded = quote(query)
        url = f"https://news.google.com/rss/search?q={query_encoded}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        feed = feedparser.parse(response.content)
        if feed.entries:
            return feed.entries[0]  # Retorna a notícia mais recente
        return None
    except Exception as e:
        return None

# Empresas de IA para buscar notícias (queries mais específicas)
EMPRESAS_IA = [
    {"nome": "OpenAI", "query": "OpenAI GPT ChatGPT 2025", "emoji": "🟢", "cor": "bg-gradient-green"},
    {"nome": "Claude", "query": "Anthropic Claude inteligência artificial", "emoji": "🟠", "cor": "bg-gradient-orange"},
    {"nome": "Gemini", "query": "Google Gemini IA 2025", "emoji": "🔵", "cor": "bg-gradient-blue"},
    {"nome": "DeepSeek", "query": "DeepSeek IA China", "emoji": "🟣", "cor": "bg-gradient-purple"},
]

col_ia1, col_ia2, col_ia3, col_ia4 = st.columns(4)

for col, empresa in zip([col_ia1, col_ia2, col_ia3, col_ia4], EMPRESAS_IA):
    noticia = get_ai_news(empresa["nome"], empresa["query"])
    
    with col:
        if noticia:
            # Limitar título a 60 caracteres
            titulo = noticia.title[:60] + "..." if len(noticia.title) > 60 else noticia.title
            link = noticia.link
            
            st.markdown(f"""
            <a href="{link}" target="_blank" style="text-decoration: none;">
                <div class="card {empresa['cor']}" style="cursor: pointer; min-height: 140px;">
                    <div class="card-title">{empresa['emoji']} {empresa["nome"]}</div>
                    <div class="card-subtitle" style="font-size: 0.95rem; line-height: 1.4;">{titulo}</div>
                    <div class="card-subtitle" style="margin-top: 8px; opacity: 0.7;">📰 Clique para ler</div>
                </div>
            </a>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="card {empresa['cor']}" style="min-height: 140px;">
                <div class="card-title">{empresa['emoji']} {empresa["nome"]}</div>
                <div class="card-subtitle">Sem notícias recentes</div>
            </div>
            """, unsafe_allow_html=True)

# 3. CLIMA
st.markdown('<div class="section-header">🌤️ Clima na Região</div>', unsafe_allow_html=True)
c1, c2 = st.columns(2)

w_quiri = get_weather(-18.4486, -50.4519)
w_coru = get_weather(-10.1264, -36.1756)

with c1:
    precip_txt = f" • 💧 {w_quiri['precipitacao']}mm" if w_quiri['precipitacao'] > 0 else ""
    st.markdown(f"""
    <div class="card bg-gradient-blue">
        <div class="card-title">📍 Quirinópolis - GO</div>
        <div class="card-value">{w_quiri['icon']} {w_quiri['temp']}°C</div>
        <div class="card-subtitle">{w_quiri['descricao']}{precip_txt}</div>
        <div class="card-subtitle">💨 {w_quiri['wind']} km/h • 💧 {w_quiri['humidity']}%</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    precip_txt = f" • 💧 {w_coru['precipitacao']}mm" if w_coru['precipitacao'] > 0 else ""
    st.markdown(f"""
    <div class="card bg-gradient-green">
        <div class="card-title">🌊 Coruripe - AL</div>
        <div class="card-value">{w_coru['icon']} {w_coru['temp']}°C</div>
        <div class="card-subtitle">{w_coru['descricao']}{precip_txt}</div>
        <div class="card-subtitle">💨 {w_coru['wind']} km/h • 💧 {w_coru['humidity']}%</div>
    </div>
    """, unsafe_allow_html=True)

# 4. AÇÕES FAVORITAS
st.markdown('<div class="section-header">📈 Ações em Destaque</div>', unsafe_allow_html=True)
stocks = {
    "PRIO3": "PRIO3.SA",
    "BBAS3": "BBAS3.SA",
    "MOVI3": "MOVI3.SA",
    "VAMO3": "VAMO3.SA",
    "AGRO3": "AGRO3.SA",
    "DÓLAR": "USDBRL=X"
}

cols_s = st.columns(3)
stocks_list = list(stocks.items())

for i in range(3):
    name, ticker = stocks_list[i]
    price, var = get_stock_data(ticker)
    symbol = "▲" if var >= 0 else "▼"
    badge_class = "stock-badge-positive" if var >= 0 else "stock-badge-negative"
    
    with cols_s[i]:
        prefix = "R$"
        st.markdown(f"""
        <div class="card bg-gradient-dark">
            <div class="card-title">{name} <span class="stock-badge {badge_class}">{symbol} {var:.1f}%</span></div>
            <div class="card-value">{prefix} {price:.2f}</div>
        </div>
        """, unsafe_allow_html=True)

cols_s2 = st.columns(3)
for i in range(3, 6):
    name, ticker = stocks_list[i]
    price, var = get_stock_data(ticker)
    symbol = "▲" if var >= 0 else "▼"
    badge_class = "stock-badge-positive" if var >= 0 else "stock-badge-negative"
    
    with cols_s2[i-3]:
        prefix = "R$"
        st.markdown(f"""
        <div class="card bg-gradient-dark">
            <div class="card-title">{name} <span class="stock-badge {badge_class}">{symbol} {var:.1f}%</span></div>
            <div class="card-value">{prefix} {price:.2f}</div>
        </div>
        """, unsafe_allow_html=True)

# 5. NOTÍCIAS
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

# 6. CARTEIRA CONSOLIDADA (no final)
st.markdown('<div class="section-header">💰 Minha Carteira</div>', unsafe_allow_html=True)

# Buscar dados
dolar = get_dolar()
var_br, patrim_br, lucro_br = calcular_variacao_carteira_br()
var_us, patrim_us, lucro_us = calcular_variacao_carteira_us()

# Converter US para BRL
var_us_brl = var_us * dolar
patrim_us_brl = patrim_us * dolar
lucro_us_brl = lucro_us * dolar

# Totais
var_total_brl = var_br + var_us_brl
patrim_total = patrim_br + patrim_us_brl
lucro_total = lucro_br + lucro_us_brl

# Cores baseadas no resultado
cor_var = "bg-gradient-green" if var_total_brl >= 0 else "bg-gradient-red"
cor_lucro = "bg-gradient-green" if lucro_total >= 0 else "bg-gradient-red"
symbol_var = "▲" if var_total_brl >= 0 else "▼"
symbol_lucro = "▲" if lucro_total >= 0 else "▼"

col_c1, col_c2, col_c3 = st.columns(3)

with col_c1:
    st.markdown(f"""
    <div class="card {cor_var}">
        <div class="card-title">📊 Variação Hoje</div>
        <div class="card-value">{symbol_var} R$ {abs(var_total_brl):,.2f}</div>
        <div class="card-subtitle">BR: R$ {var_br:+,.2f} | US: R$ {var_us_brl:+,.2f}</div>
    </div>
    """, unsafe_allow_html=True)

with col_c2:
    st.markdown(f"""
    <div class="card {cor_lucro}">
        <div class="card-title">💎 Lucro vs PM</div>
        <div class="card-value">{symbol_lucro} R$ {abs(lucro_total):,.2f}</div>
        <div class="card-subtitle">BR: R$ {lucro_br:+,.2f} | US: R$ {lucro_us_brl:+,.2f}</div>
    </div>
    """, unsafe_allow_html=True)

with col_c3:
    st.markdown(f"""
    <div class="card bg-gradient-gold">
        <div class="card-title">💵 Dólar</div>
        <div class="card-value">R$ {dolar:.4f}</div>
        <div class="card-subtitle">Cotação atual</div>
    </div>
    """, unsafe_allow_html=True)
