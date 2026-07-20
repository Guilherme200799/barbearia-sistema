import streamlit as st
from datetime import datetime, timedelta, time
import json
import os

# Configuração da página - Otimizada para Celulares e Computadores
st.set_page_config(page_title="Barbearia do Bruno", page_icon="💈", layout="centered")

ARQUIVO_BANCO = "agendamentos_barbearia.json"

def carregar_agendamentos():
    if not os.path.exists(ARQUIVO_BANCO):
        return []
    try:
        with open(ARQUIVO_BANCO, "r", encoding="utf-8") as f:
            dados = json.load(f)
            # Converte as strings de volta para objetos datetime
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

# Estilização para celulares
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab"] { font-size: 16px; padding: 10px; }
    button[data-testid="baseButton-secondary"] { width: 100%; height: 50px; }
    </style>
""", unsafe_allow_html=True)

st.title("💈 Barbearia Preto e Branco")
st.subheader("Agende seu horário")

aba1, aba2, aba3 = st.tabs(["📅 Agendar Horário", "📋 Horários Marcados", "❌ Cancelar Horário"])

# --- ABA 1: NOVO AGENDAMENTO ---
with aba1:
    st.header("Marcar Horário")
    lista_agendamentos = carregar_agendamentos()
    
    with st.form("form_agendamento", clear_on_submit=True):
        cliente = st.text_input("Nome do Cliente:").strip()
        servico = st.selectbox("Serviço:", ["Cabelo", "Barba", "Combo (Cabelo + Barba)", "Sobrancelha"])
        profissional = st.radio("Profissional:", ["Bruno", "Samuel"], horizontal=True)
        
        hoje = datetime.today()
        dias_semana_pt = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
        
        opcoes_datas = []
        for i in range(30):
            futuro = hoje + timedelta(days=i)
            if futuro.weekday() != 6:
                texto_data = f"{futuro.strftime('%d/%m/%Y')} ({dias_semana_pt[futuro.weekday()]})"
                opcoes_datas.append((futuro.date(), texto_data))
        
        data_selecionada = st.selectbox("Escolha a Data:", opcoes_datas, format_func=lambda x: x[1])
        data_atendimento = data_selecionada[0]
        
        dia_semana_selecionado = data_atendimento.weekday()
        horarios_todos = []
        inicio_expediente = datetime.combine(datetime.today(), time(8, 0))
        
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
        
        horarios_disponiveis = []
        for h in horarios_todos:
            dt_verificar = datetime.combine(data_atendimento, h)
            ocupado = any(ag["profissional"] == profissional and ag["data_hora"] == dt_verificar for ag in lista_agendamentos)
            if not ocupado:
                horarios_disponiveis.append(h)
        
        if horarios_disponiveis:
            hora_atendimento = st.selectbox("Horário Disponível:", horarios_disponiveis, format_func=lambda x: x.strftime("%H:%M"))
            botao_agendar = st.form_submit_button("Confirmar Agendamento", use_container_width=True)
        else:
            st.warning("⚠️ Todos os horários para este profissional nesta data já estão preenchidos!")
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
                    "profissional": profesional if 'profesional' in locals() else profissional,
                    "data_hora": dt_completo
                })
                lista_agendamentos.sort(key=lambda x: x["data_hora"])
                salvar_agendamentos(lista_agendamentos)
                st.success(f"🎉 Agendamento realizado para {cliente}!")
                st.rerun()
            else:
                st.error("Este horário já foi preenchido.")

# --- ABA 2: VISUALIZAR AGENDA ---
with aba2:
    st.header("Próximos Clientes")
    lista_agendamentos = carregar_agendamentos()
    
    if not lista_agendamentos:
        st.info("Nenhum agendamento marcado no momento.")
    else:
        dados_tabela = []
        for ag in lista_agendamentos:
            dados_tabela.append({
                "Data": ag["data_hora"].strftime("%d/%m/%Y"),
                "Horário": ag["data_hora"].strftime("%H:%M"),
                "Cliente": ag["cliente"],
                "Profissional": ag["profissional"],
                "Serviço": ag["servico"]
            })
        st.dataframe(dados_tabela, use_container_width=True)

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
