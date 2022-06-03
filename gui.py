from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
import threading
from runner import Runner
import sys
import os

colors = {
    'red': (179, 69, 63),
    'blue': (63, 119, 179),
    'green': (68, 185, 100),
    'black': (0, 0, 0)
}


class Communicate(QtCore.QObject):

    """
    Communication between
    GUI and
    Runner component
    """

    done = QtCore.pyqtSignal()
    wait = QtCore.pyqtSignal()
    update_prog = QtCore.pyqtSignal(int)
    update_logs = QtCore.pyqtSignal(str, str)


class RunnerWindow(QtWidgets.QWidget):
    def __init__(self, runner, communicate):
        super().__init__()

        self.file_path = None
        self.save_path = None
        self.runner = None

        self.communicate = communicate
        self.communicate.wait.connect(self.wait)
        self.communicate.done.connect(self.done)
        self.communicate.update_prog.connect(self.update_prog)
        self.communicate.update_logs.connect(self.update_logs)

        self.stop_button = QtWidgets.QPushButton(self)
        self.stop_button.clicked.connect(self.stop)
        self.stop_button.setText('Stop')
        self.stop_button.setEnabled(False)

        self.start_button = QtWidgets.QPushButton(self)
        self.start_button.clicked.connect(self.start)
        self.start_button.setText('Start')

        self.prog = QtWidgets.QProgressBar(self)
        self.logs = QtWidgets.QTextEdit(self)
        self.logs.setReadOnly(True)

        self.parameters = QtWidgets.QTextEdit(self)
        self.parameters.setReadOnly(True)

        self.layout = QtWidgets.QGridLayout(self)
        self.layout.addWidget(self.prog)
        self.layout.addWidget(self.parameters)
        self.layout.addWidget(self.logs)
        self.layout.addWidget(self.start_button)
        self.layout.addWidget(self.stop_button)

        self.runner = runner

        self.init_UI()

    def init_UI(self):

        self.prog.setValue(0)

        self.parameters.append(
            "Selected dataset is <b>'{file_path:}'</b>"
            "<br> Results are saved to <b>'{save_path:}'</b> <br>"
            "<br> Estimated cost: <b>${estimated_cost:}</b> <br>".format(
                file_path=self.runner.config['data_path'],
                save_path=self.runner.save_path,
                estimated_cost=self.runner.estimated_cost
            )
        )

        self.parameters.setFixedHeight(
            self.parameters.document().size().height()*5)

        self.setWindowTitle("OpenAI GPT-3")
        self.show()

    def set_save_path(self):
        # TODO

        pass

    def set_file_path(self):

        pass
        # TODO
        # directory = os.getenv("HOME")

#        file_path = QtWidgets.QFileDialog.getOpenFileName(
#            self,
#            'Open file',
#            './data',
#            "File containing questions  (*.txt *.json)"
#        )[0]
#
#        if file_path:
#            self.file_path = file_path
#
#        else:
#            self.show_error()
#
    def done(self):

        self.prog.setValue(100)
        self.update_logs("Done!", 'green')
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(False)

    def stop(self):
        self.runner.stop()
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        # self.update_logs('\n STOP', (179, 69, 63))

    def start(self):
        self.runner.start()
        self.update_prog(0)
        self.stop_button.setEnabled(True)

    def wait(self):

        pass
        # self.logs.append("Saving excel file, please wait...")

    def update_prog(self, x):
        self.prog.setValue(x)

    def update_logs(self, txt, color):

        self.logs.setTextColor(QtGui.QColor(*colors[color]))
        self.logs.append(txt+'\n')

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
