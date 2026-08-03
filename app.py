import time
import urllib.parse
from datetime import datetime, timedelta
from datetime import time as dt_time

import streamlit as st
from supabase import create_client

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Barbearia Preto & Branco",
    page_icon="💈",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# --- CONEXÃO COM O SUPABASE ---
@st.cache_resource
def init_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


try:
    supabase = init_supabase()
except Exception as e:
    st.error("Erro ao conectar ao Supabase. Verifique suas chaves no secrets.toml.")
    st.stop()

# --- DADOS DO NEGÓCIO ---
SERVICOS_INFO = {
    "Cabelo": {"preco": 30.0, "icon": "✂️", "desc": "Corte moderno ou tradicional"},
    "Barba": {"preco": 25.0, "icon": "🧔", "desc": "Modelagem e toalha quente"},
    "Combo (Cabelo + Barba)": {"preco": 55.0, "icon": "👑", "desc": "O pacote completo VIP"},
    "Sobrancelha": {"preco": 10.0, "icon": "📐", "desc": "Design e alinhamento"},
}

CONTATO_BRUNO = "5531985271355"
CONTATO_SAMUEL = "5531985271355"
ENDERECO_BARBEARIA = "R. dos Toureiros, 62 - Juliana"


# --- FUNÇÕES DO BANCO DE DADOS ---
def carregar_agendamentos():
    try:
        response = (
            supabase.table("agendamentos")
            .select("*")
            .order("data_hora")
            .execute()
        )
        dados = response.data
        for ag in dados:
            ag["data_hora"] = datetime.fromisoformat(
                ag["data_hora"].replace("Z", "+00:00")
            ).replace(tzinfo=None)
        return dados
    except Exception as e:
        st.error(f"Erro ao carregar agendamentos: {e}")
        return []


def salvar_agendamento(cliente, telefone, servico, profissional, data_hora):
    try:
        dados = {
            "cliente": cliente,
            "telefone": telefone,
            "servico": servico,
            "profissional": profissional,
            "data_hora": data_hora.strftime("%Y-%m-%d %H:%M:%S"),
        }
        supabase.table("agendamentos").insert(dados).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao salvar agendamento: {e}")
        return False


def deletar_agendamento(ag_id):
    try:
        id_query = int(ag_id) if str(ag_id).isdigit() else str(ag_id)
        supabase.table("agendamentos").delete().eq("id", id_query).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao cancelar agendamento: {e}")
        return False


def atualizar_agendamento(ag_id, nova_data_hora):
    try:
        data_iso = nova_data_hora.strftime("%Y-%m-%d %H:%M:%S")
        res_busca = supabase.table("agendamentos").select("*").eq("id", ag_id).execute()
        
        if not res_busca.data:
            id_num = int(ag_id) if str(ag_id).isdigit() else ag_id
            res_busca = supabase.table("agendamentos").select("*").eq("id", id_num).execute()

        if not res_busca.data:
            st.error("Agendamento não localizado.")
            return False

        ag_atual = res_busca.data[0]
        id_query = ag_atual["id"]

        resposta = (
            supabase.table("agendamentos")
            .update({"data_hora": data_iso})
            .eq("id", id_query)
            .execute()
        )

        if resposta.data and len(resposta.data) > 0:
            return True

        supabase.table("agendamentos").delete().eq("id", id_query).execute()
        dados_novos = {
            "cliente": ag_atual["cliente"],
            "telefone": ag_atual["telefone"],
            "servico": ag_atual["servico"],
            "profissional": ag_atual["profissional"],
            "data_hora": data_iso,
        }
        ins_res = supabase.table("agendamentos").insert(dados_novos).execute()
        return bool(ins_res.data)
    except Exception as e:
        st.error(f"Erro ao remarcar: {e}")
        return False


