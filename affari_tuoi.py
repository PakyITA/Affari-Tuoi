import sys
import random
from PyQt5.QtWidgets import (QApplication, QWidget, QGridLayout,
                             QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QMessageBox)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont

class AffariTuoi(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Affari Tuoi - Versione Kids")
        self.setStyleSheet("background-color: #001f3f;")

        # Premi divisi per categoria
        self.premi_blu = [0.01, 1, 5, 10, 20, 50, 75, 100, 200, 500]
        self.premi_rossi = [5000, 10000, 15000, 20000, 30000, 50000, 75000, 100000, 200000, 300000]
        self.tutti_i_premi = self.premi_blu + self.premi_rossi
        random.shuffle(self.tutti_i_premi)

        self.mappa_pacchi = {i+1: self.tutti_i_premi[i] for i in range(20)}
        self.pacco_giocatore = None
        self.fase_scelta = True

        self.init_ui()

    def init_ui(self):
        # Layout Orizzontale Principale: [Premi Blu] [Griglia Pacchi] [Premi Rossi]
        self.layout_principale = QHBoxLayout(self)

        # 1. Colonna Sinistra (Blu)
        self.colonna_blu = QVBoxLayout()
        self.labels_blu = {}
        for p in self.premi_blu:
            lbl = QLabel(f"{p} €")
            lbl.setStyleSheet("background-color: blue; color: white; border: 1px solid white; padding: 5px; font-weight: bold;")
            self.colonna_blu.addWidget(lbl)
            self.labels_blu[p] = lbl
        self.layout_principale.addLayout(self.colonna_blu)

        # 2. Parte Centrale (Titolo + Pacchi)
        centro_layout = QVBoxLayout()
        self.label_stato = QLabel("SCEGLI IL TUO PACCO")
        self.label_stato.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        self.label_stato.setAlignment(Qt.AlignCenter)
        centro_layout.addWidget(self.label_stato)

        self.grid_pacchi = QGridLayout()
        self.bottoni_pacchi = {}
        for i in range(1, 21):
            btn = QPushButton(str(i))
            btn.setFixedSize(80, 80)
            btn.setStyleSheet("background-color: orange; color: white; font-weight: bold; font-size: 16px; border-radius: 10px;")
            btn.clicked.connect(lambda checked, n=i: self.apri_pacco(n))
            row, col = (i-1) // 5, (i-1) % 5
            self.grid_pacchi.addWidget(btn, row, col)
            self.bottoni_pacchi[i] = btn
        centro_layout.addLayout(self.grid_pacchi)
        self.layout_principale.addLayout(centro_layout)

        # 3. Colonna Destra (Rossi)
        self.colonna_rossa = QVBoxLayout()
        self.labels_rossi = {}
        for p in self.premi_rossi:
            lbl = QLabel(f"{p} €")
            lbl.setStyleSheet("background-color: red; color: white; border: 1px solid white; padding: 5px; font-weight: bold;")
            self.colonna_rossa.addWidget(lbl)
            self.labels_rossi[p] = lbl
        self.layout_principale.addLayout(self.colonna_rossa)

    def apri_pacco(self, n):
        if self.fase_scelta:
            self.pacco_giocatore = n
            self.fase_scelta = False
            self.bottoni_pacchi[n].setStyleSheet("background-color: green; color: white; font-weight: bold; border-radius: 10px;")
            self.label_stato.setText(f"IL TUO PACCO: {n} | APRI GLI ALTRI")
        else:
            premio = self.mappa_pacchi[n]
            self.bottoni_pacchi[n].setEnabled(False)
            self.bottoni_pacchi[n].setText("")
            self.bottoni_pacchi[n].setStyleSheet("background-color: #333;")

            # "Spegni" il premio dalle colonne laterali
            if premio in self.labels_blu:
                self.labels_blu[premio].setStyleSheet("background-color: gray; color: darkgray; padding: 5px;")
            elif premio in self.labels_rossi:
                self.labels_rossi[premio].setStyleSheet("background-color: gray; color: darkgray; padding: 5px;")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = AffariTuoi()
    ex.show()
    sys.exit(app.exec_())
