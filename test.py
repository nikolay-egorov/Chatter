from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer

# Create a new chat bot named Charlie
chatbot = ChatBot('Charlie')

trainer = ListTrainer(chatbot)

trainer.train([
    "Привет, ты, наверное, новенький?",
    "Да, я бы хотел убраться отсюда",
    "Отсюда некуда ехать"
])

trainer.train('chatterbot.corpus.russian')
# Get a response to the input text 'I would like to book a flight.'
while True:
    message = input('Ты: ')
    if message.strip() != 'Пока':
        reply = chatbot.get_response(message)
        print('Бот:' , reply)
    if message.strip() == 'Пока':
        print('Бот : Пока')
        break