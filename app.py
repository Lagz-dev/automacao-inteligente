from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sqlite3
from datetime import datetime

secret_key = "chave_super_secreta_123"

USUARIO = "admin"
SENHA = "1234"

app = Flask(__name__)
app.secret_key = secret_key

DB = "dados.db"


# 🔧 cria banco automaticamente
def init_db():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mensagens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            mensagem TEXT,
            resposta TEXT,
            data TEXT
        )
    """)

    conn.commit()
    conn.close()

init_db()


@app.route("/admin")
def admin():
    if not session.get("logado"):
        return redirect("/login")

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM mensagens ORDER BY id DESC")
    dados = cursor.fetchall()

    conn.close()

    return render_template("admin.html", dados=dados)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form.get("usuario")
        senha = request.form.get("senha")

        if usuario == USUARIO and senha == SENHA:
            session["logado"] = True
            return redirect("/admin")

        return "Login inválido"

    return render_template("login.html")

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/enviar", methods=["POST"])
def enviar():
    nome = request.form.get("nome")
    mensagem = request.form.get("mensagem")

    resposta = processar_mensagem(mensagem)

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO mensagens (nome, mensagem, resposta, data)
        VALUES (?, ?, ?, ?)
    """, (nome, mensagem, resposta, str(datetime.now())))

    conn.commit()
    conn.close()

    return jsonify({"resposta": resposta})


def processar_mensagem(msg):
    msg = msg.lower()

    regras = [
        (("horário", "funcionamento"), "Nosso horário é de 08h às 18h."),
        (("entrega", "pedido"), "Estamos verificando sua entrega."),
        (("ajuda", "suporte"), "Um atendente será acionado."),
        (("preço", "valor", "quanto custa"), "Os valores podem variar."),
        (("pagamento", "pix", "cartão"), "Aceitamos Pix e cartão."),
        (("cancelar",), "Cancelamento registrado."),
        (("reembolso",), "Reembolso em análise."),
        (("erro", "bug"), "Vamos verificar o problema."),
        (("login", "senha"), "Redefina sua senha no login."),
        (("cadastro",), "Acesse a página de registro."),
    ]

    for palavras, resposta in regras:
        if any(p in msg for p in palavras):
            return resposta

    return "Mensagem recebida com sucesso."


app = app
    
    