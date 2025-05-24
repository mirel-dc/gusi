from docx import Document
from enum import Enum
from importlib.resources import files
from docx.table import Table
from docx.text.paragraph import Paragraph
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


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
    """Извлекает формулы с правильным отображением степеней и индексов"""
    namespaces = {
        'm2006': 'http://schemas.openxmlformats.org/officeDocument/2006/math',
        'm2010': 'http://schemas.microsoft.com/office/2007/8/2/math',
        'm2013': 'http://schemas.microsoft.com/office/2010/10/math'
    }

    formula_parts = []

    for ns_url in namespaces.values():
        try:
            # Ищем математические элементы
            math_elements = element.xpath(f'.//*[local-name()="oMath" and namespace-uri()="{ns_url}"]')

            for math in math_elements:
                # Собираем элементы формулы в правильном порядке
                stack = []
                current_text = ""

                for elem in math.iter():
                    tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag

                    if tag == "t":  # Текстовый элемент
                        if elem.text:
                            current_text += elem.text

                    elif tag == "sup":  # Верхний индекс
                        if current_text:
                            stack.append(current_text)
                            current_text = ""
                        stack.append("^")  # Добавляем символ степени перед индексом

                    elif tag == "sub":  # Нижний индекс
                        if current_text:
                            stack.append(current_text)
                            current_text = ""
                        stack.append("_")  # Добавляем символ индекса

                    elif tag in ["e", "r"]:  # Элементы выражения
                        if current_text:
                            stack.append(current_text)
                            current_text = ""

                if current_text:
                    stack.append(current_text)

                # Собираем формулу из стека
                formula = ""
                for i, item in enumerate(stack):
                    if item in ["^", "_"] and i < len(stack) - 1:
                        formula += f"{item}{stack[i + 1]}"
                        stack[i + 1] = ""  # Помечаем как обработанный
                    elif item and item not in ["^", "_"]:
                        formula += item

                if formula:
                    formula_parts.append(formula.strip())

                if formula_parts:
                    break

        except Exception as e:
            continue

    if formula_parts:
        # Улучшаем читаемость формулы
        formula = " ".join(formula_parts)
        formula = formula.replace("  ", " ").strip()
        # Добавляем пробелы вокруг операторов
        formula = formula.replace("*", " × ").replace("/", " / ")
        return f"[ФОРМУЛА: {formula}]"

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
    filename = f"{Sections.get_theoryfilename_prefix(param)}.docx"
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
    filename = f"{Sections.get_pracfilename_prefix(param)}.docx"
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

if __name__ == "__main__":
    show()