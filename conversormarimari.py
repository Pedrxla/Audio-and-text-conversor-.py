import os
import tkinter as tk
from tkinter import ttk
import sounddevice as sd
import numpy as np
import wave
import threading
import speech_recognition as sr
from datetime import datetime
import webbrowser

desktop = os.path.join(os.path.join(os.environ["USERPROFILE"]), "Desktop")
gravacoes_dir = os.path.join(desktop, "Gravações")
os.makedirs(gravacoes_dir, exist_ok=True)

gravando = False
pausado = False
audio_data = []
sample_rate = 44100


def callback(indata, frames, time, status):
    if gravando and not pausado:
        audio_data.append(indata.copy())


def iniciar_gravacao():
    global gravando, pausado, audio_data, stream
    if not gravando:
        audio_data = []
        gravando = True
        pausado = False
        indicador_gravacao.config(bg="red")
        status_label.config(text="Gravando...", fg="red")
        stream = sd.InputStream(callback=callback, channels=1, samplerate=sample_rate)
        stream.start()
    elif pausado:
        pausado = False
        indicador_gravacao.config(bg="red")
        status_label.config(text="Gravando...", fg="red")


def pausar_gravacao():
    global pausado
    if gravando and not pausado:
        pausado = True
        indicador_gravacao.config(bg="gray")
        status_label.config(text="Gravação pausada. Clique em 'Iniciar' para retomar.", fg="orange")
        threading.Thread(target=processar_audio).start()


def parar_gravacao():
    global gravando, pausado, stream
    if gravando:
        gravando = False
        pausado = False
        indicador_gravacao.config(bg="gray")
        status_label.config(text="Gravação finalizada. Arquivo salvo na pasta 'Gravações' na área de trabalho.", fg="green")
        stream.stop()
        stream.close()
        threading.Thread(target=processar_audio).start()


def salvar_audio_wav():
    agora = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"Gravacao_{agora}.wav"
    path = os.path.join(gravacoes_dir, filename)

    if audio_data:
        audio_np = np.concatenate(audio_data, axis=0)
        audio_np = (audio_np * 32767).astype(np.int16)

        with wave.open(path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(audio_np.tobytes())

        return path
    return None


def processar_audio():
    path_wav = salvar_audio_wav()
    if not path_wav:
        return

    reconhecedor = sr.Recognizer()
    with sr.AudioFile(path_wav) as source:
        audio = reconhecedor.record(source)

    try:
        texto = reconhecedor.recognize_google(audio, language="pt-BR")
        texto = pontuar_texto(texto)
    except sr.UnknownValueError:
        texto = "[Não foi possível reconhecer o áudio.]"
    except sr.RequestError as e:
        texto = f"[Erro de conexão: {e}]"

    atualizar_texto(texto)
    salvar_texto(texto)

    audio_data.clear()


def pontuar_texto(texto):
    perguntas = [
        "quem", "quando", "onde", "como", "qual",
        "quais", "por que", "o que", "pra que",
    ]
    texto_lower = texto.lower()
    for p in perguntas:
        if texto_lower.startswith(p) or f" {p} " in texto_lower:
            return texto.strip().capitalize() + "?"
    return texto.strip().capitalize() + "."


def atualizar_texto(texto):
    texto_area.insert(tk.END, texto + "\n")
    texto_area.see(tk.END)


def salvar_texto(texto):
    agora = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    caminho = os.path.join(gravacoes_dir, f"Transcricao_{agora}.txt")
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(texto)


def abrir_chatgpt():
    webbrowser.open("https://chat.openai.com")


# ===== INTERFACE GRÁFICA =====
janela = tk.Tk()
janela.title("Gravador de Voz em Texto")
janela.geometry("650x450")

abas = ttk.Notebook(janela)
aba_gravador = tk.Frame(abas)
aba_gpt = tk.Frame(abas)

abas.add(aba_gravador, text="Gravador")
abas.add(aba_gpt, text="Corretor Ortográfico")
abas.pack(expand=1, fill="both")

# ==== ABA: Gravador ====
frame_botoes = tk.Frame(aba_gravador)
frame_botoes.pack(anchor="nw", pady=10, padx=10)  # Alinhado ao canto superior esquerdo

btn_iniciar = tk.Button(frame_botoes, text="Iniciar", command=iniciar_gravacao)
btn_iniciar.grid(row=0, column=0, padx=5)

btn_pausar = tk.Button(frame_botoes, text="Pausar", command=pausar_gravacao)
btn_pausar.grid(row=0, column=1, padx=5)

btn_parar = tk.Button(frame_botoes, text="Parar", command=parar_gravacao)
btn_parar.grid(row=0, column=2, padx=5)

indicador_gravacao = tk.Canvas(
    frame_botoes, width=20, height=20, bg="gray",
    highlightthickness=1, highlightbackground="black"
)
indicador_gravacao.grid(row=0, column=3, padx=5)

# Label de status (ao lado dos botões)
status_label = tk.Label(frame_botoes, text="Aguardando...", fg="black", font=("Arial", 10, "italic"))
status_label.grid(row=0, column=4, padx=10)

texto_area = tk.Text(aba_gravador, wrap=tk.WORD, height=20)
texto_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# ==== ABA: Revisão GPT ====
mensagem = tk.Label(
    aba_gpt,
    text=(
        "Este programa utiliza inteligência artificial para converter sua fala em texto, "
        "mas pode não corrigir 100% da pontuação ou ortografia automaticamente.\n\n"
        "Para garantir a melhor qualidade na revisão do seu texto, recomendamos utilizar o ChatGPT "
        "para correções mais avançadas."
    ),
    wraplength=600,
    justify="left",
)
mensagem.pack(padx=20, pady=20)

btn_chatgpt = tk.Button(
    aba_gpt,
    text="Corrigir no GPT",
    command=abrir_chatgpt,
    bg="#10a37f",
    fg="white",
    padx=10,
    pady=5,
)
btn_chatgpt.pack(pady=10)

janela.mainloop()
