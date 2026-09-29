import pandas as pd
import streamlit as st
import requests
import os
import unicodedata
import urllib.parse

st.set_page_config(layout="wide", page_title="Secretarias de Saúde - ES", page_icon="🔍")

# --- TRUQUE CSS ATUALIZADO: Tema Azul e Verde de Saúde ---
st.markdown(
    """
    <style>
        .block-container { padding-top: 2rem !important; padding-bottom: 2rem !important; }
        div[data-testid="stVerticalBlock"] > div { border-radius: 0px; }
        h2 { color: #1E3A8A; font-weight: 600 !important; }
        h3 { color: #28a745; font-weight: 600 !important; }
        .stMarkdown p { margin-bottom: 0.5rem !important; }
    </style>
    """,
    unsafe_allow_html=True
)

if "indice_secretario_consultado" not in st.session_state:
    st.session_state["indice_secretario_consultado"] = None

# --- FUNÇÃO EXECUTORA DE BUSCA 100% DINÂMICA PELO NOME (CORRIGIDA) ---
@st.cache_data(show_spinner=False)
def buscar_coordenadas_municipio(nome_municipio):
    """Consulta a API pública do OpenStreetMap em tempo real usando o nome próprio da cidade"""
    if not nome_municipio or pd.isna(nome_municipio):
        return -20.3155, -40.3128  # Coordenada neutra de Vitória (Capital) como segurança
        
    try:
        # A MUDANÇA CRUCIAL: Converte de CAIXA ALTA para Nome Próprio e limpa espaços
        muni_limpo = str(nome_municipio).strip().title()
        
        # Estrutura o termo de busca perfeitamente aceito pela API global
        termo_completo = f"{muni_limpo}, Espirito Santo, Brazil"
        cidade_enc = urllib.parse.quote(termo_completo)
        url = f"https://openstreetmap.org{cidade_enc}&format=jsonv2&limit=1"
        
        headers = {"User-Agent": "HubSecretariosES/2.0 (bartolomeulima.corecon@gmail.com)"}
        resposta = requests.get(url, headers=headers, timeout=8)
        dados = resposta.json()
        
        if dados and len(dados) > 0:
            return float(dados[0]["lat"]), float(dados[0]["lon"])
    except Exception:
        pass
        
    return -20.3155, -40.3128

# --- CARREGAMENTO SEGURO DOS DADOS CAPÌXABAS ---
encodings_para_testar = ["utf-8-sig", "ISO-8859-1", "cp1252"]
df = None

# Tenta ler o arquivo considerando o padrão de ponto e vírgula (;) enviado no seu exemplo
for enc in encodings_para_testar:
    try:
        df = pd.read_csv("secretarios_cosems_es.csv", sep=";", encoding=enc, dtype=str, skip_blank_lines=True)
        break
    except Exception:
        continue

# Se falhar com ponto e vírgula, tenta ler com vírgula (,) por contingência
if df is None:
    for enc in encodings_para_testar:
        try:
            df = pd.read_csv("secretarios_cosems_es.csv", sep=",", encoding=enc, dtype=str, skip_blank_lines=True)
            break
        except Exception:
            continue

if df is None:
    st.error("❌ Não foi possível localizar ou ler o arquivo 'secretarios_cosems_es.csv'.")
    st.stop()
    
df = df.dropna(how="all")

def normalizar_texto(texto):
    if not isinstance(texto, str):
        return ""
    texto = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode('utf-8')
    return texto.strip().lower().replace("-", "").replace(" ", "").replace("_", "")

# --- MAPEAMENTO AUTOMÁTICO DE COLUNAS ---
mapeamento_colunas = {}
for col in df.columns:
    col_limpa = normalizar_texto(col)
    if "municip" in col_limpa: mapeamento_colunas[col] = "Município"
    elif "secretar" in col_limpa or "nome" in col_limpa: mapeamento_colunas[col] = "Secretário"
    elif "emailinstitucional" in col_limpa: mapeamento_colunas[col] = "Email Institucional"
    elif "email" in col_limpa: mapeamento_colunas[col] = "Email"
    elif "telefoneinstitucional" in col_limpa: mapeamento_colunas[col] = "Telefone Institucional"
    elif "telefon" in col_limpa: mapeamento_colunas[col] = "Telefone"
    elif "enderec" in col_limpa or "logradour" in col_limpa: mapeamento_colunas[col] = "Endereço da SEMUS"
    elif "fundodesaud" in col_limpa: mapeamento_colunas[col] = "Fundo de Saúde"
    elif "cnpj" in col_limpa: mapeamento_colunas[col] = "CNPJ"
    elif "regiaodesaud" in col_limpa: mapeamento_colunas[col] = "Região de Saúde"

