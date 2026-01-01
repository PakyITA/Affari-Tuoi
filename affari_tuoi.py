import sys
import random
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QGridLayout, QPushButton,
                             QVBoxLayout, QHBoxLayout, QLabel, QMessageBox,
                             QInputDialog)
from PyQt5.QtCore import Qt, QUrl, QTimer
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtGui import QPixmap

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def format_euro(valore):
    """Formatta i numeri con il punto come separatore delle migliaia (es: 300.000)."""
    if valore < 1: # Gestione per i centesimi (0.01)
        return "0,01"
    # Formatta l'intero con il punto come separatore delle migliaia
    return f"{int(valore):,}".replace(",", ".")

class SplashScreen(QWidget):
    def __init__(self, on_finish):
        super().__init__()
        self.on_finish = on_finish
        self.setWindowTitle("Affari Tuoi - Caricamento...")
        self.setFixedSize(600, 480)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setStyleSheet("background-color: #050a14; border: 3px solid #cc0000;")

        layout = QVBoxLayout()
        self.logo_label = QLabel()
        pixmap = QPixmap(resource_path(os.path.join("img", "logo.jpg")))
        if not pixmap.isNull():
            self.logo_label.setPixmap(pixmap.scaled(500, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.logo_label)

        self.btn_skip = QPushButton("SALTA SIGLA")
        self.btn_skip.setFixedSize(150, 40)
        self.btn_skip.setStyleSheet("background-color: #cc0000; color: white; font-weight: bold; border-radius: 5px;")
        self.btn_skip.clicked.connect(self.finish_splash)
        layout.addWidget(self.btn_skip, alignment=Qt.AlignCenter)

        self.credits = QLabel("Created by PakyITA")
        self.credits.setStyleSheet("color: rgba(255, 255, 255, 0.5); font-size: 12px; border: none;")
        layout.addWidget(self.credits, alignment=Qt.AlignRight | Qt.AlignBottom)

        self.setLayout(layout)
        self.player_sigla = QMediaPlayer()
        self.play_sigla()

        self.timer = QTimer()
        self.timer.timeout.connect(self.finish_splash)
        self.timer.start(15000)

    def play_sigla(self):
        path = resource_path(os.path.join("sound", "sigla.wav"))
        if os.path.exists(path):
            self.player_sigla.setMedia(QMediaContent(QUrl.fromLocalFile(path)))
            self.player_sigla.play()

    def finish_splash(self):
        self.timer.stop()
        self.player_sigla.stop()
        self.on_finish()
        self.close()

class AffariTuoi(QWidget):
    def __init__(self, nome_giocatore="Giocatore"):
        super().__init__()
        self.nome_giocatore = nome_giocatore
        self.setWindowTitle(f"Affari Tuoi - Sfidante: {self.nome_giocatore}")
        self.setStyleSheet("background-color: #050a14;")
        self.resize(1150, 750)

        self.player_effetti = QMediaPlayer()
        self.player_tensione = QMediaPlayer()
        self.musica_tensione_attiva = False

        self.premi_blu = [0.01, 1, 5, 10, 20, 50, 75, 100, 200, 500]
        self.premi_rossi = [5000, 10000, 15000, 20000, 30000, 50000, 75000, 100000, 200000, 300000]
        self.lista_premi = self.premi_blu + self.premi_rossi
        random.seed()
        random.shuffle(self.lista_premi)

        self.mappa_pacchi = {i+1: self.lista_premi[i] for i in range(20)}
        self.rimasti = self.premi_blu + self.premi_rossi

        self.pacco_giocatore = None
        self.fase_scelta = True
        self.attesa_dottore = False
        self.ultimo_colpo_rosso = False

        self.sequenza_round = [6, 3, 3, 3, 1, 1, 1, 1, 1]
        self.round_attuale = 0
        self.pacchi_da_aprire_ora = self.sequenza_round[self.round_attuale]
        self.pacchi_aperti_totali = 0

        self.init_ui()

    def play_sound(self, nome_file):
        path = resource_path(os.path.join("sound", nome_file))
        if os.path.exists(path):
            self.player_effetti.setMedia(QMediaContent(QUrl.fromLocalFile(path)))
            self.player_effetti.play()

    def play_tensione(self):
        if not self.musica_tensione_attiva:
            path = resource_path(os.path.join("sound", "tensione.wav"))
            if os.path.exists(path):
                self.player_tensione.setMedia(QMediaContent(QUrl.fromLocalFile(path)))
                self.player_tensione.setVolume(50)
                self.player_tensione.play()
                self.musica_tensione_attiva = True

    def init_ui(self):
        main_h_layout = QHBoxLayout(self)

        self.labels_premi = {}
        # Creazione Tabellone con formattazione . (punti)
        for col, premi in [("blu", sorted(self.premi_blu)), ("rossi", sorted(self.premi_rossi))]:
            lay = QVBoxLayout()
            for p in premi:
                l = QLabel(f"{format_euro(p)} €")
                l.setFixedSize(140, 35)
                color = "#0044cc" if col == "blu" else "#cc0000"
                l.setStyleSheet(f"background: {color}; color: white; border: 2px solid white; font-weight: bold; border-radius: 5px;")
                l.setAlignment(Qt.AlignCenter)
                lay.addWidget(l)
                self.labels_premi[p] = l
            main_h_layout.addLayout(lay)

        centro = QVBoxLayout()
        self.lbl_nome = QLabel(f"SFIDANTE: {self.nome_giocatore.upper()}")
        self.lbl_nome.setStyleSheet("color: #FFD700; font-size: 24px; font-weight: bold;")
        self.lbl_nome.setAlignment(Qt.AlignCenter)
        centro.addWidget(self.lbl_nome)

        self.lbl_round = QLabel(f"APRI {self.pacchi_da_aprire_ora} PACCHI")
        self.lbl_round.setStyleSheet("color: white; font-size: 18px;")
        self.lbl_round.setAlignment(Qt.AlignCenter)
        centro.addWidget(self.lbl_round)

        self.grid = QGridLayout()
        self.btns = {}
        for i in range(1, 21):
            b = QPushButton(str(i))
            b.setFixedSize(85, 85)
            b.setStyleSheet("background: orange; color: white; font-size: 20px; font-weight: bold; border-radius: 10px; border: 2px solid white;")
            b.clicked.connect(lambda checked, n=i: self.gestisci_pacco(n))
            self.grid.addWidget(b, (i-1)//5, (i-1)%5)
            self.btns[i] = b
        centro.addLayout(self.grid)

        self.signature = QLabel("Created by PakyITA")
        self.signature.setStyleSheet("color: rgba(255, 255, 255, 0.3); font-size: 10px;")
        centro.addWidget(self.signature, alignment=Qt.AlignRight)

        main_h_layout.insertLayout(1, centro)

    def gestisci_pacco(self, n):
        if self.attesa_dottore: return
        if self.fase_scelta:
            self.pacco_giocatore = n
            self.fase_scelta = False
            self.btns[n].setStyleSheet("background: green; color: white; border: 3px solid gold; border-radius: 10px;")
            self.lbl_nome.setText(f"{self.nome_giocatore.upper()} - PACCO {n}")
        else:
            premio = self.mappa_pacchi[n]
            self.btns[n].setEnabled(False)
            self.btns[n].setStyleSheet("background: #222; border: 1px solid #444;")

            if premio in self.premi_blu:
                self.play_sound("pacco_blu.wav")
                self.ultimo_colpo_rosso = False
            else:
                self.play_sound("pacco_rosso.wav")
                self.ultimo_colpo_rosso = True

            if premio in self.labels_premi:
                self.labels_premi[premio].setStyleSheet("background: #111; color: #333; border: 1px solid #222;")
                self.rimasti.remove(premio)

            self.pacchi_aperti_totali += 1
            self.pacchi_da_aprire_ora -= 1

            if self.pacchi_aperti_totali >= 16: self.play_tensione()

            if self.pacchi_da_aprire_ora == 0:
                self.chiamata_dottore()
            else:
                self.lbl_round.setText(f"APRI ANCORA {self.pacchi_da_aprire_ora} PACCHI")

    def chiamata_dottore(self):
        if len(self.rimasti) <= 1:
            self.scena_finale()
            return
        self.attesa_dottore = True
        self.play_sound("squillo.wav")
        QTimer.singleShot(2500, self.mostra_proposta_strategica)

    def mostra_proposta_strategica(self):
        media = sum(self.rimasti) / len(self.rimasti)
        max_r = max(self.rimasti)
        num_r = len([p for p in self.rimasti if p >= 5000])

        msg = QMessageBox(self)
        msg.setWindowTitle(f"☎️ IL DOTTORE PARLA CON {self.nome_giocatore.upper()}")

        # Logica Strategica Umana
        if self.ultimo_colpo_rosso and max_r < 300000:
            commento = f"'{self.nome_giocatore}, ti ho visto vacillare. Quel rosso faceva male...'"
            offerta = int(media * 0.4)
        elif num_r > 4:
            commento = f"'{self.nome_giocatore}, stai andando troppo forte. Devo fermarti prima che sia tardi...'"
            offerta = int(media * 0.6)
        else:
            commento = f"'{self.nome_giocatore}, il cerchio si stringe. Hai il coraggio di arrivare in fondo?'"
            offerta = int(media * 0.5)

        # Offerta CAMBIO
        if num_r >= 2 and random.random() < 0.3:
            msg.setText(f"{commento}\n\nIl Dottore ti offre il CAMBIO DEL PACCO.")
            acc = msg.addButton("ACCETTA CAMBIO", QMessageBox.ActionRole)
            rif = msg.addButton("RIFIUTA E AVANTI", QMessageBox.RejectRole)
            msg.exec_()
            if msg.clickedButton() == acc: self.gestisci_scambio()
        # Offerta SOLDI con punto delle migliaia
        else:
            offerta = max(offerta, 1)
            msg.setText(f"{commento}\n\nOfferta attuale: {format_euro(offerta)} €")
            acc = msg.addButton("ACCETTA SOLDI", QMessageBox.ActionRole)
            rif = msg.addButton("RIFIUTA E AVANTI", QMessageBox.RejectRole)
            msg.exec_()
            if msg.clickedButton() == acc:
                vincita = self.mappa_pacchi[self.pacco_giocatore]
                QMessageBox.information(self, "PARTITA CHIUSA", f"Hai accettato {format_euro(offerta)} €.\nNel tuo pacco c'erano {format_euro(vincita)} €.")
                self.chiedi_rigioca()
                return

        self.attesa_dottore = False
        self.round_attuale = min(self.round_attuale + 1, len(self.sequenza_round)-1)
        self.pacchi_da_aprire_ora = self.sequenza_round[self.round_attuale]
        self.lbl_round.setText(f"APRI {self.pacchi_da_aprire_ora} PACCHI")

    def gestisci_scambio(self):
        opzioni = [str(k) for k, v in self.btns.items() if v.isEnabled() and k != self.pacco_giocatore]
        nuovo, ok = QInputDialog.getItem(self, "SCAMBIO", f"{self.nome_giocatore}, con quale pacco scambi?", opzioni, 0, False)
        if ok:
            self.btns[self.pacco_giocatore].setStyleSheet("background: orange; border: 2px solid white; border-radius: 10px;")
            self.pacco_giocatore = int(nuovo)
            self.btns[self.pacco_giocatore].setStyleSheet("background: green; border: 3px solid gold; border-radius: 10px;")
            self.lbl_nome.setText(f"{self.nome_giocatore.upper()} - PACCO {nuovo}")

    def scena_finale(self):
        vincita = self.mappa_pacchi[self.pacco_giocatore]
        if vincita in self.premi_rossi: self.play_sound("pacco_blu.wav")
        else: self.play_sound("pacco_rosso.wav")
        QMessageBox.critical(self, "FINALE", f"{self.nome_giocatore}, nel tuo pacco ci sono:\n\n{format_euro(vincita)} €!")
        self.chiedi_rigioca()

    def chiedi_rigioca(self):
        if QMessageBox.question(self, "Rigioca", "Vuoi sfidare ancora il Dottore?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.close()
            QTimer.singleShot(100, start_game)
        else: QApplication.quit()

def start_game():
    nome, ok = QInputDialog.getText(None, "Affari Tuoi", "Il tuo nome:")
    if not ok or not nome: nome = "Giocatore"
    global main_window
    main_window = AffariTuoi(nome)
    main_window.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    splash = SplashScreen(start_game)
    splash.show()
    sys.exit(app.exec_())
