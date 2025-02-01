from spider import ejecutar_spider
import asyncio
import multiprocessing
from dotenv import load_dotenv
import os
from telegram import Bot


load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
CHECK_INTERVAL = 20  # Tiempo que el bot busca nuevos mensajes (en segundos)
mensajes_enviados = set()


async def send_message(bot: Bot) -> None:
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
                    await bot.send_message(chat_id=CHAT_ID, text=texto)
                else:
                    print(texto)
                    print("Mensaje repetido, no se enviará.")
            except Exception as e:
                texto = item.get("texto", "")
                if texto not in mensajes_enviados:
                    mensajes_enviados.add(texto)
                    await bot.send_message(chat_id=CHAT_ID, text=texto)
                else:
                    print("Mensaje repetido, no se enviará.")

        await asyncio.sleep(CHECK_INTERVAL)



def main():
    bot = Bot(token=TOKEN)
    print(mensajes_enviados)
    asyncio.run(send_message(bot))

if __name__ == '__main__':
    main()
