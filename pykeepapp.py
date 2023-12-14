import pykeepass
from pysnmp.hlapi import *
import ping3
import time

telegram_bot_api = "6008447382:AAG-tSYm3NXbiMGlk6KXrRpr1AtN9PWLIIA" # Telegram Api ID

#Funcion mensajeria Telegram
def teleSMS(sms):
    import requests

    TOKEN = "5877184377:AAGtpkkn1vv8En9dOAI8ud1Z-mE6AdUNk34"
    #CHAT_ID = "448460485"
    #CHAT_ID2 = "5877184377"
    GROUP_ID  = "-1001973955375"

    send_text = 'https://api.telegram.org/bot' + TOKEN + '/sendMessage?chat_id=' + GROUP_ID + '&parse_mode=Markdown&text=' + sms

    try:
        response = requests.get(send_text)
    except:
        teleSMS('Error en teleSMS')
    
# Funcion control de Ping    
def alive(address):
    lost = 0
    for cont in range(3):
        if ping3.ping(address) == None:
            lost += 1    
        

    if lost >= 2:
        return False
    
    else:
        teleSMS('Error de Ping')
        return True

# Captura de valores por SNMP
def getOID(address):
    oid = "1.3.6.1.4.1.1918.2.13.10.40.10.0"
    comunidad = "public"
    puerto = 161
    
    try:
        resultado = next(getCmd(SnmpEngine(),
                    CommunityData(comunidad),
                    UdpTransportTarget((address, puerto)),
                    ContextData(),
                    ObjectType(ObjectIdentity(oid))))

    
        return str(resultado[3][0].prettyPrint()[-3:])
    
    except:
        teleSMS('Error de getOID')
        return False

# Main
print("Comienza el Monitoreo")   
alarmas = {} #inicializamos el diccionario
alcanzables = {} # inicializamos diccionario de alcanzabilidad

try:
    db = pykeepass.PyKeePass(r'\\H:\Unidades compartidas\Operaciones\Mantenimiento\password.kdbx', password='aITX8QekV9IwS3f8Xij8')  # abre la base de datos
except:
    print('Error de DB')

while True:
    # itera a través de cada grupo
    for group in db.groups:
        #print("Grupo: " + group.name)
    
        if group.name == "Traza Valle Fértil" or group.name == "Traza Jáchal" or group.name == "Traza Tontal":
        
            # itera a través de cada entrada en el grupo
            for entry in group.entries:
                
                print(entry.url[8:])
            
                if entry.title != None and entry.url != None and alive(entry.url[8:]) != False and getOID(entry.url[8:]) != False:
                    
                    #print('Primer If')
                    
                    if entry.url[8:] in alarmas:
                    
                        del alarmas[entry.url[8:]]
                        
                        teleSMS(entry.title + "\t" + "El dispositivo normalizó el voltaje de entrada")
                
                    elif entry.url[8:] in alcanzables:
                    
                        del alcanzables[entry.url[8:]]
                        
                        teleSMS(entry.title + "\t" + "El dispositivo volvió a tener conectividad")
            
                elif entry.title != None and entry.url != None and alive(entry.url[8:]) != False and getOID(entry.url[8:]) == False and entry.url[8:] not in alarmas:      
                                                      
                    alarmas[entry.url[8:]] = entry.title
                
                    teleSMS(entry.title + "\t" + "Voltaje de Entrada: " + getOID(entry.url[8:]))      
                           
                elif entry.title != None and entry.url != None and alive(entry.url[8:]) != True and entry.url[8:] not in alcanzables:
                    
                    alcanzables[entry.url[8:]] = entry.title
                
                    teleSMS(entry.title + "\t" + "Dispositivo Inalcanzable ")
                              
    time.sleep(300)
