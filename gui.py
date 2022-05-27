from PyQt5 import QtCore
from PyQt5 import QtWidgets
import threading
from runner import Runner
import sys
import os


class Communicate(QtCore.QObject):

    """
    Communication between
    GUI and
    Runner component
    """

    done = QtCore.pyqtSignal()
    wait = QtCore.pyqtSignal()
    update_prog = QtCore.pyqtSignal(int)
    update_logs = QtCore.pyqtSignal(str)


class RunnerWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.file_path = None
        self.save_path = None
        self.runner = None

        self.communicate = Communicate()
        self.communicate.wait.connect(self.wait)
        self.communicate.done.connect(self.done)
        self.communicate.update_prog.connect(self.update_prog)
        self.communicate.update_logs.connect(self.update_logs)

        self.prog = QtWidgets.QProgressBar(self)
        self.logs = QtWidgets.QTextEdit(self)
        self.logs.setReadOnly(True)

        self.layout = QtWidgets.QGridLayout(self)
        self.layout.addWidget(self.prog)
        self.layout.addWidget(self.logs)

        self.init()

    def init(self):

        self.set_file_path()
        self.set_save_path()
        self.init_UI()

    def set_runner(self, config, dataset, model, logger):
        self.runner = Runner(
            ui=self.communicate,
            config=config, dataset=dataset, model=model, logger=logger
        )

        self.runner.start()

    def init_UI(self):

        self.prog.setValue(0)

        self.logs.append(
            "Selected file is '{file_path:}'"
            "\nExcel file is saved to '{save_path:}'".format(
                file_path=self.file_path,
                save_path=self.save_path
            )
        )

        self.setWindowTitle("OpenAI GPT-3")
        self.show()

    def set_save_path(self):

        pass
        # get file extension
        # check_extension = self.file_path.split(".")

        #  extension = \
        #   check_extension[-1] if isinstance(check_extension, list) else None

        #   if extension in ["db", "sqlite", "sqlite3", "db3"]:

        #   idx = len(extension)
        #   self.save_path = "{}xlsx".format(self.file_path[:-idx])

        #   else:

        # self.save_path = "{}.xlsx".format(self.file_path)

    def set_file_path(self):

        # directory = os.getenv("HOME")

        file_path = QtWidgets.QFileDialog.getOpenFileName(
            self,
            'Open file',
            './data',
            "File containing questions  (*.txt *.json)"
        )[0]

        if file_path:
            self.file_path = file_path

        else:
            self.show_error()

    def done(self):

        self.prog.setValue(100)
        self.logs.append("Done!")

    def wait(self):

        pass
        # self.logs.append("Saving excel file, please wait...")

    def update_prog(self, x):

        self.prog.setValue(x)

    def update_logs(self, txt):

        self.logs.append(txt)

    def closeEvent(self, event):

        self.runner.stop()
        # self.conv.stop()
        super().closeEvent(event)

    @staticmethod
    def show_error():

        msgbox = QtWidgets.QMessageBox()
        msgbox.setIcon(QtWidgets.QMessageBox.Critical)
        msgbox.setWindowTitle("Error")
        msgbox.setText("Selecting a file is required to proceed.")
        close = msgbox.addButton("Close", QtWidgets.QMessageBox.ActionRole)

        msgbox.exec_()

        if msgbox.clickedButton() == close:
            sys.exit()
