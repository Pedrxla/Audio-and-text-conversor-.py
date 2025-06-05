import speech_recognition as sr

reconhecedor = sr.Recognizer()
microfone = sr.Microphone()

with microfone as source:
    print("Fale alguma coisa...")
    reconhecedor.adjust_for_ambient_noise(source)
    audio = reconhecedor.listen(source)

    try:
        texto = reconhecedor.recognize_google(audio, language='pt-BR')
        print("Você disse:", texto)
    except sr.UnknownValueError:
        print("Não entendi o que você disse.")
    except sr.RequestError as e:
        print("Erro de conexão com o Google:", e)
