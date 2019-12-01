from multiprocessing.connection import Client
from random import random
from time import sleep
from Tkinter import *
from multiprocessing import Queue
from multiprocessing.connection import Listener
from multiprocessing import Process

local_listener = (('127.0.0.1', 5001),'secret client password')

def client_listener(q):
    cl = Listener(address=local_listener[0], authkey=local_listener[1])
    print '.............client listener starting' 
    print '.............accepting conexions'
    while True:
        conn = cl.accept()
        print '.............connection accepted from', cl.last_accepted        
        m = conn.recv()
        print '.............message received from server', m 
        q.put(m)

if __name__ == '__main__':
    root = Tk()
    root.title("Chat")
    root.resizable(0, 0)
    
    frame = Frame(root)    
    frame.pack()
    w = 600
    h = 200
    nombreu=''
    passw=''
    mens=''
    dest=''
    canvas = Canvas(frame, width=w, height=h, bg="green")
    canvas.grid(row=0, column=0, columnspan=6)
    obj=[]
    obj.append(canvas.create_text(300,125,text="vacio"))
    obj.append(canvas.create_text(300,75,text="vacio"))
    q = Queue()
    
    ln = Label(frame,text="Nombreusuario")
    ln.grid(row=1, column=0)
    nv = StringVar()
    nv.set(str(nombreu))
    n = Entry(frame,width=10,textvariable=nv)    
    n.grid(row=1, column=1)
    
    lk = Label(frame,text="password")
    lk.grid(row=2, column=0)
    kv = StringVar()
    kv.set(str(passw))
    k = Entry(frame,width=10,textvariable=kv)    
    k.grid(row=2, column=1)
    
    ldp = Label(frame,text="mensaje")
    ldp.grid(row=1, column=4)
    dpv = StringVar()
    dpv.set(str(mens))
    dp = Entry(frame,width=10,textvariable=dpv)
    dp.grid(row=1, column=5)
    
    ldc = Label(frame,text="destino")
    ldc.grid(row=2, column=4)
    dcv = StringVar()
    dcv.set(str(dest))
    dc = Entry(frame,width=10,textvariable=dcv)
    dc.grid(row=2, column=5)
    
    def lee_param():       
        nombreu = n.get()
        passw = k.get()
        mens = dp.get()
        dest = dc.get()
        return nombreu,passw, mens, dest

    def end():
        nombre,passwor,menss,desti=lee_param()
        q.put([(nombre,passwor),'quit'])
    end = Button(frame, text="Salir", command=end, width=7)
    end.grid(row=1, column=3)

    def send():
        nombre,passwor,menss,desti=lee_param()
        q.put([(nombre,passwor),"chat",(desti,menss)])
    send = Button(frame, text="enviar", command=send, width=7)
    send.grid(row=2, column=3)

    def go_online():
        nombre,passwor,menss,desti=lee_param()
        q.put([(nombre,passwor),"go_online",local_listener])
    go_online = Button(frame, text="go_online", command=go_online, width=7)
    go_online.grid(row=3, column=3) 

    def crear():
        nombre,passwor,menss,desti=lee_param()
        q.put([(nombre,passwor),"new_user",[]])
    crear = Button(frame, text="crear cuenta", command=crear, width=7)
    crear.grid(row=4, column=3)

    def agregar():
        nombre,passwor,menss,desti=lee_param()
        q.put([(nombre,passwor),"add_contact",desti])
    agregar = Button(frame, text="agregar", command=agregar, width=7)
    agregar.grid(row=5, column=3)

    q = Queue()
    print 'trying to connect'
    conn = Client(address=('127.0.0.1', 6000), authkey='server')
    

    cl = Process(target=client_listener, args=(q,))
    cl.start()
    
    try:
        while True:
            if not q.empty():
                s = q.get()
                if s[1] == 'quit':
                    conn.send(s)
                    answer=conn.recv()
                    if answer[1] == True:
                        conn.close()
                        cl.terminate()
                        break
                    else:
                        canvas.itemconfigure(2, text=answer)
                else:
                    if s[1] == "new_user":
                        conn.send(s)
                        answer=conn.recv()
                        canvas.itemconfigure(1,text=answer) 
                    if s[1] == "go_online":
                        conn.send(s)
                        answer=conn.recv()
                        canvas.itemconfigure(1,text=answer)    
                    if s[1] == "chat":
                        conn.send(s)
                        answer=conn.recv()
                        canvas.itemconfigure(1,text=answer)
                    if s[1] == "add_contact":
                        conn.send(s)
                        answer=conn.recv()
                        canvas.itemconfigure(1,text=answer)
                    if s[0] == "server_notify_go_online_user":
                        answer = "el usuario "+str(s[1])+" se ha conectado"
                        canvas.itemconfigure(2,text=answer)
                    if s[0] == "server_notify_quit_user":
                        answer = "el usuario "+str(s[1])+" se ha desconectado"
                        canvas.itemconfigure(2,text=answer)
                    if s[0] == "server_notify_chat":
                        answer = str(s[1][1])+" desde el usuario "+str(s[1][0])
                        canvas.itemconfigure(2,text=answer)
                    if s[0] == "server_notify_inbox":
                        answer = s
                        canvas.itemconfigure(2,text=answer)
            root.update()
    except TclError:
        pass
    conn.close()
    cl.terminate()

