import customtkinter as ctk
import socket

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

istemci = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
baglanti_aktif = False

def baglan():
    global baglanti_aktif
    try:
        istemci.connect(('127.0.0.1', 12345))
        baglanti_aktif = True
        baglanti_btn.configure(text="BAĞLANTI KURULDU", state="disabled", fg_color="#2ecc71")
        log_yaz("[SİSTEM] Alıcı düğüm ile RF tüneli açıldı.")
    except:
        log_yaz("[HATA] Alıcı cihaz bulunamadı!")

def log_yaz(mesaj):
    terminal_textbox.configure(state="normal")
    terminal_textbox.insert("end", mesaj + "\n")
    terminal_textbox.see("end")
    terminal_textbox.configure(state="disabled")

def tx_animasyon():
    # TX Led ve Sinyal Kablosu yanar
    devre_canvas.itemconfig(tx_led, fill="#ff0000")
    devre_canvas.itemconfig(sinyal_kablo, fill="#f1c40f", width=3)
    
    # RF Dalgaları Sırayla Yayılır
    devre_canvas.itemconfig(w1, outline="#00ffff")
    root.after(100, lambda: devre_canvas.itemconfig(w2, outline="#00ffff"))
    root.after(200, lambda: devre_canvas.itemconfig(w3, outline="#00ffff"))
    
    # 300ms sonra her şeyi eski haline (sönük) döndür
    root.after(300, lambda: devre_canvas.itemconfig(tx_led, fill="#440000"))
    root.after(300, lambda: devre_canvas.itemconfig(sinyal_kablo, fill="#7f8c8d", width=2))
    root.after(300, lambda: devre_canvas.itemconfig(w1, outline="#2c3e50"))
    root.after(400, lambda: devre_canvas.itemconfig(w2, outline="#2c3e50"))
    root.after(500, lambda: devre_canvas.itemconfig(w3, outline="#2c3e50"))

def veri_paketle_ve_gonder(ham_veri):
    if baglanti_aktif:
        # Paketlerin havada yapışmasını önlemek için sonuna bitiş karakteri (\n) ekliyoruz
        giden_veri = ham_veri + "\n"
        
        # Arka planda giden byte ve checksum simülasyonu
        hex_data = " ".join([hex(ord(c))[2:] for c in giden_veri]).upper()
        checksum = hex(sum([ord(c) for c in giden_veri]) % 256).upper()
        
        log_yaz(f"[TX] PAYLOAD: {ham_veri}")
        log_yaz(f"     BYTES: {hex_data} | CHK: {checksum}")
        
        istemci.send(giden_veri.encode())
        tx_animasyon()

# --- GÖRSEL ARAYÜZ ---
root = ctk.CTk()
root.title("NODE A - Gönderici Cihaz")
root.geometry("420x650")

ctk.CTkLabel(root, text="Gönderici Cihaz (Node A)", font=("Arial", 22, "bold")).pack(pady=5)
baglanti_btn = ctk.CTkButton(root, text="Ağa Bağlan", font=("Arial", 14, "bold"), command=baglan)
baglanti_btn.pack(pady=5)

# --- DEVRE ÇİZİMİ ---
ctk.CTkLabel(root, text="Fiziksel Devre Şeması", font=("Arial", 12, "bold"), text_color="gray").pack(pady=(5,0))
devre_canvas = ctk.CTkCanvas(root, width=320, height=180, bg="#2c3e50", highlightthickness=2, highlightbackground="#34495e")
devre_canvas.pack(pady=5)

# RF Dalgaları (Başlangıçta Sönük)
w1 = devre_canvas.create_arc(185, 15, 215, 45, start=45, extent=90, style="arc", outline="#2c3e50", width=3)
w2 = devre_canvas.create_arc(170, 0, 230, 60, start=45, extent=90, style="arc", outline="#2c3e50", width=3)
w3 = devre_canvas.create_arc(155, -15, 245, 75, start=45, extent=90, style="arc", outline="#2c3e50", width=3)

# Kablolar ve Sensör
devre_canvas.create_line(60, 100, 140, 100, fill="#e74c3c", width=2)
sinyal_kablo = devre_canvas.create_line(60, 110, 140, 110, fill="#7f8c8d", width=2, dash=(4, 2))
devre_canvas.create_rectangle(20, 80, 60, 140, fill="#95a5a6", outline="black")
devre_canvas.create_oval(25, 95, 55, 125, fill="#7f8c8d")
devre_canvas.create_text(40, 65, text="Sensör", fill="white", font=("Arial", 10))

# Arduino ve XBee
devre_canvas.create_rectangle(140, 50, 260, 170, fill="#006266", outline="#00474b", width=3)
devre_canvas.create_text(200, 155, text="Arduino UNO", fill="white", font=("Arial", 11, "bold"))
devre_canvas.create_polygon(170, 30, 230, 30, 220, 50, 180, 50, fill="#7f8c8d")
devre_canvas.create_rectangle(175, 50, 225, 120, fill="#1a252f")
devre_canvas.create_text(200, 75, text="XBee", fill="white", font=("Arial", 12, "bold"))
devre_canvas.create_text(185, 105, text="TX", fill="white", font=("Arial", 9))
tx_led = devre_canvas.create_oval(200, 100, 215, 115, fill="#440000")

# --- KONTROLLER ---
kontrol_frame = ctk.CTkFrame(root)
kontrol_frame.pack(pady=5, padx=20, fill="both")
ctk.CTkLabel(kontrol_frame, text="Sıcaklık Sensörü (Konu 14.4)", font=("Arial", 12)).pack(pady=5)
ctk.CTkSlider(kontrol_frame, from_=0, to=100, command=lambda val: veri_paketle_ve_gonder(f"TEMP|{int(val)}")).pack(pady=5)

ctk.CTkLabel(kontrol_frame, text="Aktüatör Tetikleme (Konu 14.5)", font=("Arial", 12)).pack(pady=(10,5))
btn_frame = ctk.CTkFrame(kontrol_frame, fg_color="transparent")
btn_frame.pack()
ctk.CTkButton(btn_frame, text="MOTOR ÇALIŞTIR", fg_color="#2ecc71", hover_color="#27ae60", width=120, command=lambda: veri_paketle_ve_gonder("CMD|START")).pack(side="left", padx=5)
ctk.CTkButton(btn_frame, text="MOTOR DURDUR", fg_color="#e74c3c", hover_color="#c0392b", width=120, command=lambda: veri_paketle_ve_gonder("CMD|STOP")).pack(side="left", padx=5)

# --- CANLI PAKET İZLEYİCİ (SNIFFER) ---
terminal_frame = ctk.CTkFrame(root, fg_color="black")
terminal_frame.pack(pady=10, padx=20, fill="both", expand=True)
ctk.CTkLabel(terminal_frame, text="Terminal | Giden Paket İzleyici", font=("Consolas", 10, "bold"), text_color="#00ff00").pack(anchor="w", padx=5)
terminal_textbox = ctk.CTkTextbox(terminal_frame, fg_color="black", text_color="#00ff00", font=("Consolas", 11))
terminal_textbox.pack(fill="both", expand=True, padx=2, pady=2)
terminal_textbox.configure(state="disabled")

root.mainloop()