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

# CONTATOS REAIS DA BARBEARIA
CONTATO_BRUNO = "5531985271355"  
CONTATO_SAMUEL = "5531985271355" 
ENDERECO_BARBEARIA = "R. dos Toureiros, 62 - Juliana"

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
            "telefone": ag.get("telefone", ""),
            "servico": ag["servico"],
            "profissional": ag["profissional"],
            "data_hora": ag["data_hora"].strftime("%Y-%m-%d %H:%M:%S")
        })
    with open(ARQUIVO_BANCO, "w", encoding="utf-8") as f:
        json.dump(dados_para_salvar, f, ensure_ascii=False, indent=4)

# --- CSS CUSTOMIZADO ADAPTÁVEL (LIGHT & DARK MODE) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700;900&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Montserrat', sans-serif !important;
    }
    
    /* Header do Agendamento estilo Barbearia */
    .header-barber {
        text-align: center;
        padding: 20px 0 15px 0;
        margin-bottom: 25px;
        border-bottom: 2px solid var(--text-color);
    }
    .header-tag {
        font-size: 0.75rem;
        letter-spacing: 5px;
        font-weight: 700;
        opacity: 0.6;
        text-transform: uppercase;
        color: var(--text-color);
        margin-bottom: 4px;
    }
    .header-title {
        font-family: 'Montserrat', sans-serif !important;
        font-size: 2.3rem !important;
        font-weight: 900 !important;
        letter-spacing: 3px !important;
        color: var(--text-color) !important;
        margin: 0 !important;
        line-height: 1.1 !important;
        text-transform: uppercase;
    }
    .header-subtitle {
        font-size: 0.8rem;
        font-weight: 600;
        color: var(--text-color);
        opacity: 0.75;
        margin-top: 8px;
        letter-spacing: 2px;
        text-transform: uppercase;
    }
    
    /* Estilização das Abas */
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
    .stTabs [aria-selected="true"] {
        opacity: 1 !important;
        background-color: var(--background-color) !important;
        box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.1) !important;
        border-radius: 6px !important;
    }
    
    /* Inputs e Seleções */
    div[data-testid="stTextInput"] input, div[data-testid="stSelectbox"] div {
        color: var(--text-color) !important;
        background-color: var(--background-color) !important;
    }
    
    /* Botões Principais */
    button[data-testid="baseButton-primary"] {
        background-color: var(--text-color) !important;
        color: var(--background-color) !important;
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 800 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        border: none !important;
        border-radius: 8px !important;
        height: 50px !important;
        font-size: 15px !important;
        transition: opacity 0.2s ease !important;
    }
    button[data-testid="baseButton-primary"]:hover {
        opacity: 0.85 !important;
    }
    
    /* Cards de Exibição de Clientes */
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
        font-size: 13px;
        display: inline-block;
    }
    
    .metric-card {
        background-color: var(--secondary-background-color) !important;
        border: 1px solid rgba(128, 128, 128, 0.2) !important;
        padding: 18px;
        border-radius: 10px;
        text-align: center;
    }
    
    .info-footer {
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(128, 128, 128, 0.2);
        padding: 15px;
        border-radius: 10px;
        margin-top: 30px;
        font-size: 14px;
        color: var(--text-color);
    }
    </style>
""", unsafe_allow_html=True)

# --- CABEÇALHO BARBEARIA PRETO & BRANCO ---
st.markdown("""
    <div class="header-barber">
        <div class="header-tag">• BARBERSHOP •</div>
        <h1 class="header-title">PRETO & BRANCO</h1>
        <div class="header-subtitle">Agendamento Online & Gestão Integrada</div>
    </div>
