from PyQt5.QtWidgets import (
    QApplication, QWidget, QGridLayout, QPushButton, QLabel, QLineEdit, QProgressBar, QComboBox, QSlider
    )
from PyQt5.QtCore import QTimer, Qt
import subprocess
import serial
import threading
import sys
import time
import datetime
class Window(QWidget):
    def __init__(self):
        super(Window, self).__init__()
        self.setMinimumSize(640, 480)
        self.setMaximumSize(640, 480)
        self.broseBtn = QPushButton('Brose', self)
        self.playBtn = QPushButton('Play', self)
        self.recordBtn = QPushButton('Record', self)
        self.saveBtn = QPushButton('Save', self)
        self.stopBtn = QPushButton('Stop', self)
        self.logLabel = QLabel('Log',self)
        self.timeLabel=QLabel('time',self)
        self.pathEditor=QLineEdit('',self)
        #self.progressBar=QProgressBar(self)
        #self.progressBar.setProperty("value", 100)
        self.comboBox=QComboBox(self)
        self.comboBox2=QComboBox(self)
        self.view1=QLabel('Input Port', self)
        self.view2=QLabel('Output Port', self)
        #self.comboBox.currentIndexChanged.connect(self.selectionChange)
        #self.timer=QTimer(self)
        #self.timer.timeout.connect(self.handleSendData)
        self.slider=QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setValue(0)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.valueChanged.connect(self.valuechange)

        self.broseBtn.clicked.connect(self.handlebroseBtn)
        self.playBtn.clicked.connect(self.handleplayBtn)
        self.recordBtn.clicked.connect(self.handlerecordBtn)
        self.saveBtn.clicked.connect(self.handlesaveBtn)
        self.stopBtn.clicked.connect(self.handlestopBtn)
        self.logList=['Welcome to this Qbe Robot Expression Editor ver.0.1.0\n','Have a nice Day !!\n',]
        self.fileCounter=0
        self.timeFlag=0
        self.timeMax=0
        self.setTime(self.timeFlag* 0.001)
        self.setLog()

        #prepareComboBox Item
        # use s.sh to get the com port
        try:
            ans = subprocess.check_output('./s.sh')
        except subprocess.CalledProcessError:
            self.logList.append('Warning!! there are no devices connected.\n')
            ans='NULL\n'
        mlist=ans.split('\n')
        mlist=mlist[:len(mlist)-1]
        for i in mlist:
            self.comboBox.addItem(i)
            self.comboBox2.addItem(i)


        layout = QGridLayout(self)
        layout.addWidget(self.broseBtn, 2, 4, 1, 1)
        layout.addWidget(self.playBtn, 3, 1, 1, 1)
        layout.addWidget(self.stopBtn, 3, 2, 1, 1)
        layout.addWidget(self.recordBtn, 3, 3, 1, 1)
        layout.addWidget(self.saveBtn, 3, 4, 1, 1)
        layout.addWidget(self.pathEditor, 2, 0, 1, 4)
        #layout.addWidget(self.progressBar, 4, 0, 1, 5)
        layout.addWidget(self.timeLabel, 3, 0, 1, 1)
        layout.addWidget(self.slider,5, 0, 1, 5)
        layout.addWidget(self.logLabel, 6, 0, 1, 5)
        layout.addWidget(self.comboBox, 0, 1, 1, 3)
        layout.addWidget(self.comboBox2,1, 1, 1, 3)
        layout.addWidget(self.view1,0, 0, 1, 1)
        layout.addWidget(self.view2,1, 0, 1, 1)
    def handlebroseBtn(self):
        self.logList.append('broseBtn Clicked!\n')
        self.setLog()
    def handleplayBtn(self):
        self.logList.append('playBtn Clicked!\n')
        self.setLog()
        SendDataHandle=threading.Thread(target=self.handleSendData, args=(self.comboBox2.currentText(),))
        self.Flag=True
        SendDataHandle.start()
        self.timeFlag=self.slider.value() * self.timeMax * 0.01
    def handlerecordBtn(self):
        self.logList.append('recordBtn Clicked!\n')
        self.setLog()

        SerialHandle=threading.Thread(target=self.handleSerial, args=(self.comboBox.currentText(),self.comboBox2.currentText(),))
        self.Flag=True
        SerialHandle.start()
    def handlesaveBtn(self):
        self.logList.append('saveBtn Clicked!\n')
        self.setLog()
    def handlestopBtn(self):
        self.logList.append('stopBtn Clicked!\n')
        self.setLog()
        self.Flag=False
        self.timeFlag=0
    def prepareComboBox(self):
        # use s.sh to get the com port
        ans = subprocess.check_output('./s.sh')
        mlist=ans.split('\n')
        mlist=mlist[:len(mlist)-1]
        for i in mlist:
            self.comboBox.addItem(i)
    def setLog(self):
        if len(self.logList) > 10 : 
            self.logList=self.logList[len(self.logList)-10: len(self.logList)]      
        s=''
        for e in self.logList:
            s+=''.join(str(e))
        self.logLabel.setText(s)

                
    def handleSerial(self, inPort, outPort):
        si = serial.Serial (port=inPort, baudrate=115200)
        so = serial.Serial (port=inPort, baudrate=115200)
        f = open('log.txt','w')
        t = time.time()
        while  self.Flag:
            data=si.readline()
            if not data: self.Flag=False
            so.write(data)
            self.timeMax=int((time.time()-t)*1000)
            data='@'+str(self.timeMax)+'@'+data
            self.logList.append(data)
            self.setLog()
            f.write(data)
            self.setTime(self.timeMax*0.001)
        f.close()
    def startCount(self):
        self.timer.start(50)    
    def handleSendData(self, devPort):
        f=open('log.txt','r+')
        fw=open('sendData.txt','w')
        si=serial.Serial(port=devPort, baudrate=115200)
        while self.Flag:
            data=f.readline()
            if not data: self.Flag=False
            s=data.split('@')
            if len(s) < 2: 
                continue
                self.Flag=False
            if int(s[1]) > int(self.timeFlag):
                self.logList.append(s[1]+'@@'+str(int(self.timeFlag))+'@@'+s[2])
                self.setLog()
                fw.write(s[2])
                si.write(s[2])
                time.sleep(0.05)
        #fw.seek(self.fileCounter)
        #data=f.readline()
        #fw.write(data)
        #self.fileCounter+=len(data)
        f.close()
        fw.close()
        #self.startCount()   
    def setTime(self, time):
        st = datetime.datetime.fromtimestamp(time).strftime('%M:%S')
        self.timeLabel.setText(st)
    def valuechange(self):
        self.timeFlag=self.timeMax * 0.01 *self.slider.value()
        self.setTime(self.timeFlag * 0.001)    

if __name__ == '__main__':

    import sys
    app = QApplication(sys.argv)
    window = Window()
    window.resize(800,600)
    window.show()
    sys.exit(app.exec_())