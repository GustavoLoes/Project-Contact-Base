import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import re


# ==========================================
# BANCO DE DADOS
# ==========================================

conexao = sqlite3.connect("contatos.db")
cursor = conexao.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS contatos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        telefone TEXT NOT NULL,
        email TEXT NOT NULL
    )
""")

conexao.commit()


# ==========================================
# FUNCOES
# ==========================================

def formatar_telefone(event=None):
    """Formata automaticamente telefones brasileiros."""

    texto = entrada_telefone.get()
    numeros = "".join(c for c in texto if c.isdigit())[:11]

    if not numeros:
        formatado = ""

    elif len(numeros) <= 2:
        formatado = "(" + numeros

    else:
        ddd = numeros[:2]
        numero = numeros[2:]

        if len(numeros) <= 10:
            # Telefone fixo: (47) 3333-4444
            formatado = f"({ddd}) "

            if len(numero) > 4:
                formatado += numero[:4] + "-" + numero[4:]
            else:
                formatado += numero

        else:
            # Celular: (47) 99999-4444
            formatado = f"({ddd}) "

            if len(numero) > 5:
                formatado += numero[:5] + "-" + numero[5:]
            else:
                formatado += numero

    # Evita atualizações desnecessárias do campo
    if texto != formatado:
        entrada_telefone.delete(0, tk.END)
        entrada_telefone.insert(0, formatado)

    entrada_telefone.icursor(tk.END)


def carregar_contatos():
    """Carrega os contatos aplicando os filtros."""

    for item in tabela.get_children():
        tabela.delete(item)

    nome_filtro = filtro_nome.get().strip()
    telefone_filtro = "".join(
        c for c in filtro_telefone.get() if c.isdigit()
    )

    cursor.execute("""
        SELECT id, nome, telefone, email
        FROM contatos
        WHERE nome LIKE ?
        ORDER BY nome COLLATE NOCASE
    """, (f"%{nome_filtro}%",))

    contatos = cursor.fetchall()

    for contato in contatos:
        # O filtro de telefone ignora parênteses,
        # espaços e hífens.
        telefone_salvo = "".join(
            c for c in contato[2] if c.isdigit()
        )

        if telefone_filtro and telefone_filtro not in telefone_salvo:
            continue

        tabela.insert("", tk.END, values=contato)

    total = len(tabela.get_children())
    label_total.config(
        text=f"Contatos encontrados: {total}"
    )


def limpar_campos():
    """Limpa os campos do formulário."""

    entrada_nome.delete(0, tk.END)
    entrada_telefone.delete(0, tk.END)
    entrada_email.delete(0, tk.END)

    for item in tabela.selection():
        tabela.selection_remove(item)

    entrada_nome.focus()


def validar_dados():
    """Valida os dados antes de salvar."""

    nome = entrada_nome.get().strip()
    telefone = entrada_telefone.get().strip()
    email = entrada_email.get().strip()

    if not nome or not telefone or not email:
        messagebox.showwarning(
            "Atenção",
            "Preencha o nome completo, telefone e e-mail."
        )
        return None

    if len(nome.split()) < 2:
        messagebox.showwarning(
            "Nome inválido",
            "Digite o nome completo da pessoa."
        )
        return None

    numeros_telefone = "".join(
        c for c in telefone if c.isdigit()
    )

    if len(numeros_telefone) not in (10, 11):
        messagebox.showwarning(
            "Telefone inválido",
            "Digite o DDD e o número completo."
        )
        return None

    if not re.fullmatch(
        r"[^@\s]+@[^@\s]+\.[^@\s]+",
        email
    ):
        messagebox.showwarning(
            "E-mail inválido",
            "Digite um endereço de e-mail válido."
        )
        return None

    # Guarda o telefone com a formatação brasileira.
    return nome, telefone, email


def cadastrar_contato():
    """Cadastra um novo contato."""

    dados = validar_dados()

    if dados is None:
        return

    try:
        cursor.execute("""
            INSERT INTO contatos (nome, telefone, email)
            VALUES (?, ?, ?)
        """, dados)

        conexao.commit()
        carregar_contatos()
        limpar_campos()

        messagebox.showinfo(
            "Sucesso",
            "Contato cadastrado com sucesso!"
        )

    except sqlite3.Error as erro:
        messagebox.showerror("Erro", str(erro))


def selecionar_contato(event=None):
    """Carrega os dados do contato selecionado."""

    selecionados = tabela.selection()

    if not selecionados:
        return

    valores = tabela.item(
        selecionados[0], "values"
    )

    entrada_nome.delete(0, tk.END)
    entrada_telefone.delete(0, tk.END)
    entrada_email.delete(0, tk.END)

    entrada_nome.insert(0, valores[1])
    entrada_telefone.insert(0, valores[2])
    entrada_email.insert(0, valores[3])


def editar_contato():
    """Atualiza o contato selecionado."""

    selecionados = tabela.selection()

    if not selecionados:
        messagebox.showwarning(
            "Atenção",
            "Selecione um contato na tabela para editar."
        )
        return

    dados = validar_dados()

    if dados is None:
        return

    valores = tabela.item(
        selecionados[0], "values"
    )
    contato_id = valores[0]

    try:
        cursor.execute("""
            UPDATE contatos
            SET nome = ?, telefone = ?, email = ?
            WHERE id = ?
        """, (*dados, contato_id))

        conexao.commit()
        carregar_contatos()
        limpar_campos()

        messagebox.showinfo(
            "Sucesso",
            "Contato atualizado com sucesso!"
        )

    except sqlite3.Error as erro:
        messagebox.showerror("Erro", str(erro))


def excluir_contato():
    """Exclui o contato selecionado."""

    selecionados = tabela.selection()

    if not selecionados:
        messagebox.showwarning(
            "Atenção",
            "Selecione um contato para excluir."
        )
        return

    valores = tabela.item(
        selecionados[0], "values"
    )

    contato_id = valores[0]
    nome = valores[1]

    confirmar = messagebox.askyesno(
        "Confirmar exclusão",
        f"Deseja excluir o contato de {nome}?"
    )

    if confirmar:
        try:
            cursor.execute(
                "DELETE FROM contatos WHERE id = ?",
                (contato_id,)
            )

            conexao.commit()
            carregar_contatos()
            limpar_campos()

            messagebox.showinfo(
                "Sucesso",
                "Contato excluído com sucesso!"
            )

        except sqlite3.Error as erro:
            messagebox.showerror("Erro", str(erro))


def limpar_filtros():
    """Limpa os filtros de pesquisa."""

    filtro_nome.set("")
    filtro_telefone.set("")


def fechar_programa():
    """Fecha a conexão e a janela."""

    conexao.close()
    janela.destroy()


# ==========================================
# INTERFACE GRAFICA
# ==========================================

janela = tk.Tk()
janela.title("Agenda de Contatos")
janela.geometry("950x680")
janela.minsize(780, 580)
janela.configure(bg="#f0f2f5")


# Estilo
estilo = ttk.Style()
estilo.theme_use("clam")

estilo.configure(
    "Treeview",
    rowheight=30,
    font=("Arial", 10),
    background="white",
    fieldbackground="white"
)

estilo.configure(
    "Treeview.Heading",
    font=("Arial", 10, "bold")
)

estilo.configure(
    "TButton",
    font=("Arial", 10),
    padding=7
)


# ==========================================
# TITULO
# ==========================================

titulo = tk.Label(
    janela,
    text="AGENDA DE CONTATOS",
    font=("Arial", 20, "bold"),
    bg="#f0f2f5",
    fg="#1d3557"
)

titulo.pack(pady=(20, 15))


# ==========================================
# FORMULARIO DE CADASTRO
# ==========================================

frame_cadastro = tk.LabelFrame(
    janela,
    text="Dados do contato",
    font=("Arial", 11, "bold"),
    bg="#f0f2f5",
    padx=15,
    pady=12
)

frame_cadastro.pack(
    fill="x",
    padx=20,
    pady=5
)


# Nome
tk.Label(
    frame_cadastro,
    text="Nome completo:",
    bg="#f0f2f5"
).grid(row=0, column=0, sticky="w", pady=5)

entrada_nome = ttk.Entry(
    frame_cadastro,
    width=35
)

entrada_nome.grid(
    row=0, column=1,
    sticky="ew", padx=8, pady=5
)


# Telefone
tk.Label(
    frame_cadastro,
    text="Telefone:",
    bg="#f0f2f5"
).grid(row=1, column=0, sticky="w", pady=5)

entrada_telefone = ttk.Entry(
    frame_cadastro,
    width=35
)

entrada_telefone.grid(
    row=1, column=1,
    sticky="ew", padx=8, pady=5
)

entrada_telefone.bind(
    "<KeyRelease>",
    formatar_telefone
)


# E-mail
tk.Label(
    frame_cadastro,
    text="E-mail:",
    bg="#f0f2f5"
).grid(row=2, column=0, sticky="w", pady=5)

entrada_email = ttk.Entry(
    frame_cadastro,
    width=35
)

entrada_email.grid(
    row=2, column=1,
    sticky="ew", padx=8, pady=5
)

frame_cadastro.columnconfigure(
    1, weight=1
)


# ==========================================
# BOTOES
# ==========================================

frame_botoes = tk.Frame(
    janela,
    bg="#f0f2f5"
)

frame_botoes.pack(
    fill="x",
    padx=20,
    pady=10
)

ttk.Button(
    frame_botoes,
    text="Cadastrar",
    command=cadastrar_contato
).pack(side="left", padx=4)

ttk.Button(
    frame_botoes,
    text="Editar selecionado",
    command=editar_contato
).pack(side="left", padx=4)

ttk.Button(
    frame_botoes,
    text="Excluir selecionado",
    command=excluir_contato
).pack(side="left", padx=4)

ttk.Button(
    frame_botoes,
    text="Limpar campos",
    command=limpar_campos
).pack(side="left", padx=4)


# ==========================================
# FILTROS
# ==========================================

frame_filtros = tk.LabelFrame(
    janela,
    text="Pesquisar contatos",
    font=("Arial", 11, "bold"),
    bg="#f0f2f5",
    padx=12,
    pady=10
)

frame_filtros.pack(
    fill="x",
    padx=20,
    pady=5
)

filtro_nome = tk.StringVar()
filtro_telefone = tk.StringVar()


# Filtro por nome
tk.Label(
    frame_filtros,
    text="Filtrar por nome:",
    bg="#f0f2f5"
).grid(
    row=0, column=0,
    sticky="w", padx=5
)

campo_filtro_nome = ttk.Entry(
    frame_filtros,
    textvariable=filtro_nome
)

campo_filtro_nome.grid(
    row=0, column=1,
    sticky="ew", padx=5
)


# Filtro por telefone
tk.Label(
    frame_filtros,
    text="Filtrar por número:",
    bg="#f0f2f5"
).grid(
    row=1, column=0,
    sticky="w", padx=5, pady=5
)

campo_filtro_telefone = ttk.Entry(
    frame_filtros,
    textvariable=filtro_telefone
)

campo_filtro_telefone.grid(
    row=1, column=1,
    sticky="ew", padx=5, pady=5
)


# Limpar filtros
ttk.Button(
    frame_filtros,
    text="Limpar filtros",
    command=limpar_filtros
).grid(
    row=0, column=2,
    rowspan=2, padx=8
)

frame_filtros.columnconfigure(
    1, weight=1
)


# Atualiza a tabela durante a pesquisa
filtro_nome.trace_add(
    "write",
    lambda *_: carregar_contatos()
)

filtro_telefone.trace_add(
    "write",
    lambda *_: carregar_contatos()
)


# ==========================================
# TABELA DE CONTATOS
# ==========================================

frame_tabela = tk.Frame(
    janela,
    bg="#f0f2f5"
)

frame_tabela.pack(
    fill="both",
    expand=True,
    padx=20,
    pady=(10, 5)
)

colunas = (
    "id",
    "nome",
    "telefone",
    "email"
)

tabela = ttk.Treeview(
    frame_tabela,
    columns=colunas,
    show="headings",
    selectmode="browse"
)


# Cabecalhos
tabela.heading("id", text="ID")
tabela.heading("nome", text="Nome completo")
tabela.heading("telefone", text="Telefone")
tabela.heading("email", text="E-mail")


# Largura das colunas
tabela.column(
    "id", width=45,
    anchor="center"
)

tabela.column(
    "nome", width=250
)

tabela.column(
    "telefone", width=160
)

tabela.column(
    "email", width=300
)


# Barra de rolagem
barra_vertical = ttk.Scrollbar(
    frame_tabela,
    orient="vertical",
    command=tabela.yview
)

tabela.configure(
    yscrollcommand=barra_vertical.set
)

tabela.pack(
    side="left",
    fill="both",
    expand=True
)

barra_vertical.pack(
    side="right",
    fill="y"
)


# Selecionar contato para editar
tabela.bind(
    "<<TreeviewSelect>>",
    selecionar_contato
)


# ==========================================
# RODAPE
# ==========================================

label_total = tk.Label(
    janela,
    text="Contatos encontrados: 0",
    font=("Arial", 10, "bold"),
    bg="#f0f2f5",
    fg="#1d3557"
)

label_total.pack(
    anchor="w",
    padx=22,
    pady=(5, 15)
)


# ==========================================
# INICIALIZACAO
# ==========================================

carregar_contatos()
entrada_nome.focus()

janela.protocol(
    "WM_DELETE_WINDOW",
    fechar_programa
)

janela.mainloop()