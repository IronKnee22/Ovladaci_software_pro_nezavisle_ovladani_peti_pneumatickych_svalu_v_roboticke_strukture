import time
import customtkinter
import re
from tkinter import messagebox

import sqlite3

from PneumoCVUTFBMI.DeviceLoader import DeviceLoader

dl = DeviceLoader()

b1 = dl.getBoard1()
b2 = dl.getBoard2()
b3 = dl.getBoard3()
b4 = dl.getBoard4()
b5 = dl.getBoard5()

b1.on()
b2.on()
b3.on()
b4.on()
b5.on()

# zde se nastavují hodnoty "koncových dorazů"
maxHodnotaSvalu = 2800
minHodnotaSvalu = 550

# barevný mód jiné možnosti jsou v oficiální dokumentaci
customtkinter.set_appearance_mode("system")
customtkinter.set_default_color_theme("blue")

class LeftFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.label_akce = customtkinter.CTkLabel(self, text="Akce",font=customtkinter.CTkFont(size=20, weight="bold"))
        self.label_akce.grid(row=0, column=0, padx=10)

        self.button_technicka_nula = customtkinter.CTkButton(
            self, text="Technická nula", command=self.techncka_nula)
        self.button_technicka_nula.grid(row=1, column=0, padx=10, pady=10)

        self.button_pracovni_poloha = customtkinter.CTkButton(
            self, text="Pracovní poloha", command=self.Pracovni_poloha)
        self.button_pracovni_poloha.grid(row=2, column=0, padx=10, pady=10)

        self.button_levo_pravo = customtkinter.CTkButton(
            self, text="Laterální flexe", command=self.levo_pravo)
        self.button_levo_pravo.grid(row=3, column=0, padx=10, pady=10)

        self.button_nahoru_dolu = customtkinter.CTkButton(
            self, text="Cervikální extenze", command=self.nahoru_dolu)
        self.button_nahoru_dolu.grid(row=4, column=0, padx=10, pady=10)

        self.button_kombinace = customtkinter.CTkButton(
            self, text="Kombinace", command=self.kombinace)
        self.button_kombinace.grid(row=5, column=0, padx=10, pady=10)

        self.label1_prazdna = customtkinter.CTkLabel(self, text=" ")
        self.label1_prazdna.grid(row=6, column=0, padx=10)

        self.label2_prazdna = customtkinter.CTkLabel(self, text=" ")
        self.label2_prazdna.grid(row=7, column=0, padx=10)

        self.label_switch = customtkinter.CTkLabel(
            self, text="Light/Dark Mode")
        self.label_switch.grid(row=8, column=0, padx=10)

        self.switch = customtkinter.CTkSwitch(self, text="Light Mode", command=self.switch_event,
                                              onvalue="on", offvalue="off")
        self.switch.grid(row=10, column=0, padx=10)


    def switch_event(self):
        if (self.switch.get() == "on"):
            customtkinter.set_appearance_mode("dark")
            self.switch.configure(text="Dark Mode")
        else:
            customtkinter.set_appearance_mode("light")
            self.switch.configure(text="Light Mode")

    def techncka_nula(self):
        svaly = {
            0: b1,
            1: b2,
            2: b3,
            3: b4,
            4: b5
            }       

        brokenMuscle = 1

        while True:  
            results = [sval.readA0() for sval in svaly.values()]

            all_in_range = all(600 <= result <= 620 for i, result in enumerate(results) if i != brokenMuscle)

            if all_in_range:
                break  
            
            for i in range(5):
                if i==brokenMuscle:
                    continue
                
                if results[i] >= 620:
                    svaly[i].go_backward(20, 10)
                    
                elif results[i] <= 600:
                    svaly[i].go_forward(20,10)

            time.sleep(1)

    def Pracovni_poloha(self): # početně tohle sedí
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()

        svaly = {
                1: b1,
                2: b5,
                3: b3,
                4: b4               
            }

        for index in range(1, 5):               
            cur.execute(f"SELECT sval{index}_mv FROM sval{index}") # tady se načte číslo rovnice
            cislo_vzorce = cur.fetchone()
            cur.execute(f"SELECT * FROM sval{index}_mv WHERE id IN ({int(cislo_vzorce[0])})")# tady se načte rovnice pro přepočet z mv na kroky
            rovnice = cur.fetchall()

            sklon = rovnice[0][1]
            posun = rovnice[0][2]
            akt_hod_mV = svaly[index].readA0() #získání aktuální hodnoty v mV

            aktualni_kroky = (akt_hod_mV - posun) / sklon
            kon_kroky = (650 - posun) / sklon

            poc_kroku = kon_kroky - aktualni_kroky
            poc_kroku = round(poc_kroku)
            print(f"sval{index} abychom došli z pozice {akt_hod_mV} na 650 je potřeba udělat {poc_kroku}")
            print(svaly[index].get_steps_from_start())

            if poc_kroku != 0:
                svaly[index].go_forward(10, poc_kroku)

        time.sleep(5)

        for index in range(1, 5):    
            print(f"sval{index} {svaly[index].get_steps_from_start()}")

    def levo_pravo(self): # početně sedí
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()

        svaly = {
                1: b1,
                2: b5,
                3: b3,
                4: b4
                
            }
        for j in range(2):
            for index in [1, 3]:           
                cur.execute(f"SELECT sval{index}_mv FROM sval{index}") # tady se načte číslo rovnice
                cislo_vzorce = cur.fetchone()
                cur.execute(f"SELECT * FROM sval{index}_mv WHERE id IN ({int(cislo_vzorce[0])})")# tady se načte rovnice pro přepočet z mv na kroky
                rovnice = cur.fetchall()

                sklon = rovnice[0][1]
                posun = rovnice[0][2]
                akt_hod_mV = svaly[index].readA0() #získání aktuální hodnoty v mV

                aktualni_kroky = (akt_hod_mV - posun) / sklon
                kon_kroky = (700 - posun) / sklon

                poc_kroku = kon_kroky - aktualni_kroky
                poc_kroku = round(poc_kroku)
                print(f"sval{index} abychom došli z pozice {akt_hod_mV} na 700 je potřeba udělat {poc_kroku}")
                print(svaly[index].get_steps_from_start())
                if poc_kroku != 0:
                    svaly[index].go_forward(10, poc_kroku)

            for index in [2, 4]:           
                cur.execute(f"SELECT sval{index}_mv FROM sval{index}") # tady se načte číslo rovnice
                cislo_vzorce = cur.fetchone()
                cur.execute(f"SELECT * FROM sval{index}_mv WHERE id IN ({int(cislo_vzorce[0])})")# tady se načte rovnice pro přepočet z mv na kroky
                rovnice = cur.fetchall()

                sklon = rovnice[0][1]
                posun = rovnice[0][2]
                akt_hod_mV = svaly[index].readA0() #získání aktuální hodnoty v mV

                aktualni_kroky = (akt_hod_mV - posun) / sklon
                kon_kroky = (630 - posun) / sklon

                poc_kroku = kon_kroky - aktualni_kroky
                poc_kroku = round(poc_kroku)
                print(f"sval{index} abychom došli z pozice {akt_hod_mV} na 630 je potřeba udělat {poc_kroku}")
                print(svaly[index].get_steps_from_start())
                if poc_kroku != 0:
                    svaly[index].go_forward(10, poc_kroku)

            time.sleep(5)
            for index in range(1, 5):    
                print(f"sval{index} {svaly[index].get_steps_from_start()}")
        
        for j in range(2):
            for index in [1, 3]:           
                cur.execute(f"SELECT sval{index}_mv FROM sval{index}") # tady se načte číslo rovnice
                cislo_vzorce = cur.fetchone()
                cur.execute(f"SELECT * FROM sval{index}_mv WHERE id IN ({int(cislo_vzorce[0])})")# tady se načte rovnice pro přepočet z mv na kroky
                rovnice = cur.fetchall()

                sklon = rovnice[0][1]
                posun = rovnice[0][2]
                akt_hod_mV = svaly[index].readA0() #získání aktuální hodnoty v mV

                aktualni_kroky = (akt_hod_mV - posun) / sklon
                kon_kroky = (630 - posun) / sklon

                poc_kroku = kon_kroky - aktualni_kroky
                poc_kroku = round(poc_kroku)
                print(f"sval{index} abychom došli z pozice {akt_hod_mV} na 630 je potřeba udělat {poc_kroku}")
                print(svaly[index].get_steps_from_start())
                if poc_kroku != 0:
                    svaly[index].go_forward(10, poc_kroku)

            for index in [2, 4]:           
                cur.execute(f"SELECT sval{index}_mv FROM sval{index}") # tady se načte číslo rovnice
                cislo_vzorce = cur.fetchone()
                cur.execute(f"SELECT * FROM sval{index}_mv WHERE id IN ({int(cislo_vzorce[0])})")# tady se načte rovnice pro přepočet z mv na kroky
                rovnice = cur.fetchall()

                sklon = rovnice[0][1]
                posun = rovnice[0][2]
                akt_hod_mV = svaly[index].readA0() #získání aktuální hodnoty v mV

                aktualni_kroky = (akt_hod_mV - posun) / sklon
                kon_kroky = (700 - posun) / sklon

                poc_kroku = kon_kroky - aktualni_kroky
                poc_kroku = round(poc_kroku)
                print(f"sval{index} abychom došli z pozice {akt_hod_mV} na 700 je potřeba udělat {poc_kroku}")
                print(svaly[index].get_steps_from_start())
                if poc_kroku != 0:
                    svaly[index].go_forward(10, poc_kroku)

            time.sleep(5)
            for index in range(1, 5):    
                print(f"sval{index} {svaly[index].get_steps_from_start()}")
                                                                                                                                                                                                                           
        for j in range(2):
            for index in range(1, 5):               
                cur.execute(f"SELECT sval{index}_mv FROM sval{index}") # tady se načte číslo rovnice
                cislo_vzorce = cur.fetchone()
                cur.execute(f"SELECT * FROM sval{index}_mv WHERE id IN ({int(cislo_vzorce[0])})")# tady se načte rovnice pro přepočet z mv na kroky
                rovnice = cur.fetchall()

                sklon = rovnice[0][1]
                posun = rovnice[0][2]
                akt_hod_mV = svaly[index].readA0() #získání aktuální hodnoty v mV

                aktualni_kroky = (akt_hod_mV - posun) / sklon
                kon_kroky = (650 - posun) / sklon

                poc_kroku = kon_kroky - aktualni_kroky
                poc_kroku = round(poc_kroku)
                print(f"sval{index} abychom došli z pozice {akt_hod_mV} na 650 je potřeba udělat {poc_kroku}")
                print(svaly[index].get_steps_from_start())
                if poc_kroku != 0:
                    svaly[index].go_forward(10, poc_kroku)

            time.sleep(5)
        
    def nahoru_dolu(self):
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()

        svaly = {
                1: b1,
                2: b5,
                3: b3,
                4: b4               
            }

        for j in range(2):
            for index in [1, 2]:           
                cur.execute(f"SELECT sval{index}_mv FROM sval{index}") # tady se načte číslo rovnice
                cislo_vzorce = cur.fetchone()
                cur.execute(f"SELECT * FROM sval{index}_mv WHERE id IN ({int(cislo_vzorce[0])})")# tady se načte rovnice pro přepočet z mv na kroky
                rovnice = cur.fetchall()

                sklon = rovnice[0][1]
                posun = rovnice[0][2]
                akt_hod_mV = svaly[index].readA0() #získání aktuální hodnoty v mV

                aktualni_kroky = (akt_hod_mV - posun) / sklon
                kon_kroky = (700 - posun) / sklon

                poc_kroku = kon_kroky - aktualni_kroky
                poc_kroku = round(poc_kroku)
                print(f"sval{index} abychom došli z pozice {akt_hod_mV} na 700 je potřeba udělat {poc_kroku}")
                print(svaly[index].get_steps_from_start())
                if poc_kroku != 0:
                    svaly[index].go_forward(10, poc_kroku)

            for index in [3, 4]:           
                cur.execute(f"SELECT sval{index}_mv FROM sval{index}") # tady se načte číslo rovnice
                cislo_vzorce = cur.fetchone()
                cur.execute(f"SELECT * FROM sval{index}_mv WHERE id IN ({int(cislo_vzorce[0])})")# tady se načte rovnice pro přepočet z mv na kroky
                rovnice = cur.fetchall()

                sklon = rovnice[0][1]
                posun = rovnice[0][2]
                akt_hod_mV = svaly[index].readA0() #získání aktuální hodnoty v mV

                aktualni_kroky = (akt_hod_mV - posun) / sklon
                kon_kroky = (630 - posun) / sklon

                poc_kroku = kon_kroky - aktualni_kroky
                poc_kroku = round(poc_kroku)
                print(f"sval{index} abychom došli z pozice {akt_hod_mV} na 630 je potřeba udělat {poc_kroku}")
                print(svaly[index].get_steps_from_start())
                if poc_kroku != 0:
                    svaly[index].go_forward(10, poc_kroku)

            time.sleep(5)
            for index in range(1, 5):    
                print(f"sval{index} {svaly[index].get_steps_from_start()}")
             
        for j in range(2):
            for index in [1, 2]:           
                cur.execute(f"SELECT sval{index}_mv FROM sval{index}") # tady se načte číslo rovnice
                cislo_vzorce = cur.fetchone()
                cur.execute(f"SELECT * FROM sval{index}_mv WHERE id IN ({int(cislo_vzorce[0])})")# tady se načte rovnice pro přepočet z mv na kroky
                rovnice = cur.fetchall()

                sklon = rovnice[0][1]
                posun = rovnice[0][2]
                akt_hod_mV = svaly[index].readA0() #získání aktuální hodnoty v mV

                aktualni_kroky = (akt_hod_mV - posun) / sklon
                kon_kroky = (630 - posun) / sklon

                poc_kroku = kon_kroky - aktualni_kroky
                poc_kroku = round(poc_kroku)
                print(f"sval{index} abychom došli z pozice {akt_hod_mV} na 630 je potřeba udělat {poc_kroku}")
                print(svaly[index].get_steps_from_start())
                if poc_kroku != 0:
                    svaly[index].go_forward(10, poc_kroku)

            for index in [3, 4]:           
                cur.execute(f"SELECT sval{index}_mv FROM sval{index}") # tady se načte číslo rovnice
                cislo_vzorce = cur.fetchone()
                cur.execute(f"SELECT * FROM sval{index}_mv WHERE id IN ({int(cislo_vzorce[0])})")# tady se načte rovnice pro přepočet z mv na kroky
                rovnice = cur.fetchall()

                sklon = rovnice[0][1]
                posun = rovnice[0][2]
                akt_hod_mV = svaly[index].readA0() #získání aktuální hodnoty v mV

                aktualni_kroky = (akt_hod_mV - posun) / sklon
                kon_kroky = (700 - posun) / sklon

                poc_kroku = kon_kroky - aktualni_kroky
                poc_kroku = round(poc_kroku)
                print(f"sval{index} abychom došli z pozice {akt_hod_mV} na 700 je potřeba udělat {poc_kroku}")
                print(svaly[index].get_steps_from_start())
                if poc_kroku != 0:
                    svaly[index].go_forward(10, poc_kroku)

            time.sleep(5)
            for index in range(1, 5):    
                print(f"sval{index} {svaly[index].get_steps_from_start()}")
                                                                                                                                                                                                                              
        for j in range(2):
            for index in range(1, 5):               
                cur.execute(f"SELECT sval{index}_mv FROM sval{index}") # tady se načte číslo rovnice
                cislo_vzorce = cur.fetchone()
                cur.execute(f"SELECT * FROM sval{index}_mv WHERE id IN ({int(cislo_vzorce[0])})")# tady se načte rovnice pro přepočet z mv na kroky
                rovnice = cur.fetchall()
    
                sklon = rovnice[0][1]
                posun = rovnice[0][2]
                akt_hod_mV = svaly[index].readA0() #získání aktuální hodnoty v mV
    
                aktualni_kroky = (akt_hod_mV - posun) / sklon
                kon_kroky = (650 - posun) / sklon
    
                poc_kroku = kon_kroky - aktualni_kroky
                poc_kroku = round(poc_kroku)
                print(f"sval{index} abychom došli z pozice {akt_hod_mV} na 650 je potřeba udělat {poc_kroku}")
                print(svaly[index].get_steps_from_start())
                if poc_kroku != 0:
                    svaly[index].go_forward(10, poc_kroku)
    
            time.sleep(5)

    def kombinace(self):
        # kombinace byla navrhnuta takle že prostě dvě jednotlivé akce jdou po sobě tak je zbytečný to kodit
        self.levo_pravo()
        time.sleep(5)
        self.nahoru_dolu()


class MainFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # inicializace globálních proměných
        global maxHodnotaSvalu
        global minHodnotaSvalu
        global sklon
        global posun
        global aktualni_poz
        aktualni_poz = [0,0,0,0,0]

        # první sloupec
        self.label_sval1 = customtkinter.CTkLabel(self, text="sval1")
        self.label_sval1.grid(row=1, column=0, padx=20)

        self.label_sval1_mv = customtkinter.CTkLabel(self, text="")
        self.label_sval1_mv.grid(row=2, column=0, padx=20)

        self.progressbar_sval1 = customtkinter.CTkProgressBar(
            self, orientation="horizontal")
        self.progressbar_sval1.grid(row=3, column=0, padx=20)
        self.progressbar_sval1.set((b1.readA0()-minHodnotaSvalu)/(maxHodnotaSvalu-minHodnotaSvalu))

        self.entry_sval1 = customtkinter.CTkEntry(self, placeholder_text="entry")
        self.entry_sval1.configure(validate='focusout', validatecommand=(self.register(self.validate_1), '%P'))
        self.entry_sval1.grid(row=4, column=0, padx=20, pady=10)


        self.label_sval3 = customtkinter.CTkLabel(self, text="sval3")
        self.label_sval3.grid(row=7, column=0, padx=20)

        self.label_sval3_mv = customtkinter.CTkLabel(self, text="")
        self.label_sval3_mv.grid(row=8, column=0, padx=20)

        self.progressbar_sval3 = customtkinter.CTkProgressBar(
            self, orientation="horizontal")
        self.progressbar_sval3.grid(row=9, column=0, padx=20)
        self.progressbar_sval3.set((b3.readA0()-minHodnotaSvalu)/(maxHodnotaSvalu-minHodnotaSvalu))

        self.entry_sval3 = customtkinter.CTkEntry(self, placeholder_text="entry3")
        self.entry_sval3.configure(validate='focusout', validatecommand=(self.register(self.validate_3), '%P'))
        self.entry_sval3.grid(row=10, column=0, padx=20, pady=10)

        # ?druhý sloupec
        self.label_nazev = customtkinter.CTkLabel(self, text="Nezávislé ovládání", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.label_nazev.grid(row=0, column=1, padx=20)

        self.label_sval5 = customtkinter.CTkLabel(self, text="sval5")
        self.label_sval5.grid(row=4, column=1, padx=20)

        self.label_sval5_mv = customtkinter.CTkLabel(self, text="")
        self.label_sval5_mv.grid(row=5, column=1, padx=20)

        self.progressbar_sval5 = customtkinter.CTkProgressBar(
            self, orientation="horizontal")
        self.progressbar_sval5.grid(row=6, column=1, padx=20)
        self.progressbar_sval5.set((b2.readA0()-minHodnotaSvalu)/(maxHodnotaSvalu-minHodnotaSvalu))

        self.entry_sval5 = customtkinter.CTkEntry(self, placeholder_text="entry5")
        self.entry_sval5.configure(validate='focusout', validatecommand=(self.register(self.validate_5), '%P'))
        self.entry_sval5.grid(row=7, column=1, padx=20, pady=10)


        self.ziskani_mv_button = customtkinter.CTkButton(
            self, text="Hodnoty svalu mV", command=self.hotnoty_svalu)
        self.ziskani_mv_button.grid(row=11, column=1, padx=20, pady=10)

        self.button_spustit = customtkinter.CTkButton(
            self, text="Spustit", command=self.button_spustit_jed_sval)
        self.button_spustit.grid(row=12, column=1, padx=20, pady=10)

        # ?třetí sloupec
        self.label_sval2 = customtkinter.CTkLabel(self, text="sval2")
        self.label_sval2.grid(row=1, column=2, padx=20)

        self.label_sval2_mv = customtkinter.CTkLabel(self, text="")
        self.label_sval2_mv.grid(row=2, column=2, padx=20)

        self.progressbar_sval2 = customtkinter.CTkProgressBar(
            self, orientation="horizontal")
        self.progressbar_sval2.grid(row=3, column=2, padx=20)
        self.progressbar_sval2.set((b5.readA0()-minHodnotaSvalu)/(maxHodnotaSvalu-minHodnotaSvalu))

        self.entry_sval2 = customtkinter.CTkEntry(self, placeholder_text="entry2")
        self.entry_sval2.configure(validate='focusout', validatecommand=(self.register(self.validate_2), '%P'))
        self.entry_sval2.grid(row=4, column=2, padx=20, pady=10)



        self.label_sval4 = customtkinter.CTkLabel(self, text="sval4")
        self.label_sval4.grid(row=7, column=2, padx=20)

        self.label_sval4_mv = customtkinter.CTkLabel(self, text="")
        self.label_sval4_mv.grid(row=8, column=2, padx=20)

        self.progressbar_sval4 = customtkinter.CTkProgressBar(
            self, orientation="horizontal")
        self.progressbar_sval4.grid(row=9, column=2, padx=20)
        self.progressbar_sval4.set((b4.readA0()-minHodnotaSvalu)/(maxHodnotaSvalu-minHodnotaSvalu))

        self.entry_sval4 = customtkinter.CTkEntry(self, placeholder_text="entry4")
        self.entry_sval4.configure(validate='focusout', validatecommand=(self.register(self.validate_4), '%P'))
        self.entry_sval4.grid(row=10, column=2, padx=20, pady=10)

    def hotnoty_svalu(self):
        self.label_sval1_mv.configure(text=str(b1.readA0()))
        self.label_sval2_mv.configure(text=str(b5.readA0()))
        self.label_sval3_mv.configure(text=str(b3.readA0()))
        self.label_sval4_mv.configure(text=str(b4.readA0()))
        self.label_sval5_mv.configure(text=str(b2.readA0()))

    def validate_1(self, value):
        pattern = r'^-?\d+$'  # Regulární výraz přijímající pouze čísla
        if re.fullmatch(pattern, value) is None:
            messagebox.showerror("Chybný vstup", "Prosím, zadejte pouze čísla. \nVstup nesmí být prázdný.")
            self.entry_sval1.delete(0, customtkinter.END)            
            return False
        else:
            return True
    
    def validate_2(self, value):
        pattern = r'^-?\d+$'  # Regulární výraz přijímající pouze čísla
        if re.fullmatch(pattern, value) is None:
            messagebox.showerror("Chybný vstup", "Prosím, zadejte pouze čísla. \nVstup nesmí být prázdný.")
            self.entry_sval2.delete(0, customtkinter.END)            
            return False
        else:
            return True
    
    def validate_3(self, value):
        pattern = r'^-?\d+$'  # Regulární výraz přijímající pouze čísla
        if re.fullmatch(pattern, value) is None:
            messagebox.showerror("Chybný vstup", "Prosím, zadejte pouze čísla. \nVstup nesmí být prázdný.")
            self.entry_sval3.delete(0, customtkinter.END)            
            return False
        else:
            return True
    
    def validate_4(self, value):
        pattern = r'^-?\d+$'  # Regulární výraz přijímající pouze čísla
        if re.fullmatch(pattern, value) is None:
            messagebox.showerror("Chybný vstup", "Prosím, zadejte pouze čísla. \nVstup nesmí být prázdný.")
            self.entry_sval4.delete(0, customtkinter.END)            
            return False
        else:
            return True
    
    def validate_5(self, value):
        pattern = r'^-?\d+$'  # Regulární výraz přijímající pouze čísla
        if re.fullmatch(pattern, value) is None:
            messagebox.showerror("Chybný vstup", "Prosím, zadejte pouze čísla. \nVstup nesmí být prázdný.")
            self.entry_sval5.delete(0, customtkinter.END)            
            return False
        else:
            return True

    def button_spustit_jed_sval(self):
        
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        
        sval1= self.entry_sval1.get()
        sval2= self.entry_sval5.get()
        sval3= self.entry_sval3.get()
        sval4= self.entry_sval4.get()
        sval5= self.entry_sval2.get()

        if radio_var.get() == 0:
            messagebox.showerror("Chybí sval", "Prosím vyber sval")
        
        if self.validate_1(sval1) and self.validate_2(sval2) and self.validate_3(sval3) and self.validate_4(sval4) and self.validate_5(sval5) and radio_var.get() !=0:

            radio_value = radio_var.get()
            entry_values = [self.entry_sval1.get(), self.entry_sval2.get(), self.entry_sval3.get(), self.entry_sval4.get(), self.entry_sval5.get()]
            entry_values = [0 if not value else value for value in entry_values]

            if radio_value == 1:
                #rovnice = hodnoty_mm
                jednotka = "mm"
            elif radio_value == 2:
                #rovnice = hodnoty_mbar
                prepocet_jednotka = "mV2bar"
                jednotka = "mbar"
            elif radio_value == 3:                
                jednotka = "mv"


            results = []

            svaly = {
                0: b1,
                1: b5,
                2: b3,
                3: b4,
                4: b2
            }

            for index, entry in enumerate(entry_values, start=1):
                if radio_value == 4: #pokud dělám jenom kroky tak nemusím nic počítat
                    result = int(entry)

                else:
                    cur.execute(f"SELECT sval{index}_{jednotka} FROM sval{index}")
                    cislo_vzorce = cur.fetchone()
                    cur.execute(f"SELECT * FROM sval{index}_{jednotka} WHERE id IN ({int(cislo_vzorce[0])})")
                    rovnice = cur.fetchall()

                    akt_hod_mV = svaly[index-1].readA0() #získání aktuální hodnoty v mV 

                    if entry !=0:

                        if radio_value == 3:
                            start_hodnta = akt_hod_mV 
                        
                        elif radio_value == 2: #! z mV na mbar
                            cur.execute(f"SELECT * FROM sval{index}_{prepocet_jednotka} WHERE id IN ({int(cislo_vzorce[0])})")
                            prepocet = cur.fetchall()
                            sklon = prepocet[0][1]
                            posun = prepocet[0][2]
                            start_hodnta =sklon * akt_hod_mV + posun #převedení hodnoty na správné jednotky

                        konecna_hodnota = float(start_hodnta) + float(entry)  #získání hodnoty na kterou se chceme dostat pomocí startovní + posunu

                        sklon = rovnice[0][1]
                        posun = rovnice[0][2]

                        kon_kroky = (konecna_hodnota - posun) / sklon #přepočet na kroky
                        start_kroky = float((start_hodnta - posun) / sklon) #přepočet na kroky

                        result = kon_kroky - start_kroky #spočítání nutných kroků
                        result = round(result)
                        
                    else:
                        result = 0

                cur.execute(f"SELECT sval{index}_mv FROM sval{index}") # tady se načte vždycky přepočet na 
                cislo_vzorce = cur.fetchone()
                cur.execute(f"SELECT * FROM sval{index}_mv WHERE id IN ({int(cislo_vzorce[0])})")
                rovnice_kon_doraz = cur.fetchall()

                sklon_kon_doraz = rovnice_kon_doraz[0][1]
                posun_kon_doraz = rovnice_kon_doraz[0][2]

                akt_hod_mV = svaly[index-1].readA0() #získání aktuální hodnoty v mV 

                aktualni_kroky = (akt_hod_mV - posun_kon_doraz) / sklon_kon_doraz
                aktualni_kroky += result

                budouci_napeti = sklon_kon_doraz * aktualni_kroky + posun_kon_doraz
                print(f"počteční napětí svalu{index} je {akt_hod_mV} konečná má být {budouci_napeti} pocet kroku co se musi udělat {result}")
                print(svaly[index-1].get_steps_from_start())

                if(budouci_napeti < maxHodnotaSvalu and budouci_napeti > minHodnotaSvalu):
                    aktualni_poz[index-1] += result
                    results.append(result)
                    provede = True
                
                else:
                    messagebox.showerror("Chybný vstup", "Hodnota nějá svalu přesáhla dovolené meze")
                    provede = False
                    break

            if (provede):          
                progressbars = [self.progressbar_sval1, self.progressbar_sval2, self.progressbar_sval3, self.progressbar_sval4, self.progressbar_sval5]

                for i in range(5):
                    if results[i] > 0:
                        svaly[i].go_forward(10, results[i])
                        #time.sleep(2)
                    elif results[i] < 0:
                        svaly[i].go_backward(10, -results[i])
                time.sleep(3)
                for i in range(5):
                    print(svaly[i].readA0())
                    b = (svaly[i].readA0() - minHodnotaSvalu) / (maxHodnotaSvalu - minHodnotaSvalu)
                    progressbars[i].set(b)

            time.sleep(5)

            for index in range(1, 5):    
                print(f"sval{index} {svaly[index-1].get_steps_from_start()}")


class RightFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        global radio_var

        
        self.label_popis = customtkinter.CTkLabel(self, text="Jednotky", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.label_popis.grid(row=0, column=0, padx=20)

        radio_var = customtkinter.IntVar(value=0)
        
        self.radiobutton_2 = customtkinter.CTkRadioButton(self, text="mbar",
                                                          command=self.radiobutton_event, variable=radio_var, value=2)
        self.radiobutton_2.grid(row=2, column=0, padx=20, pady=10)

        self.radiobutton_3 = customtkinter.CTkRadioButton(self, text="mV",
                                                          command=self.radiobutton_event, variable=radio_var, value=3)
        self.radiobutton_3.grid(row=3, column=0, padx=20, pady=10)

        self.radiobutton_4 = customtkinter.CTkRadioButton(self, text="kroky",
                                                          command=self.radiobutton_event, variable=radio_var, value=4)
        self.radiobutton_4.grid(row=4, column=0, padx=20, pady=10)

        self.label1_vzhled = customtkinter.CTkLabel(self, text=" ")
        self.label1_vzhled.grid(row=5, column=0, padx=20)

        self.label2_vzhled = customtkinter.CTkLabel(self, text=" ")
        self.label2_vzhled.grid(row=6, column=0, padx=20)

        self.label3_vzhled = customtkinter.CTkLabel(self, text=" ")
        self.label3_vzhled.grid(row=7, column=0, padx=20)

        self.label4_vzhled = customtkinter.CTkLabel(self, text=" ")
        self.label4_vzhled.grid(row=8, column=0, padx=20)

        self.label5_vzhled = customtkinter.CTkLabel(self, text=" ")
        self.label5_vzhled.grid(row=9, column=0, padx=20)

        self.label6_vzhled= customtkinter.CTkLabel(self, text=" ")
        self.label6_vzhled.grid(row=10, column=0, padx=20)

        self.back2Main_button = customtkinter.CTkButton(self, text="Hlavní stránka", command= master.back2Main) # button for login
        self.back2Main_button.grid(row=11, column=0, padx=20, pady=10)

    def radiobutton_event(self):
        print("radiobutton toggled, current value:", radio_var.get())


# toto je hlaví uživatelské okno ale jelikož by to bylo hodně nepřehledné tak se to rozdělilo do 3 framů a každý frame je dělan jakovlastní classa
class GUI(customtkinter.CTkToplevel):
    def __init__(self, mainwindow, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Nastavení velikosti okna
        width = 1100
        height = 440
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        screen_x = (screen_width - width) // 2
        screen_y = (screen_height - height) // 2

        self.geometry(f"{width}x{height}+{screen_x}+{screen_y}")

        self.title("user")
        
        # toto slouží k tomu když se zavře okno aby došlo k nějaké činosti v tomto případě je tato funkce pro technickou nulu
        self.protocol("WM_DELETE_WINDOW", self.execute_after_close)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.left_frame = LeftFrame(master=self)
        self.left_frame.grid(row=0, column=0, pady=20, sticky="nsew")

        self.main_frame = MainFrame(master=self)
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        self.right_frame = RightFrame(master=self)
        self.right_frame.grid(row=0, column=2, pady=20, sticky="nsew")

        self.mainwindow = mainwindow

    def back2Main(self):
        self.withdraw()
        self.mainwindow.deiconify()

    def execute_after_close(self):
        self.destroy()
        svaly = {
            0: b1,
            1: b2,
            2: b3,
            3: b4,
            4: b5
            }       

        brokenMuscle = 1

        while True:  
            results = [sval.readA0() for sval in svaly.values()]

            all_in_range = all(600 <= result <= 620 for i, result in enumerate(results) if i != brokenMuscle)

            if all_in_range:
                break  
            
            for i in range(5):
                if i==brokenMuscle:
                    continue
                
                if results[i] >= 620:
                    svaly[i].go_backward(20, 10)
                elif results[i] <= 600:
                    svaly[i].go_forward(20,10)

            time.sleep(3)
        
        self.quit()
    
