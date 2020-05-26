import homework_solver, subprocess, os.path, smtplib, types, getpass

course_options = {"1": "https://aprendoencasa.pe/#/nivel/secundaria/grade/3/speciality/37/resources", "2":"https://aprendoencasa.pe/#/nivel/secundaria/grade/3/speciality/33/resources", "quit":"quit"}
send_email_options = ["1", "2", "quit"]
solving_options = ["1", "2", "3", "4", "quit"]
verbose_options = ["1", "2", "quit"]

print("------------------Welcome------------------\n")
print("[!] This program should not be runned in root mode, it will crash if so")
print("This program is meant to solve the homework of DPCC and Communication, 'quit' if you wish to exit the program. Enjoy !\n")

email = ""
password = ""
document_name = ""
byOption = ""
sections_to_get = ""
sections = []
verbose = False

def clear_screen():
    subprocess.check_call("clear")

def login(email, password):
    server = smtplib.SMTP_SSL("smtp.gmail.com")
    try:
        server.login(email, password)
        return True
    except smtplib.SMTPAuthenticationError:
        return False

print("""
1) DPCC
2) Communication
""")
while True:
    subject_homework_to_solve = raw_input("> ")
    if subject_homework_to_solve not in course_options:
        print("[-] Enter a valid option")
        continue
    elif subject_homework_to_solve == "quit":
        exit()
    else:
        break

print("""
Would you like us to send an email to you as a notification when the program has finished ?
1) Yes
2) No
""")
while True:
    send = raw_input("> ")
    if send not in send_email_options:
        print("[-] Enter a valid option")
        continue
    elif send == "quit":
        exit()
    else:
        break

while True:
    if send == "1":
        email = raw_input("Email : ")
        password = getpass.getpass("Password : ")
        print("[+] Checking account...")
        if not login(email, password):
            print("[-] Incorrect Email or Password")
            continue
        elif email == "quit" or password == "quit":
            exit()
        else:
            break
    else:
        break

print("""
Do you wish to solve the homework by link or by document? ('By document' is faster)
1) By Document
2) By Link (All Homework Documents)
3) From One Section Until The Next
4) One Section
""")

while True:
    byOption = raw_input("> ")
    if byOption not in solving_options:
        print("Enter a valid option")
        continue
    elif byOption == "quit":
        exit()
    else:
        break

while True:
    if byOption == "1":
        document_name = raw_input("""Document Name (include extension and make sure its in the same directory) : """)
        course_options[subject_homework_to_solve] = ""
        if os.path.exists(document_name):
            break
        else:
            print("[-] The File Does Not Exist")
            continue
    else:
        break


if byOption == "3":
    print("[!] If you enter the wrong range, the program later on will crash")
    sections_to_get = raw_input("Sections you wish to solve (eg 1-3) : ")
    section_list = sections_to_get.split("-")
    length_of_sections_to_get = len(section_list)
    for item in section_list:
        try:
            sections.append(int(item))
        except ValueError:
            print("[-] Enter a valid option, follow the example")
            break

while True:
    print("[!] If you enter an invalid section (over range), the program later on will crash")
    if byOption == "4":
        section_to_get = raw_input("Section you wish to solve (eg 1) : ")
        try:
            sections.append(int(section_to_get))
            break
        except ValueError:
            print("[-] Enter a valid option, follow the example")
            continue
print("""
Would you like to display extra information after the program execution?
1) Yes
2) No
""")
while True:
    set_verbose = raw_input("> ")
    if set_verbose not in verbose_options:
        print("[-] Enter a valid option")
        continue
    elif set_verbose == "1":
        verbose = True
        print(verbose)
        break
    elif set_verbose == "quit":
        exit()
    else:
        break
# print(sections)
# print(email)
# print(password)
# print(document_name)
# print(byOption)
# print(section_to_get)
# print(sections)
# print(verbose)
clear_screen()
solver = homework_solver.HomeworkSolver(email, password)
solver.run(byOption, course_options[subject_homework_to_solve], document_name, sections, verbose)