import customtkinter as ctk
from tkinter import messagebox
import math

class FizikselProgramlamaLab(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("BOZ214: Bölüm 14 - Kablosuz İletişim Sanal Laboratuvarı")
        self.geometry("1350x850") 
        
        self.pin_radius = 6 
        self.mevcut_bolum = 1
        self.bolum_kilitleri = {1: False, 2: True, 3: True, 4: True, 5: True}
        self.baglantilar = {} 
        self.aktif_cizgi = None
        self.baslangic_pini = None
        self.pin_merkezleri = {} 
        self.kodlama_modu_aktif = False
        self.simulasyon_aktif = False
        
        self.animasyon_ogeleri = []
        self.sanal_buton_penceresi = None
        
        self.arayuzu_kur()
        self.bolum_yukle(1)

    def arayuzu_kur(self):
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        
        self.bolum_butonlari = {}
        bolum_isimleri = ["14.1: RFM69HCW", "14.2: XBee Temel", "14.4: XBee Sensör", "14.6: BlueSMiRF", "14.5: Etkileşimli XBee"]
        
        ctk.CTkLabel(self.sidebar, text="MODÜLLER", font=("Arial", 16, "bold")).pack(pady=(20, 10))

        for i, isim in enumerate(bolum_isimleri, 1):
            btn = ctk.CTkButton(self.sidebar, text=isim, state="disabled" if i > 1 else "normal",
                               command=lambda b=i: self.bolum_degistir(b))
            btn.pack(pady=10, padx=10)
            self.bolum_butonlari[i] = btn

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.canvas = ctk.CTkCanvas(self.main_frame, height=500, bg="#ecf0f1", highlightthickness=1, highlightbackground="#bdc3c7")
        self.canvas.pack(fill="x", pady=5)
        
        self.canvas.bind("<ButtonPress-1>", self.kablo_baslat)
        self.canvas.bind("<B1-Motion>", self.kablo_surukle)
        self.canvas.bind("<ButtonRelease-1>", self.kablo_birak)
        self.canvas.bind("<Button-3>", self.kablo_sil) 

        self.bottom_frame = ctk.CTkFrame(self.main_frame)
        self.bottom_frame.pack(fill="both", expand=True)

        self.code_frame = ctk.CTkFrame(self.bottom_frame)
        self.code_frame.pack(side="left", fill="both", expand=True, padx=5)
        ctk.CTkLabel(self.code_frame, text="Arduino Kod Editörü (sketch.ino)", font=("Arial", 12, "bold")).pack(pady=5)
        self.code_editor = ctk.CTkTextbox(self.code_frame, font=("Consolas", 14), fg_color="#1e1e1e", text_color="#d4d4d4")
        self.code_editor.pack(fill="both", expand=True, pady=5, padx=5)
        self.code_editor.configure(state="disabled")

        self.control_frame = ctk.CTkFrame(self.bottom_frame, width=300)
        self.control_frame.pack(side="right", fill="both", padx=5)
        
        self.btn_check = ctk.CTkButton(self.control_frame, text="Bağlantıları Doğrula", fg_color="#e67e22", command=self.dogrula)
        self.btn_check.pack(pady=(20, 5), padx=10)
        
        self.btn_clear = ctk.CTkButton(self.control_frame, text="Kabloları Temizle", fg_color="#c0392b", command=self.kablolari_temizle)
        self.btn_clear.pack(pady=5, padx=10)
        
        self.btn_next = ctk.CTkButton(self.control_frame, text="Sonraki Bölüme Geç", state="disabled", command=self.sonraki_bolum)
        self.btn_next.pack(pady=(5, 10), padx=10)

        self.terminal = ctk.CTkTextbox(self.control_frame, height=140, fg_color="#000000", text_color="#2ecc71", font=("Consolas", 12))
        self.terminal.pack(fill="both", expand=True, padx=10, pady=10)

    # --- ÇİZİM FONKSİYONLARI ---
    def pin_ciz(self, x, y, tag, renk="#7f8c8d", label="", offset_x=0, offset_y=15, angle=0, anchor="center", text_color="#2c3e50"):
        r = self.pin_radius
        self.canvas.create_oval(x-r, y-r, x+r, y+r, fill=renk, outline="#2c3e50", width=1, tags="pin_gorsel")
        if label:
            self.canvas.create_text(x + offset_x, y + offset_y, text=label, fill=text_color, font=("Arial", 8, "bold"), angle=angle, anchor=anchor)
        self.pin_merkezleri[tag] = (x, y)

    def ciz_tam_arduino(self, baslangic_x=30, baslangic_y=100, etiket="Arduino UNO"):
        self.canvas.create_rectangle(baslangic_x, baslangic_y, baslangic_x + 350, baslangic_y + 220, fill="#00979C", outline="#006266", width=3)
        self.canvas.create_text(baslangic_x + 175, baslangic_y + 110, text=etiket, fill="white", font=("Arial", 20, "bold"))
        self.canvas.create_rectangle(baslangic_x - 15, baslangic_y + 30, baslangic_x, baslangic_y + 80, fill="#bdc3c7")

        ust_pinler = [
            ("ard_scl", "SCL"), ("ard_sda", "SDA"), ("ard_aref", "AREF"), ("ard_gnd_3", "GND"), 
            ("ard_13", "13"), ("ard_12", "12"), ("ard_11", "11"), ("ard_10", "10"), ("ard_9", "9"), ("ard_8", "8"),
            ("bos", ""), 
            ("ard_7", "7"), ("ard_6", "6"), ("ard_5", "5"), ("ard_4", "4"), ("ard_3", "3"), ("ard_2", "2"), ("ard_tx", "TX 1"), ("ard_rx", "RX 0")
        ]
        
        x_pos = baslangic_x + 330
        for tag, lbl in ust_pinler:
            if tag != "bos":
                renk = "#34495e" if "gnd" in tag else "#ecf0f1"
                self.pin_ciz(x_pos, baslangic_y + 10, tag, label=lbl, offset_x=0, offset_y=-12, angle=90, anchor="w", renk=renk)
            x_pos -= 14 if tag != "bos" else 10 

        alt_guc_pinler = [
            ("ard_ioref", "IOREF"), ("ard_rst", "RESET"), ("ard_3v3", "3.3V"), ("ard_5v", "5V"), 
            ("ard_gnd_1", "GND"), ("ard_gnd_2", "GND"), ("ard_vin", "VIN")
        ]
        
        x_pos = baslangic_x + 70
        for tag, lbl in alt_guc_pinler:
            renk = "#e74c3c" if "5v" in tag or "3v3" in tag else ("#34495e" if "gnd" in tag else "#ecf0f1")
            self.pin_ciz(x_pos, baslangic_y + 210, tag, label=lbl, offset_x=0, offset_y=12, angle=90, anchor="e", renk=renk)
            x_pos += 14

        x_pos += 20 
        
        alt_analog_pinler = [("ard_a0", "A0"), ("ard_a1", "A1"), ("ard_a2", "A2"), ("ard_a3", "A3"), ("ard_a4", "A4"), ("ard_a5", "A5")]
        for tag, lbl in alt_analog_pinler:
            self.pin_ciz(x_pos, baslangic_y + 210, tag, label=lbl, offset_x=0, offset_y=12, angle=90, anchor="e")
            x_pos += 14

    def ciz_xbee_gercekci(self, x, y, tag_prefix, etiket="XBee"):
        self.canvas.create_polygon(x, y+20, x+25, y, x+75, y, x+100, y+20, x+100, y+180, x, y+180, fill="#ecf0f1", outline="#95a5a6", width=2)
        self.canvas.create_rectangle(x+35, y+25, x+65, y+55, fill="#bdc3c7", outline="#7f8c8d")
        self.canvas.create_text(x+50, y+100, text=etiket, fill="#2c3e50", font=("Arial", 14, "bold", "italic"))

        sol_pinler = ["3v3", "tx", "rx", "d12", "rst", "pwm0", "d11", "res", "dtr", "gnd"]
        sol_etiketler = ["3.3V", "TX", "RX", "D12", "Sıfırla", "PWM0", "D11", "Ayrılmış", "DTR", "Toprak"]
        sag_pinler = ["d0", "d1", "d2", "d3", "rts", "assoc", "vref", "sleep", "cts", "d4"]
        sag_etiketler = ["A0/D0", "A1/D1", "A2/D2", "A3/D3", "RTS", "Ağ", "VREF", "Uyku", "CTS", "D4"]

        for i in range(10):
            renk_sol = "#e74c3c" if sol_pinler[i] == "3v3" else ("#34495e" if sol_pinler[i] == "gnd" else "#ecf0f1")
            self.pin_ciz(x, y+35 + i*15, f"{tag_prefix}_{sol_pinler[i]}", label=sol_etiketler[i], offset_x=-10, offset_y=0, anchor="e", text_color="#2c3e50", renk=renk_sol)
            self.pin_ciz(x+100, y+35 + i*15, f"{tag_prefix}_{sag_pinler[i]}", label=sag_etiketler[i], offset_x=10, offset_y=0, anchor="w", text_color="#2c3e50", renk="#ecf0f1")

    # --- SİMÜLASYON VE ANİMASYON FONKSİYONLARI ---
    def simulasyonu_hazirla(self):
        self.simulasyon_aktif = True
        buton_metin = "Veri Akışını Başlat" if self.mevcut_bolum == 2 else "Donanım Simülasyonunu Başlat"
        self.sanal_btn = ctk.CTkButton(self.main_frame, text=buton_metin, fg_color="#8e44ad", hover_color="#9b59b6", command=self.animasyon_tetikle)
        self.sanal_buton_penceresi = self.canvas.create_window(175, 400, window=self.sanal_btn)
        self.log(f"[SİMÜLASYON HAZIR] {buton_metin} butonuna basınız.")

    def animasyon_tetikle(self):
        self.sanal_btn.configure(state="disabled")
        
        if self.mevcut_bolum == 1: # RFM69
            self.dalga_animasyonu(0, 650, 150, hedef_log="[RFM69 Alıcı] Got [Hello!] from 1")
        elif self.mevcut_bolum == 2: # XBee Serial
            self.log("[SERİ İLETİŞİM] TX -> RX veri akışı başladı...")
            self.veri_paketi_animasyonu("ard_tx", "xbee_rx", "#3498db")
            self.canvas.after(1000, lambda: self.veri_paketi_animasyonu("xbee_tx", "ard_rx", "#e67e22"))
        elif self.mevcut_bolum == 3: # XBee API Receiver
            self.log("[KABLOSUZ İLETİŞİM] Verici sensör verisini gönderiyor...")
            # Sol taraftan (hayali vericiden) alıcı XBee'ye sinyal gönder
            self.dalga_animasyonu(0, 300, 150, renk="#e67e22", hedef_log="[XBee] API Çerçevesi Alındı (0x7E). PWM üretildi.", hedef_led=True)
        elif self.mevcut_bolum == 4: # Bluetooth
            self.dalga_animasyonu(0, 650, 150, renk="#2980b9", hedef_log="[Telefon] Bluetooth verisi başarıyla alındı.")
        elif self.mevcut_bolum == 5: # Interaktif LED
            self.dalga_animasyonu(0, 500, 150, hedef_led=True)

    def dalga_animasyonu(self, sayac, x, y, renk="#3498db", hedef_log=None, hedef_led=False):
        for dalga in self.animasyon_ogeleri:
            self.canvas.delete(dalga)
        self.animasyon_ogeleri.clear()

        if sayac < 5:
            for i in range(1, sayac + 2):
                radius = i * 40
                dalga = self.canvas.create_arc(x - radius, y - radius, x + radius, y + radius, 
                                               start=-45, extent=90, style="arc", outline=renk, width=3)
                self.animasyon_ogeleri.append(dalga)
            self.canvas.after(150, self.dalga_animasyonu, sayac + 1, x, y, renk, hedef_log, hedef_led)
        else:
            if hedef_log: self.log(hedef_log)
            if hedef_led:
                self.canvas.itemconfig("uzaktan_led", fill="#2ecc71", outline="#27ae60") 
                self.log("[DONANIM] LED Yandı / PWM Sinyali Aktif.")
                self.canvas.after(2000, lambda: self.canvas.itemconfig("uzaktan_led", fill="#c0392b", outline="#a93226"))
            
            self.canvas.after(1000, self.animasyonu_temizle)

    def veri_paketi_animasyonu(self, baslangic_tag, bitis_tag, renk, adim=0, max_adim=20):
        if adim == 0:
            for item in self.animasyon_ogeleri: self.canvas.delete(item)
            self.animasyon_ogeleri.clear()
            
        x1, y1 = self.pin_merkezleri[baslangic_tag]
        x2, y2 = self.pin_merkezleri[bitis_tag]
        
        guncel_x = x1 + (x2 - x1) * (adim / max_adim)
        guncel_y = y1 + (y2 - y1) * (adim / max_adim)
        
        paket = self.canvas.create_oval(guncel_x-5, guncel_y-5, guncel_x+5, guncel_y+5, fill=renk, outline="white", width=2)
        self.animasyon_ogeleri.append(paket)
        
        if adim < max_adim:
            if len(self.animasyon_ogeleri) > 1:
                self.canvas.delete(self.animasyon_ogeleri.pop(0))
            self.canvas.after(30, self.veri_paketi_animasyonu, baslangic_tag, bitis_tag, renk, adim + 1, max_adim)
        else:
            self.animasyonu_temizle()

    def animasyonu_temizle(self):
        for item in self.animasyon_ogeleri: self.canvas.delete(item)
        self.animasyon_ogeleri.clear()
        if self.sanal_btn: self.sanal_btn.configure(state="disabled")
        self.basari_tamamla() # Animasyon bitince final uyarıyı tetikle

    # --- KABLO ETKİLEŞİMLERİ ---
    def pin_rengi_belirle(self, pin_tag):
        if "5v" in pin_tag or "3v3" in pin_tag or "vcc" in pin_tag or "vin" in pin_tag: return "#e74c3c"
        if "gnd" in pin_tag or "toprak" in pin_tag: return "#2c3e50"
        return "#f1c40f" 

    def kablo_baslat(self, event):
        if self.kodlama_modu_aktif and not self.simulasyon_aktif: return 
        
        self.baslangic_pini = None
        for tag, (px, py) in self.pin_merkezleri.items():
            if math.hypot(event.x - px, event.y - py) < 12: 
                self.baslangic_pini = tag
                self.baslangic_x, self.baslangic_y = px, py
                self.aktif_cizgi = self.canvas.create_line(px, py, event.x, event.y, width=4, fill=self.pin_rengi_belirle(tag), tags="temp_kablo")
                self.canvas.tag_raise(self.aktif_cizgi)
                return 

    def kablo_surukle(self, event):
        if self.aktif_cizgi:
            self.canvas.coords(self.aktif_cizgi, self.baslangic_x, self.baslangic_y, event.x, event.y)

    def kablo_birak(self, event):
        if not self.aktif_cizgi: return
        hedef_pini = None
        
        for tag, (px, py) in self.pin_merkezleri.items():
            if tag == self.baslangic_pini: continue 
            if math.hypot(event.x - px, event.y - py) < 15: 
                hedef_pini = tag
                hedef_x, hedef_y = px, py
                break
        
        if hedef_pini:
            self.canvas.coords(self.aktif_cizgi, self.baslangic_x, self.baslangic_y, hedef_x, hedef_y)
            baglanti_adi = f"{self.baslangic_pini}-{hedef_pini}"
            
            pin_dolu = False
            for bagli_kablo in self.baglantilar.keys():
                kullanilan_pinler = bagli_kablo.split('-')
                if self.baslangic_pini in kullanilan_pinler or hedef_pini in kullanilan_pinler:
                    pin_dolu = True
                    break
            
            if not pin_dolu:
                self.baglantilar[baglanti_adi] = self.aktif_cizgi
                self.log(f"[BAĞLANTI] {self.baslangic_pini} <-> {hedef_pini} kuruldu.")
            else:
                self.canvas.delete(self.aktif_cizgi)
                self.log("[HATA] Pin zaten dolu!")
        else:
            self.canvas.delete(self.aktif_cizgi) 
        self.aktif_cizgi = None

    def kablo_sil(self, event):
        if self.kodlama_modu_aktif: return
        for tag, (px, py) in self.pin_merkezleri.items():
            if math.hypot(event.x - px, event.y - py) < 12:
                silinecek = [k for k in self.baglantilar.keys() if tag in k.split('-')]
                for k in silinecek:
                    self.canvas.delete(self.baglantilar[k])
                    del self.baglantilar[k]
                    self.log(f"[SİLİNDİ] {tag} söküldü.")
                return

    def kablolari_temizle(self):
        if self.kodlama_modu_aktif: return
        for c_id in self.baglantilar.values(): self.canvas.delete(c_id)
        self.baglantilar.clear()
        self.log("[SİSTEM] Tüm kablolar temizlendi.")

    # --- BÖLÜM YÖNETİMİ VE ÇİZİMLER ---
    def bolum_yukle(self, bolum_no):
        self.canvas.delete("all")
        if self.sanal_buton_penceresi: self.canvas.delete(self.sanal_buton_penceresi)
        
        self.baglantilar.clear()
        self.pin_merkezleri.clear() 
        self.kodlama_modu_aktif = False
        self.simulasyon_aktif = False
        self.code_editor.configure(state="normal")
        self.code_editor.delete("1.0", "end")
        self.code_editor.configure(state="disabled")
        self.btn_check.configure(text="Bağlantıları Doğrula", fg_color="#e67e22")
        self.terminal.delete("1.0", "end")
        self.log(f"--- BÖLÜM {bolum_no} YÜKLENDİ ---")

        modul_x = 550
        modul_y = 100

        if bolum_no == 1:
            self.ciz_tam_arduino(baslangic_x=30, baslangic_y=100)
            self.log("Kitap Şekil 14-1: RFM69HCW SPI bağlantılarını gerçekleştirin.")
            self.hedef_baglantilar = [{"ard_5v", "rfm_vin"}, {"ard_gnd", "rfm_gnd"}, {"ard_2", "rfm_rst"}, {"ard_3", "rfm_g0"}, {"ard_4", "rfm_cs"}, {"ard_11", "rfm_mosi"}, {"ard_12", "rfm_miso"}, {"ard_13", "rfm_sck"}]
            
            self.canvas.create_rectangle(modul_x, modul_y, modul_x + 150, modul_y + 300, fill="#bdc3c7", outline="#7f8c8d", width=2)
            self.canvas.create_text(modul_x + 120, modul_y + 150, text="RFM69HCW", fill="#2c3e50", angle=270, font=("Arial", 16, "bold"))
            pins = [("vin","VIN","#e74c3c"), ("gnd","GND","#34495e"), ("g0","G0","#ecf0f1"), ("sck","SCK","#ecf0f1"), ("miso","MISO","#ecf0f1"), ("mosi","MOSI","#ecf0f1"), ("cs","CS","#ecf0f1"), ("rst","RST","#ecf0f1")]
            for i, (tag, lbl, clr) in enumerate(pins): 
                self.pin_ciz(modul_x, modul_y + 30 + i*35, f"rfm_{tag}", label=lbl, offset_x=15, offset_y=0, anchor="w", renk=clr)
            
            self.canvas.create_rectangle(850, 100, 1000, 250, fill="#95a5a6", dash=(4, 4))
            self.canvas.create_text(925, 175, text="Alıcı Cihaz", fill="white", font=("Arial", 14, "bold"))

        elif bolum_no == 2:
            self.ciz_tam_arduino(baslangic_x=30, baslangic_y=100)
            self.log("Bölüm 14.2: Çıplak XBee bağlarken mutlaka 3.3V kullanılmalıdır! (Aksi takdirde yanar)")
            self.hedef_baglantilar = [{"ard_3v3", "xbee_3v3"}, {"ard_gnd", "xbee_gnd"}, {"ard_tx", "xbee_rx"}, {"ard_rx", "xbee_tx"}]
            self.ciz_xbee_gercekci(modul_x, modul_y + 50, "xbee")

        elif bolum_no == 3:
            self.ciz_tam_arduino(baslangic_x=30, baslangic_y=100)
            self.log("Bölüm 14.4: XBee API Okuma. Arduino 3.3V pini kullanılmalıdır.")
            self.hedef_baglantilar = [{"ard_3v3", "xbee_3v3"}, {"ard_gnd", "xbee_gnd"}, {"ard_tx", "xbee_rx"}, {"ard_rx", "xbee_tx"}, {"ard_5", "led_a"}, {"ard_gnd", "led_k"}]
            self.ciz_xbee_gercekci(modul_x, modul_y, "xbee")
            
            self.canvas.create_oval(modul_x + 30, modul_y + 220, modul_x + 60, modul_y + 250, fill="#c0392b", outline="#a93226", width=2, tags="uzaktan_led")
            self.pin_ciz(modul_x + 10, modul_y + 235, "led_a", label="LED (+)", offset_x=0, offset_y=-15, renk="#e74c3c")
            self.pin_ciz(modul_x + 80, modul_y + 235, "led_k", label="LED (-)", offset_x=0, offset_y=-15, renk="#34495e")

        elif bolum_no == 4:
            self.ciz_tam_arduino(baslangic_x=30, baslangic_y=100)
            self.log("Kitap Şekil 14-10: BlueSMiRF (RN-42). D2->TX, D3->RX bağlayın.")
            self.hedef_baglantilar = [{"ard_5v", "bt_vcc"}, {"ard_gnd", "bt_toprak"}, {"ard_2", "bt_tx"}, {"ard_3", "bt_rx"}]
            
            self.canvas.create_rectangle(modul_x, modul_y + 50, modul_x + 250, modul_y + 250, fill="#2c3e50", outline="#95a5a6", width=2)
            self.canvas.create_rectangle(modul_x + 10, modul_y + 80, modul_x + 150, modul_y + 220, fill="#ecf0f1")
            self.canvas.create_text(modul_x + 80, modul_y + 150, text="RN-42", fill="#2c3e50", font=("Arial", 12, "bold"))
            self.canvas.create_text(modul_x + 125, modul_y + 235, text="BlueSMiRF", fill="white", font=("Arial", 12, "bold"))
            
            pins = [("cts","CTS","#ecf0f1"), ("vcc","VCC","#e74c3c"), ("toprak","Toprak","#34495e"), ("tx","TX","#ecf0f1"), ("rx","RX","#ecf0f1"), ("rts","RTS","#ecf0f1")]
            for i, (tag, lbl, clr) in enumerate(pins): 
                self.pin_ciz(modul_x + 250, modul_y + 70 + i*30, f"bt_{tag}", label=lbl, offset_x=-15, offset_y=0, anchor="e", renk=clr, text_color="white")
            
            self.canvas.create_rectangle(900, 70, 1000, 270, fill="#34495e", outline="#bdc3c7", width=3, corner_radius=15)
            self.canvas.create_rectangle(910, 90, 990, 230, fill="#ecf0f1")
            self.canvas.create_text(950, 160, text="Akıllı\nTelefon", fill="#2c3e50", font=("Arial", 12, "bold"), justify="center")

        elif bolum_no == 5:
            self.log("Bölüm 14.5: Uzaktan AT Komutuyla LED Yakma (Etkileşimli Simülasyon)")
            self.hedef_baglantilar = [
                {"ard_3v3", "tx_3v3"}, {"ard_gnd", "tx_gnd"}, {"ard_tx", "tx_rx"}, {"ard_rx", "tx_tx"},
                {"rx_d1", "led_a"}, {"rx_gnd", "led_k"} 
            ]

            self.ciz_tam_arduino(baslangic_x=20, baslangic_y=50, etiket="Verici Arduino")
            self.ciz_xbee_gercekci(400, 60, "tx", etiket="Verici XBee")
            
            self.canvas.create_text(900, 30, text="ALICI İSTASYON", fill="#34495e", font=("Arial", 16, "bold"))
            self.ciz_xbee_gercekci(800, 60, "rx", etiket="Alıcı XBee")
            
            self.canvas.create_oval(950, 200, 1000, 250, fill="#c0392b", outline="#a93226", width=4, tags="uzaktan_led")
            self.pin_ciz(975, 180, "led_a", label="LED (+)", offset_x=0, offset_y=-15, renk="#e74c3c")
            self.pin_ciz(975, 270, "led_k", label="LED (-)", offset_x=0, offset_y=15, renk="#34495e")

    def pin_normalize(self, pin_name):
        if "ard_gnd" in pin_name: 
            return "ard_gnd"
        if "rx_gnd" in pin_name or "tx_gnd" in pin_name:
            return pin_name 
        return pin_name

    def dogrula(self):
        if self.btn_check.cget("text") == "Bağlantıları Doğrula":
            mevcut = set()
            for b in self.baglantilar.keys():
                p1, p2 = b.split('-')
                mevcut.add(frozenset([self.pin_normalize(p1), self.pin_normalize(p2)]))
            
            hedef = set()
            for h in self.hedef_baglantilar:
                p1, p2 = list(h)[0], list(h)[1]
                hedef.add(frozenset([self.pin_normalize(p1), self.pin_normalize(p2)]))
            
            if mevcut == hedef:
                self.log("[BAŞARILI] Kablolama tamam! Şimdi kodunuzu yazın.")
                self.kodlama_modu_aktif = True
                self.code_editor.configure(state="normal")
                self.btn_check.configure(text="Kodu Doğrula", fg_color="#27ae60")
                
                # POP-UP 1: Bağlantı Başarılı
                messagebox.showinfo("Bağlantı Başarılı", "Kablolama hatasız şekilde tamamlandı.\n\nŞimdi Arduino Kod Editörü'ne gerekli komutları yazabilirsiniz.")
            else: 
                eksik = len(hedef - mevcut)
                fazla = len(mevcut - hedef)
                has_5v_error = any("ard_5v" in list(b) for b in mevcut) and self.mevcut_bolum in [2,3,5]
                if has_5v_error:
                    self.log("[KRİTİK HATA] Çıplak XBee'ye 5V bağladınız! XBee zarar gördü. 3.3V kullanın.")
                else:
                    self.log(f"[HATA] {eksik} eksik, {fazla} hatalı bağlantı var! Devreyi gözden geçirin.")
        else:
            kod = self.code_editor.get("1.0", "end").lower()
            sartlar = {
                1: ["rh_rf69", "setfrequency"], 
                2: ["serial.begin", "serial.write"], 
                3: ["0x7e", "analogwrite"], 
                4: ["softwareserial", "btserial"],
                5: ["atd1", "0x7e", "0x02"] 
            }
            if all(s in kod for s in sartlar[self.mevcut_bolum]): 
                self.log("[SİSTEM] Kod Doğrulandı!")
                self.simulasyonu_hazirla()
                
                # POP-UP 2: Kod Doğrulandı
                messagebox.showinfo("Kod Doğrulandı", "Yazdığınız kod doğrulandı!\n\nLütfen ekranda beliren butona tıklayarak donanım simülasyonunu başlatın.")
            else: 
                self.log("[HATA] Kodda kitapta istenilen kritik komutlar eksik veya hatalı!")

    def basari_tamamla(self):
        self.log("[SİSTEM] Laboratuvar tamamlandı!")
        self.btn_next.configure(state="normal", fg_color="#2980b9")
        
        # POP-UP 3: Bölüm Tamamlandı (Tam İstediğin Şekilde)
        messagebox.showinfo("Bölüm Tamamlandı", "Laboratuvarı başarıyla tamamladınız. Ekran görüntüsü alıp sonraki bölüme geçebilirsiniz.")

    def sonraki_bolum(self):
        yeni = self.mevcut_bolum + 1
        if yeni <= 5:
            self.bolum_kilitleri[yeni] = False; self.bolum_butonlari[yeni].configure(state="normal")
            self.mevcut_bolum = yeni; self.code_editor.delete("1.0", "end"); self.btn_next.configure(state="disabled"); self.bolum_yukle(yeni)
        else:
            messagebox.showinfo("Tebrikler!", "Tüm laboratuvarları bitirdiniz!")

    def bolum_degistir(self, n):
        if not self.bolum_kilitleri[n]: self.mevcut_bolum = n; self.bolum_yukle(n)
        else: messagebox.showwarning("Kilitli", "Lütfen önce bir önceki bölümü bitirin.")

    def log(self, mesaj):
        self.terminal.insert("end", mesaj + "\n"); self.terminal.see("end")

if __name__ == "__main__":
    app = FizikselProgramlamaLab()
    app.mainloop()