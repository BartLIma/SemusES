import pandas as pd
import streamlit as st
import unicodedata

st.set_page_config(layout="wide", page_title="Secretarias de Saúde - ES", page_icon="🔍")

# --- TRUQUE CSS ATUALIZADO: Tema Azul e Verde para Diferenciação ---
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

# --- BANCO DE DADOS GEOGRÁFICO MESTRE LOCAL DO ESPÍRITO SANTO ---
# Coordenadas calculadas diretamente e fixadas em memória para velocidade instantânea
coordenadas_es = {
    "afonso claudio": {"lat": -20.0747, "lon": -41.1353},
    "agua doce do norte": {"lat": -18.5478, "lon": -40.9786},
    "aguia branca": {"lat": -18.9839, "lon": -40.7403},
    "alegre": {"lat": -20.7631, "lon": -41.5381},
    "alfredo chaves": {"lat": -20.6353, "lon": -40.7511},
    "alto rio novo": {"lat": -19.0558, "lon": -41.0189},
    "anchieta": {"lat": -20.8039, "lon": -40.6472},
    "apiaca": {"lat": -21.1558, "lon": -41.5681},
    "aracruz": {"lat": -19.8194, "lon": -40.2742},
    "atilio vivacqua": {"lat": -20.9144, "lon": -41.2017},
    "baixo guandu": {"lat": -19.5186, "lon": -41.0119},
    "barra de sao francisco": {"lat": -18.7561, "lon": -40.8911},
    "boa esperanca": {"lat": -18.4908, "lon": -40.2958},
    "bom jesus do norte": {"lat": -21.1114, "lon": -41.6708},
    "brejetuba": {"lat": -20.1444, "lon": -41.2911},
    "cachoeiro de itapemirim": {"lat": -20.8489, "lon": -41.1128},
    "cariacica": {"lat": -20.2639, "lon": -40.4200},
    "castelo": {"lat": -20.6044, "lon": -41.1856},
    "colatina": {"lat": -19.5383, "lon": -40.6294},
    "conceicao da barra": {"lat": -18.5933, "lon": -39.7317},
    "conceicao do castelo": {"lat": -20.3694, "lon": -41.2439},
    "divino de sao lourenco": {"lat": -20.6211, "lon": -41.6853},
    "domingos martins": {"lat": -20.3633, "lon": -40.6592},
    "dores do rio preto": {"lat": -20.6908, "lon": -41.8453},
    "ecoporanga": {"lat": -18.3733, "lon": -40.8306},
    "fundao": {"lat": -19.9328, "lon": -40.4056},
    "governador lindenberg": {"lat": -19.2661, "lon": -40.4719},
    "guacui": {"lat": -20.7672, "lon": -41.6806},
    "guarapari": {"lat": -20.6606, "lon": -40.4975},
    "ibatiba": {"lat": -20.2339, "lon": -41.5111},
    "ibiracu": {"lat": -19.8317, "lon": -40.3703},
    "ibitirama": {"lat": -20.5414, "lon": -41.6664},
    "iconha": {"lat": -20.7933, "lon": -40.6558},
    "irupi": {"lat": -20.3414, "lon": -41.6394},
    "itaguacu": {"lat": -19.8019, "lon": -40.8544},
    "itapemirim": {"lat": -21.0111, "lon": -40.8339},
    "itarana": {"lat": -19.8744, "lon": -40.8711},
    "iuna": {"lat": -20.3458, "lon": -41.5356},
    "jaguare": {"lat": -18.9064, "lon": -40.0758},
    "jeronimo monteiro": {"lat": -20.7894, "lon": -41.3853},
    "joao neiva": {"lat": -19.7561, "lon": -40.3878},
    "laranja da terra": {"lat": -19.8994, "lon": -41.0558},
    "linhares": {"lat": -19.3911, "lon": -40.0719},
    "mantenopolis": {"lat": -18.8617, "lon": -41.1214},
    "marataizes": {"lat": -21.0433, "lon": -40.8244},
    "marechal floriano": {"lat": -20.4633, "lon": -40.6836},
    "marilandia": {"lat": -19.4128, "lon": -40.5414},
    "mimoso do sul": {"lat": -21.0639, "lon": -41.3658},
    "montanha": {"lat": -18.1264, "lon": -40.3633},
    "mucurici": {"lat": -18.0933, "lon": -40.5186},
    "muniz freire": {"lat": -20.4639, "lon": -41.4131},
    "muqui": {"lat": -20.9517, "lon": -41.3456},
    "nova venecia": {"lat": -18.7114, "lon": -40.4006},
    "pancas": {"lat": -19.2242, "lon": -40.8514},
    "pedro canario": {"lat": -18.2933, "lon": -40.1511},
    "pinheiros": {"lat": -18.3939, "lon": -40.2178},
    "piuma": {"lat": -20.8333, "lon": -40.7336},
    "ponto belo": {"lat": -18.1258, "lon": -40.5372},
    "presidente kennedy": {"lat": -21.0989, "lon": -41.0117},
    "rio bananal": {"lat": -19.2639, "lon": -40.3339},
    "rio novo do sul": {"lat": -20.8592, "lon": -40.9328},
    "santa leopoldina": {"lat": -20.1006, "lon": -40.5297},
    "santa maria de jetiba": {"lat": -20.0406, "lon": -40.7456},
    "santa teresa": {"lat": -19.9356, "lon": -40.6017},
    "sao domingos do norte": {"lat": -19.1311, "lon": -40.6214},
    "sao gabriel da palha": {"lat": -19.0167, "lon": -40.5342},
    "sao jose do calcado": {"lat": -21.0253, "lon": -41.5492},
    "sao mateus": {"lat": -18.7161, "lon": -39.8614},
    "sao roque do canaa": {"lat": -19.7389, "lon": -40.6558},
    "serra": {"lat": -20.1286, "lon": -40.3078},
    "sooretama": {"lat": -19.1975, "lon": -40.0911},
    "vargem alta": {"lat": -20.6711, "lon": -41.0067},
    "venda nova do imigrante": {"lat": -20.3414, "lon": -41.1342},
    "viana": {"lat": -20.3908, "lon": -40.4958},
    "vila pavao": {"lat": -18.6158, "lon": -40.6119},
    "vila valerio": {"lat": -18.9972, "lon": -40.3958},
    "vila velha": {"lat": -20.3297, "lon": -40.2925},
    "vitoria": {"lat": -20.3155, "lon": -40.3128}
}

