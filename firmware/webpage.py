import json
import socket


OK_200 = b'HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n'
ERR_404 = b'HTTP/1.0 404 NOT FOUND\r\nContent-type: text/html\r\n\r\n'
ERR_400 = b'HTTP/1.0 400 BAD REQUEST\r\nContent-type: text/html\r\n\r\n'



def file_responder_factory(path):
    def get_response():
        return (
            OK_200,
            open(path, 'rb').read()
        )
    return get_response



class ControlWebpage:
    def __init__(self, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        addr = socket.getaddrinfo('0.0.0.0', port)[0][-1]

        self.post_handlers = {}
        self.get_handlers = {}
        
        self.socket.bind(addr)
        self.socket.listen(4)
        self.socket.settimeout(0.05)


    def register_post_handler(self, url, function):
        assert url not in self.post_handlers
        self.post_handlers[url] = function

    def register_get_handler(self, url, function):
        assert url not in self.get_handlers
        self.get_handlers[url] = function
        
    def recv_data(self, connection):
        connection.settimeout(0.05)
        return connection.recv(1024)
        

    def update(self):
        try:
            cl, addr = self.socket.accept()
        except:
            pass
        else:
            print('client connected from', addr)
            raw_data = self.recv_data(cl)
            if raw_data is None:
                print("Aborting")
                return
            

            try:
                action = raw_data.split(b' ', 1)[0]
                url = raw_data.split(b' ', 2)[1]
                data = raw_data.split(b'\r\n\r\n', 1)[1]
            except IndexError:
                cl.send(ERR_400)
                cl.send(b'Malformed Header')

            if action == b'GET':
                for resp in self.get_page(url):
                    cl.sendall(resp)

            elif action == b'POST':
                for resp in self.do_post(url, data):
                    cl.sendall(resp)

            else:
                cl.send(ERR_400)
                cl.send(b'Unknown Action')

            cl.close()

    def get_page(self, url):
        if url in self.get_handlers:
            return self.get_handlers[url]()
        else:
            return (ERR_404,)

    def do_post(self, url, data):
        if url in self.post_handlers:
            return self.post_handlers[url](data)
        else:
            return (ERR_404,)
        

def create_webpage(port):
    server = ControlWebpage(port)

    index = file_responder_factory("index.html")
    server.register_get_handler(
        b'/index.html',
        index
    )
    server.register_get_handler(b'/', index)
    server.register_get_handler(b'/ping', lambda : (OK_200, b'pong'))


    def dummy_post_handler(data):
        print("someone sent:", data)
        return (OK_200, b'{"b":0}')

    server.register_post_handler(b'/control', dummy_post_handler)
    

    return server
    

if __name__ == "__main__":
    port = 8080
    page = None
    while page is None:
        try:
            page = create_webpage(port)
            print("Running on port", port)
        except OSError:
            port += 1
    while True:
        page.update()
    
