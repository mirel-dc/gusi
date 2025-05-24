import os
from docx import Document
from enum import Enum, auto


class Sections(Enum):
    OOP = "Объектно-ориентированное программирование"
    DB = "Базы данных"
    INFO_SEC = "Защита информации"
    NETWORK = "Сетевое программирование"
    ALGORITHMS = "Структуры и алгоритмы обработки данных"
    QUEUE_THEORY = "Теория массового обслуживания"
    SYS_ADMIN = "Сетевое и системное администрирование"

    @classmethod
    def get_all(cls):
        return [section.value for section in cls]

    @classmethod
    def get_theoryfilename_prefix(cls, section_name):
        mapping = {
            cls.OOP.value: "t_oop",
            cls.DB.value: "t_bd",
            cls.INFO_SEC.value: "t_zi",
            cls.NETWORK.value: "t_sp",
            cls.ALGORITHMS.value: "t_siaod",
            cls.QUEUE_THEORY.value: "t_tmo",
            cls.SYS_ADMIN.value: "t_sisa"
        }
        return mapping.get(section_name, "")

    @classmethod
    def get_pracfilename_prefix(cls, section_name):
        mapping = {
            cls.OOP.value: "p_oop",
            cls.DB.value: "p_bd",
            cls.INFO_SEC.value: "p_zi",
            cls.NETWORK.value: "p_sp",
            cls.ALGORITHMS.value: "p_siaod",
            cls.QUEUE_THEORY.value: "p_tmo",
            cls.SYS_ADMIN.value: "p_sisa"
        }
        return mapping.get(section_name, "")

def show_theory(param):
    filename = f"{Sections.get_theoryfilename_prefix(param)}.docx"

    doc = Document(filename)
    questions = []
    current_question = ""
    current_answer = ""

    for paragraph in doc.paragraphs:
        text = paragraph.text.strip()
        if not text:
            continue

        if text[0].isdigit() and '.' in text.split()[0]:
            if current_question:
                questions.append((current_question, current_answer))
            current_question = text
            current_answer = ""
        else:
            current_answer += text + "\n"

    if current_question:
        questions.append((current_question, current_answer))

    while True:
        for i, (question, _) in enumerate(questions, 1):
            question_text = question.split('.', 1)[1].strip()
            print(f"{i}. {question_text}")
        print(f"{len(questions) + 1}. Назад")

        try:
            choice = int(input(f"(1-{len(questions) + 1}): "))
            if 1 <= choice <= len(questions):
                print("\n" + questions[choice - 1][1])
                input("\nлюбую кнопку")
            elif choice == len(questions) + 1:
                break
            else:
                print("")
        except ValueError:
            print("")

def show_prac(param):
    filename = f"{Sections.get_pracfilename_prefix(param)}.docx"

    doc = Document(filename)
    questions = []
    current_question = ""
    current_answer = ""

    for paragraph in doc.paragraphs:
        text = paragraph.text.strip()
        if not text:
            continue

        if text[0].isdigit() and '.' in text.split()[0]:
            if current_question:
                questions.append((current_question, current_answer))
            current_question = text
            current_answer = ""
        else:
            current_answer += text + "\n"

    if current_question:
        questions.append((current_question, current_answer))

    while True:
        for i, (question, _) in enumerate(questions, 1):
            question_text = question.split('.', 1)[1].strip()
            print(f"{i}. {question_text}")
        print(f"{len(questions) + 1}. Назад")

        try:
            choice = int(input(f"(1-{len(questions) + 1}): "))
            if 1 <= choice <= len(questions):
                print("\n" + questions[choice - 1][1])
                input("\nлюбую кнопку")
            elif choice == len(questions) + 1:
                break
            else:
                print("")
        except ValueError:
            print("")


def show_submenu(param):
    while True:
        print(f"\n--- {param} ---")
        print("1. Теория")
        print("2. Практика")
        print("3. Назад")

        try:
            choice = int(input("(1-3): "))
            if choice == 1:
                show_theory(param)
            elif choice == 2:
                print(f"Вы выбрали: Практика ({param})")
                input("\nлюбую кнопку")
            elif choice == 3:
                break
            else:
                print("")
        except ValueError:
            print("")


def show():
    sections = Sections.get_all()

    while True:
        for i, section in enumerate(sections, 1):
            print(f"{i}. {section}")
        print(f"{len(sections) + 1}. Выход")

        try:
            choice = int(input("(1-8): "))
            if 1 <= choice <= len(sections):
                show_submenu(sections[choice - 1])
            elif choice == len(sections) + 1:
                break
            else:
                print("")
        except ValueError:
            print("")