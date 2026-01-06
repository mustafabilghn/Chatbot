import json
import tkinter as tk
from tkinter import simpledialog, messagebox
from ml_bot.chatbot import get_response, normalize


def load_knowledge_base():
    with open("knowledge_base.json", "r", encoding="utf-8") as f:
        return json.load(f)


def save_knowledge_base(data):
    with open("knowledge_base.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


window = tk.Tk()
window.title("Akıllı Asistan")
window.state("zoomed")

chat_container = tk.Frame(window)
chat_container.pack(fill="both", expand=True)
canvas = tk.Canvas(chat_container, bg="#f0f2f5", highlightthickness=0)
scrollbar = tk.Scrollbar(chat_container, orient="vertical", command=canvas.yview)
canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")
canvas.configure(yscrollcommand=scrollbar.set)
chat_frame = tk.Frame(canvas, bg="#f0f2f5")
chat_window = canvas.create_window((0, 0), window=chat_frame, anchor="nw")


def on_mousewheel(event):
    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


window.bind_all("<MouseWheel>", on_mousewheel)
chat_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.bind("<Configure>", lambda e: canvas.itemconfig(chat_window, width=e.width))


def add_message(text, sender="bot"):
    outer = tk.Frame(chat_frame, bg="#f0f2f5")
    outer.pack(fill=tk.X, pady=4)

    if sender == "user":
        inner = tk.Frame(outer, bg="#f0f2f5")
        inner.pack(anchor="e", padx=20)
        lbl = tk.Label(inner, text=text, bg="#0084ff", fg="white", padx=15, pady=10,
                       font=("Segoe UI", 12), wraplength=400, justify="left")
    else:
        inner = tk.Frame(outer, bg="#f0f2f5")
        inner.pack(anchor="w", padx=20)
        lbl = tk.Label(inner, text=text, bg="#ffffff", fg="black", padx=15, pady=10,
                       font=("Segoe UI", 12), wraplength=400, justify="left")

    lbl.pack()
    canvas.update_idletasks()
    canvas.yview_moveto(1.0)


def handle_learning(user_message):
    teach = messagebox.askyesno("Bilmiyorum", "Bunu henüz bilmiyorum. Öğretmek ister misin?")
    if teach:
        answer = simpledialog.askstring("Öğret", f"'{user_message}' sorusuna ne cevap vereyim?")
        if answer:
            kb = load_knowledge_base()
            kb["questions"].append({
                "question": user_message,
                "answer": answer
            })
            save_knowledge_base(kb)

            return "Teşekkürler! Bunu hafızama kaydettim. (Aktif olması için uygulamayı yeniden başlat)"
    return "Tamam, bunu öğrenmiyorum."


def send_message(event=None):
    msg = input_entry.get().strip()
    if not msg: return

    add_message(msg, sender="user")
    input_entry.delete(0, tk.END)

    response = get_response(msg)

    if response:
        add_message(response, sender="bot")
    else:
        learn_msg = handle_learning(msg)
        add_message(learn_msg, sender="bot")


input_frame = tk.Frame(window, bg="white", pady=10)
input_frame.pack(fill=tk.X, side="bottom")

input_entry = tk.Entry(input_frame, font=("Segoe UI", 14), relief=tk.SOLID, borderwidth=1)
input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=20, pady=10)
input_entry.bind("<Return>", send_message)

send_button = tk.Button(input_frame, text="Gönder", command=send_message, bg="#0084ff", fg="white",
                        font=("Segoe UI", 12, "bold"))
send_button.pack(side=tk.RIGHT, padx=20)

add_message("Merhaba! Benim adım ChatBot, bana ne sormak istersin?", sender="bot")
window.after(100, lambda: input_entry.focus_force())
window.mainloop()
