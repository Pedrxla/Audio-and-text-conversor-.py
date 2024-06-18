import pyttsx3


def convertVoz(texto):
    engine = pyttsx3.init()
    engine.say(texto)
    engine.runAndWait()
    
    
convertVoz("Oi meu nome é pedro")
convertVoz("Teste sei la")
