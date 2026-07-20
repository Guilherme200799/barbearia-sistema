import streamlit as st
from datetime import datetime, timedelta, time as dt_time
import json
import os
import urllib.parse
import time

# Configuração da página - Tema escuro/moderno por CSS personalizado
st.set_page_config(page_title="Barbearia Preto & Branco", page_icon="💈", layout="centered")

ARQUIVO_BANCO = "agendamentos_barbearia.json"

PRECOS_SERVICOS = {
    "Cabelo": 30.0,
    "Barba": 25.0,
    "Combo (Cabelo + Barba)": 55.0,
    "Sobrancelha": 10.0
}

def carregar_agendamentos():
    if not os.path.exists(ARQUIVO_BANCO):
        return []
    try:
        with open(ARQUIVO_BANCO, "r", encoding="utf-8") as f:
            dados = json.load(f)
            for ag in dados:
                ag["data_hora"] = datetime.strptime(ag["data_hora"], "%Y-%m-%d %H:%M:%S")
            return dados
    except:
        return []

def salvar_agendamentos(dados):
    dados_para_salvar = []
    for ag in dados:
        dados_para_salvar.append({
            "cliente": ag["cliente"],
            "servico": ag["servico"],
            "profissional": ag["profissional"],
            "data_hora": ag["data_hora"].strftime("%Y-%m-%d %H:%M:%S")
        })
    with open(ARQUIVO_BANCO, "w", encoding="utf-8") as f:
        json.dump(dados_para_salvar, f, ensure_ascii=False, indent=4)

