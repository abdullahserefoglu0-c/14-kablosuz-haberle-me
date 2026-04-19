import customtkinter as ctk
import socket
import threading
import math

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

motor_calisiyor = False
motor_aci = 0

def log_yaz(mesaj):
    terminal_textbox.configure(state="normal")
    terminal_textbox.insert("end", mesaj + "\n")
    terminal_textbox.see("end")
    terminal_textbox.configure(state="disabled")

def rx_animasyon():
    devre_canvas.itemconfig(rx_led, fill="#00ff00")
    devre_canvas.itemconfig(sinyal_kablo, fill="#f1c40f", width=3)
    
    # RF Dalgaları Karşılama
    devre_canvas.itemconfig(w3, outline="#00ffff")
    root.after(100, lambda: devre_canvas.itemconfig(w2, outline="#00ffff"))
    root.after(200, lambda: devre_canvas.itemconfig(w1, outline="#00ffff"))
    
    root.after(300, lambda: devre_canvas.itemconfig(rx_led, fill="#004400"))
    root.after(300, lambda: devre_canvas.itemconfig(sinyal_kablo, fill="#7f8c8d", width=2))
    root.after(300, lambda: devre_canvas.itemconfig(w1, outline="#2c3e50"))
    root.after(400, lambda: devre_canvas.itemconfig(w2, outline="#2c3e50"))
    root.after(500, lambda: devre_canvas.itemconfig(w3, outline="#2c3e50"))

def motor_dondur():
    global motor_aci
    if motor_calisiyor:
        motor_aci += 20
        if motor_aci >= 360: motor_aci = 0
        r = 22 # Pervane yarıçapı
        cx, cy = 280, 110 # Motor merkezi
        
        # 3 pervaneli fan çizimi güncellemesi (120 derece açılarla)
        for i, pervane in enumerate([pervane1, pervane2, pervane3]):
            aci_radyan = math.radians(motor_aci + (i * 120))
            x = cx + r * math.cos(aci_radyan)
            y = cy + r * math.sin(aci_radyan)
            devre_canvas.coords(pervane, cx, cy, x, y)
            
        root.after(40, motor_dondur) # Saniyede 25 kare hızında döndür

def dinlemeye_basla():
    global motor_calisiyor
    host = '127.0.0.1'
    port = 12345
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(1)
    
    log_yaz("[SİSTEM] Port 12345 dinleniyor...")
    conn, addr = server.accept()
    log_yaz("[SİSTEM] RF Sinyali Yakalandı!")
    
    while True:
        try:
            veri = conn.recv(1024).decode()
            if not veri: break
            
            # Gelen veriyi \n karakterine göre bölerek yapışan paketleri ayırıyoruz
            paketler = veri.split('\n')
            
            for paket in paketler:
                if paket == "": continue # Boş paketleri atla
                
                rx_animasyon()
                hex_data = " ".join([hex(ord(c))[2:] for c in paket]).upper()
                log_yaz(f"[RX] PAYLOAD: {paket} | BYTES: {hex_data}")
                
                try:
                    tip, deger = paket.split('|')
                    if tip == "TEMP":
                        sicaklik_etiketi.configure(text=f"Okunan Sıcaklık: {deger} °C")
                    elif tip == "CMD":
                        if deger == "START":
                            motor_calisiyor = True
                            devre_canvas.itemconfig(motor_govde, fill="#2ecc71")
                            motor_dondur() # Fan animasyonunu tetikle
                        elif deger == "STOP":
                            motor_calisiyor = False
                            devre_canvas.itemconfig(motor_govde, fill="#c0392b")
                except ValueError:
                    # Eğer veri formatı bozuksa sistemi çökertme, paketi yoksay
                    pass
        except:
            log_yaz("[HATA] Bağlantı Koptu!")
            break

# --- GÖRSEL ARAYÜZ ---
root = ctk.CTk()
root.title("NODE B - Alıcı Cihaz")
root.geometry("420x650")

ctk.CTkLabel(root, text="Alıcı Cihaz (Node B)", font=("Arial", 22, "bold")).pack(pady=5)

# --- DEVRE ÇİZİMİ ---
ctk.CTkLabel(root, text="Fiziksel Devre Şeması", font=("Arial", 12, "bold"), text_color="gray").pack(pady=(5,0))
devre_canvas = ctk.CTkCanvas(root, width=320, height=180, bg="#2c3e50", highlightthickness=2, highlightbackground="#34495e")
devre_canvas.pack(pady=5)

# Arduino ve XBee
devre_canvas.create_rectangle(60, 50, 180, 170, fill="#006266", outline="#00474b", width=3)
devre_canvas.create_text(120, 155, text="Arduino UNO", fill="white", font=("Arial", 11, "bold"))
devre_canvas.create_polygon(90, 30, 150, 30, 140, 50, 100, 50, fill="#7f8c8d")
devre_canvas.create_rectangle(95, 50, 145, 120, fill="#1a252f")
devre_canvas.create_text(120, 75, text="XBee", fill="white", font=("Arial", 12, "bold"))
devre_canvas.create_text(105, 105, text="RX", fill="white", font=("Arial", 9))
rx_led = devre_canvas.create_oval(120, 100, 135, 115, fill="#004400")

# RF Dalgaları (Ters Yönde)
w1 = devre_canvas.create_arc(105, 15, 135, 45, start=45, extent=90, style="arc", outline="#2c3e50", width=3)
w2 = devre_canvas.create_arc(90, 0, 150, 60, start=45, extent=90, style="arc", outline="#2c3e50", width=3)
w3 = devre_canvas.create_arc(75, -15, 165, 75, start=45, extent=90, style="arc", outline="#2c3e50", width=3)

# Motor Bağlantıları ve Çizimi
devre_canvas.create_line(180, 100, 250, 100, fill="#000000", width=2)
sinyal_kablo = devre_canvas.create_line(180, 120, 250, 120, fill="#7f8c8d", width=2, dash=(4, 2))
motor_govde = devre_canvas.create_oval(250, 80, 310, 140, fill="#c0392b", outline="#7f8c8d", width=3)
devre_canvas.create_text(280, 65, text="Aktüatör (Fan)", fill="white", font=("Arial", 10))

# Pervaneler
pervane1 = devre_canvas.create_line(280, 110, 280, 88, fill="white", width=4)
pervane2 = devre_canvas.create_line(280, 110, 299, 121, fill="white", width=4)
pervane3 = devre_canvas.create_line(280, 110, 261, 121, fill="white", width=4)

# --- VERİ EKRANI ---
bilgi_frame = ctk.CTkFrame(root)
bilgi_frame.pack(pady=5, padx=20, fill="x")
sicaklik_etiketi = ctk.CTkLabel(bilgi_frame, text="Okunan Sıcaklık: Bekleniyor...", font=("Arial", 14))
sicaklik_etiketi.pack(pady=10)

# --- CANLI PAKET İZLEYİCİ (SNIFFER) ---
terminal_frame = ctk.CTkFrame(root, fg_color="black")
terminal_frame.pack(pady=10, padx=20, fill="both", expand=True)
ctk.CTkLabel(terminal_frame, text="Terminal | Gelen Paket İzleyici", font=("Consolas", 10, "bold"), text_color="#00ff00").pack(anchor="w", padx=5)
terminal_textbox = ctk.CTkTextbox(terminal_frame, fg_color="black", text_color="#00ff00", font=("Consolas", 11))
terminal_textbox.pack(fill="both", expand=True, padx=2, pady=2)
terminal_textbox.configure(state="disabled")

threading.Thread(target=dinlemeye_basla, daemon=True).start()
root.mainloop()