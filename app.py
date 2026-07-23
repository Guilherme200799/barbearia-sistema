import streamlit as st
from supabase import create_client, Client
from datetime import datetime, timedelta, time as dt_time

# ==============================================================================
# CONFIGURAÇÕES DA PÁGINA E ESTILOS
# ==============================================================================
st.set_page_config(page_title="Barbearia Preto & Branco", page_icon="💈", layout="centered")

st.markdown("""
    <style>
    .client-card {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        color: #333;
    }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# CONEXÃO COM O SUPABASE
# ==============================================================================
@st.cache_resource
def init_connection() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

# ==============================================================================
# VARIÁVEIS E CONFIGURAÇÕES GERAIS
# ==============================================================================
BARBEIROS = ["Bruno", "Samuel"]
SERVICOS = ["Corte", "Barba", "Corte + Barba", "Sobrancelha", "Platinado"]
HORARIOS_PADRAO = ["08:00", "08:40", "09:20", "10:00", "10:40", "11:20", "13:20", "14:00", "14:40", "15:20", "16:00", "16:40"]

if "hora_selecionada" not in st.session_state:
    st.session_state.hora_selecionada = None

# ==============================================================================
# FUNÇÕES DE BANCO DE DADOS (AGENDAMENTOS)
# ==============================================================================
def salvar_agendamento(cliente, telefone, servico, profissional, data_hora):
    try:
        dados = {
            "cliente": cliente,
            "telefone": telefone,
            "servico": servico,
            "profissional": profissional,
            "data_hora": data_hora.isoformat()
        }
        supabase.table("agendamentos").insert(dados).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao salvar: {e}")
        return False

def buscar_meus_agendamentos(telefone):
    try:
        res = supabase.table("agendamentos").select("*").eq("telefone", telefone).execute()
        return res.data
    except Exception as e:
        st.error(f"Erro ao buscar agendamentos: {e}")
        return []

def remarcar_agendamento(id_agendamento, nova_data_dt):
    try:
        nova_data_str = nova_data_dt.isoformat()
        supabase.table("agendamentos").update({"data_hora": nova_data_str}).eq("id", id_agendamento).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao remarcar no banco de dados: {e}")
        return False

def cancelar_agendamento(id_agendamento):
    try:
        supabase.table("agendamentos").delete().eq("id", id_agendamento).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao cancelar: {e}")
        return False

def buscar_todos_agendamentos():
    try:
        res = supabase.table("agendamentos").select("*").execute()
        return res.data
    except Exception:
        return []

# ==============================================================================
# FUNÇÕES DE BANCO DE DADOS (BLOQUEIOS)
# ==============================================================================
def carregar_bloqueios():
    try:
        res = supabase.table("bloq_horarios").select("*").execute()
        bloqueios = []
        for r in res.data:
            dt_bloq = datetime.strptime(r["data"], "%Y-%m-%d").date()
            bloqueios.append({
                "id": r["id"],
                "profissional": r["profissional"],
                "data": dt_bloq,
                "hora_inicio": r["hora_inicio"],
                "hora_fim": r["hora_fim"],
                "dia_inteiro": r["dia_inteiro"],
                "motivo": r.get("motivo", ""),
            })
        return bloqueios
    except Exception as e:
        return []

def salvar_bloqueio(profissional, data_bloq, hora_inicio, hora_fim, dia_inteiro, motivo):
    try:
        dados = {
            "profissional": profissional,
            "data": data_bloq.strftime("%Y-%m-%d"),
            "dia_inteiro": dia_inteiro,
            "motivo": motivo,
        }
        if hora_inicio: dados["hora_inicio"] = hora_inicio.strftime("%H:%M")
        if hora_fim: dados["hora_fim"] = hora_fim.strftime("%H:%M")

        supabase.table("bloq_horarios").insert(dados).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao salvar bloqueio: {e}")
        return False

def deletar_bloqueio(id_bloqueio):
    try:
        supabase.table("bloq_horarios").delete().eq("id", id_bloqueio).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao deletar bloqueio: {e}")
        return False

# ==============================================================================
# INTERFACE DO USUÁRIO (TABS)
# ==============================================================================
st.title("💈 Barbearia Preto & Branco")

aba1, aba2, aba3 = st.tabs(["🗓️ Agendar", "✂️ Meus Agendamentos", "⚙️ Admin"])

# ==============================================================================
# ABA 1: AGENDAR
# ==============================================================================
with aba1:
    # Card de Contato e Endereço com link pro WhatsApp
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

    st.subheader("🗓️ Faça seu Agendamento")

    col1, col2 = st.columns(2)
    with col1:
        barbeiro_sel = st.selectbox("Profissional:", BARBEIROS)
    with col2:
        data_atendimento = st.date_input("Data:", datetime.now().date(), min_value=datetime.now().date())

    # Lógica para descobrir horários já ocupados e bloqueados
    agendamentos_existentes = buscar_todos_agendamentos()
    horarios_ocupados = []
    for ag in agendamentos_existentes:
        if ag["profissional"] == barbeiro_sel:
            dt_ag = datetime.fromisoformat(ag["data_hora"])
            if dt_ag.date() == data_atendimento:
                horarios_ocupados.append(dt_ag.strftime("%H:%M"))

    lista_bloqueios = carregar_bloqueios()
    
    horarios_finais_disponiveis = []
    for hr_str in HORARIOS_PADRAO:
        if hr_str not in horarios_ocupados:
            hr_time = datetime.strptime(hr_str, "%H:%M").time()
            esta_bloqueado = False

            for b in lista_bloqueios:
                if b["profissional"] in [barbeiro_sel, "Todos"] and b["data"] == data_atendimento:
                    if b["dia_inteiro"]:
                        esta_bloqueado = True
                        break
                    else:
                        h_ini = datetime.strptime(b["hora_inicio"], "%H:%M").time()
                        h_fim = datetime.strptime(b["hora_fim"], "%H:%M").time()
                        if h_ini <= hr_time <= h_fim:
                            esta_bloqueado = True
                            break

            if not esta_bloqueado:
                # Se for hoje, remove horários que já passaram
                if data_atendimento == datetime.now().date():
                    agora_brt = (datetime.utcnow() - timedelta(hours=3)).time()
                    if hr_time > agora_brt:
                        horarios_finais_disponiveis.append(hr_time)
                else:
                    horarios_finais_disponiveis.append(hr_time)

    # Renderizando chips responsivos (4 colunas)
    st.write("---")
    st.markdown("### ⏰ Selecione um Horário Disponível:")

    if data_atendimento.weekday() != 6: # Ignora domingo se não abrirem
        if horarios_finais_disponiveis:
            horarios_finais_disponiveis.sort()
            tamanho_bloco = 4
            for i in range(0, len(horarios_finais_disponiveis), tamanho_bloco):
                grupo_horarios = horarios_finais_disponiveis[i : i + tamanho_bloco]
                cols = st.columns(len(grupo_horarios))

                for j, hr in enumerate(grupo_horarios):
                    hr_str = hr.strftime("%H:%M")
                    is_selected = st.session_state.hora_selecionada == hr
                    btn_type = "primary" if is_selected else "secondary"
                    btn_label = f"✓ {hr_str}" if is_selected else hr_str

                    if cols[j].button(btn_label, key=f"chip_hr_{hr_str}", use_container_width=True, type=btn_type):
                        st.session_state.hora_selecionada = hr
                        st.rerun()
        else:
            st.warning("⚠️ Não há horários disponíveis para esta data.")
    else:
        st.error("Fechado aos Domingos.")

    if st.session_state.hora_selecionada:
        st.write("---")
        with st.form("form_agendamento"):
            st.markdown(f"**Horário Escolhido:** {st.session_state.hora_selecionada.strftime('%H:%M')}")
            cliente_nome = st.text_input("Seu Nome:")
            cliente_tel = st.text_input("Seu WhatsApp (apenas números):")
            servico_sel = st.selectbox("Serviço:", SERVICOS)
            
            submit = st.form_submit_button("Confirmar Agendamento", type="primary", use_container_width=True)
            
            if submit:
                if cliente_nome and cliente_tel:
                    data_hora_agendamento = datetime.combine(data_atendimento, st.session_state.hora_selecionada)
                    sucesso = salvar_agendamento(cliente_nome, cliente_tel, servico_sel, barbeiro_sel, data_hora_agendamento)
                    if sucesso:
                        st.success("✅ Agendamento realizado com sucesso!")
                        st.session_state.hora_selecionada = None # Limpa a seleção
                else:
                    st.warning("Preencha todos os campos!")

# ==============================================================================
# ABA 2: MEUS AGENDAMENTOS (REMARCAR / CANCELAR)
# ==============================================================================
with aba2:
    st.subheader("✂️ Buscar e Gerenciar Agendamentos")
    telefone_busca = st.text_input("Digite seu WhatsApp para buscar seus horários:", key="busca_tel")
    
    if st.button("Buscar Agendamentos"):
        if telefone_busca:
            resultados = buscar_meus_agendamentos(telefone_busca)
            if resultados:
                st.session_state.meus_agendamentos = resultados
            else:
                st.warning("Nenhum agendamento encontrado para este número.")
                st.session_state.meus_agendamentos = []

    if "meus_agendamentos" in st.session_state and st.session_state.meus_agendamentos:
        st.write("---")
        for ag in st.session_state.meus_agendamentos:
            dt_obj = datetime.fromisoformat(ag["data_hora"])
            with st.container():
                st.markdown(
                    f"""
                    <div class="client-card" style="margin-bottom: 10px;">
                        <b>Serviço:</b> {ag['servico']} com {ag['profissional']}<br>
                        <b>Data:</b> {dt_obj.strftime('%d/%m/%Y às %H:%M')}
                    </div>
                    """, unsafe_allow_html=True
                )
                
                col_btn1, col_btn2 = st.columns(2)
                
                # Regra de 2 horas
                agora_dt = datetime.utcnow() - timedelta(hours=3)
                diferenca_horas = (dt_obj - agora_dt).total_seconds() / 3600
                pode_alterar = diferenca_horas >= 2

                with col_btn1:
                    if st.button("Remarcar", key=f"rem_{ag['id']}", use_container_width=True):
                        st.session_state.acao_agendamento = {"tipo": "remarcar", "id": ag["id"], "data_atual": dt_obj, "pode": pode_alterar}
                with col_btn2:
                    if st.button("Cancelar", key=f"can_{ag['id']}", use_container_width=True):
                        st.session_state.acao_agendamento = {"tipo": "cancelar", "id": ag["id"], "data_atual": dt_obj, "pode": pode_alterar}

        # Tratamento das Ações
        if "acao_agendamento" in st.session_state:
            acao = st.session_state.acao_agendamento
            
            if not acao["pode"]:
                st.error(
                    "⚠️ **Atenção:** Cancelamentos ou alterações com menos de **2 horas de antecedência** "
                    "não podem ser feitos diretamente pelo sistema.\n\n"
                    "Por favor, entre em contato diretamente via WhatsApp com o seu barbeiro."
                )
            else:
                st.write("---")
                if acao["tipo"] == "cancelar":
                    st.warning("Tem certeza que deseja cancelar este horário?")
                    if st.button("Confirmar Cancelamento", type="primary"):
                        if cancelar_agendamento(acao["id"]):
                            st.success("Agendamento cancelado com sucesso!")
                            del st.session_state.meus_agendamentos
                            del st.session_state.acao_agendamento
                            st.rerun()
                
                elif acao["tipo"] == "remarcar":
                    st.markdown("### Escolha a nova data e horário:")
                    nova_data = st.date_input("Nova Data:", value=acao["data_atual"].date(), min_value=datetime.now().date())
                    novo_horario = st.selectbox("Novo Horário:", HORARIOS_PADRAO)
                    
                    if st.button("Confirmar Alteração", type="primary"):
                        hora_parsed = datetime.strptime(novo_horario, "%H:%M").time()
                        nova_data_hora = datetime.combine(nova_data, hora_parsed)
                        
                        if remarcar_agendamento(acao["id"], nova_data_hora):
                            st.success("Horário remarcado com sucesso!")
                            del st.session_state.meus_agendamentos
                            del st.session_state.acao_agendamento
                            st.rerun()

# ==============================================================================
# ABA 3: ADMIN E RELATÓRIOS
# ==============================================================================
with aba3:
    st.subheader("⚙️ Painel de Administração")
    senha = st.text_input("Senha de Acesso:", type="password")
    
    if senha == "admin123": # Troque para a senha desejada
        st.success("Acesso Liberado!")
        
        st.markdown("### 📊 Relatório de Agendamentos")
        todos_ag = buscar_todos_agendamentos()
        if todos_ag:
            # Aqui você pode usar st.dataframe para exibir os dados bonitinhos
            st.dataframe(todos_ag, use_container_width=True)
        else:
            st.info("Nenhum agendamento no sistema.")

        # --- GERENCIAMENTO DE BLOQUEIOS ---
        st.write("---")
        st.markdown("### 🚫 Gerenciamento de Bloqueios e Folgas")

        with st.form("form_bloqueio_horario"):
            col_b1, col_b2, col_b3 = st.columns(3)

            with col_b1:
                prof_bloq = st.selectbox("Barbeiro:", ["Bruno", "Samuel", "Todos"], key="prof_bloq")
                data_bloq = st.date_input("Data do Bloqueio:", datetime.now().date())

            with col_b2:
                dia_inteiro = st.checkbox("Bloquear Dia Inteiro?", value=False)
                hora_ini = st.time_input("Horário Início:", dt_time(8, 0))
                hora_fim = st.time_input("Horário Fim:", dt_time(18, 0))

            with col_b3:
                motivo_bloq = st.text_input("Motivo (Opcional):", placeholder="Ex: Folga, Médico...")
                st.write("")
                btn_salvar_bloq = st.form_submit_button("🔒 Salvar Bloqueio", type="primary", use_container_width=True)

        if btn_salvar_bloq:
            if salvar_bloqueio(prof_bloq, data_bloq, hora_ini, hora_fim, dia_inteiro, motivo_bloq):
                st.success("Bloqueio registrado com sucesso!")
                st.rerun()

        bloqueios_cadastrados = carregar_bloqueios()
        if bloqueios_cadastrados:
            st.markdown("#### Bloqueios Ativos")
            for b in bloqueios_cadastrados:
                periodo_str = "Dia Inteiro" if b["dia_inteiro"] else f"das {b['hora_inicio']} às {b['hora_fim']}"
                col_t1, col_t2 = st.columns([4, 1])
                with col_t1:
                    st.write(f"📌 **{b['profissional']}** | {b['data'].strftime('%d/%m/%Y')} ({periodo_str}) - *{b['motivo']}*")
                with col_t2:
                    if st.button("🗑️ Remover", key=f"del_bloq_{b['id']}"):
                        deletar_bloqueio(b['id'])
                        st.rerun()
    elif senha:
        st.error("Senha incorreta.")