# UI DESIGN PREMIUM CUSTOMIZADO (CSS)
st.markdown("""
    <style>
    /* Importando fonte moderna */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background-color: #0e1117;
    }
    
    /* Customização do Título Principal */
    .main-title {
        text-align: center;
        font-size: 2.5rem;
        font-weight: 700;
        color: #ffffff;
        letter-spacing: -1px;
        margin-bottom: 5px;
    }
    .main-subtitle {
        text-align: center;
        font-size: 1.1rem;
        color: #8a99ad;
        margin-bottom: 30px;
    }
    
    /* Abas Customizadas estilo Dark/Gold */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #161b22;
        padding: 6px;
        border-radius: 12px;
        border-bottom: none;
    }
    .stTabs [data-baseweb="tab"] {
        color: #8a99ad !important;
        background-color: transparent;
        border-radius: 8px;
        padding: 10px 16px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #ffffff !important;
        background-color: #21262d;
    }
    .stTabs [aria-selected="true"] {
        color: #000000 !important;
        background-color: #ffffff !important;
        box-shadow: 0 4px 12px rgba(255,255,255,0.1);
    }
    
    /* Box do Formulário de Agendamento */
    .form-container {
        background-color: #161b22;
        border: 1px solid #30363d;
        padding: 30px;
        border-radius: 16px;
        margin-top: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    /* Botão Principal Estilo Ouro Macio / Premium */
    button[data-testid="baseButton-primary"] {
        background-color: #ffffff !important;
        color: #000000 !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 10px !important;
        height: 50px !important;
        font-size: 16px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(255,255,255,0.1) !important;
    }
    button[data-testid="baseButton-primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255,255,255,0.2) !important;
        background-color: #f0f0f0 !important;
    }
    
    /* Cartões de Agendamento Ativo */
    .client-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        padding: 20px;
        border-radius: 14px;
        margin-bottom: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        transition: transform 0.2s;
    }
    .client-card:hover {
        transform: translateX(4px);
        border-color: #8a99ad;
    }
    .whatsapp-btn {
        background-color: #25D366;
        color: white !important;
        padding: 10px 18px;
        border-radius: 8px;
        font-weight: 600;
        text-decoration: none;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        font-size: 14px;
    }
    
    /* Painel Admin Cards */
    .metric-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        padding: 20px;
        border-radius: 14px;
        text-align: center;
    }
    
    /* Inputs inputs */
    div[data-testid="stTextInput"] input, div[data-testid="stSelectbox"] div {
        background-color: #21262d !important;
        color: white !important;
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
    }
    
    label {
        color: #c9d1d9 !important;
        font-weight: 500 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Cabeçalho Limpo e Profissional
st.markdown('<div class="main-title">💈 BARBEARIA PRETO & BRANCO</div>', unsafe_allow_html=True)
st.markdown('<div class="main-subtitle">Agendamento Online & Gestão Integrada</div>', unsafe_allow_html=True)

aba1, aba2, aba3, aba4 = st.tabs(["📅 Novo Agendamento", "📋 Horários Marcados", "❌ Cancelar Horário", "📊 Painel Administrativo"])

# --- ABA 1: NOVO AGENDAMENTO ---
with aba1:
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    st.subheader("Preencha os dados abaixo")
    
    lista_agendamentos = carregar_agendamentos()
    
    cliente = st.text_input("Nome completo do cliente:", key="input_cliente", placeholder="Ex: João Silva").strip()
    
    # Grid de duas colunas para o formulário ficar mais compacto e elegante
    col_form1, col_form2 = st.columns(2)
    with col_form1:
        servico = st.selectbox("Escolha o Serviço:", list(PRECOS_SERVICOS.keys()), key="select_servico")
    with col_form2:
        profissional = st.radio("Selecione o Profissional:", ["Bruno", "Samuel"], horizontal=True, key="radio_prof")
    
    hoje_dt = datetime.utcnow() - timedelta(hours=3)
    dias_semana_pt = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
    
    opcoes_datas = []
    for i in range(30):
        futuro = hoje_dt + timedelta(days=i)
        if futuro.weekday() != 6:
            texto_data = f"{futuro.strftime('%d/%m/%Y')} ({dias_semana_pt[futuro.weekday()]})"
            opcoes_datas.append((futuro.date(), texto_data))
    
    col_data, col_hora = st.columns(2)
    with col_data:
        data_selecionada = st.selectbox("Escolha a Data:", opcoes_datas, format_func=lambda x: x[1], key="select_data")
        data_atendimento = data_selecionada[0]
    
    dia_semana_selecionado = data_atendimento.weekday()
    horarios_todos = []
    minutos_inicio = 480
    minutos_fim = 1020 if dia_semana_selecionado == 5 else 1080
    
    minutos_atual = minutos_inicio
    while minutos_atual <= minutos_fim:
        h_print = minutos_atual // 60
        m_print = minutos_atual % 60
        horarios_todos.append(dt_time(h_print, m_print))
        minutos_atual += 40
    
    horarios_disponiveis = []
    for h in horarios_todos:
        dt_verificar = datetime.combine(data_atendimento, h)
        if data_atendimento == hoje_dt.date() and h < hoje_dt.time():
            continue
        ocupado = any(ag["profissional"] == profissional and ag["data_hora"] == dt_verificar for ag in lista_agendamentos)
        if not ocupado:
            horarios_disponiveis.append(h)
    
    with col_hora:
        if horarios_disponiveis:
            hora_atendimento = st.selectbox("Horários Livres:", horarios_disponiveis, format_func=lambda x: x.strftime("%H:%M"), key="select_hora")
            st.write("") # Espaçador
            botao_agendar = st.button("Confirmar Agendamento", use_container_width=True, type="primary")
        else:
            st.error("⚠️ Sem horários livres!")
            botao_agendar = False

    if botao_agendar:
        if not cliente:
            st.error("Por favor, informe o nome.")
        else:
            dt_completo = datetime.combine(data_atendimento, hora_atendimento)
            lista_agendamentos = carregar_agendamentos()
            conflito = any(ag["profissional"] == profissional and ag["data_hora"] == dt_completo for ag in lista_agendamentos)
            
            if not conflito:
                lista_agendamentos.append({
                    "cliente": cliente,
                    "servico": servico,
                    "profissional": profissional,
                    "data_hora": dt_completo
                })
                lista_agendamentos.sort(key=lambda x: x["data_hora"])
                salvar_agendamentos(lista_agendamentos)
                st.success(f"🎉 Horário reservado para {cliente}!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Conflito de última hora detectado.")
    st.markdown('</div>', unsafe_allow_html=True)

# --- ABA 2: VISUALIZAR AGENDA ---
with aba2:
    lista_agendamentos = carregar_agendamentos()
    if not lista_agendamentos:
        st.info("Nenhum cliente agendado.")
    else:
        sub_bruno, sub_samuel, sub_geral = st.tabs(["🧔 Agenda do Bruno", "👨 Agenda do Samuel", "📋 Ver Geral"])
        
        def renderizar_lista(lista_filtrada):
            if not lista_filtrada:
                st.markdown("<p style='color:#8a99ad;'>Sem horários marcados.</p>", unsafe_allow_html=True)
                return
            for ag in lista_filtrada:
                data_str = ag["data_hora"].strftime("%d/%m/%Y")
                hora_str = ag["data_hora"].strftime("%H:%M")
                msg_encodada = urllib.parse.quote(f"Olá, {ag['cliente']}! Seu horário para {ag['servico']} está confirmado para o dia {data_str} às {hora_str} com o profissional {ag['profissional']}. 💈")
                
                card_html = f"""
                <div class="client-card">
                    <div>
                        <span style="font-size: 17px; font-weight: 600; color: #ffffff;">{ag['cliente']}</span>
                        <span style="font-size: 14px; color: #8a99ad;"> • {ag['servico']}</span>
                        <div style="font-size: 13px; color: #c9d1d9; margin-top: 5px;">
                            📅 {data_str} às <b>{hora_str}</b> | Barbeiro: {ag['profissional']}
                        </div>
                    </div>
                    <div>
                        <a href="https://wa.me/?text={msg_encodada}" target="_blank" class="whatsapp-btn">Avisar</a>
                    </div>
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)

        with sub_bruno: renderizar_lista([ag for ag in lista_agendamentos if ag["profissional"] == "Bruno"])
        with sub_samuel: renderizar_lista([ag for ag in lista_agendamentos if ag["profissional"] == "Samuel"])
        with sub_geral: renderizar_lista(lista_agendamentos)