# --- ESTILO DARK PREMIUM ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Oswald:wght@600;700&display=swap');
    
    /* Fundo Escuro Mineral */
    .stApp {
        background-color: #0d0e12 !important;
        color: #f3f4f6 !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    #MainMenu, footer { visibility: hidden; }

    /* Cabeçalho VIP */
    .header-barber {
        text-align: center;
        padding: 28px 16px;
        margin-bottom: 24px;
        background: linear-gradient(180deg, #16181d 0%, #0d0e12 100%);
        border: 1px solid #272a30;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    }
    .header-tag {
        font-size: 0.75rem;
        letter-spacing: 5px;
        font-weight: 800;
        color: #d4af37;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    .header-title {
        font-family: 'Oswald', sans-serif !important;
        font-size: 2.8rem !important;
        font-weight: 700 !important;
        letter-spacing: 4px !important;
        color: #ffffff !important;
        margin: 0 !important;
        text-transform: uppercase;
    }
    .header-subtitle {
        font-size: 0.82rem;
        font-weight: 500;
        color: #9ca3af;
        margin-top: 8px;
        letter-spacing: 2px;
    }

    /* Estilização das Abas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #16181d !important;
        padding: 8px;
        border-radius: 14px;
        border: 1px solid #272a30 !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #9ca3af !important;
        background-color: transparent !important;
        border-radius: 10px !important;
        padding: 10px 16px !important;
        font-size: 0.88rem !important;
        font-weight: 700 !important;
        border: none !important;
    }
    
    .stTabs [aria-selected="true"] {
        color: #0d0e12 !important;
        background-color: #d4af37 !important;
        box-shadow: 0px 4px 15px rgba(212, 175, 55, 0.3) !important;
    }

    /* Cards e Containers */
    .card-dark {
        background-color: #16181d !important;
        border: 1px solid #272a30 !important;
        padding: 20px;
        border-radius: 16px;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    }

    .ticket-card {
        background: linear-gradient(135deg, #1c1f26 0%, #16181d 100%);
        border: 1px solid #d4af37;
        padding: 20px;
        border-radius: 16px;
        text-align: center;
        margin-top: 15px;
    }

    /* Botão WhatsApp */
    .btn-whatsapp {
        display: inline-block;
        background-color: #25d366;
        color: #000000 !important;
        font-weight: 800;
        padding: 12px 28px;
        border-radius: 10px;
        text-decoration: none;
        margin-top: 12px;
        box-shadow: 0 4px 15px rgba(37, 211, 102, 0.3);
    }

    /* Inputs e Selects */
    div[data-baseweb="input"] > div, 
    div[data-baseweb="select"] > div {
        background-color: #16181d !important;
        border: 1px solid #272a30 !important;
        color: #ffffff !important;
        border-radius: 10px !important;
    }

    label {
        color: #d1d5db !important;
        font-weight: 600 !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- CABEÇALHO ---
st.markdown(
    """
    <div class="header-barber">
        <div class="header-tag">• EXPERIENCE VIP •</div>
        <h1 class="header-title">PRETO & BRANCO</h1>
        <div class="header-subtitle">BARBEARIA & CLUB</div>
    </div>
""",
    unsafe_allow_html=True,
)

# --- ESTRUTURA DE ABAS ---
aba1, aba2, aba3, aba4, aba5 = st.tabs(
    [
        "📅 Agendar",
        "🔄 Meus Horários",
        "📋 Agenda",
        "❌ Cancelar",
        "📊 Admin",
    ]
)

if "hora_selecionada" not in st.session_state:
    st.session_state.hora_selecionada = None

if "tel_busca" not in st.session_state:
    st.session_state.tel_busca = ""

# ==============================================================================
# ABA 1: AGENDAR
# ==============================================================================
with aba1:
    st.markdown(
        """
        <div class="card-dark">
            <span style="color: #d4af37;">📍 <b>Localização:</b></span> R. dos Toureiros, 62 - Juliana<br>
            <span style="color: #d4af37;">💬 <b>Atendimento:</b></span> Bruno & Samuel (31) 98527-1355
        </div>
        """,
        unsafe_allow_html=True,
    )

    lista_agendamentos = carregar_agendamentos()

    **Passo 1: Seus Dados**
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        cliente = st.text_input("Seu Nome:", key="input_cliente", placeholder="Ex: João Silva").strip()
    with col_c2:
        telefone = st.text_input("WhatsApp:", key="input_telefone", placeholder="Ex: 31985271355").strip()

    st.write("")
    **Passo 2: Escolha o Serviço & Barbeiro**
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        servico = st.selectbox(
            "Serviço Desejado:",
            list(SERVICOS_INFO.keys()),
            format_func=lambda x: f"{SERVICOS_INFO[x]['icon']} {x} - R$ {SERVICOS_INFO[x]['preco']:.2f}",
            key="select_servico",
        )
    with col_s2:
        profissional = st.radio("Profissional:", ["Bruno", "Samuel"], horizontal=True, key="radio_prof")

    st.write("")
    **Passo 3: Data & Horário**
    hoje_dt = datetime.utcnow() - timedelta(hours=3)

    data_atendimento = st.date_input(
        "Selecione o Dia:",
        value=hoje_dt.date(),
        min_value=hoje_dt.date(),
        max_value=hoje_dt.date() + timedelta(days=30),
        format="DD/MM/YYYY",
        key="date_picker_agendar",
    )

    if data_atendimento.weekday() == 6:
        st.warning("⚠️ Fechado aos domingos. Selecione outro dia.")
        horarios_disponiveis = []
    else:
        dia_semana_selecionado = data_atendimento.weekday()
        minutos_inicio = 480
        minutos_fim = 1020 if dia_semana_selecionado == 5 else 1080

        horarios_todos = []
        minutos_atual = minutos_inicio
        while minutos_atual <= minutos_fim:
            horarios_todos.append(dt_time(minutos_atual // 60, minutos_atual % 60))
            minutos_atual += 40

        horarios_disponiveis = []
        for h in horarios_todos:
            dt_verificar = datetime.combine(data_atendimento, h)
            if data_atendimento == hoje_dt.date() and h < hoje_dt.time():
                continue

            ocupado = any(
                ag["profissional"] == profissional and ag["data_hora"] == dt_verificar
                for ag in lista_agendamentos
            )
            if not ocupado:
                horarios_disponiveis.append(h)

    if data_atendimento.weekday() != 6:
        if horarios_disponiveis:
            horarios_disponiveis.sort()
            tamanho_bloco = 4
            for i in range(0, len(horarios_disponiveis), tamanho_bloco):
                grupo = horarios_disponiveis[i : i + tamanho_bloco]
                cols = st.columns(len(grupo))
                for j, hr in enumerate(grupo):
                    hr_str = hr.strftime("%H:%M")
                    is_selected = st.session_state.hora_selecionada == hr
                    btn_type = "primary" if is_selected else "secondary"
                    btn_label = f"✓ {hr_str}" if is_selected else hr_str

                    if cols[j].button(btn_label, key=f"chip_hr_{hr_str}", use_container_width=True, type=btn_type):
                        st.session_state.hora_selecionada = hr
                        st.rerun()
        else:
            st.warning("Nenhum horário livre nesta data.")

    st.write("---")
    hora_atendimento = st.session_state.hora_selecionada

    if hora_atendimento and data_atendimento.weekday() != 6:
        st.success(f"Horário Selecionado: **{hora_atendimento.strftime('%H:%M')}**")
        botao_agendar = st.button("👑 Finalizar Agendamento", use_container_width=True, type="primary")
    else:
        st.caption("Escolha um horário acima para confirmar.")
        botao_agendar = False

    if botao_agendar:
        if not cliente or not telefone:
            st.error("Preencha seu Nome e WhatsApp para continuar.")
        else:
            dt_completo = datetime.combine(data_atendimento, hora_atendimento)
            tel_limpo = "".join(filter(str.isdigit, telefone))
            if len(tel_limpo) == 9: tel_limpo = "5531" + tel_limpo
            elif len(tel_limpo) == 11: tel_limpo = "55" + tel_limpo
            elif not tel_limpo.startswith("55") and len(tel_limpo) >= 10: tel_limpo = "55" + tel_limpo

            if salvar_agendamento(cliente, tel_limpo, servico, profissional, dt_completo):
                data_f = data_atendimento.strftime("%d/%m/%Y")
                hora_f = hora_atendimento.strftime("%H:%M")
                preco_f = SERVICOS_INFO[servico]["preco"]

                texto_msg = (
                    f"Olá! Confirmo meu agendamento na Barbearia Preto & Branco:\n\n"
                    f"👤 *Cliente:* {cliente}\n"
                    f"💈 *Serviço:* {servico} (R$ {preco_f:.2f})\n"
                    f"🧔 *Barbeiro:* {profissional}\n"
                    f"📅 *Data:* {data_f} às {hora_f}\n\n"
                    f"📍 *Endereço:* {ENDERECO_BARBEARIA}"
                )

                num_barbeiro = CONTATO_BRUNO if profissional == "Bruno" else CONTATO_SAMUEL
                link_wa = f"https://wa.me/{num_barbeiro}?text={urllib.parse.quote(texto_msg)}"

                st.session_state.hora_selecionada = None

                st.markdown(
                    f"""
                <div class="ticket-card">
                    <h3 style="color: #d4af37; margin:0 0 10px 0;">AGENDAMENTO CONFIRMADO!</h3>
                    <p style="margin: 4px 0;"><b>{cliente}</b> • {servico}</p>
                    <p style="margin: 4px 0; color: #9ca3af;">📅 {data_f} às {hora_f} com {profissional}</p>
                    <a href="{link_wa}" target="_blank" class="btn-whatsapp">
                        📲 Enviar no WhatsApp
                    </a>
                </div>
                """,
                    unsafe_allow_html=True,
                )

# ==============================================================================
# ABA 2: MEUS HORÁRIOS
# ==============================================================================
with aba2:
    st.subheader("Consultar Meus Horários")
    col_input, col_btn = st.columns([3, 1], vertical_alignment="bottom")

    with col_input:
        val_input = st.text_input("Seu WhatsApp:", value=st.session_state.tel_busca, placeholder="31985271355", key="input_consulta_cli").strip()
    with col_btn:
        if st.button("🔍 Buscar", key="btn_buscar_agendamentos", type="primary", use_container_width=True):
            st.session_state.tel_busca = val_input
            st.rerun()

    tel_consulta = st.session_state.tel_busca if st.session_state.tel_busca else val_input

    if tel_consulta:
        tel_limpo = "".join(filter(str.isdigit, tel_consulta))
        lista_agendamentos = carregar_agendamentos()

        meus_agendamentos = [
            ag for ag in lista_agendamentos
            if tel_limpo in str(ag.get("telefone", ""))
            and ag["data_hora"] >= (datetime.utcnow() - timedelta(hours=3))
        ]

        if meus_agendamentos:
            for ag in meus_agendamentos:
                ag_id = ag.get("id")
                data_f = ag["data_hora"].strftime("%d/%m/%Y")
                hora_f = ag["data_hora"].strftime("%H:%M")
                prof_ag = ag["profissional"]

                with st.expander(f"💈 {ag['servico']} com {prof_ag} - 📅 {data_f} às {hora_f}", expanded=True):
                    col_del, col_rem = st.columns(2)
                    with col_del:
                        if st.button("❌ Cancelar", key=f"cli_del_{ag_id}", use_container_width=True):
                            if deletar_agendamento(ag_id):
                                st.cache_data.clear()
                                st.success("Cancelado com sucesso!")
                                time.sleep(0.8)
                                st.rerun()

                    with col_rem:
                        with st.popover("🔄 Remarcar", use_container_width=True):
                            hoje_dt_rem = datetime.utcnow() - timedelta(hours=3)
                            nova_data = st.date_input("Nova Data:", value=ag["data_hora"].date(), min_value=hoje_dt_rem.date(), key=f"d_rem_{ag_id}", format="DD/MM/YYYY")

                            if nova_data.weekday() == 6:
                                st.warning("Fechado aos domingos.")
                            else:
                                dia_s = nova_data.weekday()
                                min_i = 480
                                min_f = 1020 if dia_s == 5 else 1080
                                hor_totais = [dt_time(c // 60, c % 60) for c in range(min_i, min_f + 1, 40)]

                                hor_livres = []
                                for h in hor_totais:
                                    dt_v = datetime.combine(nova_data, h)
                                    if nova_data == hoje_dt_rem.date() and h < hoje_dt_rem.time(): continue
                                    if dt_v == ag["data_hora"] or not any(x["profissional"] == prof_ag and x["data_hora"] == dt_v for x in lista_agendamentos):
                                        hor_livres.append(h.strftime("%H:%M"))

                                if hor_livres:
                                    nova_hora_str = st.selectbox("Novo Horário:", hor_livres, key=f"h_rem_{ag_id}")
                                    if st.button("Confirmar", key=f"btn_rem_{ag_id}", type="primary"):
                                        h_p, m_p = map(int, nova_hora_str.split(":"))
                                        if atualizar_agendamento(ag_id, datetime.combine(nova_data, dt_time(h_p, m_p))):
                                            st.cache_data.clear()
                                            st.success("Remarcado!")
                                            time.sleep(1)
                                            st.rerun()
        else:
            st.info("Nenhum agendamento futuro localizado.")

# ==============================================================================
# ABA 3: AGENDA BARBEIROS
# ==============================================================================
with aba3:
    st.subheader("Agenda do Dia")
    lista_agendamentos = carregar_agendamentos()
    hoje_dt = datetime.utcnow() - timedelta(hours=3)

    data_consulta_sel = st.date_input("Filtrar Data:", hoje_dt.date(), format="DD/MM/YYYY", key="date_picker_agenda")
    ag_filtrados = [ag for ag in lista_agendamentos if ag["data_hora"].date() == data_consulta_sel]

    col_b, col_s = st.columns(2)
    with col_b:
        st.markdown("### 🧔 Bruno")
        ag_bruno = sorted([ag for ag in ag_filtrados if ag.get("profissional") == "Bruno"], key=lambda x: x["data_hora"])
        for ag in ag_bruno:
            st.markdown(f'<div class="card-dark" style="border-left: 3px solid #d4af37 !important;"><b>{ag["data_hora"].strftime("%H:%M")}</b> - {ag["cliente"]}<br><small style="color:#9ca3af">{ag["servico"]}</small></div>', unsafe_allow_html=True)
        if not ag_bruno: st.caption("Nenhum horário ocupado.")

    with col_s:
        st.markdown("### 🧔 Samuel")
        ag_samuel = sorted([ag for ag in ag_filtrados if ag.get("profissional") == "Samuel"], key=lambda x: x["data_hora"])
        for ag in ag_samuel:
            st.markdown(f'<div class="card-dark" style="border-left: 3px solid #d4af37 !important;"><b>{ag["data_hora"].strftime("%H:%M")}</b> - {ag["cliente"]}<br><small style="color:#9ca3af">{ag["servico"]}</small></div>', unsafe_allow_html=True)
        if not ag_samuel: st.caption("Nenhum horário ocupado.")

# ==============================================================================
# ABA 4: CANCELAR
# ==============================================================================
with aba4:
    st.subheader("Painel de Cancelamentos")
    lista_agendamentos = carregar_agendamentos()

    for ag in lista_agendamentos:
        data_str = ag["data_hora"].strftime("%d/%m/%Y às %H:%M")
        ag_id = ag.get("id")

        col_i, col_b = st.columns([3, 1])
        with col_i:
            st.markdown(f"**{ag['cliente']}** ({ag['profissional']})<br><small style='color:#9ca3af'>{ag['servico']} • {data_str}</small>", unsafe_allow_html=True)
        with col_b:
            if st.button("🗑️ Excluir", key=f"del_adm_{ag_id}", use_container_width=True):
                if deletar_agendamento(ag_id):
                    st.cache_data.clear()
                    st.rerun()
        st.divider()

# ==============================================================================
# ABA 5: ADMIN
# ==============================================================================
with aba5:
    st.subheader("🔒 Acesso Restrito")

    with st.form(key="form_login_admin"):
        col_p, col_b = st.columns([3, 1], vertical_alignment="bottom")
        with col_p:
            senha = st.text_input("Senha:", type="password", key="input_senha")
        with col_b:
            st.form_submit_button("Entrar", type="primary", use_container_width=True)

    if senha == "admin123":
        st.success("Acesso Liberado")
        lista_agendamentos = carregar_agendamentos()

        if lista_agendamentos:
            faturamento_total = sum(SERVICOS_INFO.get(ag.get("servico", ""), {}).get("preco", 0.0) for ag in lista_agendamentos)
            
            m1, m2 = st.columns(2)
            with m1: st.metric("Atendimentos Totais", len(lista_agendamentos))
            with m2: st.metric("Faturamento Estimado", f"R$ {faturamento_total:.2f}")

            st.write("---")
            st.dataframe(
                [
                    {
                        "Cliente": ag.get("cliente"),
                        "Telefone": ag.get("telefone"),
                        "Serviço": ag.get("servico"),
                        "Barbeiro": ag.get("profissional"),
                        "Data/Hora": ag["data_hora"].strftime("%d/%m/%Y %H:%M"),
                    }
                    for ag in lista_agendamentos
                ],
                use_container_width=True,
            )
