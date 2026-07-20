import streamlit as st
from datetime import datetime, timedelta, time as dt_time
import json
import os
import urllib.parse
import time

# Configuração da página - Otimizada para Celulares e Computadores
st.set_page_config(page_title="Barbearia do Bruno", page_icon="💈", layout="centered")

ARQUIVO_BANCO = "agendamentos_barbearia.json"

# Definição de preços dos serviços para o relatório financeiro
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

# Estilização responsiva e componentes customizados
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab"] { font-size: 15px; padding: 10px; }
    button[data-testid="baseButton-secondary"] { width: 100%; height: 50px; }
    .css-1r6g72q { font-weight: bold; }
    
    /* Estilo para os cartões do painel administrativo */
    .metric-card {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 10px;
    }

    /* Estilo para os cards de agendamento na lista de Horários Marcados */
    .client-card {
        background-color: #ffffff;
        border: 1px solid #e9ecef;
        padding: 18px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
        margin-bottom: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .client-info {
        flex-grow: 1;
    }
    .whatsapp-btn {
        background-color: #25D366;
        color: white !important;
        border: none;
        padding: 10px 20px;
        border-radius: 8px;
        font-weight: bold;
        text-decoration: none;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        font-size: 14px;
        transition: background-color 0.2s ease;
        cursor: pointer;
    }
    .whatsapp-btn:hover {
        background-color: #1ebd59;
    }
    
    /* Ajuste para alinhar verticalmente os botões nativos de cancelar do Streamlit nos cards */
    div[data-testid="stColumn"] {
        display: flex;
        align-items: center;
    }
    </style>
""", unsafe_allow_html=True)

st.title("💈 Barbearia Preto & Branco")
st.subheader("Sistema de Gestão de Agendamentos")

# Criação das abas atualizadas
aba1, aba2, aba3, aba4 = st.tabs(["📅 Agendar Horário", "📋 Horários Marcados", "❌ Cancelar Horário", "📊 Painel Admin"])

# --- ABA 1: NOVO AGENDAMENTO ---
with aba1:
    st.header("Marcar Horário")
    lista_agendamentos = carregar_agendamentos()
    
    cliente = st.text_input("Nome do Cliente:", key="input_cliente").strip()
    servico = st.selectbox("Serviço:", list(PRECOS_SERVICOS.keys()), key="select_servico")
    profissional = st.radio("Profissional:", ["Bruno", "Samuel"], horizontal=True, key="radio_prof")
    
    # Horário atual de Brasília (UTC -3)
    hoje_dt = datetime.utcnow() - timedelta(hours=3)
    
    dias_semana_pt = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
    
    opcoes_datas = []
    for i in range(30):
        futuro = hoje_dt + timedelta(days=i)
        if futuro.weekday() != 6: # Ignora domingos
            texto_data = f"{futuro.strftime('%d/%m/%Y')} ({dias_semana_pt[futuro.weekday()]})"
            opcoes_datas.append((futuro.date(), texto_data))
    
    data_selecionada = st.selectbox("Escolha a Data:", opcoes_datas, format_func=lambda x: x[1], key="select_data")
    data_atendimento = data_selecionada[0]
    
    dia_semana_selecionado = data_atendimento.weekday()
    horarios_todos = []
    
    minutos_inicio = 480 # 08h00
    minutos_fim = 1020 if dia_semana_selecionado == 5 else 1080  # 17h00 no sábado | 18h00 na semana
    
    minutos_atual = minutos_inicio
    while minutos_atual <= minutos_fim:
        h_print = minutos_atual // 60
        m_print = minutos_atual % 60
        horarios_todos.append(dt_time(h_print, m_print))
        minutos_atual += 40
    
    horarios_disponiveis = []
    for h in horarios_todos:
        dt_verificar = datetime.combine(data_atendimento, h)
        
        if data_atendimento == hoje_dt.date():
            if h < hoje_dt.time():
                continue
            
        ocupado = any(ag["profissional"] == profissional and ag["data_hora"] == dt_verificar for ag in lista_agendamentos)
        if not ocupado:
            horarios_disponiveis.append(h)
    
    if horarios_disponiveis:
        hora_atendimento = st.selectbox("Horário Disponível:", horarios_disponiveis, format_func=lambda x: x.strftime("%H:%M"), key="select_hora")
        botao_agendar = st.button("Confirmar Agendamento", use_container_width=True, type="primary")
    else:
        st.warning("⚠️ Todos os horários para este profissional nesta data já estão preenchidos ou indisponíveis!")
        botao_agendar = False

    if botao_agendar:
        if not cliente:
            st.error("Por favor, digite o nome do cliente.")
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
                st.success(f"🎉 Agendamento realizado para {cliente}!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Este horário acabou de ser preenchido por outra pessoa.")

# --- ABA 2: VISUALIZAR AGENDA SEPARADA POR BARBEIRO (VISUAL PREMIUM) ---
with aba2:
    st.header("Próximos Clientes")
    lista_agendamentos = carregar_agendamentos()
    
    if not lista_agendamentos:
        st.info("Nenhum agendamento marcado no momento.")
    else:
        sub_bruno, sub_samuel, sub_geral = st.tabs(["🧔 Agenda do Bruno", "👨 Agenda do Samuel", "📋 Ver Geral"])
        
        def renderizar_lista(lista_filtrada):
            if not lista_filtrada:
                st.info("Nenhum agendamento para este filtro.")
                return
            for ag in lista_filtrada:
                data_str = ag["data_hora"].strftime("%d/%m/%Y")
                hora_str = ag["data_hora"].strftime("%H:%M")
                
                msg = f"Olá, {ag['cliente']}! Seu horário para {ag['servico']} está confirmado para o dia {data_str} às {hora_str} com o profissional {ag['profissional']}. Obrigado! 💈"
                msg_encodada = urllib.parse.quote(msg)
                link_whatsapp = f"https://wa.me/?text={msg_encodada}"
                
                card_html = f"""
                <div class="client-card">
                    <div class="client-info">
                        <span style="font-size: 18px; font-weight: bold; color: #212529;">🟢 {ag['cliente']}</span>
                        <span style="font-size: 16px; color: #6c757d;"> — {ag['servico']}</span>
                        <div style="font-size: 14px; color: #868e96; margin-top: 4px;">
                            📅 {data_str} às {hora_str} | <b>Barber:</b> {ag['profissional']}
                        </div>
                    </div>
                    <div>
                        <a href="{link_whatsapp}" target="_blank" class="whatsapp-btn">
                            <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16" style="margin-bottom: -2px;">
                                <path d="M13.601 2.326A7.854 7.854 0 0 0 7.994 0C3.627 0 .068 3.558.064 7.926c0 1.399.366 2.76 1.057 3.965L0 16l4.204-1.102a7.933 7.933 0 0 0 3.79.965h.004c4.368 0 7.926-3.558 7.93-7.93A7.898 7.898 0 0 0 13.6 2.326zM7.994 14.521a6.573 6.573 0 0 1-3.356-.92l-.24-.144-2.494.654.666-2.433-.156-.251a6.56 6.56 0 0 1-1.007-3.505c0-3.626 2.957-6.584 6.591-6.584a6.56 6.56 0 0 1 4.66 1.931 6.557 6.557 0 0 1 1.928 4.66c-.004 3.639-2.961 6.592-6.592 6.592zm3.69-4.98c-.202-.101-1.194-.588-1.378-.653-.185-.069-.32-.103-.454.101-.135.202-.52.653-.637.786-.117.135-.235.151-.437.05-.202-.101-.852-.313-1.623-.999-.6-.535-1.005-1.199-1.123-1.401-.117-.202-.012-.311.089-.41.09-.091.202-.235.302-.354.101-.117.135-.197.202-.33.067-.136.034-.253-.017-.354-.05-.101-.454-1.093-.622-1.499-.163-.395-.331-.341-.454-.341h-.388c-.135 0-.354.05-.539.253-.185.202-.708.692-.708 1.693 0 1.001.728 1.968.829 2.101.101.135 1.433 2.187 3.474 3.069.485.21 1.001.336 1.353.447.487.155.93.133 1.282.08.393-.059 1.194-.488 1.365-.956.17-.467.17-.868.12-.956-.05-.088-.185-.138-.388-.239z"/>
                            </svg>
                            Avisar
                        </a>
                    </div>
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)

        with sub_bruno:
            agendamentos_bruno = [ag for ag in lista_agendamentos if ag["profissional"] == "Bruno"]
            renderizar_lista(agendamentos_bruno)
            
        with sub_samuel:
            agendamentos_samuel = [ag for ag in lista_agendamentos if ag["profissional"] == "Samuel"]
            renderizar_lista(agendamentos_samuel)
            
        with sub_geral:
            renderizar_lista(lista_agendamentos)

