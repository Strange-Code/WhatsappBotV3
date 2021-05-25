from time import sleep
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
import re
from unicodedata import normalize
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("resource/botv3.json")
filepath = './resource/driver/whatsapp_session.txt'
driver = webdriver

firebase_admin.initialize_app(cred)


def crear_driver_session():

    with open(filepath) as fp:
        for cnt, line in enumerate(fp):
            if cnt == 0:
                executor_url = line
            if cnt == 1:
                session_id = line

    def new_command_execute(self, command, params=None):
        if command == "newSession":
            # Mock the response
            return {'success': 0, 'value': None, 'sessionId': session_id}
        else:
            return org_command_execute(self, command, params)
                
    org_command_execute = RemoteWebDriver.execute

    RemoteWebDriver.execute = new_command_execute

    new_driver = webdriver.Remote(command_executor=executor_url, desired_capabilities={})
    new_driver.session_id = session_id

    RemoteWebDriver.execute = org_command_execute

    return new_driver

def buscar_chats():
    print("BUSCANDO CHATS")

    if len(driver.find_elements_by_class_name("_2zkCi")) == 0:
        print("CHAT ABIERTO")
        message = identificar_mensaje()
        
        if message != None:
            return True

    chats = driver.find_elements_by_xpath('//div[@class ="_2aBzC"]')

    for chat in chats:
        #print("DETECTANDO MENSAJES SIN LEER")

        element_name = chat.find_elements_by_class_name("_3Dr46")
        name = element_name[0].text.lower().strip()

        chats_mensajes = chat.find_elements_by_class_name("_38M1B")

        if len(chats_mensajes) == 0:
            #print("CHATS ATENDIDOS")
            continue

        print("IDENTIFICANDO CONTACTO")
        firestore_db = firestore.client()
        snapshots = firestore_db.collection('contacto').where('nombre', '==', name).get()
        if not snapshots:
            print(name, "NO AUTORIZADO")
            continue

        print(name, "AUTORIZADO PARA SER ATENDIDO POR BOT")
        
        chat.click()
        return True
    return False

def normalizar(message: str):
    # -> NFD y eliminar diacríticos
    message = re.sub(
        r"([^n\u0300-\u036f]|n(?!\u0303(?![\u0300-\u036f])))[\u0300-\u036f]+", r"\1", 
        normalize( "NFD", message), 0, re.I
    )

    # -> NFC
    return normalize( 'NFC', message)

def identificar_mensaje():
    element_box_message = driver.find_elements_by_class_name("_3XpKm")
    posicion = len(element_box_message) -1

    color =  element_box_message[posicion].value_of_css_property("background-color")

    if color == "rgba(220, 248, 198, 1)" or color == "rgba(5, 97, 98, 1)":
        print("CHAT ATENDIDO")
        return
    
    element_message = element_box_message[posicion].find_elements_by_class_name("_3ExzF")
    message = element_message[0].text.lower().strip()
    print("MENSAJE RECIBIDO :", message)
    return normalizar(message)

def preparar_respuesta(message :str):
    print("PREPARANDO RESPUESTA")

    if message.__contains__("QUE ES STRANGECODE"):
        response = "StrangeCode es una comunidad de informaticos que les apasiona aprender y compartir conocimiento :-D \n" \
                        "Puedes visitar nuestra pagina web: https://strange-code.github.io/Links \n"
    elif message.__contains__("CUAL ES SU CANAL DE YOUTUBE"):
        response = "Puedes visitarnos en: https://www.youtube.com/channel/UCl24Q__MfUNDMhNWBluHcTg \n"
    elif message.__contains__("QUIERO UNIRME A LA COMUNIDAD"):
        response = "Puedes unirte a la comunidad ingresando al siguiente link: https://discord.com/invite/26ptv6URXY \n"
    elif message.__contains__("QUE PUEDES HACER"):
        text1 = open("./resource/respuesta1.txt", mode='r', encoding='utf-8')
        response = text1.readlines()
        text1.close()
    elif message.__contains__("GRACIAS"):
        response = "Ha sido un place ayudarte ;-)  \n"
    else:        
        response = "Hola, soy a Eva un bot creado por StrangeCode, preguntame ¿Qué puedo hacer? :-D \n"

    return response

