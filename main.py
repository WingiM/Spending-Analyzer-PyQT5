import sys
import sqlite3
import datetime
import re

from PyQt5 import uic
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QTableWidgetItem, QMessageBox


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


class WrongPin(Exception):
    pass


class WrongCVC(Exception):
    pass


class WrongValidDate(Exception):
    pass


class WrongNumber(Exception):
    pass


class WrongName(Exception):
    pass


class PinDoesNotMatch(Exception):
    pass


class LoadCard(QMainWindow):  # Класс, запускающий окно с загрузкой карты из базы данных
    def __init__(self):
        super(LoadCard, self).__init__()
        uic.loadUi('uis/card_load.ui', self)
        self.connect = sqlite3.connect('bank_cards_db.sqlite')
        self.card_n = 0
        self.pushButton.clicked.connect(self.find)
        self.loaded = False

    def find(self):  # Проверяет наличие карты с введеными данными в базе
        try:
            cur = self.connect.cursor()
            card_number, pin = self.card_number.text(), self.pin_code.text()
            if not card_number.isdigit() or len(card_number) != 16:
                self.label.setStyleSheet('color:red;')
                self.label_2.setStyleSheet('color:black;')
                raise WrongNumber
            if int(card_number) not in [x[0] for x in cur.execute("""SELECT number FROM Cards""")]:
                self.label.setStyleSheet('color:red;')
                self.label_2.setStyleSheet('color:black;')
                raise WrongNumber
            if len(pin) != 4 or not pin.isdigit():
                self.label.setStyleSheet('color:green;')
                self.label_2.setStyleSheet('color:red')
                raise WrongPin
            if int(pin) != cur.execute("""SELECT pin FROM Cards 
            WHERE number=?""", (card_number,)).fetchone()[0]:
                self.label.setStyleSheet('color:green;')
                self.label_2.setStyleSheet('color:red')
                raise PinDoesNotMatch
            self.label.setStyleSheet('color:green')
            self.label_2.setStyleSheet('color:green')
            self.card_n = int(card_number)
            form.active_card_id = cur.execute("""SELECT id FROM Cards 
                        WHERE number=?""", (self.card_n,)).fetchone()[0]
            form.card_loaded()
            self.statusBar().showMessage('Карта загружена')
        except WrongNumber:
            self.statusBar().showMessage('Неверный номер карты')
        except WrongPin:
            self.statusBar().showMessage('Неверный PIN-код')
        except PinDoesNotMatch:
            self.statusBar().showMessage('PIN-код не совпадает')

    def closeEvent(self, event):
        self.label.setStyleSheet('color:black;')
        self.label_2.setStyleSheet('color:black;')
        self.statusBar().showMessage('')
        self.card_number.clear()
        self.pin_code.clear()


