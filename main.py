"""
Sistema Inteligente de Medicação - ESP32 + MQTT + RTC interno
Alerta sonoro/visual permanece ativo até o usuário confirmar a dose.
"""

import network
import time
from machine import Pin, RTC
from umqtt.simple import MQTTClient
import ujson

# --- Configuração de Rede e MQTT ---
WIFI_SSID = "Wokwi-GUEST"
WIFI_PASSWORD = ""
MQTT_BROKER = "broker.emqx.io"
MQTT_CLIENT_ID = "ESP32-MedReminder"
MQTT_TOPIC_ALERT = "medicacao/alerta"
MQTT_TOPIC_STATUS = "medicacao/status"

# --- Pinos do ESP32 ---
LED_PIN = 2
BUZZER_PIN = 15
BUTTON_PIN = 4

led = Pin(LED_PIN, Pin.OUT)
buzzer = Pin(BUZZER_PIN, Pin.OUT)
button = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_UP)

# --- RTC interno do ESP32 ---
rtc = RTC()

# Configura data/hora inicial para a SIMULAÇÃO
# (ano, mês, dia, dia_semana, hora, minuto, segundo, subseg)
# Ajustei para ficar alguns segundos antes de um dos horários da lista para o teste do video
rtc.datetime((2025, 11, 12, 2, 8, 29, 50, 0))  # 2025-11-12 08:29:50

# --- Horários de medicação: lista de (hora, minuto) ---

#Pode ser adicionado novos horarios ou excluir existentes aqui:
HORARIOS_DOSE = [
    (8, 30),
    (14, 30),
    (20, 30),
]

# Marca se cada horário já disparou no dia atual
disparos_registrados = {hm: False for hm in HORARIOS_DOSE}
dia_atual = rtc.datetime()[2]  # dia do mês

wlan = None
client = None

# ------------------ FUNÇÕES AUXILIARES ------------------ #
def conectar_wifi():
    global wlan
    if wlan is None:
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
    # Enquanto o dispositivo não conecta fica escrevendo "." a cada 0.5 seg, até conectar 
    # PS: Pode demorar devido utilizar um dispositivo simulado em um servidor
    if not wlan.isconnected():
        print("Conectando ao WiFi...", end="")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        while not wlan.isconnected():
            print(".", end="")
            time.sleep(0.5)
        print("\nWiFi conectado! IP:", wlan.ifconfig()[0])
    return wlan

# Função parecida ao Wifi
def conectar_mqtt():
    global client
    print("Conectando ao broker MQTT...")
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER)
    client.connect()
    print("Conectado ao broker!")
    return client

def reconectar():
    #Tenta reconectar WiFi e MQTT quando a conexão cai.
    print("⚠️  Tentando reconectar...")
    conectar_wifi()
    conectar_mqtt()

def enviar_mqtt(topico, payload):
    #Publica mensagem no MQTT com tratamento de erro.
    global client
    if isinstance(payload, str):
        payload = payload.encode()

    try:
        client.publish(topico, payload)
    except OSError as e:
        print("Erro ao publicar (", e, ") -> reconectando...")
        reconectar()
        try:
            client.publish(topico, payload)
        except OSError as e2:
            print("Falha ao publicar mesmo após reconectar:", e2)

def enviar_status(status):
    msg = ujson.dumps({"status": status})
    print("[MQTT ENVIADO]", msg)
    enviar_mqtt(MQTT_TOPIC_STATUS, msg)

def acionar_alerta_ate_confirmacao():
    #Mantém LED e buzzer ativos até o botão ser pressionado.
    print("🚨 Horário de medicação! Esperando confirmação...")
    enviar_status("Alerta ativo - aguardando confirmação")

    while button.value() == 1:  # PULL_UP -> 1 solto, 0 pressionado
        led.on()
        buzzer.on()
        time.sleep(0.3)
        led.off()
        buzzer.off()
        time.sleep(0.3)

    enviar_status("Dose confirmada")
    print("✅ Dose confirmada pelo usuário.")
    led.off()
    buzzer.off()
    time.sleep(0.5)

# ------------------ PROGRAMA PRINCIPAL ------------------ #

conectar_wifi()
conectar_mqtt()

print("RTC inicial:", rtc.datetime())

while True:
    try:
        # lê data/hora atual
        ano, mes, dia, dsem, hora, minuto, segundo, sub = rtc.datetime()

        # se o dia mudou, reseta os disparos
        if dia != dia_atual:
            dia_atual = dia
            disparos_registrados = {hm: False for hm in HORARIOS_DOSE}
            print("🔁 Novo dia detectado, reiniciando agenda de medicação.")

        # verifica se algum horário deve disparar agora
        for (h, m) in HORARIOS_DOSE:
            if hora == h and minuto == m and not disparos_registrados[(h, m)]:
                enviar_mqtt(MQTT_TOPIC_ALERT, "ALARME_DISPARADO")
                acionar_alerta_ate_confirmacao()
                disparos_registrados[(h, m)] = True
                break  # evita disparar mais de um horário no mesmo minuto

        time.sleep(0.5)

    except OSError as e:
        print("Erro de conexão no loop principal:", e)
        reconectar()