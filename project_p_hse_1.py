from dataclasses import dataclass
import enum
import sys
import argparse
from datetime import datetime
import json
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow
from PyQt5.QtGui import QPixmap
from PyQt5 import uic, QtGui
from PyQt5 import QtCore, QtMultimedia

flag = 1


class Statuses(enum.Enum):
    new = 0
    in_progress = 1
    review = 2
    completed = 3
    cancelled = 4
    deleted = 5


@dataclass
class Task_manager:
    name: str
    Tasks = []
    Tasks_to_Json = {}
    Manager_story = []

    def add_to_task_list(self, task):
        self.Tasks.append(task)

        to_json = {'Task_name':                     task.name,
                   'Task_description':              task.description,
                   'Task_status':                   task.statuses[task.status],
                   'Task_date_of_creation':         task.date[0],
                   'Task_date_of_change_of_status': task.date[1]}
        self.Tasks_to_Json[task.name] = to_json

        with open('Tasks.json', 'w') as f:
            json.dump(self.Tasks_to_Json, f, indent=2)

    def remove_from_task_list(self, task):
        self.Tasks.remove(task)
        print(f"Task {task.name}:\n{str([str(i) for i in (self.Tasks_to_Json.pop(task.name)).values()])[1:-1]}\n has delated.\n")
        with open('Tasks.json', 'w') as f:
            json.dump(self.Tasks_to_Json, f, indent=2)

    def task_view(self, task):
        self.Manager_story.append([task.name, f"{datetime.now()}"[0:16]])
        #self.Manager_story = list(set(self.Manager_story))
        print(self.Manager_story)
        return f"Task request:{task}"[:-13]

    def manager_history(self):
        #print(self.Manager_story)
        enter = ''
        for i in self.Manager_story:
            enter += f"Task: {i[0]}    Date: {i[1]}\n"
        enter += "\n"
        return enter

    def task_status_changing(self, name, new_status):
        self.Tasks_to_Json[name]['Task_status'] = new_status
        with open('Tasks.json', 'w') as f:
            json.dump(self.Tasks_to_Json, f, indent=2)

    def __repr__(self):
        j = 0
        enter = []
        for i in self.Tasks:
            j += 1
            enter.append(f"Task{j}:\n{i}")
        return "\n".join(enter)


@dataclass
class Task(Task_manager):
    name: str
    description: str
    status: int
    date = [f"{datetime.now()}"[0:16], f"{datetime.now()}"[0:16]]
    statuses = ["new", "in_progress", "review", "completed", "cancelled", "deleted"]

    def next_status(self):
        global flag
        if self.status < 4:
            self.status += 1
            self.date[1] = f"{datetime.now()}"[0:16]
            print(f"Your Task: {self.name} status is {self.statuses[self.status]}.\n")
            Task_manager.task_status_changing(self.name, self.statuses[self.status])
            flag = 1
        else:
            print(f"Your Task: {self.name} is cancelled !\n")
            flag = 1

    def previous_status(self):
        global flag
        if self.status > 0:
            self.status -= 1
            self.date[1] = f"{datetime.now()}"[0:16]
            print(f"Your Task: {self.name} status is {self.statuses[self.status]}.\n")
            Task_manager.task_status_changing(self.name, self.statuses[self.status])
            flag = 1
        else:
            Task_manager.remove_from_task_list(self)
            flag = 0

    def __repr__(self):
        return f"\nTask_name:                                           {self.name}\n" \
               f"Task_description:                                  {self.description}\n" \
               f"Task_status:                                           {self.statuses[self.status]}\n" \
               f"Task_date_of_creation:                         {self.date[0]}\n" \
               f"Task_date_of_change_of_status:        {self.date[1]}\n" \
               f"_______________________________________________________________\n"


class JsonLoad:
    def __init__(self):
        self.count = 0
        try:
            with open('Tasks.json') as f:
                file = json.load(f)
            print(file)
            for i in file.keys():
                self.Task_name = file[i]["Task_name"]
                self.Task_description = file[i]["Task_description"]
                for g in ["new", "in_progress", "review", "completed", "cancelled", "deleted"]:
                    if g == file[i]["Task_status"]:
                        self.Task_status = self.count
                    self.count += 1
                self.count = 0
                # Task_date_of_creation = file[i][Task_date_of_creation]
                Task_manager.add_to_task_list(Task(self.Task_name, self.Task_description, self.Task_status))
        except:
            pass