def buscar_coordenadas_municipio(nome_municipio):
    """Varre a tabela estática local higienizando maiúsculas e acentos automaticamente"""
    if not nome_municipio:
        return -20.3155, -40.3128 # Vitória (Capital)
    texto = unicodedata.normalize('NFKD', str(nome_municipio)).encode('ascii', 'ignore').decode('utf-8')
    chave_limpa = texto.strip().lower().replace("-", " ").replace("  ", " ")
    if chave_limpa in coordenadas_es:
        return coordenadas_es[chave_limpa]["lat"], coordenadas_es[chave_limpa]["lon"]
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
        opcoes_completas = {"-- Selecione o registro --": -1}
        for idx, row in df.iterrows():
            muni = row["Municipio_Exibicao"]
            sec = f" ({row['Secretário']})" if pd.notna(row["Secretário"]) and row["Secretário"].strip() and row["Secretário"].lower() != 'nan' else ""
            opcoes_completas[f"{muni}{sec}"] = idx
        
        lista_ordenada = ["-- Selecione o registro --"] + sorted([k for k in opcoes_completas.keys() if k != "-- Selecione o registro --"])
        selecao = st.selectbox("Todos os municípios activos:", lista_ordenada)
        
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
            st.markdown("🗺️ **Geolocalização Estática Local**")
            
            # PUXA INSTANTANEAMENTE AS COORDENADAS DO BANCO FIXO DO BLOCO 1
            lat, lon = buscar_coordenadas_municipio(municipio_atual)
            df_mapa = pd.DataFrame({"lat": [lat], "lon": [lon]})
            
            st.map(df_mapa, size=60, color="#1E3A8A", zoom=11)

else:
    st.markdown("---")
    st.info("💡 **Aguardando seleção:** Digite ou clique em um município do Espírito Santo na barra lateral esquerda para renderizar a ficha de contatos e o mapa estático local.")

# --- RODAPÉ DISCRETO ---
st.markdown("---")
st.markdown("<p style='text-align:left; font-size:12px; color:#A3A3A3;'>Bartolomeu Lima - Corecon-ES 1541 - Fonte: Cosems-ES</p>", unsafe_allow_html=True)