def enviar_foto(foto: str):
    print("foto :", foto)
    WebDriverWait(driver, timeout= 3).until(lambda driver: driver.find_element_by_xpath('//*[@id="main"]/footer/div[1]/div[1]/div[2]/div/div')).click()
    file_image = WebDriverWait(driver, timeout= 10).until(lambda driver: driver.find_element_by_xpath('//input[@accept="image/*,video/mp4,video/3gpp,video/quicktime"]'))
    file_image.send_keys(foto)
    WebDriverWait(driver, timeout= 10).until(lambda driver: driver.find_element_by_xpath('//*[@id="app"]/div[1]/div[1]/div[2]/div[2]/span/div[1]/span/div[1]/div/div[2]/span/div/div')).click()

def enviar_documento(documento: str):
    print("documento :", documento)
    WebDriverWait(driver, timeout= 3).until(lambda driver: driver.find_element_by_xpath('//*[@id="main"]/footer/div[1]/div[1]/div[2]/div/div')).click()
    document = WebDriverWait(driver, timeout= 3).until(lambda driver: driver.find_element_by_xpath('//input[@accept="*"]'))
    document.send_keys(documento)
    WebDriverWait(driver, timeout= 10).until(lambda driver: driver.find_element_by_xpath('//*[@id="app"]/div[1]/div[1]/div[2]/div[2]/span/div[1]/span/div[1]/div/div[2]/span/div/div')).click()

def enviar_sticker(sticker: str):
    print("sticker :", sticker)
    WebDriverWait(driver, timeout= 3).until(lambda driver: driver.find_element_by_xpath('//*[@id="main"]/footer/div[1]/div[1]/div[1]/button[2]')).click()
    sleep(1)
    WebDriverWait(driver, timeout= 3).until(lambda driver: driver.find_element_by_xpath('//*[@id="main"]/footer/div[1]/div[1]/div[1]/button[4]')).click()
    WebDriverWait(driver, timeout= 3).until(lambda driver: driver.find_element_by_xpath('//*[@id="main"]/footer/div[2]/div/div[3]/div[1]/div/div[1]/div[1]/div/div/div[2]')).click()
    sticker_path = '//*[@id="main"]/footer/div[2]/div/div[3]/div[1]/div/div[1]/div[2]/div/div[{}]'.format(sticker)
    #print("sticker_path :", sticker_path)
    WebDriverWait(driver, timeout= 3).until(lambda driver: driver.find_element_by_xpath(sticker_path)).click()
    #Cierra
    WebDriverWait(driver, timeout= 3).until(lambda driver: driver.find_element_by_xpath('//*[@id="main"]/footer/div[1]/div[1]/div[1]/button[1]')).click()

def enviar_respuesta(respuesta: str):
    chatbox = driver.find_element_by_xpath('//*[@id="main"]/footer/div[1]/div[2]/div/div[2]')
    if respuesta.startswith("sticker_"):
        enviar_sticker(respuesta.replace('sticker_',''))
    elif respuesta.startswith("foto_"):
        enviar_foto(respuesta.replace('foto_',''))
    elif respuesta.startswith("documento_"):
        enviar_documento(respuesta.replace('documento_',''))
    else:
        print("respuesta : ", respuesta)
        chatbox.send_keys(respuesta+Keys.ENTER)

def procesar_mensaje(message :str):
    firestore_db = firestore.client()
    snapshots = firestore_db.collection('chat').get()

    for snapshot in snapshots:
        snap_dict = snapshot.to_dict()
        if message.__contains__(snap_dict.get("mensaje")):
            if "respuestas" in snap_dict:
                for respuesta in snap_dict.get("respuestas"):
                    enviar_respuesta(respuesta)
            else:
                response = snapshot.get("respuesta")
                enviar_respuesta(response)
            return
    enviar_respuesta("Lo siento, no te comprendí :-( . Puedes explicarme mejor :-D")

def whatsapp_boot_init():
    global driver
    driver = crear_driver_session()

    while True:
        if not buscar_chats():
            sleep(1)
            continue
        
        message = identificar_mensaje()

        if message == None:
            continue

        procesar_mensaje(message)


if __name__ == '__main__':
    whatsapp_boot_init()
