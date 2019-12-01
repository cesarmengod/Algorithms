from multiprocessing.connection import Listener
from multiprocessing import Process, Manager
from multiprocessing.connection import Client
from multiprocessing import Lock
from multiprocessing.connection import AuthenticationError

from time import time

def crearcuenta(m, cuentas, contactos):
    if m[0][0] in cuentas.keys():
        answer = ['notify_new', (False, 'usuario ya existente')]
    else:
        buzon[m[0][0]] = []
        cuentas[m[0][0]] = m[0][1],'Offline'
        contactos[m[0][0]] = m[2]
        answer = ['notify_new', (True, 'cuenta creada con exito')]
    conn.send(answer)
        
def agregar(m, id, cuentas, contactos):
    if m[0][0] in cuentas.keys():
        if cuentas.get(m[0][0])[0]==m[0][1]:
            if cuentas.get(m[0][0])[1] == 'Online':
                if cuentas.get(m[0][0])[2] == id:
                    if m[2] in cuentas.keys():
                        if m[2] not in contactos.get(m[0][0]):
                            contacto = contactos.get(m[0][0])
                            contacto.append(m[2])
                            contactos[m[0][0]] = contacto
                            answer = ['notify_add_contact', (True, "contacto agregado")]
                        else:
                            answer = ['notify_add_contact', (False, "el contacto estaba agregado")]
                    else:
                        answer = ['notify_add_contact', (False, "el usuario no existe")]
                else:
                    answer = ['server_notify_chat', (False, 'conectado en otro pc')]
            else:
                answer = ['notify_add_contact', (False, 'usted esta offline')]
        else:
            answer = ['notify_add_contact', (False, 'password incorrecta')]
    else:
        answer = ['notify_add_contact', (False, 'su usuario no existe')]
    conn.send(answer)
    
def online(conn, id, cuentas, rel_lastacp_dirl, contactos, m):
    if id not in rel_lastacp_dirl.keys():
        if m[0][0] in cuentas.keys():
            if (m[0][0], (m[0][1], 'Offline')) in cuentas.items():
                rel_lastacp_dirl[id] = m[2]
                cuentas[m[0][0]] = m[0][1], 'Online', id, rel_lastacp_dirl.get(id)
                answer = ['notify_go_online', (True, 'usted se ha conectado')]
                conn.send(answer)
                for client, info in cuentas.items():
                    if info[1] == 'Online':
                        if not info[2] == id:
                            if client in contactos.get(m[0][0]):
                                conn = Client(address=info[3][0], authkey=info[3][1])
                                conn.send(["server_notify_go_online_user", m[0][0]])
                                conn.close()
                if buzon.get(m[0][0]) != []:
                    info = cuentas.get(m[0][0])
                    conn = Client(address=info[3][0], authkey=info[3][1])
                    mensajes = buzon.pop(m[0][0])
                    conn.send(["server_notify_inbox", mensajes])
                    conn.close()
            else:
                if (cuentas.get(m[0][0])[1] == 'Online') and (m[0][1] == cuentas.get(m[0][0])[0]):
                    answer = ['notify_go_online', (False, 'usted esta online')]
                else:
                    answer = ['notify_go_online', (False, 'password incorrecta')]
                conn.send(answer)
        else:
            answer = ['notify_go_online', (False, 'no existe la cuenta')]
            conn.send(answer)
    else:
        answer = ['notify_go_online', (False, 'usted estaba online o conflicto de ip')]
        conn.send(answer)

def offline(conn, id, cuentas, rel_lastacp_dirl, contactos, m):
    if m[0][0] in cuentas.keys():
        if cuentas.get(m[0][0])[0]==m[0][1]:
            if cuentas.get(m[0][0])[1] == 'Online':
                if cuentas.get(m[0][0])[2] == id:
                    cuentas[m[0][0]] = m[0][1], 'Offline'
                    rel_lastacp_dirl.pop(id)
                    answer = ["notify_quit", True]
                    conn.send(answer)
                    for client, info in cuentas.items():
                        if info[1] == 'Online':
                            if not info[2] == id:
                                if client in contactos.get(m[0][0]):
                                    conn = Client(address=info[3][0], authkey=info[3][1])
                                    conn.send(["server_notify_quit_user", m[0][0]])
                                    conn.close()
                else:
                    answer = ['notify_quit', False]
                    conn.send(answer)
            else:
                answer = ["notify_quit", False]
                conn.send(answer)
        else:
            answer = ["notify_quit", False]
            conn.send(answer)
    else:
        answer = ["notify_quit", False]
        conn.send(answer)

            