""", unsafe_allow_html=True)

aba1, aba2, aba3, aba4 = st.tabs(["📅 Novo Agendamento", "📋 Horários Marcados", "❌ Cancelar Horário", "📊 Painel Administrativo"])

# --- ABA 1: NOVO AGENDAMENTO ---
with aba1:
    with st.container():
        st.subheader("Preencha os dados abaixo")
        
        lista_agendamentos = carregar_agendamentos()
        
        col_c1, col_c2 = st.columns([2, 1])
        with col_c1:
            cliente = st.text_input("Nome completo do cliente:", key="input_cliente", placeholder="Ex: João Silva").strip()
        with col_c2:
            telefone = st.text_input("WhatsApp / Celular:", key="input_telefone", placeholder="Ex: 31985271355").strip()
        
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
            elif not telefone:
                st.error("Por favor, informe o telefone de contato.")
            else:
                dt_completo = datetime.combine(data_atendimento, hora_atendimento)
                lista_agendamentos = carregar_agendamentos()
                conflito = any(ag["profissional"] == profissional and ag["data_hora"] == dt_completo for ag in lista_agendamentos)
                
                if not conflito:
                    tel_limpo = "".join(filter(str.isdigit, telefone))
                    if len(tel_limpo) == 9:
                        tel_limpo = "5531" + tel_limpo
                    elif len(tel_limpo) == 11:
                        tel_limpo = "55" + tel_limpo
                    elif not tel_limpo.startswith("55") and len(tel_limpo) >= 10:
                        tel_limpo = "55" + tel_limpo

                    lista_agendamentos.append({
                        "cliente": cliente,
                        "telefone": tel_limpo,
                        "servico": servico,
                        "profissional": profissional,
                        "data_hora": dt_completo
                    })
                    lista_agendamentos.sort(key=lambda x: x["data_hora"])
                    salvar_agendamentos(lista_agendamentos)
                    
                    data_f = data_atendimento.strftime('%d/%m/%Y')
                    hora_f = hora_atendimento.strftime('%H:%M')
                    
                    texto_msg = (
                        f"Olá! Confirmo meu agendamento na Barbearia Preto & Branco:\n\n"
                        f"👤 *Cliente:* {cliente}\n"
                        f"💈 *Serviço:* {servico}\n"
                        f"🧔 *Barbeiro:* {profissional}\n"
                        f"📅 *Data:* {data_f} às {hora_f}\n\n"
                        f"📍 *Endereço:* {ENDERECO_BARBEARIA}"
                    )
                    
                    num_barbeiro = CONTATO_BRUNO if profissional == "Bruno" else CONTATO_SAMUEL
                    link_wa = f"https://wa.me/{num_barbeiro}?text={urllib.parse.quote(texto_msg)}"
                    
                    st.success(f"🎉 Horário reservado com sucesso para {cliente}!")
                    
                    st.markdown(f"""
                    <div style="background-color: var(--secondary-background-color); border: 2px solid #23a55a; padding: 20px; border-radius: 10px; text-align: center; margin-top: 15px; margin-bottom: 20px;">
                        <h4 style="margin: 0 0 8px 0; color: var(--text-color);">Quase lá! Envie a confirmação:</h4>
                        <p style="font-size: 14px; opacity: 0.8; margin-bottom: 15px;">Clique no botão abaixo para notificar o barbeiro via WhatsApp.</p>
                        <a href="{link_wa}" target="_blank" class="whatsapp-btn" style="font-size: 15px; padding: 12px 24px;">
                            📲 Enviar confirmação no WhatsApp
                        </a>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error("Conflito de última hora detectado.")

        formato_bruno = f"https://wa.me/{CONTATO_BRUNO}"
        formato_samuel = f"https://wa.me/{CONTATO_SAMUEL}"
        
        st.markdown(f"""
        <div class="info-footer">
            <b>📍 Endereço:</b> {ENDERECO_BARBEARIA}<br>
            <b>📞 Contatos para Dúvidas:</b> 
            Bruno: <a href="{formato_bruno}" target="_blank" style="color: #23a55a; text-decoration: none; font-weight: bold;">(31) 98527-1355</a> | 
            Samuel: <a href="{formato_samuel}" target="_blank" style="color: #23a55a; text-decoration: none; font-weight: bold;">(31) 98527-1355</a>
        </div>
        """, unsafe_allow_html=True)