class AddCard(QMainWindow):  # Класс, запускающий окно с добавлением карты в базу данных
    def __init__(self):
        super(AddCard, self).__init__()
        uic.loadUi('uis/card_add.ui', self)
        self.pushButton.clicked.connect(self.add_card)
        self.connect = sqlite3.connect('bank_cards_db.sqlite')

    def add_card(self):  # Добавляет новую карту в базу данных
        try:
            is_id = False
            card_number, name = self.card_number.text(), self.cardholder_name.text().split()
            valid, cvc, pin = self.valid.text().split('/'), self.cvc_code.text(), self.pin_code.text()
            if not card_number.isdigit() or len(card_number) != 16:
                self.label.setStyleSheet('color:red;')
                self.label_5.setStyleSheet('color:black;')
                self.label_4.setStyleSheet('color:black;')
                self.label_3.setStyleSheet('color:black;')
                self.label_2.setStyleSheet('color:black;')
                raise WrongNumber
            if not self.luhn_algorithm(card_number):
                self.label.setStyleSheet('color:red;')
                self.label_5.setStyleSheet('color:black;')
                self.label_4.setStyleSheet('color:black;')
                self.label_3.setStyleSheet('color:black;')
                self.label_2.setStyleSheet('color:black;')
                raise WrongNumber
            if '=' not in name:
                if len(name) != 2 or not name[0].isalpha() or not name[1].isalpha():
                    self.label.setStyleSheet('color:green;')
                    self.label_2.setStyleSheet('color:red;')
                    self.label_5.setStyleSheet('color:black;')
                    self.label_4.setStyleSheet('color:black;')
                    self.label_3.setStyleSheet('color:black;')
                    raise WrongName
                if re.search(r'[^A-Za-z]', ''.join(name)):
                    self.label.setStyleSheet('color:green;')
                    self.label_2.setStyleSheet('color:red;')
                    self.label_5.setStyleSheet('color:black;')
                    self.label_4.setStyleSheet('color:black;')
                    self.label_3.setStyleSheet('color:black;')
                    raise WrongName
            else:
                cardholder_id = int(name[2])
                is_id = True
            if len(valid) != 2 or not (valid[0].isdigit() and int(valid[0]) < 13 and len(valid[0]) == 2) \
                    or not (valid[1].isdigit() and len(valid[1]) == 2):
                self.label_3.setStyleSheet('color:red;')
                self.label_2.setStyleSheet('color:green;')
                self.label.setStyleSheet('color:green;')
                self.label_5.setStyleSheet('color:black;')
                self.label_4.setStyleSheet('color:black;')
                raise WrongValidDate
            if len(cvc) != 3 or not cvc.isdigit():
                self.label_4.setStyleSheet('color:red;')
                self.label_2.setStyleSheet('color:green;')
                self.label_3.setStyleSheet('color:green;')
                self.label.setStyleSheet('color:green;')
                self.label_5.setStyleSheet('color:black;')
                raise WrongCVC
            if len(pin) != 4 or not pin.isdigit():
                self.label_5.setStyleSheet('color:red;')
                self.label_4.setStyleSheet('color:green;')
                self.label_3.setStyleSheet('color:green;')
                self.label_2.setStyleSheet('color:green;')
                self.label.setStyleSheet('color:green;')
                raise WrongPin
            self.label_5.setStyleSheet('color:green;')
            self.label_4.setStyleSheet('color:green;')
            self.label_3.setStyleSheet('color:green;')
            self.label_2.setStyleSheet('color:green;')
            self.label.setStyleSheet('color:green;')
            valid = '/'.join(valid)
            cur = self.connect.cursor()
            d = QMessageBox.question(self, '', 'Добавить карту?', QMessageBox.Yes, QMessageBox.No)
            if d == QMessageBox.Yes:
                if not is_id:
                    cur.execute("""INSERT INTO Cardholders(name, surname) 
                    VALUES (?, ?)""", (name[0].upper(), name[1].upper()))
                    self.connect.commit()
                    cardholder_id = cur.execute(f"SELECT id FROM Cardholders "
                                                f"WHERE name = '{name[0].upper()}' "
                                                f"AND Surname = '{name[1].upper()}'").fetchall()[-1][0]
                cur.execute("""INSERT INTO Cards(number, valid, cvc, pin, cardholder_id) 
                Values (?, ?, ?, ?, ?)""", (int(card_number), str(valid), int(cvc), int(pin), int(cardholder_id)))
                self.connect.commit()
                req = f'SELECT id FROM Cards WHERE number={int(card_number)}'
                cur.execute(f"INSERT INTO Card_balances VALUES "
                            f"({cur.execute(req).fetchone()[0]}, {0})")
                self.statusBar().showMessage('Карта успешно добавлена!')
                self.connect.commit()
            else:
                self.close()
        except WrongNumber:
            self.statusBar().showMessage('Неверный номер карты')
        except WrongName:
            self.statusBar().showMessage('Неверное имя')
        except WrongValidDate:
            self.statusBar().showMessage('Неверная дата')
        except WrongCVC:
            self.statusBar().showMessage('Неверный CVC-код')
        except WrongPin:
            self.statusBar().showMessage('Неверный PIN-код')
        except sqlite3.IntegrityError:
            if not is_id:
                cur.execute("""DELETE FROM Cardholders WHERE id = ?""", (cardholder_id,))
                cur.execute("""UPDATE sqlite_sequence SET seq = seq - 1 WHERE name='Cardholders'""")
                self.connect.commit()
            self.label.setStyleSheet('color:red;')
            self.statusBar().showMessage('Такая карта уже есть в базе данных')

    @staticmethod
    def double(x):
        res = x * 2
        if res > 9:
            res = res - 9
        return res

    def luhn_algorithm(self, number):  # Проверяет подлинность номера введеной карты
        odd = map(lambda x: self.double(int(x)), number[::2])
        even = map(int, number[1::2])
        return (sum(odd) + sum(even)) % 10 == 0

    def closeEvent(self, event):
        self.card_number.clear()
        self.cardholder_name.clear()
        self.valid.clear()
        self.pin_code.clear()
        self.cvc_code.clear()
        self.label_5.setStyleSheet('color:black;')
        self.label_4.setStyleSheet('color:black;')
        self.label_3.setStyleSheet('color:black;')
        self.label_2.setStyleSheet('color:black;')
        self.label.setStyleSheet('color:black;')
        self.statusBar().showMessage('')


