import streamlit as st
from datetime import datetime, date
import json
import os

# Configuração da página do site
st.set_page_config(page_title="Controle de Validade - Cozinha", page_icon="🍳", layout="wide")

# Título principal do Site
st.title("🍳 Sistema de Controle da Cozinha")
st.write("Sistema permanente ativo. Aguardando comandos do cozinheiro **Victor**.")

ARQUIVO_BANCO = "estoque.json"

# FUNÇÃO PARA CARREGAR OS DADOS SALVOS NO ARQUIVO
def carregar_dados():
    if os.path.exists(ARQUIVO_BANCO):
        try:
            with open(ARQUIVO_BANCO, "r", encoding="utf-8") as f:
                dados = json.load(f)
                # Converte as datas de texto para o formato correto do Python
                for item in dados:
                    item["validade"] = datetime.strptime(item["validade"], "%Y-%m-%d").date()
                return dados
        except:
            return []
    return []

# FUNÇÃO PARA SALVAR OS DADOS NO ARQUIVO PARA SEMPRE
def salvar_dados(dados):
    dados_para_salvar = []
    for item in dados:
        dados_para_salvar.append({
            "nome": item["nome"],
            "local": item["local"],
            "validade": item["validade"].strftime("%Y-%m-%d")
        })
    with open(ARQUIVO_BANCO, "w", encoding="utf-8") as f:
        json.dump(dados_para_salvar, f, ensure_ascii=False, indent=4)

# Inicializa o banco de dados carregando o arquivo salvo
if "produtos" not in st.session_state:
    st.session_state.produtos = carregar_dados()

# Divisão da tela em duas colunas
col1, col2 = st.columns([1, 2])

# COLUNA 1: Formulário para o Victor digitar os produtos
with col1:
    st.header("📥 Cadastrar Novo Produto")
    
    nome = st.text_input("Nome do Alimento / Bebida:", placeholder="Ex: Queijo, Leite, Carne...")
    
    # Seus eletrodomésticos exatos da cozinha
    local = st.selectbox("Onde este produto será guardado?", [
        "Geladeira Principal (1)", 
        "Freezer Branco", 
        "Freezer Red Bull", 
        "Freezer Grande"
    ])
    
    data_val = st.date_input("Data de Validade do Produto:", min_value=date.today())
    
    # Botão para salvar
    if st.button("Adicionar ao Estoque"):
        if nome:
            # Adiciona na lista da memória
            st.session_state.produtos.append({
                "nome": nome.strip(), 
                "local": local, 
                "validade": data_val
            })
            # Grava direto no arquivo permanente
            salvar_dados(st.session_state.produtos)
            st.success("🟢 {0} adicionado e salvo com sucesso!".format(nome))
            st.rerun()
        else:
            st.error("⚠️ Por favor, digite o nome do produto antes de adicionar.")

# COLUNA 2: O painel de Alarmes Automáticos
with col2:
    st.header("🚨 Alarmes e Estoque Atual")
    
    # Se não tiver nada cadastrado, mostra que o estoque está zerado
    if len(st.session_state.produtos) == 0:
        st.info("O estoque está completamente vazio. Victor pode começar a enviar os produtos!")
    else:
        # Botão para limpar tudo e zerar o arquivo se quiser começar de novo
        if st.button("🗑️ Limpar Todo o Estoque"):
            st.session_state.produtos = []
            salvar_dados([])
            st.rerun()
            
        st.write("---")
        
        # Lista os produtos e calcula o alarme automático de dias restantes
        for item in st.session_state.produtos:
            hoje = date.today()
            dias_restantes = (item["validade"] - hoje).days
            
            # Lógica Inteligente do Alarme Automático
            if dias_restantes < 0:
                status_texto = "❌ VENCIDO HÁ {0} DIAS!".format(abs(dias_restantes))
                cor_alarme = "#ef4444"
                cor_fundo = "#fee2e2"
            elif dias_restantes <= 3:
                status_texto = "🚨 CRÍTICO! Vence em {0} dias.".format(dias_restantes)
                cor_alarme = "#dc2626"
                cor_fundo = "#fee2e2"
            elif dias_restantes <= 7:
                status_texto = "⚠️ ATENÇÃO! Vence em {0} dias.".format(dias_restantes)
                cor_alarme = "#d97706"
                cor_fundo = "#fef3c7"
            else:
                status_texto = "✅ Seguro ({0} dias restantes)".format(dias_restantes)
                cor_alarme = "#16a34a"
                cor_fundo = "#dcfce7"
            
            # Estrutura visual idêntica e sem bugs de chaves
            html_card = """
            <div style="padding: 12px; border-radius: 8px; border-left: 6px solid {0}; background-color: {1}; margin-bottom: 12px; color: #1e293b;">
                <span style="font-size: 12pt; font-weight: bold;">{2}</span> <br>
                <span style="font-size: 10pt;">📍 Local: <b>{3}</b> | Validade: {4}</span><br>
                <span style="font-size: 10.5pt; font-weight: bold; color: {0};">{5}</span>
            </div>
            """.format(cor_alarme, cor_fundo, item['nome'], item['local'], item['validade'].strftime('%d/%m/%Y'), status_texto)
            
            st.markdown(html_card, unsafe_allow_code=True)
