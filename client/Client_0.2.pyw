#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QApplication, QLineEdit, QTextEdit, QMainWindow, QInputDialog
from PyQt5.QtCore import Qt, QCoreApplication, QTimer, QByteArray, QDataStream, QIODevice
from PyQt5.Qt import QColor, QIcon
from PyQt5.QtNetwork import *
PORT = 90090

class MWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initial()

    def initial(self):
        text, ok = QInputDialog.getText(self, 'Login', 'Enter your name:')
        if (ok):
            self.name = text
        else: exit()
        self.RockButton = QPushButton("Rock")
        self.ScissorsButton = QPushButton("Scissors")
        self.PaperButton = QPushButton("Paper")
        r_icon = QIcon('rock.png')
        s_icon = QIcon('sci.png')
        p_icon = QIcon('paper.png')
        self.RockButton.setIcon(r_icon)
        self.ScissorsButton.setIcon(s_icon)
        self.PaperButton.setIcon(p_icon)
        self.RockButton.clicked.connect(self.RockButtonClicked)
        self.ScissorsButton.clicked.connect(self.ScissorsButtonClicked)
        self.PaperButton.clicked.connect(self.PaperButtonClicked)

        self.yc_label = QLabel("Your choose: ")
        self.sc_label = QLabel("Server choose: ")
        self.result_label = QLabel("Result: ")
        
        v_layout = QVBoxLayout()
        v_layout.addWidget(self.yc_label)
        v_layout.addWidget(self.sc_label)
        v_layout.addWidget(self.result_label)

        h_layout = QHBoxLayout()
        h_layout.addWidget(self.RockButton)
        h_layout.addWidget(self.ScissorsButton)
        h_layout.addWidget(self.PaperButton)

        m_layout = QVBoxLayout()
        m_layout.addLayout(v_layout)
        m_layout.addLayout(h_layout)
        widg = QWidget()
        widg.setLayout(m_layout)
        self.setCentralWidget(widg)

        self.tcpSocket = QTcpSocket()
        self.tcpSocket.connectToHost('localhost', 12345)
        self.tcpSocket.readyRead.connect(self.getResponse)
        self.tcpSocket.disconnected.connect(self.reconnect)
        self.tcpSocket.connected.connect(self.auth)
        self.block_size = 0

        self.reconnect_timer = QTimer() # таймер переподключения к серверу
        self.reconnect_timer.timeout.connect(self.reconnect)
        self.reconnect_timer.setSingleShot(True)
        self.setGeometry(500, 500, 500, 250)
        self.setWindowTitle('Rock, scissors, paper!')
        self.statusBar().showMessage('Ready!')
        self.show()
        
    def RockButtonClicked(self):
        block = QByteArray()
        outstream = QDataStream(block, QIODevice.WriteOnly)
        outstream.writeInt(0) # размер сообщения
        s = block.size()
        outstream.writeInt(0) # Тип сообщения: 0 - команда, 1 - ответ сервера с результатом, 2 - логин, 3 - монитор
        s = block.size()
        block.push_back("Rock".encode("utf-8"))
        s = block.size()
        outstream.device().seek(0)
        outstream.writeUInt32(block.size() - 4)
        s = block.size()
        if self.tcpSocket.state() == 3:
            self.tcpSocket.write(block)
            self.yc_label.setText("You choose: Rock")
            self.RockButton.setEnabled(False)
            self.ScissorsButton.setEnabled(False)
            self.PaperButton.setEnabled(False)
        else: self.statusBar().showMessage('No connection to the server!')
                   

    def ScissorsButtonClicked(self):
        block = QByteArray()
        outstream = QDataStream(block, QIODevice.WriteOnly)
        outstream.writeInt(0) # размер сообщения
        s = block.size()
        outstream.writeInt(0) # Тип сообщения: 0 - команда, 1 - ответ сервера с результатом, 2 - логин, 3 - монитор
        s = block.size()
        block.push_back("Scissors".encode("utf-8"))
        s = block.size()
        outstream.device().seek(0)
        outstream.writeUInt32(block.size() - 4)
        s = block.size()
        if self.tcpSocket.state() == 3:
            self.tcpSocket.write(block)
            self.yc_label.setText("You choose: Scissors")
            self.RockButton.setEnabled(False)
            self.ScissorsButton.setEnabled(False)
            self.PaperButton.setEnabled(False)  
        else: self.statusBar().showMessage('No connection to the server!')

    def PaperButtonClicked(self):
        block = QByteArray()
        outstream = QDataStream(block, QIODevice.WriteOnly)
        outstream.writeInt(0) # размер сообщения
        s = block.size()
        outstream.writeInt(0) # Тип сообщения: 0 - команда, 1 - ответ сервера с результатом, 2 - логин, 3 - монитор
        s = block.size()
        block.push_back("Paper".encode("utf-8"))
        s = block.size()
        outstream.device().seek(0)
        outstream.writeInt(block.size() - 4)
        s = block.size()
        if self.tcpSocket.state() == 3:
            self.tcpSocket.write(block)
            self.yc_label.setText("You choose: Paper")
            self.RockButton.setEnabled(False)
            self.ScissorsButton.setEnabled(False)
            self.PaperButton.setEnabled(False)
        else: self.statusBar().showMessage('No connection to the server!')  
    
    def getResponse(self):
        input_stream = QDataStream(self.tcpSocket)
        if self.block_size == 0:                        #если сообщение пришло в первый раз
            if self.tcpSocket.bytesAvailable() < 2:
                return
            self.block_size = input_stream.readInt()
        if self.tcpSocket.bytesAvailable() < self.block_size: #Если пришло меньше байт, чем разжер сообщения, ждем остальное
            return
        type_mesg = input_stream.readInt()
        raw_data = input_stream.readRawData(self.block_size-4)
        if(type_mesg == 0):
            server_choise = raw_data.decode('utf-8')
            self.sc_label.setText("Server Choose: "+server_choise)
        if(type_mesg == 1): 
            result = raw_data.decode('utf-8')
            self.result_label.setText('Result: '+ result)
            self.RockButton.setEnabled(True)
            self.ScissorsButton.setEnabled(True)
            self.PaperButton.setEnabled(True)
        self.block_size = 0
        if (self.tcpSocket.bytesAvailable() != 0): 
            self.getResponse() 

    def reconnect(self):
        if self.tcpSocket.state() != 3:
            self.statusBar().showMessage('Connection lost. Try to reconnect...')
            self.tcpSocket.connectToHost('localhost', 12345)
            self.reconnect_timer.start(10000)
            
    def auth(self):
        self.statusBar().showMessage('Connected!')
        block = QByteArray()
        outstream = QDataStream(block, QIODevice.WriteOnly)
        outstream.writeInt(0) 
        outstream.writeInt(2) 
        block.push_back(self.name.encode("utf-8"))
        outstream.device().seek(0)
        outstream.writeUInt32(block.size() - 4)
        if self.tcpSocket.state() == 3:
            self.tcpSocket.write(block)
        else: self.statusBar().showMessage('No connection to the server!')
        self.RockButton.setEnabled(True)
        self.ScissorsButton.setEnabled(True)
        self.PaperButton.setEnabled(True)        
           
if __name__ == '__main__':

    app = QApplication(sys.argv)
    mwindow = MWindow()
    sys.exit(app.exec_())