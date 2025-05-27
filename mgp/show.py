import re
import subprocess
from docx import Document
from enum import Enum
from importlib.resources import files
from docx.table import Table
from docx.text.paragraph import Paragraph


class Sections(Enum):
    DEEPSEEK = "deepseek"
    OOP = "Объектно-ориентированное программирование"
    DB = "Базы данных"
    INFO_SEC = "Защита информации"
    NETWORK = "Сетевое программирование"
    PROGRAMMING = "Программирование"
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
            cls.NETWORK.value: "p_sp",
            cls.PROGRAMMING.value: "p_p",
            cls.QUEUE_THEORY.value: "p_tmo",
            cls.SYS_ADMIN.value: "p_sisa"
        }
        return mapping.get(section_name, "")


def print_table(table):
    """Печатает таблицу из docx в консоль"""
    col_widths = [0] * len(table.columns)

    for row in table.rows:
        for i, cell in enumerate(row.cells):
            if len(cell.text) > col_widths[i]:
                col_widths[i] = len(cell.text)

    for row in table.rows:
        for i, cell in enumerate(row.cells):
            print(cell.text.ljust(col_widths[i] + 2), end='')
        print()


def extract_formula(element):
    """Извлекает формулы с правильной обработкой скобок и дробных выражений"""
    namespaces = {
        'm': 'http://schemas.openxmlformats.org/officeDocument/2006/math',
        'm2006': 'http://schemas.openxmlformats.org/officeDocument/2006/math',
        'm2010': 'http://schemas.microsoft.com/office/2007/8/2/math',
        'm2013': 'http://schemas.microsoft.com/office/2010/10/math'
    }

    def process_element(elem, in_frac=False, in_bracket=False):
        """Рекурсивно обрабатывает элементы формулы"""
        tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag

        if tag == "t":  # Текстовый элемент
            return elem.text if elem.text else ""

        elif tag == "sup":  # Верхний индекс
            content = "".join(process_element(e, in_frac, in_bracket) for e in elem)
            return f"^{{{content}}}" if content else ""

        elif tag == "sub":  # Нижний индекс
            content = "".join(process_element(e, in_frac, in_bracket) for e in elem)
            return f"_{{{content}}}" if content else ""

        elif tag in ["frac", "m:f"]:  # Дробь
            if len(elem) >= 2:
                num = "".join(process_element(e, True, in_bracket) for e in elem[0])
                den = "".join(process_element(e, True, in_bracket) for e in elem[1])
                return f"({num})/({den})"

        elif tag in ["d", "m:d"]:  # Скобки
            bracket_type = elem.get("m:begChr", "(")  # Начальная скобка
            content = "".join(process_element(e, in_frac, True) for e in elem)
            return f"{bracket_type}{content})"  # Закрывающая скобка

        elif tag in ["num", "m:num", "den", "m:den"]:  # Числитель/знаменатель
            return "".join(process_element(e, in_frac, in_bracket) for e in elem)

        elif tag in ["r", "e"]:  # Группирующие элементы
            content = "".join(process_element(e, in_frac, in_bracket) for e in elem)
            # Добавляем скобки только если внутри дроби и выражение сложное
            if in_frac and not in_bracket and ("+" in content or "-" in content or "*" in content):
                return f"({content})"
            return content

        else:
            return "".join(process_element(e, in_frac, in_bracket) for e in elem)

    for ns_prefix, ns_url in namespaces.items():
        try:
            math_elements = element.xpath(f'.//*[local-name()="oMath" and namespace-uri()="{ns_url}"]')
            for math in math_elements:
                formula = "".join(process_element(e) for e in math)
                if formula:
                    # Постобработка формулы
                    formula = formula.replace("  ", " ").strip()
                    formula = formula.replace("...", "…")
                    # Убираем лишние скобки вокруг простых переменных
                    formula = re.sub(r'\((\w+)\)', r'\1', formula)
                    # Добавляем пробелы вокруг операторов
                    formula = formula.replace("+", " + ").replace("-", " - ")
                    return f"[ФОРМУЛА: {formula}]"
        except Exception as e:
            continue

    return ""


def process_element(element, doc):
    """Обрабатывает элемент документа и возвращает его текстовое представление"""
    text = ""

    # Обработка параграфов
    if element.tag.endswith('p'):
        paragraph = Paragraph(element, doc)
        text = paragraph.text.strip()

        # Проверяем наличие формул в параграфе
        formula_text = extract_formula(element)
        if formula_text:
            text += " " + formula_text

    # Обработка таблиц
    elif element.tag.endswith('tbl'):
        table = Table(element, doc)
        text = "\nТаблица:\n"
        col_widths = [0] * len(table.columns)
        for row in table.rows:
            for i, cell in enumerate(row.cells):
                if len(cell.text) > col_widths[i]:
                    col_widths[i] = len(cell.text)

        for row in table.rows:
            row_text = ""
            for i, cell in enumerate(row.cells):
                row_text += cell.text.ljust(col_widths[i] + 2)
            text += row_text + "\n"

    return text


def show_theory(param):
    filenameprefix = Sections.get_theoryfilename_prefix(param)
    if len(filenameprefix) <= 0:
        print("Теории нет")
        return
    filename = f"{filenameprefix}.docx"
    doc_path = files('mgp').joinpath(filename)
    doc = Document(doc_path)

    questions = []
    current_question = ""
    current_answer = ""

    for element in doc.element.body.xpath('*'):
        element_text = process_element(element, doc)

        if not element_text:
            continue

        if element_text[0].isdigit() and '.' in element_text.split()[0]:
            if current_question:
                questions.append((current_question, current_answer))
            current_question = element_text
            current_answer = ""
        else:
            current_answer += element_text + "\n"

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
                input("\nНажмите Enter чтобы продолжить...")
            elif choice == len(questions) + 1:
                break
            else:
                print("")
        except ValueError:
            print("")


def show_prac(param):
    filenameprefix = Sections.get_pracfilename_prefix(param)
    if len(filenameprefix) <= 0:
        print("Практики нет")
        return

    filename = f"{filenameprefix}.docx"
    doc_path = files('mgp').joinpath(filename)
    doc = Document(doc_path)

    questions = []
    current_question = ""
    current_answer = ""

    for element in doc.element.body.xpath('*'):
        element_text = process_element(element, doc)

        if not element_text:
            continue

        if element_text[0].isdigit() and '.' in element_text.split()[0]:
            if current_question:
                questions.append((current_question, current_answer))
            current_question = element_text
            current_answer = ""
        else:
            current_answer += element_text + "\n"

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
                input("\nНажмите Enter чтобы продолжить...")
            elif choice == len(questions) + 1:
                break
            else:
                print("")
        except ValueError:
            print("")


def show_submenu(param):
    # Если выбрана секция deepseek, запускаем файл deepseek.py и ждем завершения
    if param == Sections.DEEPSEEK.value:
        try:
            print("Запуск deepseek.py...")
            script_path = files('mgp').joinpath('deepseek.py')
            process = subprocess.Popen(["python", str(script_path)])
            process.wait()  # Ждем завершения процесса
            print("deepseek.py завершен.")
            return
        except FileNotFoundError:
            print("Файл deepseek.py не найден!")
            return

    # Для других секций показываем обычное меню
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
                show_prac(param)
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


# if __name__ == "__main__":
#     show()