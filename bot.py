# -*- coding: utf-8 -*-
import telebot
from datetime import datetime, time

TOKEN = "8890779534:AAEe4i6q72RYGcWL14JvqcymPI_YcQJ90us"
bot = telebot.TeleBot(TOKEN)

users = {}
tests = {}
answers = {}
results = []
question_wrong = []

# -------- START (ism olish) --------
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Ism-familiyangizni kiriting:")
    bot.register_next_step_handler(message, save_name)

def save_name(message):
    users[message.chat.id] = message.text
    bot.send_message(message.chat.id, f"Salom {message.text}! Testni kuting.")

# -------- TEST YARATISH --------
@bot.message_handler(commands=['yangi_test'])
def yangi_test(message):
    bot.send_message(message.chat.id, "Test nomini kiriting:")
    bot.register_next_step_handler(message, test_name)

def test_name(message):
    tests["nom"] = message.text
    bot.send_message(message.chat.id, "Javob kalitini kiriting:")
    bot.register_next_step_handler(message, test_key)

def test_key(message):
    tests["kalit"] = message.text.strip().upper()
    bot.send_message(message.chat.id, "Tugash vaqtini kiriting (masalan 20:30):")
    bot.register_next_step_handler(message, test_time)

def test_time(message):
    h, m = map(int, message.text.strip().split(":"))
    tests["deadline"] = time(h, m)

    answers.clear()
    results.clear()
    question_wrong.clear()

    bot.send_message(message.chat.id,
        f"Test saqlandi ?\n"
        f"Nom: {tests['nom']}\n"
        f"Tugash vaqti: {message.text}")

# -------- TEST YOPILGANMI --------
def is_closed():
    return datetime.now().time() >= tests["deadline"]

# -------- JAVOB TEKSHIRISH --------
@bot.message_handler(func=lambda m: True)
def check(message):

    if "kalit" not in tests:
        bot.send_message(message.chat.id, "Hozircha test yo‘q ?")
        return

    if is_closed():
        bot.send_message(message.chat.id, "Test yopilgan ??")
        return

    if message.chat.id in answers:
        bot.send_message(message.chat.id, "Siz allaqachon javob yuborgansiz ?")
        return

    user_ans = message.text.strip().upper()
    key = tests["kalit"]

    correct = 0

    for i, (u, k) in enumerate(zip(user_ans, key)):
        if u == k:
            correct += 1
        else:
            question_wrong.append(i + 1)

    score = correct
    answers[message.chat.id] = (score, datetime.now())

    results.append({
        "id": message.chat.id,
        "name": users.get(message.chat.id, "O‘quvchi"),
        "score": score,
        "time": datetime.now()
    })

    bot.send_message(message.chat.id,
        f"?? {tests['nom']}\n"
        f"? Natija: {score}/{len(key)}\n"
        f"?? Foiz: {score/len(key)*100:.0f}%")

# -------- YAKUNLASH + REYTING --------
@bot.message_handler(commands=['yakunla'])
def yakunla(message):

    if not results:
        bot.send_message(message.chat.id, "Hech kim qatnashmagan")
        return

    sorted_results = sorted(
        results,
        key=lambda x: (-x["score"], x["time"])
    )

    text = "?? NATIJALAR:\n\n"

    medals = ["??", "??", "??"]

    for i, r in enumerate(sorted_results):
        if i < 3:
            text += f"{medals[i]} {r['name']} - {r['score']}\n"
        else:
            text += f"?? {r['name']} - {r['score']}\n"

    # -------- 50%+ xato savollar --------
    text += "\n?? 50%+ xato savollar:\n"

    wrong_count = {}
    total = len(results)

    for q in question_wrong:
        wrong_count[q] = wrong_count.get(q, 0) + 1

    found = False

    for q, c in wrong_count.items():
        if c / total >= 0.5:
            text += f"? Savol {q}\n"
            found = True

    if not found:
        text += "Yuqori xatolik yo‘q ??"

    bot.send_message(message.chat.id, text)

# -------- BOT ISHLASH --------
bot.polling()
