import telebot
import urllib.request
import os
from model_style_transfer import style_transfer, imsave
import matplotlib.pyplot as plt

token = '1721312891:AAFR7qoUMRnJuf8rEDvTfYXm323d8NxtlpM'
bot = telebot.TeleBot(token)
state = 'wait_content'

# сохраняем фото в /tmp и очищаем его
result_storage_path = 'tmp'  

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, f'Привет, {message.from_user.first_name}. Это Style-Transfer бот. Нужно прислать последовательно картинки контента и стиля, чтобы получить результат.')

    bot.send_photo(message.chat.id, open("{0}".format('demo.jpeg'), 'rb'), 'Это пример работы продвинутого Style Transfer алгоритма')

    if state == 'wait_content':
        bot.send_message(message.from_user.id, 'Пришлите изображение контента')
    else:
        bot.send_message(message.from_user.id, 'Пришлите изображение стиля')

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    bot.send_message(message.from_user.id, 'Не понимаю, что это значит.')
    if state == 'wait_content':
        bot.send_message(message.from_user.id, 'Пришлите изображение контента')
    else:
        bot.send_message(message.from_user.id, 'Пришлите изображение стиля')

@bot.message_handler(content_types=['photo'])
def get_photo_messages(message):
    global state
    if state == 'wait_content':
        image_name = save_image_from_message(message, 'content')

        # processing
        # bot.send_photo(message.chat.id, open("{0}/{1}".format(result_storage_path, image_name), 'rb'), 'Просто дублирование картинки')
        
        # send results
        output = 'Теперь пришлите изображение стиля\n'
        bot.reply_to(message, output)
        state = 'wait_style'
    else:
        image_name = save_image_from_message(message, 'style')
        output = 'Идет обработка изображений, пожалуйста ожидайте\n'
        bot.reply_to(message, output)

        # processing
        output = style_transfer( )

        imsave(output, "{0}/{1}".format(result_storage_path, 'output.png'))
        
        
        # send results
        bot.send_photo(message.chat.id, open("{0}/{1}".format(result_storage_path, 'output.png'), 'rb'), 'Стилизованное изображение')

        state = 'wait_content'

   
    



# ----------- Вспомогательные функции ---------------

def get_image_id_from_message(message):
    # Для альбома фото возьмем последний файл
    return message.photo[len(message.photo)-1].file_id

def save_image_from_message(message, type='content'):
    cid = message.chat.id
    
    image_id = get_image_id_from_message(message)
    
    # bot.send_message(cid, 'Преобразование изображения')
    
    # подготовить изображение к загрузке
    file_path = bot.get_file(image_id).file_path

    # генерация url картинки
    image_url = "https://api.telegram.org/file/bot{0}/{1}".format(token, file_path)
    print(image_url)
    
    # создаем временную папку
    if not os.path.exists(result_storage_path):
        os.makedirs(result_storage_path)
    
    # получение и сохранение картинки
    image_name = type + ".jpg"
    urllib.request.urlretrieve(image_url, "{0}/{1}".format(result_storage_path,image_name))
    
    return image_name

def cleanup_remove_image(image_name):
    os.remove('{0}/{1}'.format(result_storage_path, image_name))

bot.polling(none_stop=True)