class ADD_Task(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('Add Task.ui', self)
        self.pushButton.clicked.connect(self.MainMenue)
        self.get_name = ''
        self.get_description = ''
        self.get_status = 0

    def MainMenue(self):
        global ex
        self.get_name = self.lineEdit.text()
        self.get_description = self.lineEdit_2.text()
        self.get_status = self.comboBox.currentIndex()
        Task_manager.add_to_task_list(Task(self.get_name, self.get_description, self.get_status))
        ex = MyWidget()
        ex.show()
        pal = ex.palette()
        pal.setColor(QtGui.QPalette.Normal, QtGui.QPalette.Window, QtGui.QColor('orange'))
        ex.setPalette(pal)
        self.hide()


class CHANGE_Task(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('Task Update.ui', self)
        self.index = 0
        self.pushButton.clicked.connect(self.next_status)
        self.pushButton_2.clicked.connect(self.previous_status)
        self.pushButton_3.clicked.connect(self.remove)
        self.pushButton_4.clicked.connect(self.MainMenue)
        self.textBrowser.setText("\n\n\n\n\n\n\n                                CHOOSE TASK IN COMBOBOX")
        self.get_task_name = ''
        self.get_task = 0
        self.comboBox.insertItem(0, "choose")
        for task in Task_manager.Tasks:
            self.comboBox.insertItem(self.index + 1, task.name)
            self.index += 1
            self.comboBox.currentIndexChanged.connect(self.next_step)

    def next_step(self):
        self.get_task_name = self.comboBox.currentText()
        for i in Task_manager.Tasks:
            if i.name == self.get_task_name:
                self.get_task = i
                break
        self.textBrowser.setText(str(Task_manager.task_view(self.get_task)))

    def next_status(self):
        self.get_task.next_status()
        self.textBrowser.setText(str(Task_manager.task_view(self.get_task)))

    def previous_status(self):
        global flag
        if flag == 0:
            flag = 1
            CHANGE_Task.MainMenue(self)
        else:
            self.get_task.previous_status()
            self.textBrowser.setText(str(Task_manager.task_view(self.get_task)))

    def remove(self):
        Task_manager.remove_from_task_list(self.get_task)
        self.hide()
        self.exC = CHANGE_Task()
        self.exC.show()
        pal = self.exC.palette()
        pal.setColor(QtGui.QPalette.Normal, QtGui.QPalette.Window, QtGui.QColor('grey'))
        self.exC.setPalette(pal)

    def update(self):
        global ex
        ex = MyWidget()
        ex.show()
        pal1 = ex.palette()
        pal1.setColor(QtGui.QPalette.Normal, QtGui.QPalette.Window, QtGui.QColor('orange'))
        ex.setPalette(pal1)

    def MainMenue(self):
        global ex
        ex = MyWidget()
        ex.show()
        pal = ex.palette()
        pal.setColor(QtGui.QPalette.Normal, QtGui.QPalette.Window, QtGui.QColor('orange'))
        ex.setPalette(pal)
        self.hide()


class SERCH_History_Task(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('Search Hstory.ui', self)
        self.pushButton.clicked.connect(self.MainMenue)
        self.pushButton_2.clicked.connect(self.json)
        self.serch_result = Task_manager.manager_history()
        #self.serch_result
        print(self.serch_result)
        self.textBrowser.setText(str(Task_manager.manager_history())) #--------------------------------------------------------------------

    def json(self):
        self.hide()
        self.exC = Tasks_in_Json()
        self.exC.show()
        pal = self.exC.palette()
        pal.setColor(QtGui.QPalette.Normal, QtGui.QPalette.Window, QtGui.QColor('grey'))
        self.exC.setPalette(pal)

    def MainMenue(self):
        global ex
        ex = MyWidget()
        ex.show()
        pal = ex.palette()
        pal.setColor(QtGui.QPalette.Normal, QtGui.QPalette.Window, QtGui.QColor('orange'))
        ex.setPalette(pal)
        self.hide()


class Tasks_in_Json(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('Json_file.ui', self)
        self.pushButton.clicked.connect(self.MainMenue)
        with open('Tasks.json') as f:
            self.file = f.read()
            print(self.file)
        self.textBrowser.setText(str(self.file))

    def MainMenue(self):
        global ex
        ex = MyWidget()
        ex.show()
        pal = ex.palette()
        pal.setColor(QtGui.QPalette.Normal, QtGui.QPalette.Window, QtGui.QColor('orange'))
        ex.setPalette(pal)
        self.hide()


class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('Task Manager.ui', self)
        self.pushButton.clicked.connect(self.ADD_Task)
        self.pushButton_2.clicked.connect(self.CHANGE_Task)
        self.pushButton_3.clicked.connect(self.SERCH_History_Task)
        self.textBrowser.setText(str(Task_manager))

    def ADD_Task(self):
        self.exW = ADD_Task()
        self.exW.show()
        pal = self.exW.palette()
        pal.setColor(QtGui.QPalette.Normal, QtGui.QPalette.Window, QtGui.QColor('orange'))
        self.exW.setPalette(pal)

    def CHANGE_Task(self):
        self.exC = CHANGE_Task()
        self.exC.show()
        pal = self.exC.palette()
        pal.setColor(QtGui.QPalette.Normal, QtGui.QPalette.Window, QtGui.QColor('grey'))
        self.exC.setPalette(pal)

    def SERCH_History_Task(self):
        self.exS = SERCH_History_Task()
        self.exS.show()
        pal = self.exS.palette()
        pal.setColor(QtGui.QPalette.Normal, QtGui.QPalette.Window, QtGui.QColor('grey'))
        self.exS.setPalette(pal)


Task_manager = Task_manager("Manager_1")
JsonLoad()
#task0 = Task("EXAMPLE", "EXAMPLE", 4)
#Task_manager.add_to_task_list(task0)
#task1 = Task("TASK1", "make ore will make", 0)
#Task_manager.add_to_task_list(task1)
#task2 = Task("TASK2", "make ore will make", 0)
#Task_manager.add_to_task_list(task2)
#task3 = Task("TASK3", "BLA BLA BLA", 3)
#Task_manager.add_to_task_list(task3)
#Task_manager.remove_from_task_list(task0)

app = QApplication(sys.argv)
ex = MyWidget()
ex.show()
pal = ex.palette()
pal.setColor(QtGui.QPalette.Normal, QtGui.QPalette.Window, QtGui.QColor('orange'))
ex.setPalette(pal)
sys.exit(app.exec_())