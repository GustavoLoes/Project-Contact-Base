import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import re


# =========================
# BANCO DE DADOS
# =========================

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


# =========================
# FUNCOES
# =========================

def carregar_contatos():
    """Carrega os contatos aplicando os filtros."""
    for item in tabela.get_children():
        tabela.delete(item)

    nome_filtro = filtro_nome.get().strip()
    telefone_filtro = filtro_telefone.get().strip()

    cursor.execute("""
        SELECT id, nome, telefone, email
        FROM contatos
        WHERE nome LIKE ? AND telefone LIKE ?
        ORDER BY nome COLLATE NOCASE
    """, (
        f"%{nome_filtro}%",
        f"%{telefone_filtro}%"
    ))

    for contato in cursor.fetchall():
        tabela.insert("", tk.END, values=contato)

    total = len(tabela.get_children())
    label_total.config(text=f"Contatos encontrados: {total}")


def limpar_campos():
    entrada_nome.delete(0, tk.END)
    entrada_telefone.delete(0, tk.END)
    entrada_email.delete(0, tk.END)

    for item in tabela.selection():
        tabela.selection_remove(item)

    entrada_nome.focus()


def validar_dados():
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

    if not re.fullmatch(r"[0-9()+.\-\s]{8,25}", telefone):
        messagebox.showwarning(
            "Telefone inválido",
            "Digite um número de telefone válido."
        )
        return None

    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        messagebox.showwarning(
            "E-mail inválido",
            "Digite um endereço de e-mail válido."
        )
        return None

    return nome, telefone, email


def cadastrar_contato():
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
    selecionados = tabela.selection()

    if not selecionados:
        return

    valores = tabela.item(selecionados[0], "values")

    limpar_campos()

    entrada_nome.insert(0, valores[1])
    entrada_telefone.insert(0, valores[2])
    entrada_email.insert(0, valores[3])


def editar_contato():
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

    valores = tabela.item(selecionados[0], "values")
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
    selecionados = tabela.selection()

    if not selecionados:
        messagebox.showwarning(
            "Atenção",
            "Selecione um contato para excluir."
        )
        return

    valores = tabela.item(selecionados[0], "values")
    contato_id = valores[0]
    nome = valores[1]

    confirmar = messagebox.askyesno(
        "Confirmar exclusão",
        f"Deseja excluir o contato de {nome}?"
    )

    if confirmar:
        cursor.execute(
            "DELETE FROM contatos WHERE id = ?",
            (contato_id,)
        )

        conexao.commit()
        carregar_contatos()
        limpar_campos()

        messagebox.showinfo(
            "Sucesso",
            "Contato excluído."
        )


def limpar_filtros():
    filtro_nome.set("")
    filtro_telefone.set("")
    carregar_contatos()


def fechar_programa():
    conexao.close()
    janela.destroy()


# =========================
# INTERFACE GRAFICA
# =========================

janela = tk.Tk()
janela.title("Agenda de Contatos")
janela.geometry("900x650")
janela.minsize(750, 550)
janela.configure(bg="#f0f2f5")

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

# Título
titulo = tk.Label(
    janela,
    text="AGENDA DE CONTATOS",
    font=("Arial", 20, "bold"),
    bg="#f0f2f5",
    fg="#1d3557"
)
titulo.pack(pady=(20, 15))

# Área de cadastro
frame_cadastro = tk.LabelFrame(
    janela,
    text="Dados do contato",
    font=("Arial", 11, "bold"),
    bg="#f0f2f5",
    padx=15,
    pady=12
)
frame_cadastro.pack(fill="x", padx=20, pady=5)

tk.Label(
    frame_cadastro,
    text="Nome completo:",
    bg="#f0f2f5"
).grid(row=0, column=0, sticky="w", pady=5)

entrada_nome = ttk.Entry(frame_cadastro, width=35)
entrada_nome.grid(row=0, column=1, sticky="ew", padx=8, pady=5)

