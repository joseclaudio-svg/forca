import tkinter as tk
from tkinter import messagebox
import random
import os
import sys

def resource_path(relative_path):
    """ Obtém o caminho absoluto para o recurso, funciona para desenvolvimento e para o PyInstaller """
    try:
        # PyInstaller cria uma pasta temporária e armazena o caminho em _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
class JogoDaForcaGUI:
    def __init__(self, master):
        self.master = master
        master.title("Jogo da Forca")
        master.geometry("800x700")
        master.resizable(True, True)
        master.configure(bg="#2c3e50")

        self.palavras_por_dificuldade = {
            "Fácil": [],
            "Normal": [],
            "Difícil": []
        }
        self.dificuldade_atual = "Normal"
        self.carregar_palavras_por_dificuldade()

        if not any(self.palavras_por_dificuldade.values()):
            messagebox.showerror("Erro", "Não foi possível carregar as palavras. Verifique os arquivos 'facil.txt', 'normal.txt' e 'dificil.txt'.")
            master.destroy()
            return

        self.max_tentativas = 6
        self.palavra_secreta = ""
        self.letras_descobertas = []
        self.letras_erradas = []
        self.tentativas_atuais = 0
        self.vitorias = 0
        self.derrotas = 0

        self.criar_widgets()
        self.iniciar_novo_jogo()

    def carregar_palavras_por_dificuldade(self):
        """Carrega palavras de arquivos de texto específicos para cada dificuldade."""
        arquivos = {
            "Fácil": "facil.txt",
            "Normal": "normal.txt",
            "Difícil": "dificil.txt"
        }

        for dificuldade, arquivo in arquivos.items():
            caminho_arquivo = resource_path(arquivo)
            if not os.path.exists(caminho_arquivo):
                print(f"Aviso: Arquivo '{arquivo}' para a dificuldade '{dificuldade}' não encontrado.")
                continue
            try:
                with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                    palavras = [linha.strip().upper() for linha in f if linha.strip()]
                    self.palavras_por_dificuldade[dificuldade] = palavras
                    print(f"Carregadas {len(palavras)} palavras do arquivo '{arquivo}'.")
            except Exception as e:
                print(f"Erro ao carregar palavras de '{caminho_arquivo}': {e}")
                
    def criar_widgets(self):
        """Cria e posiciona os elementos da interface gráfica."""
        self.top_frame = tk.Frame(self.master, bg="#34495e", bd=2, relief="groove")
        self.top_frame.pack(pady=10, padx=20, fill="x")

        self.score_label = tk.Label(self.top_frame, text=f"Vitórias: {self.vitorias} | Derrotas: {self.derrotas}",
                                     bg="#34495e", fg="white", font=("Arial", 14, "bold"))
        self.score_label.pack(side="left", padx=10)

        tk.Label(self.top_frame, text="Dificuldade:", bg="#34495e", fg="white", font=("Arial", 12)).pack(side="left", padx=10)
        
        self.dificuldade_var = tk.StringVar(self.master)
        self.dificuldade_var.set("Normal")
        self.dificuldade_menu = tk.OptionMenu(self.top_frame, self.dificuldade_var, "Fácil", "Normal", "Difícil", command=self.mudar_dificuldade)
        self.dificuldade_menu.config(bg="#556b82", fg="white", font=("Arial", 12), highlightbackground="#34495e")
        self.dificuldade_menu["menu"].config(bg="#556b82", fg="white", font=("Arial", 12))
        self.dificuldade_menu.pack(side="left", padx=5)

        self.dica_btn = tk.Button(self.top_frame, text="Pedir Dica (-1 tentativa)", command=self.pedir_dica,
                                     bg="#9b59b6", fg="white", font=("Arial", 12, "bold"), relief="raised", bd=3)
        self.dica_btn.pack(side="right", padx=10)

        self.novo_jogo_btn = tk.Button(self.top_frame, text="Novo Jogo", command=self.iniciar_novo_jogo,
                                     bg="#27ae60", fg="white", font=("Arial", 12, "bold"), relief="raised", bd=3)
        self.novo_jogo_btn.pack(side="right", padx=10)

        self.canvas = tk.Canvas(self.master, width=300, height=250, bg="#ecf0f1", bd=2, relief="sunken")
        self.canvas.pack(pady=10)

        self.palavra_label = tk.Label(self.master, text="", font=("Courier New", 36, "bold"), bg="#2c3e50", fg="#ecf0f1")
        self.palavra_label.pack(pady=10)

        self.letras_erradas_label = tk.Label(self.master, text="Letras Erradas: ", font=("Arial", 14), bg="#2c3e50", fg="#e74c3c")
        self.letras_erradas_label.pack(pady=5)

        self.keyboard_frame = tk.Frame(self.master, bg="#2c3e50")
        self.keyboard_frame.pack(pady=10)

        self.letter_buttons = {}
        row = 0
        col = 0
        for char_code in range(ord('A'), ord('Z') + 1):
            letter = chr(char_code)
            button = tk.Button(self.keyboard_frame, text=letter, width=4, height=2,
                               command=lambda l=letter: self.processar_chute(l),
                               bg="#3498db", fg="white", font=("Arial", 12, "bold"), relief="raised", bd=2)
            button.grid(row=row, column=col, padx=3, pady=3)
            self.letter_buttons[letter] = button
            col += 1
            if col > 9:
                col = 0
                row += 1
        
        self.chutar_palavra_btn = tk.Button(self.master, text="Chutar Palavra Completa", 
                                             command=self.chutar_palavra_completa_dialog,
                                             bg="#f39c12", fg="white", font=("Arial", 12, "bold"), relief="raised", bd=3)
        self.chutar_palavra_btn.pack(pady=10)

    def mudar_dificuldade(self, dificuldade):
        """Define o número máximo de tentativas e a lista de palavras com base na dificuldade."""
        self.dificuldade_atual = dificuldade
        if dificuldade == "Fácil":
            self.max_tentativas = 8
        elif dificuldade == "Normal":
            self.max_tentativas = 6
        elif dificuldade == "Difícil":
            self.max_tentativas = 4
        self.iniciar_novo_jogo()

    def verificar_estado_dica_btn(self):
        """Verifica se o botão de dica deve estar habilitado ou desabilitado."""
        if (self.tentativas_atuais >= self.max_tentativas - 1 or
            "_" not in self.letras_descobertas or
            not self.letras_restantes_para_dica()):
            self.dica_btn.config(state=tk.DISABLED, bg="#7f8c8d")
        else:
            self.dica_btn.config(state=tk.NORMAL, bg="#9b59b6")

    def letras_restantes_para_dica(self):
        """Retorna uma lista de letras na palavra secreta que ainda não foram descobertas."""
        letras_disponiveis = []
        for i, letra in enumerate(self.palavra_secreta):
            if self.letras_descobertas[i] == "_" and letra not in self.letras_erradas:
                letras_disponiveis.append(letra)
        return list(set(letras_disponiveis))

    def pedir_dica(self):
        """Fornece uma dica ao jogador, revelando uma letra e custando uma tentativa."""
        if self.tentativas_atuais >= self.max_tentativas:
            return

        letras_para_dica = self.letras_restantes_para_dica()

        if not letras_para_dica:
            messagebox.showinfo("Dica", "Não há mais letras para dar dicas!")
            self.dica_btn.config(state=tk.DISABLED, bg="#7f8c8d")
            return

        dica_letra = random.choice(letras_para_dica)

        messagebox.showinfo("Dica", f"Uma letra da palavra é: '{dica_letra}'")
        self.processar_chute(dica_letra)
        
        self.tentativas_atuais += 1
        self.atualizar_interface()

        if self.tentativas_atuais >= self.max_tentativas:
            self.derrotas += 1
            self.atualizar_interface()
            messagebox.showinfo("Jogo da Forca", f"Você perdeu! A palavra era: {self.palavra_secreta}")
            self.desabilitar_botoes()
        
        self.verificar_estado_dica_btn()

    def desenhar_forca(self):
        """Desenha as partes da forca no canvas."""
        self.canvas.delete("all")

        self.canvas.create_line(50, 240, 250, 240, width=3)
        self.canvas.create_line(100, 240, 100, 50, width=3)
        self.canvas.create_line(100, 50, 200, 50, width=3)
        self.canvas.create_line(200, 50, 200, 80, width=3)

        if self.tentativas_atuais >= 1:
            self.canvas.create_oval(180, 80, 220, 120, width=3)
        if self.tentativas_atuais >= 2:
            self.canvas.create_line(200, 120, 200, 170, width=3)
        if self.tentativas_atuais >= 3:
            self.canvas.create_line(200, 130, 170, 150, width=3)
        if self.tentativas_atuais >= 4:
            self.canvas.create_line(200, 130, 230, 150, width=3)
        if self.tentativas_atuais >= 5:
            self.canvas.create_line(200, 170, 170, 200, width=3)
        if self.tentativas_atuais >= 6:
            self.canvas.create_line(200, 170, 230, 200, width=3)

    def iniciar_novo_jogo(self):
        """Reinicia o estado do jogo com uma nova palavra da dificuldade atual."""
        palavras_do_nivel = self.palavras_por_dificuldade.get(self.dificuldade_atual)
        if not palavras_do_nivel:
            messagebox.showerror("Erro", f"Nenhuma palavra disponível para a dificuldade '{self.dificuldade_atual}'.")
            self.desabilitar_botoes()
            return
            
        self.palavra_secreta = random.choice(palavras_do_nivel)
        self.letras_descobertas = ["_" for _ in self.palavra_secreta]
        self.letras_erradas = []
        self.tentativas_atuais = 0
        self.atualizar_interface()
        self.desenhar_forca()
        self.habilitar_botoes()
        print(f"Nova palavra ({self.dificuldade_atual}): {self.palavra_secreta}")
        self.verificar_estado_dica_btn()

    def atualizar_interface(self):
        """Atualiza os labels e o placar na GUI."""
        self.palavra_label.config(text=" ".join(self.letras_descobertas))
        self.letras_erradas_label.config(text=f"Letras Erradas: {', '.join(self.letras_erradas)}")
        self.score_label.config(text=f"Vitórias: {self.vitorias} | Derrotas: {self.derrotas}")
        self.desenhar_forca()

    def desabilitar_botoes(self):
        """Desabilita todos os botões de letras e o botão de chutar palavra."""
        for button in self.letter_buttons.values():
            button.config(state=tk.DISABLED)
        self.chutar_palavra_btn.config(state=tk.DISABLED)

    def habilitar_botoes(self):
        """Habilita todos os botões de letras e o botão de chutar palavra."""
        for button in self.letter_buttons.values():
            button.config(state=tk.NORMAL, bg="#3498db")
        self.chutar_palavra_btn.config(state=tk.NORMAL)

    def processar_chute(self, chute):
        """Processa o chute de uma letra."""
        if self.tentativas_atuais >= self.max_tentativas or "_" not in self.letras_descobertas:
            return

        self.letter_buttons[chute].config(state=tk.DISABLED, bg="#7f8c8d")

        if chute in self.palavra_secreta:
            for i, letra in enumerate(self.palavra_secreta):
                if letra == chute:
                    self.letras_descobertas[i] = chute
            self.atualizar_interface()
            if "_" not in self.letras_descobertas:
                self.vitorias += 1
                self.atualizar_interface()
                messagebox.showinfo("Jogo da Forca", f"Parabéns! Você adivinhou a palavra: {self.palavra_secreta}")
                self.desabilitar_botoes()
        else:
            if chute not in self.letras_erradas:
                self.letras_erradas.append(chute)
                self.tentativas_atuais += 1
            
            self.atualizar_interface()
            if self.tentativas_atuais >= self.max_tentativas:
                self.derrotas += 1
                self.atualizar_interface()
                messagebox.showinfo("Jogo da Forca", f"Você perdeu! A palavra era: {self.palavra_secreta}")
                self.desabilitar_botoes()
        
        self.verificar_estado_dica_btn()

    def chutar_palavra_completa_dialog(self):
        """Abre uma caixa de diálogo para o usuário chutar a palavra completa."""
        dialog = tk.Toplevel(self.master)
        dialog.title("Chutar Palavra")
        dialog.geometry("300x150")
        dialog.transient(self.master)
        dialog.grab_set()

        tk.Label(dialog, text="Qual é a palavra?", font=("Arial", 12)).pack(pady=10)
        entry = tk.Entry(dialog, font=("Arial", 14))
        entry.pack(pady=5)
        entry.focus_set()

        def verificar_chute_palavra():
            chute_palavra = entry.get().upper().strip()
            dialog.destroy()

            if not chute_palavra.isalpha():
                messagebox.showwarning("Chute Inválido", "Por favor, digite apenas letras.")
                return

            if chute_palavra == self.palavra_secreta:
                self.vitorias += 1
                self.letras_descobertas = list(self.palavra_secreta)
                self.atualizar_interface()
                messagebox.showinfo("Jogo da Forca", f"Parabéns! Você adivinhou a palavra completa: {self.palavra_secreta}")
                self.desabilitar_botoes()
            else:
                self.tentativas_atuais += 1
                self.atualizar_interface()
                messagebox.showinfo("Jogo da Forca", "Palavra errada!")
                if self.tentativas_atuais >= self.max_tentativas:
                    self.derrotas += 1
                    self.atualizar_interface()
                    messagebox.showinfo("Jogo da Forca", f"Você perdeu! A palavra era: {self.palavra_secreta}")
                    self.desabilitar_botoes()

        tk.Button(dialog, text="Chutar", command=verificar_chute_palavra,
                  bg="#27ae60", fg="white", font=("Arial", 12, "bold")).pack(pady=10)
        
        dialog.bind("<Return>", lambda event=None: verificar_chute_palavra())

if __name__ == "__main__":
    root = tk.Tk()
    game = JogoDaForcaGUI(root)
    root.mainloop()