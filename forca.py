import random

def escolher_palavra():
    palavras = ["gato", "cachorro", "elefante", "peixe", "tartaruga"]
    return random.choice(palavras).upper() # <<< Adicione .upper() aqui

def mostrar_forca(erros):
    """Desenha o boneco da forca com base no número de erros."""
    estagios = [
        # Cabeça
        """
           -----
           |   |
               |
               |
               |
             -----
        """,
        # Corpo
        """
           -----
           |   |
           O   |
           |   |
               |
             -----
        """,
        # Braço esquerdo
        """
           -----
           |   |
           O   |
          /|   |
               |
             -----
        """,
        # Braço direito
        """
           -----
           |   |
           O   |
          /|\\  |
               |
             -----
        """,
        # Perna esquerda
        """
           -----
           |   |
           O   |
          /|\\  |
          /    |
             -----
        """,
        # Perna direita (Game Over)
        """
           -----
           |   |
           O   |
          /|\\  |
          / \\  |
             -----
        """
    ]
    print(estagios[erros])

def jogar_forca():
    """Função principal do jogo da forca."""
    palavra_secreta = escolher_palavra()
    letras_descobertas = ["_" for _ in palavra_secreta]
    letras_erradas = []
    tentativas = 0
    max_tentativas = 4 # 6 estágios do boneco da forca

    print("Bem-vindo ao Jogo da Forca!")
    print(f"A palavra tem {len(palavra_secreta)} letras.")

    while True:
        mostrar_forca(tentativas)
        print("\n" + " ".join(letras_descobertas))
        print(f"Letras erradas: {', '.join(letras_erradas)}")

        if "_" not in letras_descobertas:
            print("\nParabéns! Você adivinhou a palavra!")
            print(f"A palavra era: {palavra_secreta}")
            break

        if tentativas >= max_tentativas:
            print("\nVocê perdeu! O boneco foi enforcado.")
            print(f"A palavra era: {palavra_secreta}")
            break

        try:
            chute = input("Digite uma letra ou a palavra completa: ").upper().strip()
            
            if not chute.isalpha():
                print("Entrada inválida. Digite apenas letras.")
                continue

            if len(chute) > 1: # Chute da palavra completa
                if chute == palavra_secreta:
                    print("\nParabéns! Você adivinhou a palavra completa!")
                    print(f"A palavra era: {palavra_secreta}")
                    break
                else:
                    print("Palavra errada!")
                    tentativas += 1
                    continue # Continua para a próxima rodada

            if chute in letras_descobertas or chute in letras_erradas:
                print("Você já tentou esta letra.")
                continue

            if chute in palavra_secreta:
                print(f"Boa! A letra '{chute}' está na palavra.")
                for i, letra in enumerate(palavra_secreta):
                    if letra == chute:
                        letras_descobertas[i] = chute
            else:
                print(f"Que pena! A letra '{chute}' não está na palavra.")
                letras_erradas.append(chute)
                tentativas += 1

        except Exception as e:
            print(f"esta não era palavra: {e}. Tente novamente.")

if __name__ == "__main__":
    jogar_forca()