import speech_recognition as sr

def convertVoz():
    r = sr.SpeechRecognition()
    with sr.Microphone() as source:
        audio = r.listen(source)
        print("Capturou o audio")
        try:
            print("Pode falar")
            text = self.r.recognize_sphinx(audio)
            print(text)
        except sr.UnknowValueError:
            print("Sphinx could not understand audio")
        except sr.RequestError as e:
            print("Sphinx error; {0}".format(e))
        
convertVoz()