class About(QWidget):  # Окно "О программе"
    def __init__(self):
        super(About, self).__init__()
        uic.loadUi('uis/about.ui', self)


class SpendCredit(QMainWindow):  # Класс, запускающий окно, с которого можно добавить расходы
    def __init__(self):
        super(SpendCredit, self).__init__()
        uic.loadUi('uis/spendings.ui', self)
        self.connect = sqlite3.connect('bank_cards_db.sqlite')
        self.pushButton.clicked.connect(self.add_to_card)
        self.spends = [i.rstrip('\n') for i in open('spendings.txt', encoding='utf8').readlines()]
        self.comboBox.addItems(self.spends)
        self.credits = [i.rstrip('\n') for i in open('credits.txt', encoding='utf8').readlines()]
        self.added = False
        for i in self.radios.buttons():
            i.toggled.connect(self.reload)

    def reload(self):  # Меняет значение в comboBox, в зависимости от выбранной категории
        self.comboBox.clear()
        if self.sender().text() == 'Расход':
            self.comboBox.addItems(self.spends)
        else:
            self.comboBox.addItems(self.credits)

    def add_to_card(self):  # Добавляет расход в базу данных карты
        try:
            cur = self.connect.cursor()
            if self.spinBox.value() == 0:
                raise ValueError
            card_id = form.active_card_id
            value = self.spinBox.value()
            operation = self.comboBox.currentText()
            selected = 1 if self.spend.isChecked() else 0
            date = self.dateEdit.date()
            dat = datetime.datetime(date.year(), date.month(), date.day())
            dat = dat.strftime('%Y-%m-%d')
            if not selected:
                cur.execute("""INSERT INTO Card_operations(card_id, classification, value, date) 
                                VALUES (?, ?, ?, ?)""", (card_id, operation, value, dat))
                self.statusBar().showMessage('Успешное пополнение')
                cur.execute("""UPDATE Card_balances SET Balance=Balance + ? 
                WHERE card_id = ?""", (value, card_id))
                self.connect.commit()
                self.added = True
            elif cur.execute("""SELECT Balance FROM Card_balances 
            WHERE card_id = ?""", (card_id,)).fetchone()[0] >= value and selected:
                cur.execute("""INSERT INTO Card_operations(card_id, classification, value, date) 
                VALUES (?, ?, ?, ?)""", (card_id, operation, -value, dat))
                self.statusBar().showMessage('Операция выполнена')
                cur.execute("""UPDATE Card_balances SET Balance=Balance - ? 
                WHERE card_id = ?""", (value, card_id))
                self.connect.commit()
                self.added = True
            else:
                self.statusBar().showMessage('Недостаточно денег на счету')
        except ValueError:
            self.statusBar().showMessage('Сумма не может быть равна нулю')

    def closeEvent(self, event):
        self.spinBox.setValue(0)
        self.statusBar().showMessage('')
        if self.added:
            form.find_spendings()
            form.find_credits()
            form.load_full_table()


