import json
from difflib import get_close_matches
import tkinter as tk
from tkinter import simpledialog, messagebox


def load_knowledge_base(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_knowledge_base(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def find_best_match(user_question, questions):
    matches = get_close_matches(user_question, questions, n=1, cutoff=0.6)
    return matches[0] if matches else None


def get_answer_for_question(question, kb):
    for q in kb["questions"]:
        if q["question"] == question:
            return q["answer"]
    return None


knowledge_base = load_knowledge_base("knowledge_base.json")

window = tk.Tk()
window.title("Chatbot")
window.state("zoomed")

chat_container = tk.Frame(window)
chat_container.pack(fill="both", expand=True)

canvas = tk.Canvas(chat_container, bg="#f5f5f5", highlightthickness=0)
scrollbar = tk.Scrollbar(chat_container, orient="vertical", command=canvas.yview)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")


def on_mousewheel(event):
    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


window.bind_all("<MouseWheel>", on_mousewheel)

canvas.configure(yscrollcommand=scrollbar.set)

chat_frame = tk.Frame(canvas, bg="#f5f5f5")
chat_window = canvas.create_window((0, 0), window=chat_frame, anchor="nw")


def resize_chat_frame(event):
    canvas.itemconfig(chat_window, width=event.width)


canvas.bind("<Configure>", resize_chat_frame)

chat_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)


def add_message(text, sender="bot"):
    outer = tk.Frame(chat_frame, bg="#f5f5f5")
    outer.pack(fill=tk.X, pady=6)

    if sender == "user":
        inner = tk.Frame(outer, bg="#f5f5f5")
        inner.pack(anchor="e", padx=80)
        bg = "#dcf8c6"
    else:
        inner = tk.Frame(outer, bg="#f5f5f5")
        inner.pack(anchor="w", padx=80)
        bg = "#ffffff"

    msg = tk.Label(
        inner,
        text=text,
        bg=bg,
        fg="black",
        padx=12,
        pady=8,
        wraplength=500,
        justify="left",
        font=("Helvetica", 14)
    )
    msg.pack()

    canvas.update_idletasks()
    canvas.yview_moveto(1.0)


def get_bot_response(user_message):
    best = find_best_match(
        user_message,
        [q["question"] for q in knowledge_base["questions"]]
    )

    if best:
        return get_answer_for_question(best, knowledge_base)

    teach = messagebox.askyesno(
        "Bilmiyorum",
        "Bu sorunun cevabını bilmiyorum, bana öğretmek ister misin?"
    )

    if teach:
        return learn_new_answer(user_message)

    return "Tamam, bunu öğrenmiyorum."


def learn_new_answer(question):
    answer = simpledialog.askstring(
        "Bana öğret",
        f"{question}\n\nNasıl cevap vermeliyim?"
    )

    if answer:
        knowledge_base["questions"].append({
            "question": question,
            "answer": answer
        })
        save_knowledge_base("knowledge_base.json", knowledge_base)
        return "Teşekkürler, yeni şeyler öğrendim 😊"

    return "Tamam."


def send_message(event=None):
    msg = input_entry.get().strip()
    if not msg:
        return

    add_message(msg, sender="user")
    bot = get_bot_response(msg)
    add_message(bot, sender="bot")

    input_entry.delete(0, tk.END)


input_frame = tk.Frame(window, bg="#d0d0d0")
input_frame.pack(fill=tk.X, side="bottom")

input_entry = tk.Entry(
    input_frame,
    font=("Helvetica", 14),
    relief=tk.FLAT
)
input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=10)
input_entry.bind("<Return>", send_message)

send_button = tk.Button(
    input_frame,
    text="Gönder",
    command=send_message,
    bg="#4a90e2",
    fg="white",
    font=("Helvetica", 12),
    relief=tk.FLAT
)
send_button.pack(side=tk.RIGHT, padx=10, pady=10)

add_message("Merhaba! Ben ChatBot 😊", sender="bot")

window.after(100, lambda: input_entry.focus_force())

window.mainloop()
