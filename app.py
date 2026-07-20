import streamlit as st
from datetime import datetime, timedelta, time
import json
import os
import urllib.parse

# Configuração da página - Otimizada para Celulares e Computadores
st.set_page_config(page_title="Barbearia do Bruno", page_icon="💈", layout="centered")

ARQUIVO_BANCO = "agendamentos_barbearia.json"

# Definição de preços dos serviços para o relatório financeiro
PRECOS_SERVICOS = {
    "Cabelo": 40.0,
    "Barba": 30.0,
    "Combo (Cabelo + Barba)": 60.0,
    "Sobrancelha": 15.0
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

# Estilização responsiva para celulares
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab"] { font-size: 15px; padding: 10px; }
    button[data-testid="baseButton-secondary"] { width: 100%; height: 50px; }
    .css-1r6g72q { font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.title("💈 Barbearia do Bruno & Samuel")
st.subheader("Sistema de Gestão de Agendamentos")

# Criação das abas incluindo o Painel Admin
aba1, aba2, aba3, aba4 = st.tabs(["📅 Agendar", "📋 Agenda", "❌ Cancelar", "📊 Painel Admin"])

# --- ABA 1: NOVO AGENDAMENTO ---
with aba1:
    st.header("Marcar Horário")
    lista_agendamentos = carregar_agendamentos()
    
    with st.form("form_agendamento", clear_on_submit=True):
        cliente = st.text_input("Nome do Cliente:").strip()
        servico = st.selectbox("Serviço:", list(PRECOS_SERVICOS.keys()))
        profissional = st.radio("Profissional:", ["Bruno", "Samuel"], horizontal=True)
        
        # Correção do Fuso: Força o horário com base no fuso do servidor ajustado para o Brasil (-3 horas)
        fuso_ajuste = timedelta(hours=-3)
        hoje_dt = datetime.utcnow() + fuso_ajuste
        
        dias_semana_pt = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
        
        opcoes_datas = []
        for i in range(30):
            futuro = hoje_dt + timedelta(days=i)
            if futuro.weekday() != 6: # Ignora domingos
                texto_data = f"{futuro.strftime('%d/%m/%Y')} ({dias_semana_pt[futuro.weekday()]})"
                opcoes_datas.append((futuro.date(), texto_data))
        
        data_selecionada = st.selectbox("Escolha a Data:", opcoes_datas, format_func=lambda x: x[1])
        data_atendimento = data_selecionada[0]
        
        dia_semana_selecionado = data_atendimento.weekday()
        horarios_todos = []
        inicio_expediente = datetime.combine(hoje_dt.date(), time(8, 0))
        
        # Gera a grade padrão de horários (Sábado vs Semana)
        if dia_semana_selecionado == 5:
            for i in range(15):
                hora_gerada = (inicio_expediente + timedelta(minutes=40 * i)).time()
                if hora_gerada <= time(17, 0):
                    horarios_todos.append(hora_gerada)
        else:
            for i in range(17):
                hora_gerada = (inicio_expediente + timedelta(minutes=40 * i)).time()
                if hora_gerada <= time(18, 0):
                    horarios_todos.append(hora_gerada)
        
        # --- FILTRO DE HORÁRIOS OCUPADOS E HORÁRIOS PASSADOS ---
        horarios_disponiveis = []
        for h in horarios_todos:
            dt_verificar = datetime.combine(data_atendimento, h)
            
            # Só bloqueia se a data selecionada for EXATAMENTE o dia de hoje no Brasil
            if data_atendimento == hoje_dt.date():
                if dt_verificar.time() < hoje_dt.time():
                    continue
                
            ocupado = any(ag["profissional"] == profissional and ag["data_hora"] == dt_verificar for ag in lista_agendamentos)
            if not ocupado:
                horarios_disponiveis.append(h)
        
        if horarios_disponiveis:
            hora_atendimento = st.selectbox("Horário Disponível:", horarios_disponiveis, format_func=lambda x: x.strftime("%H:%M"))
            botao_agendar = st.form_submit_button("Confirmar Agendamento", use_container_width=True)
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
            
            if not不动 conflito:
                lista_agendamentos.append({
                    "cliente": cliente,
                    "servico": servico,
                    "profissional": profissional,
                    "data_hora": dt_completo
                })
                lista_agendamentos.sort(key=lambda x: x["data_hora"])
                salvar_agendamentos(lista_agendamentos)
                st.success(f"🎉 Agendamento realizado para {cliente}!")
                st.rerun()
            else:
                st.error("Este horário acabou de ser preenchido por outra pessoa.")

# --- ABA 2: VISUALIZAR AGENDA + WHATSAPP ---
with aba2:
    st.header("Próximos Clientes")
    lista_agendamentos = carregar_agendamentos()
    
    if not lista_agendamentos:
        st.info("Nenhum agendamento marcado no momento.")
    else:
        for ag in lista_agendamentos:
            data_str = ag["data_hora"].strftime("%d/%m/%Y")
            hora_str = ag["data_hora"].strftime("%H:%M")
            
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**🟢 {ag['cliente']}** — {ag['servico']}")
                    st.caption(f"📅 {data_str} às {hora_str} | Barber: {ag['profissional']}")
                with col2:
                    msg = f"Olá, {ag['cliente']}! Seu horário para {ag['servico']} está confirmado para o dia {data_str} às {hora_str} com o profissional {ag['profissional']}. Obrigado! 💈"
                    msg_encodada = urllib.parse.quote(msg)
                    link_whatsapp = f"https://wa.me/?text={msg_encodada}"
                    
                    st.markdown(f'<a href="{link_whatsapp}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:8px; border-radius:5px; cursor:pointer;">📲 Avisar</button></a>', unsafe_allow_html=True)
                st.divider()

# --- ABA 3: CANCELAR AGENDAMENTO ---
with aba3:
    st.header("Desmarcar Horário")
    lista_agendamentos = carregar_agendamentos()
    
    if not lista_agendamentos:
        st.info("Nenhum agendamento disponível para exclusão.")
    else:
        opcoes_cancelar = []
        for i, ag in enumerate(lista_agendamentos):
            texto = f"{ag['data_hora'].strftime('%d/%m %H:%M')} - {ag['cliente']} ({ag['profissional']})"
            opcoes_cancelar.append((i, texto))
            
        selecionado = st.selectbox("Escolha o agendamento que deseja remover:", opcoes_cancelar, format_func=lambda x: x[1])
        botao_cancelar = st.button("Remover Agendamento da Lista", type="primary", use_container_width=True)
        
        if botao_cancelar:
            indice_para_remover = selecionado[0]
            lista_agendamentos.pop(indice_para_remover)
            salvar_agendamentos(lista_agendamentos)
            st.success("✅ Agendamento cancelado com sucesso!")
            st.rerun()

# --- ABA 4: PAINEL ADMINISTRATIVO COM SENHA ---
with aba4:
    st.header("Área Restrita")
    
    senha = st.text_input("Digite a senha de administrador:", type="password")
    
    if senha == "admin123":
        st.success("🔓 Acesso liberado!")
        lista_agendamentos = carregar_agendamentos()
        
        if not lista_agendamentos:
            st.info("Ainda não há dados suficientes para gerar relatórios.")
        else:
            total_atendimentos = len(lista_agendamentos)
            faturamento_total = sum(PRECOS_SERVICOS.get(ag["servico"], 0) for ag in lista_agendamentos)
            
            faturamento_bruno = sum(PRECOS_SERVICOS.get(ag["servico"], 0) for ag in lista_agendamentos if ag["profissional"] == "Bruno")
            faturamento_samuel = sum(PRECOS_SERVICOS.get(ag["servico"], 0) for ag in lista_agendamentos if ag["profissional"] == "Samuel")
            
            m1, m2 = st.columns(2)
            m1.metric("Faturamento Bruto Geral", f"R$ {faturamento_total:,.2f}")
            m2.metric("Total de Agendamentos", total_atendimentos)
            
            st.subheader("Desempenho por Profissional")
            c1, c2 = st.columns(2)
            c1.metric("Faturamento do Bruno", f"R$ {faturamento_bruno:,.2f}")
            c2.metric("Faturamento do Samuel", f"R$ {faturamento_samuel:,.2f}")
            
            st.subheader("Serviços Mais Procurados")
            contagem_servicos = {}
            for ag in lista_agendamentos:
                contagem_servicos[ag["servico"]] = contagem_servicos.get(ag["servico"], 0) + 1
            
            for serv, qtd in contagem_servicos.items():
                st.write(f"**{serv}**: {qtd} atendimentos")
                st.progress(min(qtd / total_atendimentos, 1.0))
                
    elif senha != "":
        st.error("❌ Senha incorreta! Digite novamente.")
