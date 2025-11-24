# Sistema Inteligente de Lembrete de Medicação com ESP32 e MQTT

Projeto IoT de um dispositivo portátil para lembretes de medicação. O sistema aciona alertas **sonoros (buzzer)** e **visuais (LED)** nos horários programados e permanece ativo até o usuário confirmar a dose pressionando um **botão físico**. O status dos eventos é enviado via **MQTT**, permitindo monitoramento remoto.

---

## Visão Geral

Este protótipo utiliza um **ESP32 DevKit C V4** como unidade central.  
Na simulação (Wokwi), o horário é controlado pelo **RTC interno do ESP32** configurado no código.  
No protótipo físico, o controle de tempo é garantido por um **RTC externo DS1307**, oferecendo maior estabilidade temporal sem depender de internet.

O projeto contribui para o **ODS 3 (Saúde e Bem-Estar)** ao apoiar a adesão correta a tratamentos medicamentoso.

---

## Funcionalidades

- ⏰ **Agenda de medicação** com múltiplos horários programáveis no código.
- 🔔 **Alerta sonoro e visual**: LED + buzzer intermitentes ao atingir o horário.
- ✅ **Confirmação de dose manual** por botão físico (encerra o alerta).
- 📡 **Comunicação MQTT** com envio de alertas e status.
- 🔄 **Reconexão automática** ao Wi-Fi e ao broker MQTT.
- 📅 **Reset diário automático** da agenda quando o dia muda.

---

## Hardware Utilizado

- ESP32 DevKit C V4
- RTC DS1307 (protótipo físico)
- LED indicador
- Buzzer piezoelétrico
- Push Button (confirmação)
- Jumpers e protoboard  
- (Opcional) Bateria Li-Po 3,7 V + módulo TP4056 (versão portátil)

---

## Ligações (GPIO)

| Componente | Pino ESP32 |
|-----------|------------|
| LED       | GPIO 2     |
| Buzzer    | GPIO 15    |
| Botão     | GPIO 4 (PULL_UP interno) |
| RTC DS1307 (I2C) | SDA GPIO 21 / SCL GPIO 22 |

---

## Software / Firmware

O código da simulação foi escrito em **MicroPython** e implementa:

- conexão Wi-Fi
- conexão MQTT
- controle de agenda via lista `HORARIOS_DOSE`
- leitura do RTC interno (simulação)
- acionamento de LED/buzzer até confirmação
- publicação de mensagens MQTT

### Principais parâmetros do código

- **Broker MQTT:** `broker.hivemq.com`
- **Tópicos MQTT:**
  - `medicacao/alerta` → enviado quando o alarme dispara
  - `medicacao/status` → enviado para status (*alerta ativo*, *dose confirmada*)
- **Horários da dose:** definidos em `HORARIOS_DOSE`  
  Exemplo:
  ```python
  HORARIOS_DOSE = [
      (8, 30),
      (14, 30),
      (20, 30),
  ]