df = df.rename(columns=mapeamento_colunas)

lista_colunas_secretarios = ["Município", "Secretário", "Email", "Email Institucional", "Telefone", "Telefone Institucional", "Endereço da SEMUS", "Fundo de Saúde", "CNPJ", "Região de Saúde"]
for col_nome in lista_colunas_secretarios:
    if col_nome not in df.columns:
        df[col_nome] = ""

df["Municipio_Exibicao"] = df["Município"].astype(str).str.strip()
df["Secretário"] = df["Secretário"].astype(str).str.strip()

# --- PAINEL LATERAL DE BUSCA (78 MUNICÍPIOS) ---
with st.sidebar:
    st.header("🔍 Painel de Busca — ES")
    st.write("Selecione ou digite:")
    
    busca_termo = st.text_input("Digite o Município ou Gestor:", value="")
    
    if busca_termo.strip():
        termo = busca_termo.lower().strip()
        filtro = df["Municipio_Exibicao"].str.lower().str.contains(termo) | df["Secretário"].str.lower().str.contains(termo)
        registros_encontrados = df[filtro]
        
        if not registros_encontrados.empty:
            opcoes_secretarios = {}
            for idx, row in registros_encontrados.iterrows():
                muni = row["Municipio_Exibicao"]
                sec = f" ({row['Secretário']})" if pd.notna(row["Secretário"]) and row["Secretário"].strip() and row["Secretário"].lower() != 'nan' else ""
                opcoes_secretarios[f"{muni}{sec}"] = idx
            
            lista_ordenada = ["-- Selecione o registro --"] + sorted(list(opcoes_secretarios.keys()))
            selecao = st.selectbox("Registros localizados:", lista_ordenada)
            
            if selecao and selecao != "-- Selecione o registro --":
                st.session_state["indice_secretario_consultado"] = opcoes_secretarios[selecao]
            else:
                st.session_state["indice_secretario_consultado"] = None
        else:
            st.session_state["indice_secretario_consultado"] = None
            st.sidebar.warning("Nenhum município localizado.")
    else:
        # Se a caixa de texto estiver vazia, exibe a lista completa de cidades em ordem alfabética
        opcoes_completas = {"-- Selecione o registro --": -1}
        for idx, row in df.iterrows():
            muni = row["Municipio_Exibicao"]
            sec = f" ({row['Secretário']})" if pd.notna(row["Secretário"]) and row["Secretário"].strip() and row["Secretário"].lower() != 'nan' else ""
            opcoes_completas[f"{muni}{sec}"] = idx
        
        lista_ordenada = ["-- Selecione o registro --"] + sorted([k for k in opcoes_completas.keys() if k != "-- Selecione o registro --"])
        selecao = st.selectbox("Todos os municípios ativos:", lista_ordenada)
        
        if selecao and selecao != "-- Selecione o registro --":
            st.session_state["indice_secretario_consultado"] = opcoes_completas[selecao]
        else:
            st.session_state["indice_secretario_consultado"] = None

# --- ÁREA PRINCIPAL ---
st.title("🏛️ COSEMS/ES — Painel de Consulta Institucional")

