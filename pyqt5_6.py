import sys
import cv2
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QPalette, QBrush, QPixmap
from PyQt5.QtWidgets import QApplication,QWidget,QVBoxLayout,QListView,QMessageBox
from PyQt5.QtCore import QStringListModel
from PyQt5.QtCore import QThread, pyqtSignal
import os
import time
import threading
import serial 
import RPi.GPIO as GPIO
from getkey import getkey, keys
import matplotlib.pyplot as plt
import numpy as np
from openpyxl import Workbook
from adafruit_rplidar import RPLidar
import matplotlib.pyplot as plt
import re
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PIL.ImageQt import ImageQt


class MyWidget(QWidget,object):
    
    def __init__(self):
        super().__init__()

        self.initUI()
        self.timer_camera = QtCore.QTimer()
        self.cap = cv2.VideoCapture()        
        self.CAM_NUM = 0
       # self.set_ui()
        self.slot_init()        
        self.__flag_work = 0
        self.x = 0
        self.count = 0
        self.a = []    #儲存感測器數據地方            
        
    def initUI(self):
               
        self.setWindowTitle('my window')
        self.setGeometry(50, 50, 1600, 1100)
        #self.setStyleSheet('''QWidget{background-color:rgb(255, 255, 255);}''')
        
        self.button1 = QPushButton(u'遙控模式', self)
        self.button1.move(60, 50)
        self.button1.clicked.connect(self.Button1Click_thread)
        self.button1.setGeometry(60, 50, 150, 60)
        self.button1.setStyleSheet('''QPushButton{background:#F7D674;border-radius:5px;}QPushButton:hover{background:yellow;}''')
        self.button1.setCheckable(True)
        #self.button1.toggle()
        
        self.button2 = QPushButton('自動避障', self)
        self.button2.move(60, 150)
        self.button2.clicked.connect(self.Button2Click_thread)
        self.button2.setGeometry(60, 150, 150, 60)
        self.button2.setStyleSheet('''QPushButton{background:#F7D674;border-radius:5px;}QPushButton:hover{background:yellow;}''')
        self.button2.setCheckable(True)
        #self.button2.toggle()
        
        self.button3 = QPushButton('停止', self)
        self.button3.move(60, 250)  
        self.button3.clicked.connect(self.Button3Click)
        self.button3.setGeometry(60, 250, 150, 60)
        self.button3.setStyleSheet('''QPushButton{background:#F7D674;border-radius:5px;}QPushButton:hover{background:yellow;}''')
        
        """
        self.button5 = QPushButton('拍照', self)
        self.button5.move(650, 150)   
        self.button5.clicked.connect(self.Button5Click)
        self.button5.setGeometry(650, 150, 150, 60)
        self.button5.setStyleSheet('''QPushButton{background:#F7D674;border-radius:5px;}QPushButton:hover{background:yellow;}''')
        """
        
        self.button6 = QPushButton(u'開始量測', self)
        self.button6.move(650, 550)
        self.button6.clicked.connect(self.gas_sensor_thread)
        self.button6.setGeometry(650, 550, 150, 60)
        self.button6.setStyleSheet('''QPushButton{background:#F7D674;border-radius:5px;}QPushButton:hover{background:yellow;}''')
        self.button6.setCheckable(True)
        
        """
        self.button7 = QPushButton(u'匯出Ecxel', self)
        self.button7.move(650, 650)
        self.button7.clicked.connect(self.export_thread)
        self.button7.setGeometry(650, 650, 150, 60)
        self.button7.setStyleSheet('''QPushButton{background:#F7D674;border-radius:5px;}QPushButton:hover{background:yellow;}''')
        """
        
        self.listwidget = QtWidgets.QListWidget(self)
        self.listwidget.setGeometry(300,50,250,500)
        self.listwidget.addItems([])  
        
                                
        self.label_show_camera = QLabel(self)        
        self.label_show_camera.setGeometry(900,50,641,450)
        #self.label_show_camera .setStyleSheet('background-color: rgb(128, 128, 128)')
        self.cameraBox = QtWidgets.QGroupBox(self)
        self.cameraBox.setGeometry(QtCore.QRect(890, 40, 661, 470))
        self.cameraBox.setObjectName("groupBox")
        
        
        
        self.label_show_image = QLabel(self)        
        self.label_show_image.setGeometry(900,560,640,450)
        #self.label_show_image .setStyleSheet('background-color: rgb(255, 0, 0)')
        
        self.groupBox = QtWidgets.QGroupBox(self)
        self.groupBox.setGeometry(QtCore.QRect(890, 550, 661, 470))
        self.groupBox.setObjectName("groupBox")
        
        
        
        
    def slot_init(self):
        
        self.button4 = QPushButton('開啟相機', self)
        self.button4.move(650, 50)
        self.button4.clicked.connect(self.Button4Click)
        self.button4.setGeometry(650, 50, 150, 60)
        self.button4.setStyleSheet('''QPushButton{background:#F7D674;border-radius:5px;}QPushButton:hover{background:yellow;}''')                
        self.timer_camera.timeout.connect(self.show_camera)
    
    def Button1Click_thread(self):
        thread_remote = threading.Thread(target=self.Button1Click)
        thread_remote.start()
        
    
    def Button2Click_thread(self):
        thread_aviod = threading.Thread(target=self.Button2Click)
        thread_aviod.start()
          
    """
    def export_thread(self):
        thread_export = threading.Thread(target=self.export)
        thread_export.start()
    """    
    
    def gas_sensor_thread(self):    
        thread_gas = threading.Thread(target=self.gas_sensor)
        thread_gas.start() 
    
    
    def Button1Click(self):
        GPIO.setmode(GPIO.BCM)
        if self.button1.isChecked():
            print("open")
            time.sleep(2)
            self.button1.setText('關閉遙控') 
            self.listwidget.addItem('開啟遙控...')
            
            #GPIO.setmode(GPIO.BCM)
            
            GPIO.setwarnings(False)
            
            motor = Motor(13, 19, 16, 20, 21, 26)
            motor_speed = 100
            
            while True:
                motor.speed(motor_speed)
                key = getkey()
                if key == keys.UP:
                    print('forward')
                    motor.forward()
                elif key == keys.DOWN:
                    print('backward')
                    motor.backward()
                elif key == keys.LEFT:
                    print('turn left')
                    motor.turn_left()
                elif key == keys.RIGHT:
                    print('turn right')
                    motor.turn_right()
                elif key == 'l':
                    motor_speed -= 10
                    if motor_speed <= 30:
                        motor_speed = 30
                elif key == 'h':
                    motor_speed += 10
                    if motor_speed >= 100:
                        motor_speed = 100
                elif key == 's':
                    motor.stop()
                elif key == keys.ESCAPE:
                    self.button1.setText('遙控模式')
                    self.listwidget.addItem('退出遙控模式')
                    motor.stop()
                    break
                
        else:
            time.sleep(2)
            print('close')
            self.button1.setText('遙控模式')
            self.listwidget.addItem('退出遙控模式')
            GPIO.cleanup()
            
            
    def Button2Click(self):
        
        PORT_NAME = '/dev/ttyUSB0'
        lidar = RPLidar(None, PORT_NAME, timeout=3)
        
        GPIO.setmode(GPIO.BCM)
        
        a_angle = np.array([])
        b_angle = np.array([])
        c_angle = np.array([])
        d_angle = np.array([])
        e_angle = np.array([])
        f_angle = np.array([])
        g_angle = np.array([])
        h_angle = np.array([])
        
        
        if self.button2.isChecked():
            time.sleep(2)
            self.button2.setText('關閉避障') 
            self.listwidget.addItem('開啟避障...')
            GPIO.setwarnings(False)
            motor = Motor(13, 19, 16, 20, 21, 26)
            motor_speed = 100
            
                                    
            while True:
            #print(lidar.get_info())
                for i in lidar.iter_scans():
                    for (_, angle, distance) in i:
                        #print(angle,distance)
                        
                        if 170 <= angle <= 190:
                            a_angle = distance
                            if a_angle >= 600:
                                motor.forward()
                                print("motor.forward")
                                
                        if 215 <= angle <= 235:
                            b_angle = distance
                        
                        
                        if 260 <= angle <= 280:
                            c_angle = distance
                            
                                
                            
                        if 305 <= angle <= 325:
                            d_angle = distance
                        
                        if 350 <= angle <= 10:
                            
                            e_angle = distance
                            
                        if 35 <= angle <= 55:
                             
                            f_angle = distance   
                            
                        if 80 <= angle <= 100:
                            g_angle = distance   
                            if a_angle <= 600 and g_angle >= 400 and c_angle >= 400 :
                                motor.turn_right()
                                print("motor.turn_left_1")
                            
                            if a_angle <= 600 and g_angle <= 400 and c_angle >= 400 :
                                motor.turn_right()
                                print("motor.turn_right")
                            if a_angle <= 600 and c_angle <= 400 and g_angle <= 400:
                                motor.stop()
                                print("motor.stop")
                            
                            if a_angle <= 600 and c_angle <= 400 and g_angle >= 400:
                                motor.turn_left()
                                print("motor.turn_left")
                             
                        if 125 <= angle <= 145:
                            h_angle = distance    
                        
                        
                        
            
        else:
            
            self.button2.setText('自動避障')
            self.listwidget.addItem('退出自動避障')
            GPIO.cleanup()
            print('666')
            """
            motor.stop()
            lidar.stop()
            lidar.disconnect()
                 
            """
    def Button3Click(self):    
        self.listwidget.addItem('停止...')
        
        
    def Button4Click(self):                                                 
        if self.timer_camera.isActive() == False:
            flag = self.cap.open(self.CAM_NUM)
            if flag == False:
                msg = QtWidgets.QMessageBox.warning(self, u"Warning", u"請檢查電腦是否與相機正確連接",
                                                    buttons=QtWidgets.QMessageBox.Ok,
                                                    defaultButton=QtWidgets.QMessageBox.Ok)
            
            else:
                self.listwidget.addItem('開啟相機...')
                self.timer_camera.start(20)
                
                self.button4.setText(u'關閉相機')
        else:
            self.timer_camera.stop()
            self.cap.release()
            self.label_show_camera.clear()
            self.listwidget.addItem('關閉相機...')
            self.button4.setText(u'打開相機')
        
    """                  
    def Button5Click(self): 
        self.listwidget.addItem('拍照...')
    """ 
    
    
        
    
    
    def show_camera(self):       
        flag, self.image = self.cap.read()
        
        show = cv2.resize(self.image, (640,480 ))
        show = cv2.cvtColor(show, cv2.COLOR_BGR2RGB)
        
        self.showImage = QtGui.QImage(show.data, show.shape[1], show.shape[0], QtGui.QImage.Format_RGB888)
        self.label_show_camera.setPixmap(QtGui.QPixmap.fromImage(self.showImage))
      
     
    def closeEvent(self, event):
        ok = QtWidgets.QPushButton()
        cacel = QtWidgets.QPushButton()

        msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, u"關閉", u"是否關閉！")

        msg.addButton(ok, QtWidgets.QMessageBox.ActionRole)
        msg.addButton(cacel, QtWidgets.QMessageBox.RejectRole)
        ok.setText(u'確定')
        cacel.setText(u'取消')
        # msg.setDetailedText('sdfsdff')
        if msg.exec_() == QtWidgets.QMessageBox.RejectRole:
            event.ignore()
        else:
            
            if self.cap.isOpened():
                self.cap.release()
            if self.timer_camera.isActive():
                self.timer_camera.stop()
                self.ser.close()
            event.accept()    
            

    

    def gas_sensor(self):
        COM_PORT = '/dev/ttyUSB1'    # 指定通訊埠名稱
        BAUD_RATES = 9600    # 設定傳輸速率
        serialport = serial.Serial(COM_PORT, BAUD_RATES)   # 初始化序列通訊埠 

        if serialport.isOpen():
            print("open success")
            self.listwidget.addItem('open success')
        else:
            print("open failed")
            self.listwidget.addItem('open failed')
            
        #F = MyFigure(1, 1, 100)
       # plt = F.fig.add_subplot(111)
        #self.fig = Figure(figsize=(width, height), dpi=dpi)
        plt.grid(True) # 添加网格
        plt.ion()	# interactive mode
        #F = plt.figure(1)
        plt.xlabel('times')
        plt.ylabel('data')
        plt.ylim(0,400)
        plt.title('Diagram of UART data by Python')
        t = [0]
        m = [0]
        i = 0
        intdata = 0
        data = ''
        count = 0
        #QtWidgets.QGridLayout(self.groupBox).addWidget(F)
        try: 
            while True:
                #self.label_show_image.setPixmap(QtGui.QPixmap.fromImage(\home\k307\path\666\pyqt_serise\test\pyqt\plot.png))
                if i > 300:    # 300次数据后，清除画布，重新开始，避免数据量过大导致卡顿。
                    t = [0]
                    m = [0]
                    i = 0
                    plt.cla()
                count = serialport.inWaiting()
                while serialport.in_waiting:
                    self.button6.setText(u'關閉量測')
                    #self.listwidget.addItem('開始量測...')
                    self.listwidget.addItem(data)
                    data_raw = serialport.readline()  # 讀取一行
                    data = data_raw.decode()
                    a = np.array([data])
                    
                    if data !='':
                        #intdata = int.from_bytes(data, byteorder='big', signed = False)
                        #print('%d byte data %d' % (bytes, intdata))
                        #intdata = int.from_bytes(data,signed = False)
                        
                        #print(data)
                        i = i+1
                        t.append(i)
                        m.append(a)
                        plt.plot(t, m, '-r')     
                        # plt.scatter(i, intdata)
                        plt.draw()
                        plt.savefig('plot.png')
                        self.label_show_image.setPixmap(QPixmap("/home/k307/path/666/pyqt_serise/test/pyqt/plot.png"))
                        #self.label_show_image.setPixmap(QtGui.QPixmap.fromImage(qimage))
             
                plt.pause(0.002)
        except KeyboardInterrupt:
            serialport.close()    # 清除序列通訊物件
            print('再見！')
        
        
    """
    def export(self): 
        self.listwidget.addItem('export...')
        ser.close()    # 清除序列通訊物件        
        mybook = Workbook()
        wa = mybook.active
        wa['A1'] = a
        
        mybook.save('hh.xlsx')
     """
