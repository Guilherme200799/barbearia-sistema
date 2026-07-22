import streamlit as st
from supabase import create_client, Client
from datetime import datetime, date, time

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Barbearia Preto & Branco",
    page_icon="💈",
    layout="centered"
)

# --- CONEXÃO COM O SUPABASE ---
# As chaves são lidas automaticamente doSecrets do Streamlit
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error("Erro ao carregar as credenciais do Supabase. Verifique a aba Secrets no Streamlit Cloud.")

# --- FUNÇÕES DE BANCO DE DADOS ---
def carregar_agendamentos():
    """Busca todos os agendamentos registrados no Supabase."""
    try:
        response = supabase.table("agendamentos").select("*").order("data_hora").execute()
        return response.data
    except Exception as e:
        st.error(f"Erro ao carregar agendamentos: {e}")
        return []

def salvar_novo_agendamento(cliente, telefone, servico, profissional, data_hora_str):
    """Insere um novo agendamento na tabela do Supabase."""
    try:
        dados = {
            "cliente": cliente,
            "telefone": telefone,
            "servico": servico,
            "profissional": profissional,
            "data_hora": data_hora_str
        }
        supabase.table("agendamentos").insert(dados).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao salvar agendamento: {e}")
        return False

def deletar_agendamento(id_agendamento):
    """Remove um agendamento pelo ID."""
    try:
        supabase.table("agendamentos").delete().eq("id", id_agendamento).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao cancelar agendamento: {e}")
        return False

# --- CABEÇALHO BARBEARIA PRETO & BRANCO ---
st.markdown("""
    <style>
        .header-barber {
            text-align: center;
            padding: 20px 0;
            border-bottom: 2px solid #333;
            margin-bottom: 25px;
        }
        .header-tag {
            font-size: 14px;
            letter-spacing: 2px;
            color: #888;
            font-weight: bold;
            text-transform: uppercase;
        }
        .header-title {
            font-size: 32px;
            font-weight: 800;
            margin: 10px 0;
        }
        .header-subtitle {
            font-size: 16px;
            color: #aaa;
        }
    </style>
    
    <div class="header-barber">
        <div class="header-tag">• BARBERSHOP •</div>
        <h1 class="header-title">💈 BARBEARIA 💈 PRETO & BRANCO</h1>
        <div class="header-subtitle">Agendamento Online & Gestão Integrada</div>
    </div>
""", unsafe_allow_html=True)

# --- ABAS DA APLICAÇÃO ---
tab_agendar, tab_painel = st.tabs(["📅 Novo Agendamento", "📊 Painel de Gestão"])

# --- ABA 1: NOVO AGENDAMENTO ---
with tab_agendar:
    st.subheader("Faça seu Agendamento")
    
    with st.form("form_agendamento", clear_on_submit=True):
        nome_cliente = st.text_input("Nome Completo:*")
        telefone_cliente = st.text_input("Telefone / WhatsApp:*", placeholder="(31) 99999-9999")
        
        col1, col2 = st.columns(2)
        with col1:
            servico = st.selectbox(
                "Serviço:*",
                ["Corte Cabelo", "Barba Completa", "Corte + Barba", "Acabamento / Pezinho", "Pintura / Nevou"]
            )
        with col2:
            profissional = st.selectbox(
                "Profissional:*",
                ["Qualquer Profissional", "Barbeiro 1", "Barbeiro 2"]
            )
            
        col3, col4 = st.columns(2)
        with col3:
            data_agendamento = st.date_input("Data:*", min_value=date.today())
        with col4:
            horario_agendamento = st.time_input("Horário:*", value=time(9, 0))

        submeter = st.form_submit_button("Confirmar Agendamento 💈")

        if submeter:
            if not nome_cliente.strip() or not telefone_cliente.strip():
                st.warning("Por favor, preencha o seu nome e telefone.")
            else:
                data_hora_formatada = f"{data_agendamento.strftime('%d/%m/%Y')} às {horario_agendamento.strftime('%H:%M')}"
                
                sucesso = salvar_novo_agendamento(
                    cliente=nome_cliente,
                    telefone=telefone_cliente,
                    servico=servico,
                    profissional=profissional,
                    data_hora=data_hora_formatada
                )
                
                if sucesso:
                    st.success(f"✅ Agendamento de **{nome_cliente}** realizado para **{data_hora_formatada}** com sucesso!")

# --- ABA 2: PAINEL DE GESTÃO ---
with tab_painel:
    st.subheader("Agendamentos Confirmados")
    
    # Carrega agendamentos atualizados do banco
    lista_agendamentos = carregar_agendamentos()

    if not lista_agendamentos:
        st.info("Nenhum agendamento cadastrado até o momento.")
    else:
        st.write(f"Total de agendamentos registrados: **{len(lista_agendamentos)}**")
        st.divider()

        for item in lista_agendamentos:
            with st.expander(f"📌 {item.get('cliente')} — {item.get('data_hora')}"):
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.write(f"**Telefone:** {item.get('telefone')}")
                    st.write(f"**Serviço:** {item.get('servico')}")
                    st.write(f"**Profissional:** {item.get('profissional')}")
                with c2:
                    if st.button("Cancelar", key=f"btn_del_{item.get('id')}"):
                        if deletar_agendamento(item.get('id')):
                            st.success("Cancelado!")
                            st.rerun()