class SpendingReport(QMainWindow):  # Класс с основным окном
    def __init__(self):
        super().__init__()
        # self.setupUi(self)
        uic.loadUi('uis/proj.ui', self)
        self.setWindowTitle('Анализатор расходов')
        self.main_label.setText('\n''\n' + self.main_label.text())
        self.main_label.setStyleSheet("""text-decoration: overline, underline; font-size:64px;""")
        self.active_card_id = 0
        self.connect = sqlite3.connect('bank_cards_db.sqlite')
        self.about_window_action, self.add_card_action, = About(), AddCard()
        self.about_window_action.to_img.setPixmap(QPixmap('pyqt.png'))
        self.load_card_action, self.add_spending_action = LoadCard(), SpendCredit()
        self.about_window_action.setStyleSheet("""QPushButton { 
                                                border: 1px solid rgb(128, 128, 128);
                                                background-color: rgb(204, 204, 204);
                                                }""")
        self.add_card_action.setStyleSheet("""QPushButton { 
                                                border: 1px solid rgb(128, 128, 128);
                                                background-color: rgb(204, 204, 204);
                                                }""")
        self.load_card_action.setStyleSheet("""QPushButton { 
                                                border: 1px solid rgb(128, 128, 128);
                                                background-color: rgb(204, 204, 204);
                                                }""")
        self.add_spending_action.setStyleSheet("""QPushButton { 
                                                border: 1px solid rgb(128, 128, 128);
                                                background-color: rgb(204, 204, 204);
                                                }""")
        self.action_about_programm.triggered.connect(self.about)
        self.action_add_card.triggered.connect(self.add_card)
        self.action_load_card.triggered.connect(self.load_card)
        self.load_card_button.clicked.connect(self.load_card)
        self.add_card_button.clicked.connect(self.add_card)
        combo_items_spent = ['Все'] + [i.rstrip('\n')
                                       for i in open('spendings.txt', encoding='utf8').readlines()]
        combo_items_credit = ['Все'] + [i.rstrip('\n')
                                        for i in open('credits.txt', encoding='utf8').readlines()]
        self.comboBox_spent.addItems(combo_items_spent)
        self.comboBox_credit.addItems(combo_items_credit)
        self.add_new_spending_button.clicked.connect(self.spending)
        self.calculate_spent_button.clicked.connect(self.find_spendings)
        self.calculate_credit_button.clicked.connect(self.find_credits)
        self.add_new_credit_button.clicked.connect(self.spending)
        self.tableWidget_total.setColumnCount(4)
        self.tableWidget_total.setHorizontalHeaderLabels(['id операции', 'Категория', 'Сумма', 'Дата'])

    def about(self):  # Показывает окно "о программе"
        self.about_window_action.show()

    def add_card(self):  # Показывает окно добавления карты
        self.add_card_action.show()

    def load_card(self):  # Показывает окно загрузки карты
        self.load_card_action.show()

    def spending(self):  # Показывает окно добавления расходов/зачислений
        if self.active_card_id:
            if 'расход' in self.sender().text():
                self.add_spending_action.get.setEnabled(False)
                self.add_spending_action.spend.setEnabled(True)
                self.add_spending_action.spend.toggle()
            else:
                self.add_spending_action.spend.setEnabled(False)
                self.add_spending_action.get.setEnabled(True)
                self.add_spending_action.get.toggle()
            self.add_spending_action.show()

    def card_loaded(self):  # Метод, активирующийся сразу после корректной загрузки карты
        cur = self.connect.cursor()
        holder_id, name = cur.execute("""SELECT Cardholders.id, Name FROM Cardholders, Cards 
        WHERE cardholder_id = Cardholders.id AND Cards.id = ?""", (self.active_card_id,)).fetchone()
        self.greet_label.setText(f"Здравствуйте, {name}.\nВаш id пользователя - {holder_id}.\n"
                                 f"Используйте его при добавлении новых карт на ваше имя.")
        self.main_label.setText('Карта успешно подключена.')
        self.find_spendings()
        self.find_credits()
        self.load_full_table()

    def find_spendings(self):  # Обновляет список затрат
        self.listWidget_spent.clear()
        cur = self.connect.cursor()
        d1, d2 = self.dateEdit_spent1.date(), self.dateEdit_spent2.date()
        if self.comboBox_spent.currentText() == 'Все':
            if d1 >= d2:
                a = cur.execute("""SELECT SUM(value) FROM Card_operations 
                                WHERE value < 0 AND card_id=?""", (self.active_card_id,)).fetchone()[0]
                total_spent = abs(a if a else 0)
                for i in cur.execute("""SELECT classification, ABS(value), date 
                FROM Card_operations WHERE card_id=? AND value < 0 
                ORDER BY date""", (self.active_card_id,)).fetchall():
                    category, value, date = i
                    percent = f'{value / total_spent * 100:.2f}'
                    self.listWidget_spent.addItem(f'{category} - {value} рублей - {percent}% - {date}')
            else:
                dat1 = f'{d1.year()}-{d1.month():0>2}-{d1.day():0>2}'
                dat2 = f'{d2.year()}-{d2.month():0>2}-{d2.day():0>2}'
                a = cur.execute("""SELECT SUM(value) FROM Card_operations 
                                WHERE value < 0 AND card_id=? 
                                AND date BETWEEN ? 
                                AND ?""", (self.active_card_id, dat1, dat2)).fetchone()[0]
                total_spent = abs(a if a else 0)
                for i in cur.execute("""SELECT classification, ABS(value), date 
                FROM Card_operations WHERE card_id=? AND value < 0 AND date BETWEEN ? AND ?
                ORDER BY date""", (self.active_card_id, dat1, dat2)).fetchall():
                    category, value, date = i
                    percent = f'{value / total_spent * 100:.2f}'
                    self.listWidget_spent.addItem(f'{category} - {value} рублей - {percent}% - {date}')
        else:
            if d1 >= d2:
                a = cur.execute("""SELECT SUM(value) FROM Card_operations WHERE value < 0 
                AND classification=? 
                AND card_id=?""", (self.comboBox_spent.currentText(), self.active_card_id)).fetchone()[0]
                total_spent = abs(a if a else 0)
                for i in cur.execute("""SELECT ABS(value), date 
                FROM Card_operations WHERE card_id=? 
                AND value < 0 
                AND classification=? 
                ORDER BY date""", (self.active_card_id, self.comboBox_spent.currentText())).fetchall():
                    value, date = i
                    percent = f'{value / total_spent * 100:.2f}'
                    self.listWidget_spent.addItem(f'{value} рублей - {percent}% - {date}')
            else:
                dat1 = f'{d1.year()}-{d1.month():0>2}-{d1.day():0>2}'
                dat2 = f'{d2.year()}-{d2.month():0>2}-{d2.day():0>2}'
                a = cur.execute("""SELECT SUM(value) FROM Card_operations WHERE value < 0 
                AND classification=? AND card_id=? 
                AND date BETWEEN ? AND ?""",
                                (self.comboBox_spent.currentText(),
                                 self.active_card_id, dat1, dat2)).fetchone()[0]
                total_spent = abs(a if a else 0)
                for i in cur.execute("""SELECT ABS(value), date 
                FROM Card_Operations WHERE card_id=? 
                AND value < 0
                AND classification=? AND date 
                BETWEEN ? AND ? 
                ORDER BY 
                date""", (self.active_card_id, self.comboBox_spent.currentText(), dat1, dat2)).fetchall():
                    value, date = i
                    percent = f'{value / total_spent * 100:.2f}'
                    self.listWidget_spent.addItem(f'{value} рублей - {percent}% - {date}')
        self.listWidget_spent.addItem('')
        balance = cur.execute("""SELECT Balance FROM Card_balances 
        WHERE card_id=?""", (self.active_card_id,)).fetchone()[0]
        self.listWidget_spent.addItem(f'Всего денег было потрачено за этот период: {total_spent} рублей')
        self.listWidget_spent.addItem(f'Сейчас денег на счету: {balance} рублей')

    def find_credits(self):  # Обновляет список зачислений
        self.listWidget_credit.clear()
        cur = self.connect.cursor()
        d1, d2 = self.dateEdit_credit1.date(), self.dateEdit_credit2.date()
        if self.comboBox_credit.currentText() == 'Все':
            if d1 >= d2:
                a = cur.execute("""SELECT SUM(value) FROM Card_operations 
                                WHERE value > 0 AND card_id=?""", (self.active_card_id,)).fetchone()[0]
                total_credited = abs(a if a else 0)
                for i in cur.execute("""SELECT classification, ABS(value), date 
                FROM Card_operations WHERE card_id=? AND value > 0 
                ORDER BY date""", (self.active_card_id,)).fetchall():
                    category, value, date = i
                    self.listWidget_credit.addItem(f'{category} - {value} рублей - {date}')
            else:
                dat1 = f'{d1.year()}-{d1.month():0>2}-{d1.day():0>2}'
                dat2 = f'{d2.year()}-{d2.month():0>2}-{d2.day():0>2}'
                a = cur.execute("""SELECT SUM(value) FROM Card_operations 
                                WHERE value > 0 AND card_id=? 
                                AND date BETWEEN ? 
                                AND ?""", (self.active_card_id, dat1, dat2)).fetchone()[0]
                total_credited = abs(a if a else 0)
                for i in cur.execute("""SELECT classification, ABS(value), date 
                FROM Card_operations WHERE card_id=? AND value > 0 AND date BETWEEN ? AND ?
                ORDER BY date""", (self.active_card_id, dat1, dat2)).fetchall():
                    category, value, date = i
                    self.listWidget_credit.addItem(f'{category} - {value} рублей - {date}')
        else:
            if d1 >= d2:
                a = cur.execute("""SELECT SUM(value) FROM Card_operations WHERE value > 0 
                AND classification=? 
                AND card_id=?""", (self.comboBox_credit.currentText(), self.active_card_id)).fetchone()[0]
                total_credited = abs(a if a else 0)
                for i in cur.execute("""SELECT ABS(value), date 
                FROM Card_operations WHERE card_id=? 
                AND value > 0 
                AND classification=? 
                ORDER BY date""", (self.active_card_id, self.comboBox_credit.currentText())).fetchall():
                    value, date = i
                    self.listWidget_credit.addItem(f'{value} рублей - {date}')
            else:
                dat1 = f'{d1.year()}-{d1.month():0>2}-{d1.day():0>2}'
                dat2 = f'{d2.year()}-{d2.month():0>2}-{d2.day():0>2}'
                a = cur.execute("""SELECT SUM(value) FROM Card_operations WHERE value > 0 
                AND classification=? AND card_id=? 
                AND date BETWEEN ? AND ?""",
                                (self.comboBox_credit.currentText(),
                                 self.active_card_id, dat1, dat2)).fetchone()[0]
                total_credited = abs(a if a else 0)
                for i in cur.execute("""SELECT ABS(value), date 
                FROM Card_Operations WHERE card_id=? 
                AND value > 0
                AND classification=? AND date 
                BETWEEN ? AND ? 
                ORDER BY 
                date""", (self.active_card_id, self.comboBox_credit.currentText(), dat1, dat2)).fetchall():
                    value, date = i
                    self.listWidget_credit.addItem(f'{value} рублей - {date}')
        self.listWidget_credit.addItem('')
        balance = cur.execute("""SELECT Balance FROM Card_balances 
                WHERE card_id=?""", (self.active_card_id,)).fetchone()[0]
        self.listWidget_credit.addItem(f'Всего денег было начислено за этот период: {total_credited} рублей')
        self.listWidget_credit.addItem(f'Сейчас денег на счету: {balance} рублей')

    def load_full_table(self):  # Загружает таблицу на последней вкладке
        cur = self.connect.cursor()
        res = cur.execute("""SELECT operation_id, classification, value, date 
        FROM Card_operations WHERE card_id=?""", (self.active_card_id,)).fetchall()
        for i, info in enumerate(res):
            self.tableWidget_total.setRowCount(i + 1)
            for j, inf in enumerate(info):
                self.tableWidget_total.setItem(i, j, QTableWidgetItem(str(inf)))

    def closeEvent(self, event):
        self.about_window_action.close()
        self.add_spending_action.close()
        self.add_card_action.close()
        self.load_card_action.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = SpendingReport()
    form.setStyleSheet("""QPushButton { 
    border: 1px solid rgb(128, 128, 128);
    background-color: rgb(204, 204, 204);
    }
    QComboBox {
    border: 1px solid rgb(9, 19, 42);
    margin-top: 5px;
    }
    QTableWidget {
    border: 1px solid rgb(9, 19, 42);
    }
    QListWidget {
    border: 1px solid rgb(9, 19, 42);
    }
    QDateEdit {
    border: 1px solid rgb(9, 19, 42);
    }""")
    form.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
