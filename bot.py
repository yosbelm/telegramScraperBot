import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext, JobQueue
from datetime import time
from spider import ejecutar_spider
import asyncio
import multiprocessing
from dotenv import load_dotenv
import os

# Configura tu token
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
bot_active = False
mensajes_enviados = set()


async def start(update: Update, context: CallbackContext) -> None:
    global bot_active
    if not bot_active:
        bot_active = True
        await update.message.reply_text('¡Hola! Soy un bot y te enviaré mensajes cada 5 minutos.')
        context.job_queue.run_repeating(send_message, interval=10, first=0, chat_id=update.effective_chat.id)
    else:
        await update.message.reply_text('El bot ya está en funcionamiento.')



async def exit_bot(update: Update, context: CallbackContext) -> None:
    global bot_active
    bot_active = False
    await update.message.reply_text('El bot se ha detenido. Usa /start para iniciarlo.')
    context.job_queue.stop()



# Función que envía un mensaje cada x minutos
async def send_message(update: Update, context: CallbackContext) -> None:
    while True:
        # Crear un proceso separado para ejecutar la spider
        with multiprocessing.Pool(1) as pool:
            datos = pool.apply(ejecutar_spider)

        print("Resultados obtenidos:")
        for item in datos:
            try:
                texto = item.get("texto", "").encode('utf-8').decode('utf-8')

                # Comprobar si el mensaje ya fue enviado
                if texto not in mensajes_enviados:
                    mensajes_enviados.add(texto)
                    await update.message.reply_text(text=texto)
                else:
                    print("Mensaje repetido, no se enviará.")
            except Exception as e:
                texto = item.get("texto", "")
                if texto not in mensajes_enviados:
                    mensajes_enviados.add(texto)
                    await update.message.reply_text(text=texto)
                else:
                    print("Mensaje repetido, no se enviará.")

        await asyncio.sleep(1*60)



def main() -> None:
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("exit", exit_bot))
    app.add_handler(CommandHandler("activar", send_message))

    app.run_polling()

if __name__ == '__main__':
    main()
