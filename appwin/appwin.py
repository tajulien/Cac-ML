import os
import sys

import mysql.connector
import pandas as pd
import tokened

from PySide2 import QtWidgets,QtCore,QtWebEngineWidgets


def justerecup():
    #on se connecte au serveur
    #SELECT * FROM `market_indics` WHERE `act_name` = 'Michelin' ORDER BY `date`  ASC LIMIT 10

    connection = mysql.connector.connect(host=tokened.bddurl,
                                         database='market_datas',
                                         user=tokened.bdduserjuwl,
                                         password=tokened.bddpassjuwl)
    
    # on récupère la table qui contient les données sources
    sql_select_Query = "SELECT * FROM `market_indics`"
    cursor = connection.cursor()
    cursor.execute(sql_select_Query)
    records = cursor.fetchall()
    dfi = pd.DataFrame(records,columns=["Prim_key", "act_name", "act_isin", "date", "mk_value", "mma10", "mma20", "mma50", "mma100","mma200", "macd","bollinger_inf","bollinger_sup","signaleuh"])
    mk_name = dfi["act_name"].drop_duplicates().tolist()
    return mk_name


class Window(QtWidgets.QTableWidget):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("QWidget{background-color: #343a40;}")


        self.main_layout = QtWidgets.QGridLayout(self)


        self.listaction = QtWidgets.QComboBox(self)
        self.listaction.insertItems(42, justerecup())

        self.spin = QtWidgets.QSpinBox()
        self.spin.setValue(300)
        self.spin.setRange(7, 1200)

        self.btn_refresh = QtWidgets.QPushButton("Refresh")
        self.btn_refresh.clicked.connect(self.refresh)

        self.spin.setStyleSheet("color: white;")
        self.btn_refresh.setStyleSheet("color: white;")
        self.btn_refresh.setFlat(True)


        self.view = QtWebEngineWidgets.QWebEngineView()
        self.view.load(QtCore.QUrl("http://127.0.0.1:8000"))

        self.setWindowTitle("Application de suivi des actions - CAC 40")

        self.main_layout.addWidget(self.spin, 0, 0, 1, 1)
        self.main_layout.addWidget(self.btn_refresh, 0, 1, 1, 1)
        self.main_layout.addWidget(self.listaction,0, 2, 1, 1)
        self.main_layout.addWidget(self.view, 1, 0, 1, 3)

    def refresh(self):
        days = self.spin.value()
        nom_action = self.listaction.currentText()
        self.view.load(QtCore.QUrl(f"http://127.0.0.1:8000/days={days}&nom_action={nom_action}"))

app = QtWidgets.QApplication([])
win = Window()
win.showFullScreen()
app.exec_()