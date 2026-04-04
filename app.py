usuarios = {"admin": "1234"}

if "logado" not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    st.subheader("🔐 Login")

    user = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if user in usuarios and usuarios[user] == senha:
            st.session_state.logado = True
            st.success("Login realizado")
        else:
            st.error("Login inválido")

    st.stop()import streamlit as st
import pandas as pd
import random
import os

st.set_page_config(layout="wide")

st.title("IA Loteria Profissional V13")

arquivo = st.file_uploader("Envie o CSV", type=["csv"])

# -------------------------
# BANCO LOCAL (CSV)
# -------------------------

def salvar_jogos(jogos, user):
    df = pd.DataFrame(jogos, columns=["jogo", "score"])

    nome = f"historico_{user}.csv"

    if os.path.exists(nome):
        antigo = pd.read_csv(nome)
        df = pd.concat([antigo, df])

    df.to_csv(nome, index=False)

# -------------------------
# CICLO
# -------------------------
def analisar_ciclo(df):
    todos = set(range(1, 26))
    acumulado = set()
    concursos = 0

    for i in range(len(df)-1, -1, -1):
        linha = set(df.iloc[i].dropna().astype(int))
        acumulado.update(linha)
        concursos += 1

        if acumulado == todos:
            break

    faltantes = list(todos - acumulado)

    if concursos <= 2:
        fase = "INÍCIO"
    elif concursos <= 4:
        fase = "MEIO"
    else:
        fase = "FINAL"

    return concursos, fase, faltantes

# -------------------------
# MÉTRICAS
# -------------------------
def calcular_metricas(df):
    freq = {n: 0 for n in range(1, 26)}
    ultimo = df.iloc[-1].dropna().astype(int).tolist()

    for _, row in df.iterrows():
        for n in row.dropna():
            freq[int(n)] += 1

    return freq, ultimo

# -------------------------
# BASE
# -------------------------
def gerar_base(freq):
    return sorted(freq, key=freq.get, reverse=True)[:20]

# -------------------------
# GERAR JOGO
# -------------------------
def gerar_jogo(base):
    return sorted(random.sample(base, 15))

# -------------------------
# SCORE
# -------------------------
def pontuar(jogo, ultimo):
    score = 0

    pares = sum(1 for n in jogo if n % 2 == 0)
    repetidos = len(set(jogo) & set(ultimo))

    if 6 <= pares <= 9:
        score += 3

    if 8 <= repetidos <= 11:
        score += 3

    return score
# distribuição por linhas (1–5, 6–10, etc)
linhas = [0]*5
for n in jogo:
    linhas[(n-1)//5] += 1

if all(l >= 2 for l in linhas):
    score += 2
# -------------------------
# INTERFACE
# -------------------------
if arquivo is not None:
    df = pd.read_csv(arquivo)

    concursos, fase, faltantes = analisar_ciclo(df)
    freq, ultimo = calcular_metricas(df)

    st.subheader("📊 Ciclo")
    st.write(f"Concursos: {concursos}")
    st.write(f"Fase: {fase}")
    st.write(f"Faltantes: {faltantes}")

    # gráfico
    st.subheader("📊 Frequência das dezenas")
    df_freq = pd.DataFrame(list(freq.items()), columns=["Dezena", "Frequência"])
    st.bar_chart(df_freq.set_index("Dezena"))

    base = gerar_base(freq)

    st.subheader("🧠 Base")
    st.write(base)

    if st.button("🚀 Gerar Jogos"):
        jogos = []

        for _ in range(10):
            j = gerar_jogo(base)
            s = pontuar(j, ultimo)
            jogos.append((str(j), s))

        salvar_jogos(jogos)

        st.subheader("🎯 Jogos")
        for j, s in jogos:
            st.write(f"{j} | Score: {s}")

    # histórico
    st.subheader("📁 Histórico de Jogos")
    hist = carregar_historico()

    if hist is not None:
        st.dataframe(hist.tail(10))
