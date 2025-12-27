import json
from difflib import get_close_matches
import tkinter as tk
from tkinter import simpledialog, messagebox


def load_knowledge_base(file_path: str):
    with open(file_path, 'r', encoding="utf-8") as file:
        data: dict = json.load(file)
    return data


def save_knowledge_base(file_path: str, data: dict):
    with open(file_path, 'w', encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def find_best_match(user_question: str, questions: list[str]) -> str | None:
    matches: list = get_close_matches(user_question, questions, n=1, cutoff=0.6)
    return matches[0] if matches else None


def get_answer_for_question(question: str, knowledge_base: dict) -> str | None:
    for q in knowledge_base["questions"]:
        if q["question"] == question:
            return q["answer"]
    return None


knowledge_base = load_knowledge_base('knowledge_base.json')
window = tk.Tk()
window.state('zoomed')
window.bind("<Escape>", lambda e: window.attributes("-fullscreen", False))
window.title("Chatbot")


def get_bot_response(user_message: str, knowledge_base: dict) -> str:
    best_match = find_best_match(
        user_message,
        [q["question"] for q in knowledge_base["questions"]]
    )

    if best_match:
        return get_answer_for_question(best_match, knowledge_base)

    teach = messagebox.askyesno(
        "Bilmiyorum",
        "Bu sorunun cevabını bilmiyorum, bana öğretmek ister misin?"
    )

    if teach:
        return learn_new_answer(user_message)
    else:
        return "Peki, bunu geçiyorum."


def learn_new_answer(question: str):
    answer = simpledialog.askstring(
        "Bana öğret",
        f"Bu sorunun cevabını bilmiyorum:\n\n{question}\n\nNasıl cevap vermeliyim?"
    )

    if answer and answer.strip():
        knowledge_base["questions"].append({
            "question": question,
            "answer": answer
        })
        save_knowledge_base('knowledge_base.json', knowledge_base)
        return "Teşekkürler, yeni şeyler öğrendim 😊"

    return "Tamam, bunu öğrenmeyeceğim."


def send_message(event=None):
    message = input_entry.get()

    if message.strip() == "":
        return

    chat_area.config(state="normal")
    chat_area.insert(tk.END, f"Sen: {message}\n")

    bot_response = get_bot_response(message, knowledge_base)
    chat_area.insert(tk.END, f"ChatBot: {bot_response}\n\n")

    chat_area.config(state="disabled")

    input_entry.delete(0, tk.END)


chat_frame = tk.Frame(window)
chat_frame.pack(fill=tk.BOTH, expand=True)

input_frame = tk.Frame(window)
input_frame.pack(fill=tk.X)

chat_area = tk.Text(chat_frame, height=20, width=60)
chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
chat_area.config(state="disabled")

input_entry = tk.Entry(input_frame)
input_entry.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.X, expand=True)
input_entry.bind("<Return>", send_message)

send_button = tk.Button(input_frame, text="Gönder", command=send_message)
send_button.pack(side=tk.RIGHT, padx=10)

window.mainloop()