# --- ABA 3: CANCELAR AGENDAMENTO (CORRIGIDO SEM DUPLICIDADE DE KEY) ---
with aba3:
    st.header("Desmarcar Horário")
    lista_agendamentos = carregar_agendamentos()
    
    if not lista_agendamentos:
        st.info("Nenhum agendamento disponível para exclusão.")
    else:
        st.write("Selecione o profissional para listar os horários e clique em **Cancelar Horário**:")
        
        canc_bruno, canc_samuel, canc_geral = st.tabs(["🧔 Cancelar do Bruno", "👨 Cancelar do Samuel", "📋 Ver Todos"])
        
        def renderizar_lista_cancelamento(lista_filtrada, sufixo):
            if not lista_filtrada:
                st.info("Nenhum agendamento encontrado.")
                return
                
            for ag in lista_filtrada:
                data_str = ag["data_hora"].strftime("%d/%m/%Y")
                hora_str = ag["data_hora"].strftime("%H:%M")
                
                indice_real = next((i for i, item in enumerate(lista_agendamentos) if 
                                     item["cliente"] == ag["cliente"] and 
                                     item["profissional"] == ag["profissional"] and 
                                     item["data_hora"] == ag["data_hora"]), None)
                
                if indice_real is None:
                    continue
                
                col_info, col_btn = st.columns([3, 1])
                
                with col_info:
                    st.markdown(f"""
                    <div style="padding: 5px 0;">
                        <span style="font-size: 16px; font-weight: bold; color: #dc3545;">🔴 {ag['cliente']}</span>
                        <span style="font-size: 14px; color: #495057;"> — {ag['servico']}</span><br>
                        <span style="font-size: 13px; color: #6c757d;">📅 {data_str} às {hora_str} | Barbeiro: {ag['profissional']}</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_btn:
                    if st.button("🗑️ Cancelar", key=f"del_{sufixo}_{indice_real}", type="primary", use_container_width=True):
                        lista_agendamentos.pop(indice_real)
                        salvar_agendamentos(lista_agendamentos)
                        st.success(f"Horário de {ag['cliente']} cancelado!")
                        time.sleep(0.8)
                        st.rerun()
                st.divider()

        with canc_bruno:
            agenda_bruno = [ag for ag in lista_agendamentos if ag["profissional"] == "Bruno"]
            renderizar_lista_cancelamento(agenda_bruno, "bruno")
            
        with canc_samuel:
            agenda_samuel = [ag for ag in lista_agendamentos if ag["profissional"] == "Samuel"]
            renderizar_lista_cancelamento(agenda_samuel, "samuel")
            
        with canc_geral:
            renderizar_lista_cancelamento(lista_agendamentos, "geral")

# --- ABA 4: PAINEL ADMINISTRATIVO COM SENHA ---
with aba4:
    st.header("Área Restrita")
    
    senha = st.text_input("Digite a senha de administrador:", type="password", key="input_senha")
    
    if senha == "admin123":
        st.success("🔓 Acesso liberado!")
        lista_agendamentos = carregar_agendamentos()
        
        if not lista_agendamentos:
            st.info("Ainda não há dados suficientes para gerar relatórios.")
        else:
            st.subheader("🗓️ Filtro do Relatório")
            filtro_tempo = st.selectbox(
                "Visualizar dados de:",
                ["Todo o Período", "Este Mês", "Esta Semana"],
                key="filtro_tempo"
            )
            
            hoje = (datetime.utcnow() - timedelta(hours=3)).date()
            
            agendamentos_filtrados = []
            for ag in lista_agendamentos:
                data_ag = ag["data_hora"].date()
                if filtro_tempo == "Este Mês":
                    if data_ag.year == hoje.year and data_ag.month == hoje.month:
                        agendamentos_filtrados.append(ag)
                elif filtro_tempo == "Esta Semana":
                    inicio_semana = hoje - timedelta(days=hoje.weekday())
                    fim_semana = inicio_semana + timedelta(days=6)
                    if inicio_semana <= data_ag <= fim_semana:
                        agendamentos_filtrados.append(ag)
                else:
                    agendamentos_filtrados.append(ag)
            
            if not agendamentos_filtrados:
                st.warning(f"Nenhum agendamento encontrado para o período: {filtro_tempo}")
            else:
                total_atendimentos = len(agendamentos_filtrados)
                faturamento_total = sum(PRECOS_SERVICOS.get(ag["servico"], 0) for ag in agendamentos_filtrados)
                
                faturamento_bruno = sum(PRECOS_SERVICOS.get(ag["servico"], 0) for ag in agendamentos_filtrados if ag["profissional"] == "Bruno")
                faturamento_samuel = sum(PRECOS_SERVICOS.get(ag["servico"], 0) for ag in agendamentos_filtrados if ag["profissional"] == "Samuel")
                
                st.divider()
                st.subheader(f"📊 Métricas Gerais — {filtro_tempo}")
                
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <span style="color:#6c757d; font-size:14px; font-weight:bold;">Faturamento Bruto</span><br>
                        <span style="font-size:26px; font-weight:bold; color:#2e7d32;">R$ {faturamento_total:,.2f}</span>
                    </div>
                    """, unsafe_allow_html=True)
                with col_m2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <span style="color:#6c757d; font-size:14px; font-weight:bold;">Total de Atendimentos</span><br>
                        <span style="font-size:26px; font-weight:bold; color:#1565c0;">{total_atendimentos}</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.subheader("👤 Desempenho por Profissional")
                col_p1, col_p2 = st.columns(2)
                with col_p1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <span style="color:#495057; font-size:14px;">Faturamento do <b>Bruno</b></span><br>
                        <span style="font-size:22px; font-weight:bold; color:#212529;">R$ {faturamento_bruno:,.2f}</span>
                    </div>
                    """, unsafe_allow_html=True)
                with col_p2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <span style="color:#495057; font-size:14px;">Faturamento do <b>Samuel</b></span><br>
                        <span style="font-size:22px; font-weight:bold; color:#212529;">R$ {faturamento_samuel:,.2f}</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.subheader("📈 Serviços Mais Procurados")
                contagem_servicos = {}
                for ag in agendamentos_filtrados:
                    contagem_servicos[ag["servico"]] = contagem_servicos.get(ag["servico"], 0) + 1
                
                for serv, qtd in contagem_servicos.items():
                    st.write(f"**{serv}**: {qtd} atendimento(s)")
                    st.progress(min(qtd / total_atendimentos, 1.0))
                
    elif senha != "":
        st.error("❌ Senha incorreta! Digite novamente.")