"""    
class MyFigure(FigureCanvas):
    def __init__(self, width=5, height=4, dpi=100):
        # 第一步：创建一个创建Figure
        self.plt = Figure(figsize=(width, height), dpi=dpi)
        # 第二步：在父类中激活Figure窗口
        super(MyFigure, self).__init__(self.plt)  # 此句必不可少，否则不能显示图形
"""
        
class Motor(MyWidget):
    def __init__(self, ena, in1, in2, enb, in3, in4):
        self.ENA = ena
        self.IN1 = in1
        self.IN2 = in2
        self.ENB = enb
        self.IN3 = in3
        self.IN4 = in4
        # 設定右輪
        GPIO.setup(self.ENA, GPIO.OUT, initial=GPIO.LOW)
        # 利用PWN來改變車子馬達轉速（改變車子速度），初始值為全速100
        self.ENA_SPEED = GPIO.PWM(self.ENA, 600)
        self.ENA_SPEED.start(0)
        self.ENA_SPEED.ChangeDutyCycle(100)
        GPIO.setup(self.IN1, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.IN2, GPIO.OUT, initial=GPIO.LOW)
        # 設定左輪
        GPIO.setup(self.ENB, GPIO.OUT, initial=GPIO.LOW)
        self.ENB_SPEED = GPIO.PWM(self.ENB, 600)
        self.ENB_SPEED.start(0)
        self.ENB_SPEED.ChangeDutyCycle(100)
        GPIO.setup(self.IN3, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.IN4, GPIO.OUT, initial=GPIO.LOW)

    def right_speed(self, speed):
        self.ENA_SPEED.ChangeDutyCycle(speed)

    def left_speed(self, speed):
        self.ENB_SPEED.ChangeDutyCycle(speed)

    def speed(self, speed):
        self.right_speed(speed)
        self.left_speed(speed)

    

    def forward(self):
        GPIO.output(self.ENA, True)
        GPIO.output(self.ENB, True)
        GPIO.output(self.IN1, False)
        GPIO.output(self.IN2, True)
        GPIO.output(self.IN3, False)
        GPIO.output(self.IN4, True)
        
    def backward(self):
        GPIO.output(self.ENA, True)
        GPIO.output(self.ENB, True)
        GPIO.output(self.IN1, True)
        GPIO.output(self.IN2, False)
        GPIO.output(self.IN3, True)
        GPIO.output(self.IN4, False)  

    def turn_right(self):
        GPIO.output(self.ENA, True)
        GPIO.output(self.ENB, True)
        GPIO.output(self.IN1, False)
        GPIO.output(self.IN2, True)
        GPIO.output(self.IN3, True)
        GPIO.output(self.IN4, False)

    def turn_left(self):
        GPIO.output(self.ENA, True)
        GPIO.output(self.ENB, True)
        GPIO.output(self.IN1, True)
        GPIO.output(self.IN2, False)
        GPIO.output(self.IN3, False)
        GPIO.output(self.IN4, True)

    def stop(self):
        GPIO.output(self.ENA, True)
        GPIO.output(self.ENB, True)
        GPIO.output(self.IN1, False)
        GPIO.output(self.IN2, False)
        GPIO.output(self.IN3, False)
        GPIO.output(self.IN4, False)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MyWidget()
    w.show()
    sys.exit(app.exec_())        
