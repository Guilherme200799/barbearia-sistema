import locale
import time
import urllib.parse
from datetime import datetime, timedelta
from datetime import time as dt_time

import requests
import streamlit as st
from supabase import create_client

# Configuração da página
st.set_page_config(
    page_title="Barbearia Preto & Branco", page_icon="💈", layout="centered"
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
    st.error(
        "Erro ao conectar ao Supabase. Verifique suas chaves no secrets.toml."
    )
    st.stop()

# --- CONFIGURAÇÃO DE SERVIÇOS E PREÇOS ---
PRECOS_SERVICOS = {
    "Cabelo": 30.0,
    "Barba": 25.0,
    "Combo (Cabelo + Barba)": 55.0,
    "Sobrancelha": 10.0,
}

CONTATO_BRUNO = "5531985271355"
CONTATO_SAMUEL = "5531985271355"
ENDERECO_BARBEARIA = "R. dos Toureiros, 62 - Juliana"


# --- FUNÇÕES DO BANCO DE DADOS (SUPABASE) ---
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
        st.error(f"Erro ao carregar agendamentos do banco: {e}")
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
        st.error(f"Erro ao salvar no banco de dados: {e}")
        return False


def deletar_agendamento(ag_id):
    try:
        try:
            id_query = int(ag_id)
        except (ValueError, TypeError):
            id_query = str(ag_id)

        supabase.table("agendamentos").delete().eq("id", id_query).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao cancelar agendamento: {e}")
        return False


def atualizar_agendamento(ag_id, nova_data_hora):
    try:
        data_iso = nova_data_hora.strftime("%Y-%m-%d %H:%M:%S")

        # 1. Tenta recuperar os dados do agendamento atual antes da alteração
        res_busca = supabase.table("agendamentos").select("*").eq("id", ag_id).execute()
        if not res_busca.data:
            # Tenta com ID em formato numérico/string se não achar de primeira
            id_num = int(ag_id) if str(ag_id).isdigit() else ag_id
            res_busca = supabase.table("agendamentos").select("*").eq("id", id_num).execute()

        if not res_busca.data:
            st.error(f"O agendamento ID {ag_id} não foi localizado no Supabase.")
            return False

        ag_atual = res_busca.data[0]

        # 2. Tenta fazer o UPDATE direto
        id_query = ag_atual["id"]
        resposta = (
            supabase.table("agendamentos")
            .update({"data_hora": data_iso})
            .eq("id", id_query)
            .execute()
        )

        if resposta.data and len(resposta.data) > 0:
            return True

        # 3. Fallback: Se o RLS/permissão do Supabase bloqueou o UPDATE direto,
        # deletamos o registro antigo e inserimos o novo com a data atualizada
        del_res = supabase.table("agendamentos").delete().eq("id", id_query).execute()

        dados_novos = {
            "cliente": ag_atual["cliente"],
            "telefone": ag_atual["telefone"],
            "servico": ag_atual["servico"],
            "profissional": ag_atual["profissional"],
            "data_hora": data_iso,
        }
        ins_res = supabase.table("agendamentos").insert(dados_novos).execute()

        if ins_res.data and len(ins_res.data) > 0:
            return True
        else:
            st.error("Não foi possível salvar o novo horário no banco de dados.")
            return False

    except Exception as e:
        st.error(f"Erro ao remarcar horário no banco de dados: {e}")
        return False


# --- ESTILOS CSS PERSONALIZADOS ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700;900&family=Oswald:wght@500;700&display=swap');
    
    /* Fundo escuro geral do App */
    [data-testid="stAppViewContainer"] {
        background-color: #0f0f10 !important;
        color: #e0e0e0 !important;
        font-family: 'Montserrat', sans-serif !important;
    }

    [data-testid="stHeader"] {
        background-color: rgba(15, 15, 16, 0.8) !important;
    }

    /* Oculta menus indesejados do Streamlit */
    #MainMenu, footer { visibility: hidden; }

    /* Cabeçalho no estilo Barbershop */
    .header-barber {
        text-align: center;
        padding: 25px 15px;
        margin-bottom: 25px;
        background: linear-gradient(180deg, #18181b 0%, #0f0f10 100%);
        border: 1px solid #27272a;
        border-radius: 16px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
    }
    .header-tag {
        font-size: 0.8rem;
        letter-spacing: 6px;
        font-weight: 700;
        color: #23a55a;
        text-transform: uppercase;
        margin-bottom: 6px;
    }
    .header-title {
        font-family: 'Oswald', sans-serif !important;
        font-size: 2.8rem !important;
        font-weight: 700 !important;
        letter-spacing: 4px !important;
        color: #ffffff !important;
        margin: 0 !important;
        line-height: 1.1 !important;
        text-transform: uppercase;
        text-shadow: 0 2px 10px rgba(0,0,0,0.5);
    }
    .header-subtitle {
        font-size: 0.82rem;
        font-weight: 600;
        color: #a1a1aa;
        margin-top: 10px;
        letter-spacing: 3px;
        text-transform: uppercase;
    }

    /* Estilização das Abas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #18181b !important;
        padding: 8px;
        border-radius: 12px;
        border: 1px solid #27272a !important;
    }
    .stTabs [data-baseweb="tab"] {
        color: #a1a1aa !important;
        background-color: transparent !important;
        border-radius: 8px !important;
        padding: 10px 16px !important;
        font-weight: 700 !important;
        border: none !important;
        transition: all 0.2s ease;
    }
    .stTabs [aria-selected="true"] {
        color: #ffffff !important;
        background-color: #27272a !important;
        box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.3) !important;
    }

    /* Cards Informativos e do Cliente */
    .client-card {
        background-color: #18181b !important;
        border: 1px solid #27272a !important;
        padding: 18px;
        border-radius: 12px;
        margin-bottom: 15px;
        color: #e4e4e7 !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }

    /* Customização dos Inputs e Selects */
    div[data-baseweb="input"] > div, 
    div[data-baseweb="select"] > div {
        background-color: #18181b !important;
        border: 1px solid #3f3f46 !important;
        color: #ffffff !important;
        border-radius: 8px !important;
    }
    
    input {
        color: #ffffff !important;
    }
    
    label {
        color: #e4e4e7 !important;
        font-weight: 600 !important;
    }

    /* Botões Secundários (Horários Livres) */
    button[kind="secondary"] {
        background-color: #18181b !important;
        color: #f4f4f5 !important;
        border: 1px solid #3f3f46 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease-in-out !important;
    }
    button[kind="secondary"]:hover {
        border-color: #23a55a !important;
        color: #23a55a !important;
        background-color: #27272a !important;
        transform: translateY(-1px);
    }

    /* Botões Primários (Confirmar / Selecionado) */
    button[kind="primary"] {
        background-color: #23a55a !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 14px rgba(35, 165, 90, 0.3) !important;
        transition: all 0.2s ease-in-out !important;
    }
    button[kind="primary"]:hover {
        background-color: #1f924f !important;
        transform: translateY(-1px);
        box-shadow: 0 6px 18px rgba(35, 165, 90, 0.4) !important;
    }

    /* Botão estilo WhatsApp */
    .whatsapp-btn {
        background-color: #23a55a !important;
        color: #ffffff !important;
        padding: 12px 24px;
        border-radius: 8px;
        font-weight: 700;
        text-decoration: none;
        font-size: 15px;
        display: inline-block;
        box-shadow: 0 4px 14px rgba(35, 165, 90, 0.3);
        transition: all 0.2s;
    }
    .whatsapp-btn:hover {
        background-color: #1f924f !important;
        transform: translateY(-1px);
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- CABEÇALHO ---
st.markdown(
    """
    <div class="header-barber">
        <div class="header-tag">•💈BARBEARIA💈•</div>
        <h1 class="header-title">• Preto & Branco •</h1>
        <div class="header-subtitle">Agendamento Online & Gestão Integrada</div>
    </div>
""",
    unsafe_allow_html=True,
)

# Estrutura de Abas
aba1, aba2, aba3, aba4, aba5 = st.tabs(
    [
        "📅 Agendar",
        "🔄 Meus Agendamentos",
        "📋 Horários Marcados",
        "❌ Cancelar Horário",
        "📊 Admin",
    ]
)

if "hora_selecionada" not in st.session_state:
    st.session_state.hora_selecionada = None

if "tel_busca" not in st.session_state:
    st.session_state.tel_busca = ""

# ==============================================================================
# ABA 1: AGENDAR (PÁGINA INICIAL)
# ==============================================================================
with aba1:
    st.markdown(
        """
        <div class="client-card" style="margin-bottom: 25px;">
            <p style="margin: 0 0 5px 0;">📍 <b>Endereço:</b> R. dos Toureiros, 62 - Juliana</p>
            <p style="margin: 0;">
                📞 <b>Contatos para Dúvidas:</b> 
                Bruno: <a href="https://wa.me/5531985271355" target="_blank" style="color: #23a55a; font-weight: bold; text-decoration: none;">(31) 98527-1355</a> | 
                Samuel: <a href="https://wa.me/5531985271355" target="_blank" style="color: #23a55a; font-weight: bold; text-decoration: none;">(31) 98527-1355</a>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("Preencha os dados para agendar")

    lista_agendamentos = carregar_agendamentos()

    col_c1, col_c2 = st.columns([2, 1])
    with col_c1:
        cliente = st.text_input(
            "Nome completo:",
            key="input_cliente",
            placeholder="Ex: João Silva",
        ).strip()
    with col_c2:
        telefone = st.text_input(
            "WhatsApp / Celular:",
            key="input_telefone",
            placeholder="Ex: 31985271355",
        ).strip()

    col_form1, col_form2 = st.columns(2)
    with col_form1:
        servico = st.selectbox(
            "Escolha o Serviço:",
            list(PRECOS_SERVICOS.keys()),
            key="select_servico",
        )
    with col_form2:
        profissional = st.radio(
            "Selecione o Profissional:",
            ["Bruno", "Samuel"],
            horizontal=True,
            key="radio_prof",
        )

    hoje_dt = datetime.utcnow() - timedelta(hours=3)

    data_atendimento = st.date_input(
        "Escolha a Data:",
        value=hoje_dt.date(),
        min_value=hoje_dt.date(),
        max_value=hoje_dt.date() + timedelta(days=30),
        format="DD/MM/YYYY",
        key="date_picker_agendar",
    )

    if data_atendimento.weekday() == 6:
        st.warning("⚠️ A barbearia não abre aos domingos. Por favor, escolha outra data.")
        horarios_disponiveis = []
    else:
        dia_semana_selecionado = data_atendimento.weekday()
        minutos_inicio = 480
        minutos_fim = 1020 if dia_semana_selecionado == 5 else 1080

        horarios_todos = []
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

            ocupado = any(
                ag["profissional"] == profissional
                and ag["data_hora"] == dt_verificar
                for ag in lista_agendamentos
            )
            if not ocupado:
                horarios_disponiveis.append(h)

    st.write("---")
    st.markdown("### ⏰ Selecione um Horário Disponível:")

    if data_atendimento.weekday() != 6:
        if horarios_disponiveis:
            horarios_disponiveis.sort()

            tamanho_bloco = 4
            for i in range(0, len(horarios_disponiveis), tamanho_bloco):
                grupo_horarios = horarios_disponiveis[i : i + tamanho_bloco]
                cols = st.columns(len(grupo_horarios))

                for j, hr in enumerate(grupo_horarios):
                    hr_str = hr.strftime("%H:%M")
                    is_selected = st.session_state.hora_selecionada == hr

                    btn_type = "primary" if is_selected else "secondary"
                    btn_label = f"✓ {hr_str}" if is_selected else hr_str

                    if cols[j].button(
                        btn_label,
                        key=f"chip_hr_{hr_str}",
                        use_container_width=True,
                        type=btn_type,
                    ):
                        st.session_state.hora_selecionada = hr
                        st.rerun()
        else:
            st.warning("⚠️ Não há horários disponíveis para esta data.")

    st.write("---")

    hora_atendimento = st.session_state.hora_selecionada
    if hora_atendimento and data_atendimento.weekday() != 6:
        st.info(f"Horário selecionado: **{hora_atendimento.strftime('%H:%M')}**")
        botao_agendar = st.button("Confirmar Agendamento", use_container_width=True, type="primary")
    else:
        st.caption("Clique em um dos horários acima para escolher.")
        botao_agendar = False

    if botao_agendar:
        if not cliente:
            st.error("Por favor, informe o seu nome completo.")
        elif not telefone:
            st.error("Por favor, informe o seu WhatsApp de contato.")
        else:
            dt_completo = datetime.combine(data_atendimento, hora_atendimento)

            tel_limpo = "".join(filter(str.isdigit, telefone))
            if len(tel_limpo) == 9:
                tel_limpo = "5531" + tel_limpo
            elif len(tel_limpo) == 11:
                tel_limpo = "55" + tel_limpo
            elif not tel_limpo.startswith("55") and len(tel_limpo) >= 10:
                tel_limpo = "55" + tel_limpo

            sucesso = salvar_agendamento(cliente, tel_limpo, servico, profissional, dt_completo)

            if sucesso:
                data_f = data_atendimento.strftime("%d/%m/%Y")
                hora_f = hora_atendimento.strftime("%H:%M")

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
                st.session_state.hora_selecionada = None

                st.markdown(
                    f"""
                <div style="background-color: var(--secondary-background-color); border: 2px solid #23a55a; padding: 20px; border-radius: 10px; text-align: center; margin-top: 15px; margin-bottom: 20px;">
                    <h4 style="margin: 0 0 8px 0; color: var(--text-color);">Quase lá! Notifique o barbeiro:</h4>
                    <a href="{link_wa}" target="_blank" class="whatsapp-btn">
                        📲 Enviar confirmação no WhatsApp
                    </a>
                </div>
                """,
                    unsafe_allow_html=True,
                )

# ==============================================================================
# ABA 2: REAGENDAMENTO / AUTONOMIA DO CLIENTE
# ==============================================================================
with aba2:
    st.subheader("Área do Cliente: Meus Agendamentos")
    st.write("Digite seu número de WhatsApp para ver, remarcar ou cancelar seus horários.")

    col_input, col_btn = st.columns([3, 1], vertical_alignment="bottom")

    with col_input:
        val_input = st.text_input(
            "Número do seu WhatsApp:",
            value=st.session_state.tel_busca,
            placeholder="Ex: 31985271355",
            key="input_consulta_cli",
        ).strip()

    with col_btn:
        if st.button("🔍 Buscar", key="btn_buscar_agendamentos", type="primary", use_container_width=True):
            st.session_state.tel_busca = val_input
            st.rerun()

    tel_consulta = st.session_state.tel_busca if st.session_state.tel_busca else val_input

    if tel_consulta:
        tel_limpo = "".join(filter(str.isdigit, tel_consulta))
        lista_agendamentos = carregar_agendamentos()

        meus_agendamentos = [
            ag
            for ag in lista_agendamentos
            if tel_limpo in str(ag.get("telefone", ""))
            and ag["data_hora"] >= (datetime.utcnow() - timedelta(hours=3))
        ]

        if meus_agendamentos:
            st.write(f"Encontrado(s) **{len(meus_agendamentos)}** agendamento(s):")
            for ag in meus_agendamentos:
                ag_id = ag.get("id")
                data_f = ag["data_hora"].strftime("%d/%m/%Y")
                hora_f = ag["data_hora"].strftime("%H:%M")
                prof_ag = ag["profissional"]

                with st.expander(
                    f"💈 {ag['servico']} com {prof_ag} - 📅 {data_f} às {hora_f}",
                    expanded=True,
                ):
                    st.write(f"**Cliente:** {ag['cliente']}")
                    st.write(f"**Barbeiro:** {prof_ag}")
                    st.write(f"**Data e Hora Atual:** {data_f} às {hora_f}")

                    col_cli_rem, col_cli_del = st.columns(2)

                    with col_cli_del:
                        if st.button("❌ Cancelar este horário", key=f"cli_del_{ag_id}", use_container_width=True):
                            if deletar_agendamento(ag_id):
                                st.cache_data.clear()
                                st.success("Agendamento cancelado com sucesso!")
                                time.sleep(0.8)
                                st.rerun()

                    with col_cli_rem:
                        with st.popover("🔄 Remarcar data/horário", use_container_width=True):
                            st.write("**Escolha a nova data e horário:**")

                            hoje_dt_rem = datetime.utcnow() - timedelta(hours=3)

                            nova_data = st.date_input(
                                "Nova Data:",
                                value=ag["data_hora"].date(),
                                min_value=hoje_dt_rem.date(),
                                max_value=hoje_dt_rem.date() + timedelta(days=30),
                                key=f"d_rem_{ag_id}",
                                format="DD/MM/YYYY",
                            )

                            if nova_data.weekday() == 6:
                                st.warning("⚠️ Não funcionamos aos domingos.")
                                nova_hora_str = None
                            else:
                                dia_s = nova_data.weekday()
                                min_i = 480
                                min_f = 1020 if dia_s == 5 else 1080

                                hor_totais = []
                                curr = min_i
                                while curr <= min_f:
                                    hor_totais.append(dt_time(curr // 60, curr % 60))
                                    curr += 40

                                hor_livres = []
                                for h in hor_totais:
                                    dt_v = datetime.combine(nova_data, h)

                                    if nova_data == hoje_dt_rem.date() and h < hoje_dt_rem.time():
                                        continue

                                    # Permite selecionar o próprio horário caso seja na mesma data/barbeiro
                                    if dt_v == ag["data_hora"]:
                                        hor_livres.append(h.strftime("%H:%M"))
                                        continue

                                    ocupado = any(
                                        x["profissional"] == prof_ag and x["data_hora"] == dt_v
                                        for x in lista_agendamentos
                                    )
                                    if not ocupado:
                                        hor_livres.append(h.strftime("%H:%M"))

                                if hor_livres:
                                    nova_hora_str = st.selectbox(
                                        "Novo Horário:",
                                        hor_livres,
                                        key=f"h_rem_{ag_id}",
                                    )
                                else:
                                    st.warning("Nenhum horário vago nesta data.")
                                    nova_hora_str = None

                            if nova_hora_str and st.button("Confirmar Alteração", key=f"btn_rem_{ag_id}", type="primary"):
                                h_p, m_p = map(int, nova_hora_str.split(":"))
                                nova_dt_comp = datetime.combine(nova_data, dt_time(h_p, m_p))

                                if atualizar_agendamento(ag_id, nova_dt_comp):
                                    st.cache_data.clear()
                                    st.success("Horário remarcado com sucesso!")
                                    time.sleep(1)
                                    st.rerun()
        else:
            st.info("Nenhum agendamento futuro encontrado para este WhatsApp.")

# ==============================================================================
# ABA 3: HORÁRIOS MARCADOS (AGENDA BARBEIRO)
# ==============================================================================
with aba3:
    st.subheader("Consultar Agenda dos Barbeiros")
    lista_agendamentos = carregar_agendamentos()

    hoje_dt = datetime.utcnow() - timedelta(hours=3)

    data_consulta_sel = st.date_input(
        "Filtrar por data:",
        hoje_dt.date(),
        format="DD/MM/YYYY",
        key="date_picker_agenda_barbeiros",
    )

    ag_filtrados = [
        ag for ag in lista_agendamentos if ag["data_hora"].date() == data_consulta_sel
    ]

    st.write("---")

    col_bruno, col_samuel = st.columns(2)

    with col_bruno:
        st.markdown("### 🧔 Bruno")
        ag_bruno = [ag for ag in ag_filtrados if ag.get("profissional") == "Bruno"]

        if ag_bruno:
            ag_bruno.sort(key=lambda x: x["data_hora"])
            for ag in ag_bruno:
                hora_str = ag["data_hora"].strftime("%H:%M")
                st.markdown(
                    f"""
                <div class="client-card" style="border-left: 4px solid #23a55a !important;">
                    <b>{ag['cliente']}</b> • {ag['servico']}<br>
                    <small>⏰ <b>{hora_str}</b> | 📱 {ag.get('telefone','')}</small>
                </div>
                """,
                    unsafe_allow_html=True,
                )
        else:
            st.info("Nenhum agendamento para o Bruno nesta data.")

    with col_samuel:
        st.markdown("### 🧔 Samuel")
        ag_samuel = [ag for ag in ag_filtrados if ag.get("profissional") == "Samuel"]

        if ag_samuel:
            ag_samuel.sort(key=lambda x: x["data_hora"])
            for ag in ag_samuel:
                hora_str = ag["data_hora"].strftime("%H:%M")
                st.markdown(
                    f"""
                <div class="client-card" style="border-left: 4px solid #23a55a !important;">
                    <b>{ag['cliente']}</b> • {ag['servico']}<br>
                    <small>⏰ <b>{hora_str}</b> | 📱 {ag.get('telefone','')}</small>
                </div>
                """,
                    unsafe_allow_html=True,
                )
        else:
            st.info("Nenhum agendamento para o Samuel nesta data.")

# ==============================================================================
# ABA 4: CANCELAR HORÁRIO (ADMINISTRATIVO / GERAL)
# ==============================================================================
with aba4:
    st.subheader("Painel de Cancelamento Geral")
    lista_agendamentos = carregar_agendamentos()

    if not lista_agendamentos:
        st.info("Sem agendamentos no banco.")
    else:
        for ag in lista_agendamentos:
            data_str = ag["data_hora"].strftime("%d/%m/%Y")
            hora_str = ag["data_hora"].strftime("%H:%M")
            ag_id = ag.get("id")

            col_info, col_btn = st.columns([3, 1])
            with col_info:
                st.markdown(
                    f"**{ag['cliente']}** - {ag['servico']} ({ag['profissional']})<br><small>📅 {data_str} às {hora_str}</small>",
                    unsafe_allow_html=True,
                )
            with col_btn:
                if st.button("🗑️ Excluir", key=f"del_adm_{ag_id}", use_container_width=True):
                    if deletar_agendamento(ag_id):
                        st.cache_data.clear()
                        st.success("Cancelado!")
                        time.sleep(0.5)
                        st.rerun()
            st.divider()

# ==============================================================================
# ABA 5: PAINEL ADMINISTRATIVO
# ==============================================================================
with aba5:
    st.subheader("🔒 Acesso Restrito - Gestão da Barbearia")

    with st.form(key="form_login_admin"):
        col_pass, col_btn_login = st.columns([3, 1], vertical_alignment="bottom")
        with col_pass:
            senha = st.text_input("Senha administrativa:", type="password", key="input_senha")
        with col_btn_login:
            btn_login = st.form_submit_button("🔓 Entrar", type="primary", use_container_width=True)

    if senha == "admin123":
        st.success("Painel do Administrador Autenticado")
        st.write("---")

        lista_agendamentos = carregar_agendamentos()

        if not lista_agendamentos:
            st.info("Nenhum dado cadastrado até o momento.")
        else:
            st.markdown("### 🔍 Filtros do Relatório")
            col_f1, col_f2 = st.columns(2)

            with col_f1:
                periodo_sel = st.selectbox(
                    "Filtrar por Período:",
                    [
                        "Todos",
                        "Hoje (Diário)",
                        "Últimos 7 dias (Semanal)",
                        "Mês Atual (Mensal)",
                        "Últimos 6 meses (Semestral)",
                        "Ano Atual (Anual)",
                    ],
                    key="filtro_periodo_admin",
                )

            with col_f2:
                barbeiro_sel = st.selectbox(
                    "Filtrar por Barbeiro:",
                    ["Todos os Barbeiros", "Bruno", "Samuel"],
                    key="filtro_barbeiro_admin",
                )

            hoje_dt = datetime.utcnow() - timedelta(hours=3)
            ag_filtrados = []

            for ag in lista_agendamentos:
                dt_ag = ag["data_hora"]

                passou_periodo = False
                if periodo_sel == "Todos":
                    passou_periodo = True
                elif periodo_sel == "Hoje (Diário)":
                    passou_periodo = dt_ag.date() == hoje_dt.date()
                elif periodo_sel == "Últimos 7 dias (Semanal)":
                    passou_periodo = (
                        hoje_dt.date() - timedelta(days=7)
                        <= dt_ag.date()
                        <= hoje_dt.date() + timedelta(days=7)
                    )
                elif periodo_sel == "Mês Atual (Mensal)":
                    passou_periodo = dt_ag.year == hoje_dt.year and dt_ag.month == hoje_dt.month
                elif periodo_sel == "Últimos 6 meses (Semestral)":
                    seis_meses_atras = hoje_dt - timedelta(days=180)
                    passou_periodo = dt_ag >= seis_meses_atras
                elif periodo_sel == "Ano Atual (Anual)":
                    passou_periodo = dt_ag.year == hoje_dt.year

                passou_barbeiro = False
                if barbeiro_sel == "Todos os Barbeiros":
                    passou_barbeiro = True
                else:
                    passou_barbeiro = ag.get("profissional") == barbeiro_sel

                if passou_periodo and passou_barbeiro:
                    ag_filtrados.append(ag)

            total_agendamentos = len(ag_filtrados)
            faturamento_total = sum(
                PRECOS_SERVICOS.get(ag.get("servico", ""), 0.0) for ag in ag_filtrados
            )

            st.write("---")

            m1, m2 = st.columns(2)
            with m1:
                st.metric("Total de Agendamentos", f"{total_agendamentos}")
            with m2:
                st.metric("Faturamento Projetado", f"R$ {faturamento_total:.2f}")

            st.write("---")

            st.markdown("### 📊 Desempenho e Quantidade de Serviços")
            col_b1, col_b2 = st.columns(2)

            ag_bruno = [ag for ag in ag_filtrados if ag.get("profissional") == "Bruno"]
            fat_bruno = sum(PRECOS_SERVICOS.get(ag.get("servico", ""), 0.0) for ag in ag_bruno)

            ag_samuel = [ag for ag in ag_filtrados if ag.get("profissional") == "Samuel"]
            fat_samuel = sum(PRECOS_SERVICOS.get(ag.get("servico", ""), 0.0) for ag in ag_samuel)

            def contar_servicos(lista):
                contagem = {}
                for ag in lista:
                    s = ag.get("servico", "Outro")
                    contagem[s] = contagem.get(s, 0) + 1
                return contagem

            servicos_bruno = contar_servicos(ag_bruno)
            servicos_samuel = contar_servicos(ag_samuel)

            with col_b1:
                st.markdown(
                    f"""
                <div class="client-card" style="border-left: 4px solid #23a55a !important;">
                    <h4 style="margin:0;">🧔 Bruno</h4>
                    <p style="margin:5px 0 0 0;"><b>Total Atendimentos:</b> {len(ag_bruno)}</p>
                    <p style="margin:0 0 10px 0;"><b>Faturamento:</b> R$ {fat_bruno:.2f}</p>
                    <hr style="margin: 8px 0; opacity: 0.3;">
                    <b>Serviços realizados:</b><br>
                    {''.join([f'<small>• {srv}: <b>{qtd}</b></small><br>' for srv, qtd in servicos_bruno.items()]) if servicos_bruno else '<small>Nenhum serviço no período.</small>'}
                </div>
                """,
                    unsafe_allow_html=True,
                )

            with col_b2:
                st.markdown(
                    f"""
                <div class="client-card" style="border-left: 4px solid #23a55a !important;">
                    <h4 style="margin:0;">🧔 Samuel</h4>
                    <p style="margin:5px 0 0 0;"><b>Total Atendimentos:</b> {len(ag_samuel)}</p>
                    <p style="margin:0 0 10px 0;"><b>Faturamento:</b> R$ {fat_samuel:.2f}</p>
                    <hr style="margin: 8px 0; opacity: 0.3;">
                    <b>Serviços realizados:</b><br>
                    {''.join([f'<small>• {srv}: <b>{qtd}</b></small><br>' for srv, qtd in servicos_samuel.items()]) if servicos_samuel else '<small>Nenhum serviço no período.</small>'}
                </div>
                """,
                    unsafe_allow_html=True,
                )

            st.write("---")

            st.markdown("### 📋 Lista de Agendamentos (Filtrados)")

            if ag_filtrados:
                tabela_dados = []
                for ag in ag_filtrados:
                    tabela_dados.append(
                        {
                            "Cliente": ag.get("cliente"),
                            "Telefone": ag.get("telefone"),
                            "Serviço": ag.get("servico"),
                            "Barbeiro": ag.get("profissional"),
                            "Data/Hora": ag["data_hora"].strftime("%d/%m/%Y às %H:%M"),
                            "Valor": f"R$ {PRECOS_SERVICOS.get(ag.get('servico',''), 0.0):.2f}",
                        }
                    )

                st.dataframe(tabela_dados, use_container_width=True)
            else:
                st.info("Nenhum agendamento encontrado para os filtros selecionados.")

    elif senha != "":
        st.error("Senha incorreta. Verifique e tente novamente.")
