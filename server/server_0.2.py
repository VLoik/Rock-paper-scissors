#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket, random, pickle
import threading

choices = ['Rock', 'Scissors', 'Paper']
# функция для упаковывания сообщения в единый формат
def prepare_data(mesg, type):
    if (type != 3):
        mesg = mesg.encode("utf-8")
    mesg_type = type
    mesg_type = mesg_type.to_bytes(4, byteorder='big')
    mesg_size = len(mesg)+4
    return (mesg_size).to_bytes(4, byteorder='big') + mesg_type + mesg 

    
#функция-поток, основная обработка сообщений
def give_choise(connections, num):
    clients= []
    random.seed()
    conn = connections[num]['sock']
    addr = connections[num]['address']
    curr_connection = connections[num] # копируем ссылку на текущее соединение, дабы при удалении и смещении других, ничего не ломалось
    wins = 0
    losses = 0
    rounds = 0
    while (True):
        try:        
            mesg_size = conn.recv(4)
            mesg_size = int.from_bytes(mesg_size, byteorder='big')
            receive = 0
            data = b''
            while receive < mesg_size:
                block = conn.recv(min(mesg_size - receive, 2048))
                if block == '':
                    raise RuntimeError("Socket connection broken")
                data=data +block
                receive = receive + len(block)
            mesg_type = data[:4]   
            mesg_type = int.from_bytes(mesg_type, byteorder='big')
            data = data[4:].decode("utf-8")
            if(mesg_type == 0):                                       # тип сообщения: 0 - обычное сообщение с выбором игрока/сервера
                print("Client from: ", addr)                          #                1 - ответ сервера с результатом игры 
                print('Name: ' + curr_connection['name'])             #                2 - сообщение с именем клиента при логине
                print("User choice: " + data)                         #                3 - прием/передача сообщений от/к клиенту-монитору
                choice = choices[random.randint(0,2)]                        
                conn.send(prepare_data(choice, 0))
                print("Server choice: " + choice)
            
                if (data == choice): 
                    result = 'Tie'
                    rounds +=1
                    conn.send(prepare_data(result, 1))
                if ((data == 'Rock' and choice == 'Scissors') or (data == 'Paper' and choice == 'Rock') or (data == 'Scissors' and choice == 'Paper')): 
                    result = 'Win'
                    rounds +=1
                    wins +=1
                    conn.send(prepare_data(result, 1))
                if ((data == 'Rock' and choice == 'Paper') or (data == 'Paper' and choice == 'Scissors') or (data == 'Scissors' and choice == 'Rock')): 
                    result = 'Lose'
                    rounds +=1
                    losses +=1
                    conn.send(prepare_data(result, 1))
                print('Wins/games: ', wins/rounds*100, '%')
                curr_connection['stats'] = wins/rounds*100
            if (mesg_type == 2):
                curr_connection['name'] = data
            if (mesg_type == 3):   # выписываем все клиенты, кроме мониторов (зачем их учитывать в статистике?), сериализуем и отправляем клиенту-монитору
                curr_connection['stats'] = 'Monitor' 
                for client in connections:
                    if (client['stats'] != 'Monitor'):
                        clients.append({'name': client['name'], 'address' : client['address'], 'stats': client['stats']})
                dump = pickle.dumps(clients)
                conn.send(prepare_data(dump, 3))
                clients = []                          
        except Exception as err:
            print(err)
            print('Connection lost on: ', addr)
            conn.close()
            for i in range(len(connections)):  #ищем в общем списке текущее соединение и выпиливаем его
                if connections[i] is curr_connection:
                    break
            connections.pop(i)
            exit()
    

def main():
    connections = []
    sock = socket.socket()
    sock.bind(('', 12345))
    print("Ready! Waiting for connection")
    sock.listen(5)
    while (True):  
        conn, addr = sock.accept()
        print("New connection on:", addr)
        connections.append({'sock' : conn, 'address' : addr, 'stats': 0, 'name': 'Unknown'})        
        th = threading.Thread(name='th'+str(len(connections)), target=give_choise, args=(connections,len(connections)-1))
        th.start()        

if __name__ == '__main__':
    main()