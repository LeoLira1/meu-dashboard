import streamlit as st

# Exemplo de card com imagem de fundo

st.markdown("""
<style>
    .card-com-imagem {
        border-radius: 16px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.2s;
        
        /* Imagem de fundo */
        background-image: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.6)), 
                          url('https://images.unsplash.com/photo-1447933601403-0c6688de566e?w=800');
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        
        /* Efeito de sombra no texto para melhorar legibilidade */
        text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
    }
    
    .card-com-imagem:hover {
        transform: translateY(-2px);
    }
    
    .card-title { 
        font-size: 0.9rem; 
        opacity: 0.9; 
        margin-bottom: 0.5rem; 
    }
    
    .card-value { 
        font-size: 1.8rem; 
        font-weight: 700; 
        margin-bottom: 0.2rem; 
    }
    
    .card-subtitle { 
        font-size: 0.8rem; 
        opacity: 0.9; 
        font-weight: 500; 
    }
    
    .stock-badge {
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 0.8rem;
        margin-left: 10px;
        font-weight: 600;
        background: #00C853;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Card com imagem de café
st.markdown("""
<div class="card-com-imagem">
    <div class="card-title">☕ CAFÉ <span class="stock-badge">▲ 1.2%</span></div>
    <div class="card-value">$345.80</div>
    <div class="card-subtitle">USD (ETN)</div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.markdown("### 📝 Explicação:")
st.markdown("""
**Como funciona:**

1. **`background-image`**: Define a imagem de fundo
   - Usa `linear-gradient` para criar uma camada escura sobre a imagem (melhor legibilidade)
   - Depois coloca a URL da imagem

2. **`background-size: cover`**: Faz a imagem cobrir todo o card

3. **`background-position: center`**: Centraliza a imagem

4. **`text-shadow`**: Adiciona sombra no texto para destacar sobre a imagem

**Fontes de imagens gratuitas:**
- Unsplash: https://unsplash.com/
- Pexels: https://www.pexels.com/
- Pixabay: https://pixabay.com/

**Dica:** O `linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.6))` 
cria um filtro escuro sobre a imagem. Ajuste os valores (0.4 e 0.6) 
para controlar a escuridão:
- 0.0 = completamente transparente
- 1.0 = completamente preto
""")