def chat(conn, id, cuentas, contactos, m, lock):
    if m[0][0] in cuentas.keys():
        if cuentas.get(m[0][0])[0]==m[0][1]:
            if cuentas.get(m[0][0])[1] == 'Online':
                if cuentas.get(m[0][0])[2] == id:
                    if m[2][0] in cuentas.keys():
                        if m[2][0] in contactos.get(m[0][0]) and m[0][0] in contactos.get(m[2][0]):
                            if cuentas.get(m[2][0])[1] == 'Online':
                                answer = ['server_notify_chat', (True, 'mensaje recibido instantaneamente')]
                                conn.send(answer)
                                info = cuentas.get(m[2][0])
                                conn = Client(address=info[3][0], authkey=info[3][1])
                                conn.send(["server_notify_chat", (m[0][0], m[2][1])])
                                conn.close()
                            if cuentas.get(m[2][0])[1] == 'Offline':
                                lock.acquire()
                                answer = ['server_notify_chat', (True, 'mensaje almacenado en buzon')]
                                conn.send(answer)
                                correo = buzon.get(m[2][0])
                                correo.append((m[0][0], m[2][1]))
                                buzon[m[2][0]] = correo
                                lock.release()
                        else:
                            answer = ['server_notify_chat', (False, 'no sois contactos')]
                            conn.send(answer)
                    else:
                        answer = ['server_notify_chat', (False, 'no existe el destinatario')]
                        conn.send(answer)
                else:
                    answer = ['server_notify_chat', (False, 'conectado en otro pc')]
                    conn.send(answer)
            else:
                answer = ['server_notify_chat', (False, 'usted esta offline')]
                conn.send(answer)
        else:
            answer = ['server_notify_chat', (False, 'password incorrecta')]
            conn.send(answer)
    else:
        answer = ['server_notify_chat', (False, 'no existe tu nombre usuario')]
        conn.send(answer)
            
            
def serve_client(conn, id, cuentas, rel_lastacp_dirl, contactos, m, lock):
    connected = True
    ver = True
    while connected:
        try:
            m = conn.recv()
        except (EOFError, IOError):
            print 'connection abruptly closed by client'
            connected = False
        print 'received message:', m, 'from', id
        try:
            if m[1] == "new_user":
                try:
                    crearcuenta(m, cuentas, contactos)
                except IOError:
                    print 'conexion cerrada (crear cuenta)'
                    connected = False
            if m[1] == "go_online":
                try:
                    online(conn, id, cuentas, rel_lastacp_dirl, contactos, m)
                except IOError:
                    print 'conexion cerrada (online)'
                    connected = False
            if m[1] == "chat":
                try:
                    chat(conn, id, cuentas, contactos, m, lock)
                except IOError:
                    print 'conexion cerrada (chat)'
                    connected = False
            if m[1] == "add_contact":
                try:
                    agregar(m, id, cuentas, contactos)
		except IOError:
                    print 'conexion cerrada (add_contact)'
                    connected = False
            if m[1] == "quit":  
                connected = False
                ver = False
                offline(conn, id, cuentas, rel_lastacp_dirl, contactos, m)
                conn.close()  
            print cuentas
            print buzon
            print rel_lastacp_dirl
            print contactos
        except TypeError:
            print 'connection abruptly closed by client'
            connected = False
            ver = True
    print id, 'connection closed'
    if ver:
        for client, info in cuentas.items():
            if info[1] == 'Online':
                if info[2] == id:
                    rel_lastacp_dirl.pop(id)
                    inf = cuentas.get(client)
                    cuentas[client] = inf[0], 'Offline'
                    for client, info in cuentas.items():
                        if info[1] == 'Online':
                            if not info[2] == id:
                                if client in contactos.get(m[0][0]):
                                    conn = Client(address=info[3][0], authkey=info[3][1])
                                    conn.send(["server_notify_quit_user", m[0][0]])
                                    conn.close()
    

if __name__ == '__main__':
    listener = Listener(address=('127.0.0.1', 6000), authkey='server')
    print 'listener starting'

    m = Manager()
    buzon = m.dict()
    rel_lastacp_dirl = m.dict()
    cuentas = m.dict()
    contactos = m.dict()
    lock = Lock()
    
    while True:
        print 'accepting conexions'
        try:
            conn = listener.accept()
            print 'connection accepted from', listener.last_accepted
            p = Process(target=serve_client, args=(conn, listener.last_accepted, cuentas,
                                                   rel_lastacp_dirl, contactos, m, lock))
            p.start()
        except AuthenticationError:
            print 'Connection refused, incorrect password'
    listener.close()
    print 'end server'
