import os
import subprocess
import telebot
from telebot import types # Importamos los tipos para los botones
import threading

# --- CONFIGURACIÓN ---
API_TOKEN = 'token de telegram'
ID_DUENO = id # Reemplaza con tu ID de Telegram (puedes obtenerlo enviando un mensaje al bot @userinfobot) 
bot = telebot.TeleBot(API_TOKEN)

# --- SCRIPT DE LIMPIEZA (POWERSHELL) ---
POWERSHELL_CLEAN = """
$ErrorActionPreference = 'SilentlyContinue'
# Limpieza de Escritorio, Descargas y Temporales
$Paths = @("$env:USERPROFILE\\Desktop\\*", "$env:USERPROFILE\\Downloads\\*", "$env:TEMP\\*")
foreach ($p in $Paths) { Remove-Item -Path $p -Recurse -Force }

# Desinstalación de apps no nativas
winget uninstall --all --silent --force --accept-source-agreements

# OPCIONAL: Para reseteo total de fábrica, descomenta la línea de abajo:
# systemreset -factoryreset
"""

def ejecutar_limpieza():
    subprocess.Popen(["powershell.exe", "-ExecutionPolicy", "Bypass", "-Command", POWERSHELL_CLEAN])

# 1. Comando inicial
@bot.message_handler(commands=['wipe_pc'])
def ask_confirmation(message):
    if message.from_user.id == ID_DUENO:
        # Creamos los botones
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn_confirmar = types.InlineKeyboardButton("🚀 SÍ, EJECUTAR PURGA", callback_data="confirmar_wipe")
        btn_cancelar = types.InlineKeyboardButton("❌ CANCELAR", callback_data="cancelar_wipe")
        
        markup.add(btn_confirmar, btn_cancelar)
        
        bot.send_message(ID_DUENO, "❗ **ATENCIÓN: SE HA SOLICITADO LIMPIEZA REMOTA**\n"
                                   "Esta acción eliminará archivos del escritorio, descargas y programas.\n"
                                   "¿Deseas continuar?", reply_markup=markup, parse_mode="Markdown")
    else:
        bot.reply_to(message, "Acceso denegado.")

# 2. Manejador de la respuesta de los botones
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "confirmar_wipe":
        # Editamos el mensaje para que no se puedan volver a pulsar los botones
        bot.edit_message_text(chat_id=ID_DUENO, message_id=call.message.message_id, 
                              text="☢️ **PURGA INICIADA.** El equipo se está formateando...")
        
        # Ejecutar limpieza en segundo plano
        threading.Thread(target=ejecutar_limpieza).start()
        
    elif call.data == "cancelar_wipe":
        bot.edit_message_text(chat_id=ID_DUENO, message_id=call.message.message_id, 
                              text="✅ **Acción cancelada.** No se realizaron cambios.")

if __name__ == "__main__":
    print("Agente con confirmación activo...")
    bot.infinity_polling()