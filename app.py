import streamlit as st
from datetime import datetime, timedelta, time as dt_time
import json
import os
import urllib.parse
import time

# Configuração da página
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

# CSS DINÂMICO - ADAPTA AUTOMATICAMENTE ENTRE LIGHT E DARK MODE
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Títulos dinâmicos com base no tema do sistema */
    .main-title {
        text-align: center;
        font-size: 2.2rem;
        font-weight: 700;
        color: var(--text-color) !important;
        letter-spacing: -0.5px;
        margin-bottom: 2px;
        padding-top: 10px;
    }
    .main-subtitle {
        text-align: center;
        font-size: 1rem;
        color: var(--text-color) !important;
        opacity: 0.8;
        margin-bottom: 25px;
        font-weight: 500;
    }
    
    /* Container do Formulário acompanhando o fundo do tema */
    .form-container {
        background-color: var(--secondary-background-color) !important;
        border: 1px solid rgba(128, 128, 128, 0.2) !important;
        padding: 25px;
        border-radius: 12px;
        margin-top: 15px;
    }
    
    /* CORREÇÃO DAS ABAS (TABS) PARA EVITAR BLOCOS PRETOS INVISÍVEIS */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background-color: var(--secondary-background-color) !important;
        padding: 6px;
        border-radius: 10px;
        border-bottom: none !important;
    }
    .stTabs [data-baseweb="tab"] {
        color: var(--text-color) !important;
        opacity: 0.7;
        background-color: transparent !important;
        border-radius: 6px;
        padding: 8px 14px;
        font-weight: 700 !important;
    }
    /* Aba ativa herda o contraste correto do tema atual */
    .stTabs [aria-selected="true"] {
        opacity: 1 !important;
        background-color: var(--background-color) !important;
        box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.1) !important;
        border-radius: 6px !important;
    }
    
    /* Inputs de texto e seletores */
    div[data-testid="stTextInput"] input, div[data-testid="stSelectbox"] div {
        color: var(--text-color) !important;
        background-color: var(--background-color) !important;
    }
    
    /* Botão Principal de Confirmação (Estilo Invertido/Contraste) */
    button[data-testid="baseButton-primary"] {
        background-color: var(--text-color) !important;
        color: var(--background-color) !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 8px !important;
        height: 50px !important;
        font-size: 16px !important;
    }
    
    /* Cards da Listagem de Clientes */
    .client-card {
        background-color: var(--secondary-background-color) !important;
        border: 1px solid rgba(128, 128, 128, 0.2) !important;
        padding: 16px;
        border-radius: 10px;
        margin-bottom: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .whatsapp-btn {
        background-color: #23a55a !important;
        color: #ffffff !important;
        padding: 8px 16px;
        border-radius: 6px;
        font-weight: 700;
        text-decoration: none;
        font-size: 14px;
    }
    
    /* Cards do Painel Admin */
    .metric-card {
        background-color: var(--secondary-background-color) !important;
        border: 1px solid rgba(128, 128, 128, 0.2) !important;
        padding: 18px;
        border-radius: 10px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# Cabeçalho
st.markdown('<div class="main-title">💈 BARBEARIA PRETO & BRANCO</div>', unsafe_allow_html=True)
st.markdown('<div class="main-subtitle">Agendamento Online & Gestão Integrada</div>', unsafe_allow_html=True)

aba1, aba2, aba3, aba4 = st.tabs(["📅 Novo Agendamento", "📋 Horários Marcados", "❌ Cancelar Horário", "📊 Painel Administrativo"])

# --- ABA 1: NOVO AGENDAMENTO ---
with aba1:
    # Usamos o container nativo do Streamlit que já respeita o tema perfeitamente
    with st.container():
        st.subheader("Preencha os dados abaixo")
        
        lista_agendamentos = carregar_agendamentos()
        
        cliente = st.text_input("Nome completo do cliente:", key="input_cliente", placeholder="Ex: João Silva").strip()
        
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
                st.write("") 
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
# --- ABA 2: VISUALIZAR AGENDA ---
with aba2:
    lista_agendamentos = carregar_agendamentos()
    if not lista_agendamentos:
        st.info("Nenhum cliente agendado.")
    else:
        sub_bruno, sub_samuel, sub_geral = st.tabs(["🧔 Agenda do Bruno", "👨 Agenda do Samuel", "📋 Ver Geral"])
        
        def renderizar_lista(lista_filtrada):
            if not lista_filtrada:
                st.write("Sem horários marcados.")
                return
            for ag in lista_filtrada:
                data_str = ag["data_hora"].strftime("%d/%m/%Y")
                hora_str = ag["data_hora"].strftime("%H:%M")
                msg_encodada = urllib.parse.quote(f"Olá, {ag['cliente']}! Seu horário para {ag['servico']} está confirmado para o dia {data_str} às {hora_str} com o profissional {ag['profissional']}. 💈")
                
                card_html = f"""
                <div class="client-card">
                    <div>
                        <span style="font-size: 16px; font-weight: 700; color: var(--text-color);">{ag['cliente']}</span>
                        <span style="font-size: 14px; color: var(--text-color); opacity: 0.8;"> • {ag['servico']}</span>
                        <div style="font-size: 13px; color: var(--text-color); opacity: 0.7; margin-top: 4px;">
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
                    <div style="padding: 5px 0;">
                        <span style="font-size: 16px; font-weight: 700; color: #ff4b4b;">{ag['cliente']}</span><br>
                        <span style="font-size: 13px; color: var(--text-color);">📅 {data_str} às {hora_str} | {ag['servico']}</span>
                    </div>
                    """, unsafe_allow_html=True)
                with col_btn:
                    if st.button("🗑️ Cancelar", key=f"del_{sufixo}_{indice_real}", use_container_width=True, type="secondary"):
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
            st.info("Sem dados suficientes para gerar relatórios.")
        else:
            filtro_tempo = st.selectbox("Período:", ["Todo o Período", "Este Mês", "Esta Semana"])
            hoje = (datetime.utcnow() - timedelta(hours=3)).date()
            
            # Filtragem por período
            agendamentos_filtrados = []
            for ag in lista_agendamentos:
                data_ag = ag["data_hora"].date()
                if filtro_tempo == "Este Mês" and (data_ag.year != hoje.year or data_ag.month != hoje.month): 
                    continue
                if filtro_tempo == "Esta Semana" and not (hoje - timedelta(days=hoje.weekday()) <= data_ag <= hoje - timedelta(days=hoje.weekday()) + timedelta(days=6)): 
                    continue
                agendamentos_filtrados.append(ag)
            
            if agendamentos_filtrados:
                # Cálculos Gerais
                total_atendimentos = len(agendamentos_filtrados)
                faturamento_total = sum(PRECOS_SERVICOS.get(ag["servico"], 0) for ag in agendamentos_filtrados)
                
                # Separação por Profissional
                ag_bruno = [ag for ag in agendamentos_filtrados if ag["profissional"] == "Bruno"]
                ag_samuel = [ag for ag in agendamentos_filtrados if ag["profissional"] == "Samuel"]
                
                fat_bruno = sum(PRECOS_SERVICOS.get(ag["servico"], 0) for ag in ag_bruno)
                fat_samuel = sum(PRECOS_SERVICOS.get(ag["servico"], 0) for ag in ag_samuel)
                
                # Contagem de serviços individual e total
                contagem_servicos = {s: {"Bruno": 0, "Samuel": 0, "Total": 0} for s in PRECOS_SERVICOS.keys()}
                for ag in agendamentos_filtrados:
                    s = ag["servico"]
                    p = ag["profissional"]
                    if s in contagem_servicos:
                        contagem_servicos[s][p] += 1
                        contagem_servicos[s]["Total"] += 1

                # Descobrir o serviço que mais rendeu (Faturamento por serviço)
                def servico_mais_rentavel(lista_ag):
                    if not lista_ag:
                        return "Nenhum"
                    rendimento_por_servico = {}
                    for ag in lista_ag:
                        s = ag["servico"]
                        rendimento_por_servico[s] = rendimento_por_servico.get(s, 0) + PRECOS_SERVICOS.get(s, 0)
                    return max(rendimento_por_servico, key=rendimento_por_servico.get)

                mais_rentavel_bruno = servico_mais_rentavel(ag_bruno)
                mais_rentavel_samuel = servico_mais_rentavel(ag_samuel)
                
                # --- LAYOUT DO PAINEL ---
                st.markdown("<h3 style='margin-top:20px;'>Resumo Geral</h3>", unsafe_allow_html=True)
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    st.markdown(f'<div class="metric-card"><span style="color:var(--text-color);opacity:0.7;font-size:14px;font-weight:700;">Faturamento Total</span><br><span style="font-size:26px;font-weight:700;color:#23a55a;">R$ {faturamento_total:,.2f}</span></div>', unsafe_allow_html=True)
                with col_m2:
                    st.markdown(f'<div class="metric-card"><span style="color:var(--text-color);opacity:0.7;font-size:14px;font-weight:700;">Total de Atendimentos</span><br><span style="font-size:26px;font-weight:700;color:var(--text-color);">{total_atendimentos}</span></div>', unsafe_allow_html=True)
                
                st.markdown("<h3 style='margin-top:25px;'>Desempenho por Barbeiro</h3>", unsafe_allow_html=True)
                col_b1, col_b2 = st.columns(2)
                
                # Bloco do Bruno
                with col_b1:
                    st.markdown(f"""
                    <div class="metric-card" style="text-align: left; padding: 20px;">
                        <span style="font-size: 18px; font-weight: 700; color: var(--text-color);">🧔 Bruno</span><br>
                        <hr style="margin: 10px 0; opacity: 0.2;">
                        <span style="font-size: 13px; color: var(--text-color); opacity: 0.7;">Faturamento:</span><br>
                        <span style="font-size: 20px; font-weight: 700; color: var(--text-color);">R$ {fat_bruno:,.2f}</span><br><br>
                        <span style="font-size: 13px; color: var(--text-color); opacity: 0.7;">Mais rendeu:</span><br>
                        <span style="font-size: 15px; font-weight: 700; color: #23a55a;">{mais_rentavel_bruno}</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Bloco do Samuel
                with col_b2:
                    st.markdown(f"""
                    <div class="metric-card" style="text-align: left; padding: 20px;">
                        <span style="font-size: 18px; font-weight: 700; color: var(--text-color);">👨 Samuel</span><br>
                        <hr style="margin: 10px 0; opacity: 0.2;">
                        <span style="font-size: 13px; color: var(--text-color); opacity: 0.7;">Faturamento:</span><br>
                        <span style="font-size: 20px; font-weight: 700; color: var(--text-color);">R$ {fat_samuel:,.2f}</span><br><br>
                        <span style="font-size: 13px; color: var(--text-color); opacity: 0.7;">Mais rendeu:</span><br>
                        <span style="font-size: 15px; font-weight: 700; color: #23a55a;">{mais_rentavel_samuel}</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Nova Seção: Quantidade de Serviços Detalhada
                st.markdown("<h3 style='margin-top:25px;'>Quantidade de Serviços</h3>", unsafe_allow_html=True)
                
                linhas_tabela = ""
                for servico, dados in contagem_servicos.items():
                    linhas_tabela += f"""
                    <tr style="border-bottom: 1px solid rgba(128,128,128,0.2);">
                        <td style="padding: 10px; font-weight: 600; color: var(--text-color);">{servico}</td>
                        <td style="padding: 10px; text-align: center; color: var(--text-color);">{dados['Bruno']}</td>
                        <td style="padding: 10px; text-align: center; color: var(--text-color);">{dados['Samuel']}</td>
                        <td style="padding: 10px; text-align: center; font-weight: 700; color: #23a55a;">{dados['Total']}</td>
                    </tr>
                    """
                
                tabela_html = f"""
                <div class="metric-card" style="padding: 15px; overflow-x: auto;">
                    <table style="width: 100%; border-collapse: collapse; text-align: left;">
                        <thead>
                            <tr style="border-bottom: 2px solid rgba(128,128,128,0.4);">
                                <th style="padding: 10px; color: var(--text-color);">Serviço</th>
                                <th style="padding: 10px; text-align: center; color: var(--text-color);">Bruno</th>
                                <th style="padding: 10px; text-align: center; color: var(--text-color);">Samuel</th>
                                <th style="padding: 10px; text-align: center; color: var(--text-color);">Total Junto</th>
                            </tr>
                        </thead>
                        <tbody>
                            {linhas_tabela}
                        </tbody>
                    </table>
                </div>
                """
                st.markdown(tabela_html, unsafe_allow_html=True)
                
            else:
                st.info("Nenhum agendamento encontrado para o período selecionado.")
