#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding=utf8  
import requests, PyPDF2, os, re, time, types, sys, smtplib, platform
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, WebDriverException

class HomeworkSolver:
    def send_mail(self, email, password, message):
        server = smtplib.SMTP_SSL("smtp.gmail.com")
        server.login(email, password)
        server.sendmail(email, email, message)
        server.quit()

    def __init__(self, email, password):
        self.start_time = time.time()
        self.user_operating_system = platform.system()
        if self.user_operating_system == "Windows":
            program_files_x86_path = os.environ['programfiles(x86)']
            files_in_program_files_x86 = os.listdir(program_files_x86_path)  
            main_path = os.environ["homepath"]
            if "Google" in files_in_program_files_x86:
                if "chrome" in os.listdir("{}\\{}\\{}\\{}".format(main_path, program_files_x86_path, "Google", "Chrome")):
                    self.browser = webdriver.Chrome()
        elif self.user_operating_system == "Linux":
            if "firefox" in os.listdir("/usr/bin"):
                self.browser = webdriver.Firefox()
        else:
            print("[-] This program is not for mac")
            sys.exit()
        print("[!] If this program is interrupted in any given moment, it will crash\n")
        reload(sys)
        sys.setdefaultencoding('utf8')
        self.homework_files_names = []
        self.total_pdf_text_extraction = ""
        self.file_extraction_dict = {} # For each file there is corresponding text. File is key, text is value
        self.homework_questions = []
        self.websites_of_first_page_search_result = {}
        self.data_set_questions_and_links = {} # For each brainly link there is a corresponding question. Link is key, question is value
        self.lookuped_questions = []
        self.brainly_links = []
        self.total_amount_of_urls_found = 0
        self.content_of_valid_brainly_links = {} # For each brainly link, there is a corresponding answer. Link is key, answer is value
        self.email = email
        self.password = password
        self.questions_answers = {}
        self.space_between_lines = "\n"
        self.docs_questions_answers = {}
        self.doc_subject = {} # For each document, there is a subject

    def terminate(self):
        self.browser.quit()
        playsound("time-is-now.wav")

    def download(self, url):
        print("[+] Downloading " + str(url))
        if isinstance(url, types.ListType):
            file_names = []
            for link in url:
                response = requests.get(link)
                file_name = link.split("/")[-1]
                with open(file_name, "wb") as file_to_download:
                    file_to_download.write(response.content)
                file_names.append(file_name)
            return file_names
        else:
            response = requests.get(url)
            file_name = url.split("/")[-1]
            with open(file_name, "wb") as file_to_download:
                file_to_download.write(response.content)
            return file_name

    def delete_file(self, file_name):
        print("[+] Deleting file(s) " + str(file_name))
        if isinstance(file_name, types.ListType):
            for file in file_name:
                os.remove(file)
        else:
            os.remove(file_name)


    def download_homework_of_each_week_section(self):
        print("[+] Downloading homework of each section")
        for section in self.week_sections:
            section.click() # Click the section
            extra_resources_to_download = []
            homework_hrefs = []
            homework_a_tags = self.browser.find_element_by_class_name("resources__week__sections").find_elements_by_class_name(
                "resources__week__section")[1].find_elements_by_tag_name("a") 
            for a_tag in homework_a_tags:
                homework_hrefs.append(a_tag.get_attribute("href")) # The href link of the homework
            try:
                extra_resources = self.browser.find_element_by_class_name("resources__week__sections").find_elements_by_class_name(
                "resources__week__section")[0].find_elements_by_tag_name("a")
                for resource in extra_resources:
                    # We need to split the url to found out if it is a pdf file
                    if "pdf" in resource.get_attribute("href").split("/")[-1]:
                        extra_resources_to_download.append(resource)

            except NoSuchElementException:
                pass
            
            homework_pdfs = self.download(homework_hrefs) 

            for homework_name in homework_pdfs:
                self.homework_files_names.append(homework_name)

            for resource in extra_resources_to_download:
                resource_pdf_file_name = self.download(resource.get_attribute("href"))
                self.homework_files_names.append(resource_pdf_file_name)

    def extract_text_from_pdf_file(self, pdf_file_name):
        print("[+] Extracting text from pdf file(s) " + str(pdf_file_name))
        possible_subjects = []
        if isinstance(pdf_file_name, types.ListType):
            for file_name in pdf_file_name:
                total_pdf_text_extraction = ""
                pdf_file = open(file_name, "rb")
                pdfReader = PyPDF2.PdfFileReader(pdf_file)
                
                for page in pdfReader.pages: 
                    total_pdf_text_extraction = total_pdf_text_extraction + page.extractText().replace("\n", "")
                self.file_extraction_dict[file_name] = total_pdf_text_extraction
                
                for i in range(0, 3):
                    possible_subjects.append(self.file_extraction_dict[file_name].replace("\n", "").split()[i])
                
                self.doc_subject[file_name] = possible_subjects
        else:
            total_pdf_text_extraction = ""
            pdf_file = open(pdf_file_name, "rb")
            pdfReader = PyPDF2.PdfFileReader(pdf_file)
            for page in pdfReader.pages: 
                total_pdf_text_extraction = total_pdf_text_extraction + page.extractText().replace("\n", "")
            
            for i in range(0, 3):
                possible_subjects.append(page.extractText().replace("\n", "").split()[i])
            self.doc_subject[pdf_file_name] = possible_subjects
            self.file_extraction_dict[pdf_file_name] = total_pdf_text_extraction

    def extract_spanish_questions_from_text(self, text):
        homework_questions_not_complete = []
        questions_disorganized_encoded = re.findall("¿[^-_/.,\\\\]+\?", (text).encode(encoding="utf-8"))
        questions_to_add = []
        for encoded_question in questions_disorganized_encoded:
            homework_questions_not_complete.append(encoded_question)

        for question in homework_questions_not_complete:
            implanted_questions = question.replace("\xc2\xbf", "¿").split("¿")
            for implanted_question in implanted_questions:
                self.homework_questions.append(implanted_question)
                questions_to_add.append(implanted_question.replace("\xc2\xbf", "¿").decode("utf-8"))

    def lookup_questions(self):
        try:
            # Search questions on google
            for question in self.homework_questions:
                if question != "" and question not in self.lookuped_questions:
                    self.browser.get("https://www.google.com/")
                    search_bar = self.browser.find_elements_by_tag_name("input")[3]
                    search_bar.click()
                    search_bar.send_keys(question.replace("\xc2\xbf", "¿").decode("utf-8"))
                    search_bar.send_keys(Keys.ENTER)
                    print("[+] Google Searching Question :  " + question.replace("\xc2\xbf", "¿").decode("utf-8"))
                    self.lookuped_questions.append(question)
                    time.sleep(5.0)
                    for site in self.browser.find_elements_by_class_name("r"):
                        try:
                            url_link = site.find_element_by_tag_name("a").get_attribute("href")
                            text_below_or_onTopof_url = site.find_element_by_tag_name("cite").text
                            self.websites_of_first_page_search_result[url_link] = text_below_or_onTopof_url
                            if "brainly" in text_below_or_onTopof_url:
                                if self.data_set_questions_and_links.has_key(url_link):
                                    data = self.data_set_questions_and_links[url_link] + question.replace("\xc2\xbf", "¿").decode("utf-8")
                                else:
                                    self.data_set_questions_and_links[url_link] = question.replace("\xc2\xbf", "¿").decode("utf-8")
                        except (NoSuchElementException, KeyboardInterrupt) as error:
                            if error == KeyboardInterrupt:
                                break
                            elif error == NoSuchElementException:
                                continue
                    else:
                        continue
        except KeyboardInterrupt:
            pass

    def filter_brainly_links_and_store_them_in_a_list(self):
        print("[+] Filtering urls")
        for url_link in self.websites_of_first_page_search_result:
            if "brainly" in self.websites_of_first_page_search_result[url_link]:
                self.brainly_links.append(url_link)
                time.sleep(5.0)
            self.total_amount_of_urls_found = self.total_amount_of_urls_found + 1

    def open_brainly_links_catch_answer_text(self):
        print("[+] Opening brainly links and catching answers")
        for link in self.brainly_links:
            self.browser.get(link)
            try:
                for content in self.browser.find_elements_by_class_name("sg-text.js-answer-content.brn-rich-content"):
                    for answer_line in content.find_elements_by_tag_name("p"):
                        if self.content_of_valid_brainly_links.has_key(link):
                            self.content_of_valid_brainly_links[link] = self.content_of_valid_brainly_links[link] + answer_line.text.encode("utf-8")
                        else:
                            self.content_of_valid_brainly_links[link] = answer_line.text.encode("utf-8")
            except NoSuchElementException:
                continue
            time.sleep(5.0)

    def relate_questions_to_answers(self):
        print("[+] Organizing answers to corresponding questions")
        for link in self.brainly_links:
            if self.data_set_questions_and_links.has_key(link): # If the brainly link has a question
                if self.content_of_valid_brainly_links.has_key(link): # If the brainly link has an answer
                    question = self.data_set_questions_and_links[link]
                    answer = self.content_of_valid_brainly_links[link]
                    if self.questions_answers.has_key(question):
                        self.questions_answers[question] = self.questions_answers[question] + answer
                    else:
                        self.questions_answers[question] = answer
        
    def relate_file_to_question_and_answer_set(self):
        for homework_file in self.homework_files_names:
            print("[+] Relating " + str(homework_file) + " to its corresponding questions and answers")
            dict_questions_answers = {}
            text_of_homework_file = self.file_extraction_dict[homework_file]
            for link in self.brainly_links:
                question = self.data_set_questions_and_links[link]
                if question != "" and question in text_of_homework_file:
                    try:
                        dict_questions_answers[question] = self.questions_answers[question.replace("\xc2\xbf", "¿").decode("utf-8")]
                    except KeyError:
                        continue
                self.docs_questions_answers[homework_file] = dict_questions_answers 

    def general_return_answers(self):
        self.filter_brainly_links_and_store_them_in_a_list()
        self.open_brainly_links_catch_answer_text()
        self.relate_questions_to_answers()
        self.relate_file_to_question_and_answer_set()
        self.get_homework_result()

    def get_homework_result(self): # The Gold of The program
        for doc in sorted(self.docs_questions_answers):
            print("Document : " + doc + "\n")
            print("Possible Subjects : " + str(self.doc_subject[doc]) + "\n")
            for question in self.docs_questions_answers[doc]:
                print(question + "\n")
                for content in self.docs_questions_answers[doc][question].split(":"):
                    print(content)
                print("\n\n")

    def get_extra_data(self):
        print("\n\n-------------Data-------------\n\n")
        print("Amount of Brainly Links Captured : " + str(len(self.brainly_links)) + self.space_between_lines)
        print("Amount of Homework Answers Extracted : " + str(len(self.content_of_valid_brainly_links)) + self.space_between_lines)
        print("Elapsed Time : {} minutes ({} seconds) {}".format(((time.time() - self.start_time)/60.0), (time.time() - self.start_time), self.space_between_lines))
        print("Filtered : " + str(self.total_amount_of_urls_found) + " links" + self.space_between_lines)
        print("Brainly Links Extracted : " + str(self.brainly_links) + self.space_between_lines)
        print("Amount of Homework Questions Captured : " + str(len(self.homework_questions)) + self.space_between_lines)
        print("Homework Files : "  + str(self.homework_files_names) + self.space_between_lines)
        print("Deleted Files : " + str(self.homework_files_names) + self.space_between_lines)
        print("Extracted Text : " + str(self.total_pdf_text_extraction.encode(encoding="utf-8")) + self.space_between_lines)
        print("Questions Extracted : " + str(self.homework_questions) + self.space_between_lines)
        print("Homework Answers : " + str(self.content_of_valid_brainly_links) + self.space_between_lines)
        print("Websites of First Page Results : " + str(self.websites_of_first_page_search_result) + self.space_between_lines)


    def return_answers_by_url(self, email, password, homework_url, sections_to_click_through, verbose):
        self.homework_url = homework_url
        self.resource_homework_url = self.homework_url
        self.browser.get(self.resource_homework_url)
        self.week_sections = []
        sections = []
        if sections_to_click_through != [] and (len(sections_to_click_through) > 1):
            try:
                section_index = range(sections_to_click_through[0], sections_to_click_through[1])
                section_index.append(int(sections_to_click_through[-1]))
                sections = self.browser.find_element_by_class_name("resources__week__weeks").find_elements_by_tag_name("button")
                for index in section_index:
                    self.week_sections.append(sections[index - 1])
            except IndexError:
                print("[-] Session Cancelled Due To Range Error")
        elif len(sections_to_click_through) == 1:
            sections = self.browser.find_element_by_class_name("resources__week__weeks").find_elements_by_tag_name("button")
            self.week_sections.append(sections[sections_to_click_through[0] - 1])
        

        # Step 1. Go through each week section, and download the pdf files.
        self.download_homework_of_each_week_section()

        # Step 2. Extract text from the pdf files.
        self.extract_text_from_pdf_file(self.homework_files_names)

        # Step 3. Extract the questions from the text of each pdf file.
        print("[+] Extracting questions from text") 
        for name in self.homework_files_names:
            self.extract_spanish_questions_from_text(self.file_extraction_dict[name])

        # Step 4. Delete all the homework files.
        self.delete_file(self.homework_files_names)

        # Step 5. Lookup all the questions of the text of each homework file.
        self.lookup_questions()

        # Step 6
        self.general_return_answers()

        # Step 7
        self.get_homework_result()

        # Check if extra data should be printed
        if verbose == True:
            self.get_extra_data()

        # Check if email notification should be sent
        if email != "" and password != "":
            self.send_mail(email, password, "Homework Task Successful")

        # Step 8
        self.terminate()

    def return_answers_by_document(self, document_name, email, password, verbose):
        # Append the document to the homework files 
        self.homework_files_names.append(document_name)

        # Step 1
        self.extract_text_from_pdf_file(document_name)
        
        # Step 2
        for name in self.homework_files_names:
            self.extract_spanish_questions_from_text(self.file_extraction_dict[name], name)

        # Step 3 
        self.lookup_questions()

        # Step 4
        self.general_return_answers()

        if verbose == True:
            self.get_extra_data()

        if email != "" and password != "":
            self.send_mail(email, password, "Homework Task Successful")

        # Step 5
        self.terminate()

    def run(self, method_to_apply, homework_url, document_name, sections, verbose):

        if ((homework_url == "") and (document_name != "") and (method_to_apply == "1")):
            self.return_answers_by_document(document_name, self.email, self.password, verbose)

        elif ((homework_url != "") and (document_name == "") and (method_to_apply == "2" or method_to_apply == "3" or method_to_apply == "4")):
            self.return_answers_by_url(self.email, self.password, homework_url, sections, verbose)