tk.Label(
    frame_cadastro,
    text="Telefone:",
    bg="#f0f2f5"
).grid(row=1, column=0, sticky="w", pady=5)

entrada_telefone = ttk.Entry(frame_cadastro, width=35)
entrada_telefone.grid(row=1, column=1, sticky="ew", padx=8, pady=5)

tk.Label(
    frame_cadastro,
    text="E-mail:",
    bg="#f0f2f5"
).grid(row=2, column=0, sticky="w", pady=5)

entrada_email = ttk.Entry(frame_cadastro, width=35)
entrada_email.grid(row=2, column=1, sticky="ew", padx=8, pady=5)

frame_cadastro.columnconfigure(1, weight=1)

# Botões de cadastro
frame_botoes = tk.Frame(janela, bg="#f0f2f5")
frame_botoes.pack(fill="x", padx=20, pady=10)

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

# Área de filtros
frame_filtros = tk.LabelFrame(
    janela,
    text="Pesquisar contatos",
    font=("Arial", 11, "bold"),
    bg="#f0f2f5",
    padx=12,
    pady=10
)
frame_filtros.pack(fill="x", padx=20, pady=5)

filtro_nome = tk.StringVar()
filtro_telefone = tk.StringVar()

tk.Label(
    frame_filtros,
    text="Filtrar por nome:",
    bg="#f0f2f5"
).grid(row=0, column=0, sticky="w", padx=5)

campo_filtro_nome = ttk.Entry(
    frame_filtros,
    textvariable=filtro_nome
)
campo_filtro_nome.grid(
    row=0, column=1, sticky="ew", padx=5
)

tk.Label(
    frame_filtros,
    text="Filtrar por número:",
    bg="#f0f2f5"
).grid(row=1, column=0, sticky="w", padx=5, pady=5)

campo_filtro_telefone = ttk.Entry(
    frame_filtros,
    textvariable=filtro_telefone
)
campo_filtro_telefone.grid(
    row=1, column=1, sticky="ew", padx=5, pady=5
)

ttk.Button(
    frame_filtros,
    text="Limpar filtros",
    command=limpar_filtros
).grid(row=0, column=2, rowspan=2, padx=8)

frame_filtros.columnconfigure(1, weight=1)

# Pesquisa automática enquanto digita
filtro_nome.trace_add(
    "write",
    lambda *_: carregar_contatos()
)

filtro_telefone.trace_add(
    "write",
    lambda *_: carregar_contatos()
)

# Tabela
frame_tabela = tk.Frame(janela, bg="#f0f2f5")
frame_tabela.pack(
    fill="both",
    expand=True,
    padx=20,
    pady=(10, 5)
)

colunas = ("id", "nome", "telefone", "email")

tabela = ttk.Treeview(
    frame_tabela,
    columns=colunas,
    show="headings",
    selectmode="browse"
)

tabela.heading("id", text="ID")
tabela.heading("nome", text="Nome completo")
tabela.heading("telefone", text="Telefone")
tabela.heading("email", text="E-mail")

tabela.column("id", width=45, anchor="center")
tabela.column("nome", width=230)
tabela.column("telefone", width=150)
tabela.column("email", width=260)

barra_vertical = ttk.Scrollbar(
    frame_tabela,
    orient="vertical",
    command=tabela.yview
)

tabela.configure(yscrollcommand=barra_vertical.set)

tabela.pack(side="left", fill="both", expand=True)
barra_vertical.pack(side="right", fill="y")

tabela.bind("<<TreeviewSelect>>", selecionar_contato)

# Rodapé
label_total = tk.Label(
    janela,
    text="Contatos encontrados: 0",
    font=("Arial", 10, "bold"),
    bg="#f0f2f5",
    fg="#1d3557"
)
label_total.pack(anchor="w", padx=22, pady=(5, 15))

# Inicialização
carregar_contatos()
entrada_nome.focus()

janela.protocol("WM_DELETE_WINDOW", fechar_programa)
janela.mainloop()