if st.session_state["indice_secretario_consultado"] is not None and st.session_state["indice_secretario_consultado"] in df.index:
    s_idx = st.session_state["indice_secretario_consultado"]
    
    municipio_atual = df.loc[s_idx, 'Municipio_Exibicao']
    secretario_atual = df.loc[s_idx, 'Secretário']
    regiao_atual = df.loc[s_idx, 'Região de Saúde']
    
    def obter_valor_valido(campo):
        val = df.loc[s_idx, campo]
        if pd.isna(val) or str(val).lower() == 'nan' or str(val).strip() == "":
            return "Não informado"
        return str(val).strip()

    txt_em = obter_valor_valido("Email")
    txt_emi = obter_valor_valido("Email Institucional")
    txt_tl = obter_valor_valido("Telefone")
    txt_tli = obter_valor_valido("Telefone Institucional")
    txt_end = obter_valor_valido("Endereço da SEMUS")
    txt_fund = obter_valor_valido("Fundo de Saúde")
    txt_cnpj = obter_valor_valido("CNPJ")

    texto_exportacao = f"""### 📍 FICHA INSTITUCIONAL — {municipio_atual.upper()} (ES)
    
👤 **Secretário(a):** {secretario_atual}
🗺️ **Região de Saúde:** {regiao_atual}
📧 **E-mail Geral:** {txt_em}
🏢 **E-mail Institucional:** {txt_emi}
📱 **Telefone Geral:** {txt_tl}
☎️ **Telefone Institucional:** {txt_tli}
🏢 **Endereço da SEMUS:** {txt_end}
🏥 **Fundo de Saúde:** {txt_fund}
📋 **CNPJ:** {txt_cnpj}
"""

    col_ficha, col_mapa = st.columns([1.2, 0.8], gap="large")
    
    with col_ficha:
        with st.container(border=True):
            st.subheader(f"📍 Ficha Institucional — {municipio_atual}")
            st.markdown("---")
            
            f_col1, f_col2 = st.columns(2)
            with f_col1:
                st.markdown(f"👤 **Secretário(a) de Saúde:**<br><span style='font-size: 18px; color: #1E3A8A; font-weight: bold;'>{secretario_atual}</span>", unsafe_allow_html=True)
                st.write("") 
                st.write(f"📧 **E-mail Pessoal/Geral:** {txt_em}")
                st.write(f"🏢 **E-mail Institucional:** {txt_emi}")
                
            with f_col2:
                st.markdown(f"🗺️ **Região de Saúde:**<br><span style='font-size: 18px; color: #28a745; font-weight: bold;'>{regiao_atual}</span>", unsafe_allow_html=True)
                st.write("") 
                st.write(f"📱 **Telefone Geral:** {txt_tl}")
                st.write(f"☎️ **Telefone Institucional:** {txt_tli}")
            
            st.markdown("---")
            st.info(f"🏢 **Endereço da SEMUS:** {txt_end}")
            st.warning(f"🏥 **Fundo de Saúde:** {txt_fund}  |  📋 **CNPJ:** {txt_cnpj}")

    with col_mapa:
        with st.container(border=True):
            st.subheader("🛠️ Ferramentas e Mapa")
            st.markdown("---")
            
            c1, c2 = st.columns(2)
            with c1:
                st.download_button(
                    label="📥 Baixar Ficha (TXT)",
                    data=texto_exportacao,
                    file_name=f"ficha_es_{municipio_atual.lower().replace(' ', '_')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            with c2:
                with st.popover("📋 Copiar Ficha", use_container_width=True):
                    st.code(texto_exportacao, language="markdown")
            
            st.markdown(" ")
            st.markdown("🗺️ **Geolocalização Automática por Município**")
            
            # CHAMA A FUNÇÃO DE BUSCA EM TEMPO REAL CONFIANDO NO ISOLAMENTO DO APP
            lat, lon = buscar_coordenadas_municipio(municipio_atual)
            df_mapa = pd.DataFrame({"lat": [lat], "lon": [lon]})
            
            st.map(df_mapa, size=60, color="#1E3A8A", zoom=11)

else:
    st.markdown("---")
    st.info("💡 **Aguardando seleção:** Digite ou clique em um município do Espírito Santo na barra lateral esquerda para renderizar a ficha de contatos e o mapa em tempo real.")

# --- RODAPÉ DISCRETO ---
st.markdown("---")
st.markdown("<p style='text-align:right; font-size:12px; color:#A3A3A3;'>Bartolomeu Lima - Corecon-ES 1541</p>", unsafe_allow_html=True)
