import os, telebot  # For telebot
import requests, pyaudio, speech_recognition as sr  # For querying context
from pydub import AudioSegment   # To create a PCM .wav file

# Uses pyTelegramBotAPI to create bot
TELE_BOT_TOKEN = '5691095287:AAGNxj2Rbh7IKLBVm0f1v0UBlZPfYhcoXxk'
bot = telebot.TeleBot(TELE_BOT_TOKEN)

# Global variables
global CHAT_ID, username, contact
CHAT_ID = ""
username = ""
contact = "+65 61234567"

# Uses "distilbert-base-cased-distilled-squad" model from HuggingFace
HF_API_TOKEN = "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"
HF_API_URL = "https://api-inference.huggingface.co/models/distilbert-base-cased-distilled-squad"
headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}

# Reads the FAQ and stores as 'context'
text_file = open("context.txt", "r")
context = text_file.read()

def query(payload):
    """Function to query context using Hugging Face API."""
    response = requests.post(HF_API_URL, headers=headers, json=payload)
    return response.json()

def ogg2wav(ofn):
    """Function to convert telegram .ogg file to .wav"""
    wfn = ofn.replace('.ogg','.wav')
    x = AudioSegment.from_file(ofn)
    x.export(wfn, format='wav')    

def check_score(score, contact):
    """Function to check confidence score and output to user."""
    if score <= 0.3:
        score_message = f'I am not very confident with my answer. Perhaps you can contact us @ {contact}. '
    elif score >= 0.7:
        score_message = f'I am confident with my answer. Source: Trust me. '
    else:
        score_message = ''
    return score_message

# Start command in bot

@bot.message_handler(commands=['start', 'help'])   
def send_welcome(pm):
    # Start message
    sent_msg = bot.send_message(pm.chat.id, "Hey there! Michael here. What would you like to know about Diamond PC Solutions?" + 
                                "\n\n" + "Type them out or send me a voice message. I'm not smart but I am a little smart.")
    bot.parse_mode
    id = pm.chat.id
    name = pm.chat.username
    global CHAT_ID, username
    CHAT_ID = id
    username = name
    print(f'User: {username} with id:{CHAT_ID} clicked /start')
    
    bot.register_next_step_handler(sent_msg, user_question)     #   Message to call user_question function

#   Further queries

@bot.message_handler(commands=['ask'])   
def further_qns(pm):
    # Function to prompt for further questions from users
    sent_msg = bot.send_message(pm.chat.id, "What's your question?")
    bot.parse_mode
    bot.register_next_step_handler(sent_msg, user_question)     #   Message to call user_question function

# Get user question

def user_question(question):
    # Save user question for text input
    if question.content_type == 'text':
        query = str(question.text)
        question_text = query 
        get_answer(question_text)

    elif question.content_type == 'voice':
        voice_info = bot.get_file(question.voice.file_id)
        downloaded_file = bot.download_file(voice_info.file_path)   # Get user voice message as audio file

        with open('query.ogg', 'wb') as new_file:
            new_file.write(downloaded_file)

        ogg2wav('query.ogg')            # Convert .ogg to PCM .wav file

        # use the audio file as the audio source
        r = sr.Recognizer()
        with sr.AudioFile('query.wav') as source:
            audio = r.record(source)  # read the entire audio file

        data = r.recognize_google(audio, show_all=True)     # To print audio into text
        question_text = data['alternative'][0]['transcript']
        get_answer(question_text)

# Get answer for user's query
    
def get_answer(question_text):
    output = query({
	    "inputs": {"question": question_text + '\n' + 'Give me a detailed answer.',
                    "context": context
                    }})
    
    print(output)
    response_answer = output['answer']
    
    # Print question and answer
    print(f"Question: {question_text}\n")
    print(f"Response: {output['answer']}")

    user_id = CHAT_ID

    # Send response to user
    contact_number = contact
    confidence = check_score(float(output['score']), contact)
    response = bot.send_message(user_id, text = f"{response_answer} \n\n{confidence}If you still have further questions, please /ask me.")
    return response_answer

bot.infinity_polling()