# --- ABA 2: VISUALIZAR AGENDA & CONSULTAR HORÁRIOS LIVRES ---
with aba2:
    st.subheader("Consultar Agenda e Horários Livres")
    
    lista_agendamentos = carregar_agendamentos()
    
    hoje_dt = datetime.utcnow() - timedelta(hours=3)
    dias_semana_pt = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
    
    opcoes_datas_consulta = []
    for i in range(30):
        futuro = hoje_dt + timedelta(days=i)
        if futuro.weekday() != 6:
            texto_data = f"{futuro.strftime('%d/%m/%Y')} ({dias_semana_pt[futuro.weekday()]})"
            opcoes_datas_consulta.append((futuro.date(), texto_data))
            
    data_consulta_sel = st.selectbox("Selecione a data para consultar:", opcoes_datas_consulta, format_func=lambda x: x[1], key="select_data_consulta")
    data_consulta = data_consulta_sel[0]
    
    def obter_horarios_vagos(profissional, data_alvo):
        dia_semana = data_alvo.weekday()
        horarios_todos = []
        minutos_inicio = 480
        minutos_fim = 1020 if dia_semana == 5 else 1080
        
        minutos_atual = minutos_inicio
        while minutos_atual <= minutos_fim:
            h_print = minutos_atual // 60
            m_print = minutos_atual % 60
            horarios_todos.append(dt_time(h_print, m_print))
            minutos_atual += 40
            
        horarios_vagos = []
        for h in horarios_todos:
            dt_verificar = datetime.combine(data_alvo, h)
            if data_alvo == hoje_dt.date() and h < hoje_dt.time():
                continue
            ocupado = any(ag["profissional"] == profissional and ag["data_hora"] == dt_verificar for ag in lista_agendamentos)
            if not ocupado:
                horarios_vagos.append(h.strftime("%H:%M"))
                
        return horarios_vagos

    sub_bruno, sub_samuel, sub_geral = st.tabs(["🧔 Bruno", "👨 Samuel", "📋 Visão Geral"])
    
    def renderizar_lista(lista_filtrada):
        if not lista_filtrada:
            st.info("Nenhum cliente agendado para esta data.")
            return
        for ag in lista_filtrada:
            data_str = ag["data_hora"].strftime("%d/%m/%Y")
            hora_str = ag["data_hora"].strftime("%H:%M")
            msg_encodada = urllib.parse.quote(f"Olá, {ag['cliente']}! Seu horário para {ag['servico']} está confirmado para o dia {data_str} às {hora_str} com o profissional {ag['profissional']}. 💈")
            
            destino_whatsapp = ag.get("telefone", "")
            link_whatsapp = f"https://wa.me/{destino_whatsapp}?text={msg_encodada}" if destino_whatsapp else f"https://wa.me/?text={msg_encodada}"
            
            card_html = f"""
            <div class="client-card">
                <div>
                    <span style="font-size: 16px; font-weight: 700; color: var(--text-color);">{ag['cliente']}</span>
                    <span style="font-size: 14px; color: var(--text-color); opacity: 0.8;"> • {ag['servico']}</span>
                    <div style="font-size: 13px; color: var(--text-color); opacity: 0.7; margin-top: 4px;">
                        📅 {data_str} às <b>{hora_str}</b> | Barbeiro: {ag['profissional']} {f'| 📱 {ag["telefone"]}' if ag.get("telefone") else ''}
                    </div>
                </div>
                <div>
                    <a href="{link_whatsapp}" target="_blank" class="whatsapp-btn">Avisar</a>
                </div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)

    with sub_bruno:
        ag_bruno_data = [ag for ag in lista_agendamentos if ag["profissional"] == "Bruno" and ag["data_hora"].date() == data_consulta]
        vagos_bruno = obter_horarios_vagos("Bruno", data_consulta)
        
        with st.expander(f"🟢 Ver {len(vagos_bruno)} horários vagos do Bruno para {data_consulta.strftime('%d/%m/%Y')}", expanded=False):
            if vagos_bruno:
                cols = st.columns(4)
                for idx, hr in enumerate(vagos_bruno):
                    cols[idx % 4].button(f"⏰ {hr}", key=f"vago_bruno_{hr}", disabled=True)
            else:
                st.warning("Nenhum horário livre para este dia!")
                
        st.markdown("#### Clientes Marcados")
        renderizar_lista(ag_bruno_data)

    with sub_samuel:
        ag_samuel_data = [ag for ag in lista_agendamentos if ag["profissional"] == "Samuel" and ag["data_hora"].date() == data_consulta]
        vagos_samuel = obter_horarios_vagos("Samuel", data_consulta)
        
        with st.expander(f"🟢 Ver {len(vagos_samuel)} horários vagos do Samuel para {data_consulta.strftime('%d/%m/%Y')}", expanded=False):
            if vagos_samuel:
                cols = st.columns(4)
                for idx, hr in enumerate(vagos_samuel):
                    cols[idx % 4].button(f"⏰ {hr}", key=f"vago_samuel_{hr}", disabled=True)
            else:
                st.warning("Nenhum horário livre para este dia!")
                
        st.markdown("#### Clientes Marcados")
        renderizar_lista(ag_samuel_data)

    with sub_geral:
        ag_geral_data = [ag for ag in lista_agendamentos if ag["data_hora"].date() == data_consulta]
        st.markdown("#### Todos os Clientes Marcados do Dia")
        renderizar_lista(ag_geral_data)

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
            
            agendamentos_filtrados = []
            for ag in lista_agendamentos:
                data_ag = ag["data_hora"].date()
                if filtro_tempo == "Este Mês" and (data_ag.year != hoje.year or data_ag.month != hoje.month): 
                    continue
                if filtro_tempo == "Esta Semana" and not (hoje - timedelta(days=hoje.weekday()) <= data_ag <= hoje - timedelta(days=hoje.weekday()) + timedelta(days=6)): 
                    continue
                agendamentos_filtrados.append(ag)
            
            if agendamentos_filtrados:
                total_atendimentos = len(agendamentos_filtrados)
                faturamento_total = sum(PRECOS_SERVICOS.get(ag["servico"], 0) for ag in agendamentos_filtrados)
                
                ag_bruno = [ag for ag in agendamentos_filtrados if ag["profissional"] == "Bruno"]
                ag_samuel = [ag for ag in agendamentos_filtrados if ag["profissional"] == "Samuel"]
                
                fat_bruno = sum(PRECOS_SERVICOS.get(ag["servico"], 0) for ag in ag_bruno)
                fat_samuel = sum(PRECOS_SERVICOS.get(ag["servico"], 0) for ag in ag_samuel)
                
                contagem_servicos = {s: {"Bruno": 0, "Samuel": 0, "Total": 0} for s in PRECOS_SERVICOS.keys()}
                for ag in agendamentos_filtrados:
                    s = ag["servico"]
                    p = ag["profissional"]
                    if s in contagem_servicos:
                        contagem_servicos[s][p] += 1
                        contagem_servicos[s]["Total"] += 1

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
                
                st.markdown("<h3 style='margin-top:20px;'>Resumo Geral</h3>", unsafe_allow_html=True)
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    st.markdown(f'<div class="metric-card"><span style="color:var(--text-color);opacity:0.7;font-size:14px;font-weight:700;">Faturamento Total</span><br><span style="font-size:26px;font-weight:800;color:#23a55a;">R$ {faturamento_total:,.2f}</span></div>', unsafe_allow_html=True)
                with col_m2:
                    st.markdown(f'<div class="metric-card"><span style="color:var(--text-color);opacity:0.7;font-size:14px;font-weight:700;">Total de Atendimentos</span><br><span style="font-size:26px;font-weight:800;color:var(--text-color);">{total_atendimentos}</span></div>', unsafe_allow_html=True)
                
                st.markdown("<h3 style='margin-top:25px;'>Desempenho por Barbeiro</h3>", unsafe_allow_html=True)
                col_b1, col_b2 = st.columns(2)
                
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
                
                st.markdown("<h3 style='margin-top:25px;'>Quantidade de Serviços</h3>", unsafe_allow_html=True)
                
                linhas_html = ""
                for servico_item, dados in contagem_servicos.items():
                    linhas_html += (
                        f"<tr style='border-bottom: 1px solid rgba(128,128,128,0.2);'>"
                        f"<td style='padding: 12px; font-weight: 600; color: var(--text-color);'>{servico_item}</td>"
                        f"<td style='padding: 12px; text-align: center; color: var(--text-color);'>{dados['Bruno']}</td>"
                        f"<td style='padding: 12px; text-align: center; color: var(--text-color);'>{dados['Samuel']}</td>"
                        f"<td style='padding: 12px; text-align: center; font-weight: 700; color: #23a55a;'>{dados['Total']}</td>"
                        f"</tr>"
                    )
                
                tabela_html = (
                    f"<div class='metric-card' style='padding: 15px; overflow-x: auto; text-align: left;'>""<table style='width: 100%; border-collapse: collapse;'>""<thead>""<tr style='border-bottom: 2px solid rgba(128,128,128,0.4);'>"
                    f"<th style='padding: 12px; color: var(--text-color); text-align: left;'>Serviço</th>"
                    f"<th style='padding: 12px; text-align: center; color: var(--text-color);'>Bruno</th>"
                    f"<th style='padding: 12px; text-align: center; color: var(--text-color);'>Samuel</th>"
                    f"<th style='padding: 12px; text-align: center; color: var(--text-color);'>Total Junto</th>"
                    f"</tr>""</thead>""<tbody>"
                    f"{linhas_html}"
                    f"</tbody>""</table>""</div>"
                )
                st.markdown(tabela_html, unsafe_allow_html=True)
                
            else:
                st.info("Nenhum agendamento encontrado para o período selecionado.")
