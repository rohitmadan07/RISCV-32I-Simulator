import os
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from include import *
import main
from io import StringIO


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.fontSize = 10  # Default font size
        self.initUI()


    def initUI(self):
        # Create central widget and layout
        centralWidget = QWidget(self)
        self.setCentralWidget(centralWidget)
        hLayout = QHBoxLayout(centralWidget)

        # Add file upload option to the left side
        vLayoutLeft = QVBoxLayout()
        vLayoutLeft.setSpacing(10)
        fileHeading = QLabel("Uploaded file:")
        fileHeading.setMinimumHeight(30)  # set minimum height to 30 pixels
        vLayoutLeft.addWidget(fileHeading)
        self.fileLabel = QLabel("No file selected")
        self.fileLabel.setMinimumHeight(30)  # set minimum height to 30 pixels
        vLayoutLeft.addWidget(self.fileLabel)
        vLayoutLeft.addStretch()

        # Add upload button to the left side
        uploadButton = QPushButton("Upload File", self)
        uploadButton.setStyleSheet("QPushButton{background-color: #FFCCCB; text-align: center}")
        uploadButton.setFixedSize(150, 60)
        uploadButton.clicked.connect(self.upload_file)
        vLayoutLeft.addWidget(uploadButton, alignment = Qt.AlignHCenter) # add the alignment here

        # Add assemble button to the left side
        assembleButton = QPushButton("Assemble", self)
        assembleButton.setStyleSheet("QPushButton{background-color: #ADD8E6; text-align: center}")
        assembleButton.setFixedSize(150, 60)
        assembleButton.clicked.connect(self.assemble_code)
        vLayoutLeft.addWidget(assembleButton, alignment = Qt.AlignHCenter)

        # Add run button to the left side
        runButton = QPushButton("Run", self)
        runButton.setStyleSheet("QPushButton{background-color: #90EE90; text-align: center}")
        runButton.setFixedSize(150, 60)
        runButton.clicked.connect(self.run_main)
        vLayoutLeft.addWidget(runButton, alignment = Qt.AlignHCenter)

        vLayoutLeft.addStretch()  # add stretch to push widgets upwards

        # Add knob to switch between different modes
        mode1Label = QLabel("Select mode:")
        vLayoutLeft.addWidget(mode1Label)
        self.mode1Knob = QCheckBox("Knob 1 (Enable Pipelining or not)", self)
        self.mode1Knob.setChecked(False)
        vLayoutLeft.addWidget(self.mode1Knob)

        self.mode2Knob = QCheckBox("Knob 2 (Enable Data Forwarding or not)", self)
        self.mode2Knob.setChecked(False)
        vLayoutLeft.addWidget(self.mode2Knob)

        self.mode3Knob = QCheckBox("Knob 3 (Enable printing values in reg file or not)", self)
        self.mode3Knob.setChecked(False)
        vLayoutLeft.addWidget(self.mode3Knob)

        self.mode4Knob = QCheckBox("Knob 4 (Enable printing info in pipeline registers or not)", self)
        self.mode4Knob.setChecked(False)
        vLayoutLeft.addWidget(self.mode4Knob)

        self.mode5Knob = QCheckBox("Knob 5 (Like Knob 4, enter instruction number)", self)
        self.mode5Knob.setChecked(False)
        vLayoutLeft.addWidget(self.mode5Knob)

        self.mode5ValueLabel = QLabel("Enter instruction number:")
        self.mode5ValueLabel.hide()
        vLayoutLeft.addWidget(self.mode5ValueLabel)

        self.mode5ValueInput = QSpinBox(self)
        self.mode5ValueInput.setMinimum(0)
        self.mode5ValueInput.setMaximum(1000000)
        self.mode5ValueInput.setValue(0)
        self.mode5ValueInput.hide()
        vLayoutLeft.addWidget(self.mode5ValueInput)

        self.mode5Knob.stateChanged.connect(self.mode5_value_input)

        vLayoutLeft.addStretch()  # add stretch to push widgets upwards

        hLayout.addLayout(vLayoutLeft)

        # Add console windows to the right side
        vLayoutRight = QVBoxLayout()

        # Add machine code console 
        consoleLayout3 = QHBoxLayout()
        self.console4 = QTextEdit(self)
        self.console4.setReadOnly(True)
        consoleLayout3.addWidget(self.console4)

        # Add output stats console
        self.console5 = QTextEdit(self)
        self.console5.setReadOnly(True)
        consoleLayout3.addWidget(self.console5)
        vLayoutRight.addLayout(consoleLayout3)

        # Add register values console
        consoleLayout = QHBoxLayout()
        self.console1 = QTextEdit(self)
        self.console1.setReadOnly(True)
        consoleLayout.addWidget(self.console1)

        # Add memory console
        self.console2 = QTextEdit(self)
        self.console2.setReadOnly(True)
        consoleLayout.addWidget(self.console2)
        vLayoutRight.addLayout(consoleLayout)

        # Add output console
        consoleLayout2 = QHBoxLayout()
        self.console3 = QTextEdit(self)
        self.console3.setReadOnly(True)
        consoleLayout2.addWidget(self.console3)
        vLayoutRight.addLayout(consoleLayout2)

        hLayout.addLayout(vLayoutRight)

        self.setGeometry(500, 500, 800, 500)
        self.setWindowTitle('RISC-V Simulator')

        # Add font size option to toolbar
        fontSizeAction = QAction('Font Size', self)
        fontSizeAction.triggered.connect(self.set_font_size)
        self.toolbar = self.addToolBar('Font Size')
        self.toolbar.addAction(fontSizeAction)

        # Set font size of console widgets
        self.console1.setFontPointSize(self.fontSize)
        self.console2.setFontPointSize(self.fontSize)
        self.console3.setFontPointSize(self.fontSize)
        self.console4.setFontPointSize(self.fontSize)
        self.console5.setFontPointSize(self.fontSize)

        text1 = "<b style='font-size: 12pt'>Register:</b> <br>"
        self.console1.setText(text1)
        txt1 = ""
        for i in range(0, len(mem.RegisterFile)):
            txt1 += "X" + str(i) + ": "+ str(mem.RegisterFile[i]) + "\n"
        self.console1.append(txt1)


        text2 = "<b style='font-size: 12pt'>Memory:</b> <br>"
        self.console2.setText(text2)
        self.console2.append("<b style='font-size: 10pt'>Address : Data </b>")


        text3 = "<b style='font-size: 12pt'>Output Stats:</b> <br>"
        self.console5.setText(text3)

        text4 = "<b style='font-size: 12pt'>RISC-V Machine Code:</b> <br>"
        self.console4.setText(text4)

        text5 = "<b style='font-size: 12pt'>Details of each Cycle:</b> <br>"
        self.console3.setText(text5)


    def upload_file(self):
        # Disable the button to prevent multiple clicks
        uploadButton = self.sender()
        uploadButton.setEnabled(False)

        self.fileName, _ = QFileDialog.getOpenFileName(self, "Upload File", "", "All Files (*);;Text Files (*.txt)")
        self.console1.append(str(os.path.basename(self.fileName)))
        if self.fileName:
            self.fileLabel.setText(str(os.path.basename(self.fileName)))   


    def assemble_code(self):
        # Disable the button to prevent multiple clicks
        assembleButton = self.sender()
        assembleButton.setEnabled(False)

        text4 = ""
        with open(self.fileName, 'r+') as m:
            lines = m.readlines()
            for line in lines:
                text4 += line

        self.console2.clear()
        self.console4.append(text4)
        self.console4.moveCursor(QTextCursor.Start)

        mem.load_program_memory(self.fileName)
        text6 = ""
        for i in mem.data_memory:
            #text6 += "{}:  {} <br>".format(hex(i), mem.data_memory[i])
            text6 += "<span style='font-size: 16px;'>{}:</span>  <span style='font-size: 16px;'>{}</span> <br>".format(hex(i), mem.data_memory[i])

        self.console2.clear()
        text2 = "<b style='font-size: 12pt'>Memory:</b> <br>"
        self.console2.setText(text2)
        self.console2.append("<b style='font-size: 10pt'>Address : Data </b>")
        self.console2.append(text6)
        self.console2.moveCursor(QTextCursor.Start)
        

    def set_font_size(self):
        size, ok = QInputDialog.getInt(self, 'Font Size', 'Enter font size:', self.fontSize)
        if ok:
            self.fontSize = size
            self.console1.setFontPointSize(self.fontSize)
            self.console2.setFontPointSize(self.fontSize)
            self.console3.setFontPointSize(self.fontSize)
            self.console4.setFontPointSize(self.fontSize)
            self.console5.setFontPointSize(self.fontSize)


    def mode5_value_input(self):
        if self.mode5Knob.isChecked():
            self.mode5ValueLabel.show()
            self.mode5ValueInput.show()
        else:
            self.mode5ValueLabel.hide()
            self.mode5ValueInput.hide()


    def run_main(self):
        # Disable the button to prevent multiple clicks
        runButton = self.sender()
        runButton.setEnabled(False)

        if self.mode1Knob.isChecked():
            knob.turnOnKnob(1)

        if self.mode2Knob.isChecked():
            knob.turnOnKnob(2)
            knob.turnOnKnob(1)

        if self.mode3Knob.isChecked():
            knob.turnOnKnob(3)

        if self.mode4Knob.isChecked():
            knob.turnOnKnob(4)

        if self.mode5Knob.isChecked():
            knob.turnOnKnob(5)

        print("knob 1 value: ", knob.knob1)

        knob.instrNoInp = self.mode5ValueInput.value()


        # redirect standard output to a StringIO object
        string_io = StringIO()
        sys.stdout = string_io

        # call the main2_function
        main.run_main()

        # get the output from the StringIO object
        output = string_io.getvalue()

        # restore standard output
        sys.stdout = sys.__stdout__

        # display output in console3
        self.console3.append(output)
        self.console3.moveCursor(QTextCursor.Start)


        text2 = "<b style='font-size: 12pt'>Memory:</b> <br>"
        self.console2.setText(text2)
        self.console2.append("<b style='font-size: 10pt'>Address : Data </b>")
        
        self.console2.setFontWeight(QFont.Normal)  # Set font weight to normal
        self.console2.setFontPointSize(self.fontSize)
        with open('data_mem.mc', 'r+') as p:
            lines = p.readlines()
            text = ''.join(lines)
            self.console2.append(text)
            self.console2.moveCursor(QTextCursor.Start)


        text1 = "<b style='font-size: 12pt'>Register:</b> <br>"
        self.console1.setText(text1)
        

        with open('register_values.mc', 'r+') as f:
            lines = f.readlines()
            text = ''.join(lines)
            self.console1.append(text)
            self.console1.moveCursor(QTextCursor.Start)

        if(knob.knob1==1):
            with open('OutputStats.txt', 'r+') as o:
                lines = o.readlines()
                text = ''.join(lines)
                self.console5.append(text)
                self.console5.moveCursor(QTextCursor.Start)
        



if __name__ == '__main__':

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())