# --- ABA 3: CANCELAR HORÁRIO ---
with aba3:
    lista_agendamentos = carregar_agendamentos()
    if not lista_agendamentos:
        st.info("Sem agendamentos para cancelar.")
    else:
        canc_bruno, canc_samuel, canc_geral = st.tabs(["🧔 Cancelar Bruno", "👨 Cancelar Samuel", "📋 Ver Todos"])
        
        def renderizar_lista_cancelamento(lista_filtrada, sufixo):
            if not lista_filtrada:
                st.info("Nenhum agendamento encontrado.")
                return
            for ag in lista_filtrada:
                data_str = ag["data_hora"].strftime("%d/%m/%Y")
                hora_str = ag["data_hora"].strftime("%H:%M")
                indice_real = next((i for i, item in enumerate(lista_agendamentos) if item["cliente"] == ag["cliente"] and item["data_hora"] == ag["data_hora"]), None)
                
                if indice_real is None: continue
                
                col_info, col_btn = st.columns([3, 1])
                with col_info:
                    st.markdown(f"""
                    <div style="padding: 10px 0;">
                        <span style="font-size: 15px; font-weight: 600; color: #ff6b6b;">{ag['cliente']}</span><br>
                        <span style="font-size: 13px; color: #8a99ad;">📅 {data_str} às {hora_str} | {ag['servico']}</span>
                    </div>
                    """, unsafe_allow_html=True)
                with col_btn:
                    if st.button("🗑️ Remover", key=f"del_{sufixo}_{indice_real}", use_container_width=True):
                        lista_agendamentos.pop(indice_real)
                        salvar_agendamentos(lista_agendamentos)
                        st.success("Cancelado!")
                        time.sleep(0.6)
                        st.rerun()
                st.divider()

        with canc_bruno: renderizar_lista_cancelamento([ag for ag in lista_agendamentos if ag["profissional"] == "Bruno"], "bruno")
        with canc_samuel: renderizar_lista_cancelamento([ag for ag in lista_agendamentos if ag["profissional"] == "Samuel"], "samuel")
        with canc_geral: renderizar_lista_cancelamento(lista_agendamentos, "geral")

# --- ABA 4: PAINEL ADMINISTRATIVO ---
with aba4:
    senha = st.text_input("Senha administrativa:", type="password", key="input_senha")
    if senha == "admin123":
        lista_agendamentos = carregar_agendamentos()
        if not lista_agendamentos:
            st.info("Sem dados suficientes.")
        else:
            filtro_tempo = st.selectbox("Período:", ["Todo o Período", "Este Mês", "Esta Semana"])
            hoje = (datetime.utcnow() - timedelta(hours=3)).date()
            
            agendamentos_filtrados = []
            for ag in lista_agendamentos:
                data_ag = ag["data_hora"].date()
                if filtro_tempo == "Este Mês" and (data_ag.year != hoje.year or data_ag.month != hoje.month): continue
                if filtro_tempo == "Esta Semana" and not (hoje - timedelta(days=hoje.weekday()) <= data_ag <= hoje - timedelta(days=hoje.weekday()) + timedelta(days=6)): continue
                agendamentos_filtrados.append(ag)
            
            if agendamentos_filtrados:
                total = len(agendamentos_filtrados)
                faturamento = sum(PRECOS_SERVICOS.get(ag["servico"], 0) for ag in agendamentos_filtrados)
                
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    st.markdown(f'<div class="metric-card"><span style="color:#8a99ad;font-size:13px;">Faturamento</span><br><span style="font-size:24px;font-weight:700;color:#25D366;">R$ {faturamento:,.2f}</span></div>', unsafe_allow_html=True)
                with col_m2:
                    st.markdown(f'<div class="metric-card"><span style="color:#8a99ad;font-size:13px;">Atendimentos</span><br><span style="font-size:24px;font-weight:700;color:#ffffff;">{total}</span></div>', unsafe_allow_html=True)
