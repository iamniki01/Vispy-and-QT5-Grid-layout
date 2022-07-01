import sys
import numpy as np
from PyQt5.QtWidgets import QFileDialog,QComboBox, QScrollArea,QMainWindow,QGroupBox,QVBoxLayout, QPushButton,QAction, qApp, QApplication, QLabel, QMenu, QActionGroup, QGridLayout, QSlider, QWidget
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore    import  Qt, QRect
from vispy import app,  scene,  visuals, gloo

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
#from matplotlib.figure import Figure
import random


class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = plt.figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

class basicMenubar(QMainWindow):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)        
        
        self.initUI()        
        
    def initUI(self):    
        
        self.widget = QWidget()
        #self.setGeometry(200, 200, 200, 200)  
        # menu bars 
        self.label = QLabel()        
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        algo = menubar.addMenu('&Algorithms')

        exitAction = QAction('&Exit', self)        
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(qApp.quit)

        openAction = QAction('Open', self) 
        self.checked= False 
        openAction.triggered.connect(self.openImage) 
        fileMenu.addAction(openAction)

        self.clm = QAction('3D data', self, checkable=True)
        self.clm.setStatusTip('Selected 3D')
        self.clm.setCheckable(True)
        self.clm.setChecked(True)
        self.clm.triggered.connect(self.toggleMenu)

        fir = QAction('2D data', self, checkable=True)
        fir.setStatusTip('Selected 2D')
        fir.setCheckable(True)
        self.clm.triggered.connect(self.toggleMenu)

        fileMenu.addAction(exitAction)
        algo.addAction(self.clm)
        algo.addAction(fir)
        action_group = QActionGroup(self) 
        action_group.addAction(self.clm)
        action_group.addAction(fir)

        self.statusbar = self.statusBar()
        self.statusbar.showMessage('Ready')
        self.bkg_info = QLabel()
        self.canvas = scene.SceneCanvas(keys='interactive')
        self.canvas.size = [1200, 875]
        #self.canvas.setMinimumSize(640, 480)
        # data
        # Add a ViewBox to let the user zoom/rotate
        self.view = self.canvas.central_widget.add_view()
        self.view.camera = "turntable"
        self.view.camera.fov = 45
        self.view.camera.distance = 500
        n = 5000
        pos = np.zeros((n, 3))
        colors = np.ones((n, 4), dtype=np.float32)
        radius, theta, dtheta = 1.0, 0.0, 10.5 / 180.0 * np.pi
        for i in range(500):
            theta += dtheta
            x = 0.0 + radius * np.cos(theta)
            y = 0.0 + radius * np.sin(theta)
            z = 1.0 * radius
            r = 10.1 - i * 0.02
            radius -= 0.45
            pos[i] = x, y, z
            colors[i] = (i / 5000, 1.0 - i / 5000, 0, 0.8)

        # plot ! note the parent parameter
        Scatter3D = scene.visuals.create_visual_node(visuals.MarkersVisual)
        self.p1 = Scatter3D(parent=self.view.scene)
        self.p1.set_gl_state("translucent", blend=True, depth_test=True)
        self.p1.set_data(
            pos, face_color=colors, symbol="o", size=10, edge_width=0.5, edge_color="blue"
        )
        #self.p1.visible =True
     
        # self.scrollArea = QScrollArea(self.widget)
        # self.scrollArea.setWidgetResizable(True)
        # self.scrollAreaWidgetContents = QWidget(self.widget)
        # #self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 100, 100))
        # self.verticalLayout = QVBoxLayout(self.scrollAreaWidgetContents)
        # self.verticalLayout.addWidget(self.canvas.native)
        # self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        # self.scrollAreaWidgetContents.setLayout(self.verticalLayout)
        #self.scrollarea.setWidget(self.widget)
        # #self.canvas.events.mouse_move.connect(self.bkg_mouse_handler)
        # l = QVBoxLayout(self)
        lo = QGridLayout()
        lo.setContentsMargins(0, 3, 3, 3)
        lo.setSpacing(5)
        #lo.addWidget(self.label, 0, 0,3,1)
        if not self.clm.isChecked():
            lo.addWidget(self.label, 0, 0,3,1)
            
        elif self.clm.isChecked():
            lo.addWidget(self.canvas.native, 0, 0,3,1)
            #lo.addWidget(self.scrollArea, 0, 0,3,1)
                     
        lo.addWidget(self.control_widget, 0,1,1,1)
        lo.addWidget(self.main_control_widget, 0,2,1,1)
        lo.addWidget(self.draw,1,1,2,2)
        #lo.addWidget(self.scrollArea)

        
        self.widget.setLayout(lo)
        
        #self.widget = widget
        self.setCentralWidget(self.widget)
        self.setWindowTitle('GUI-Sample') 
        self.resize(1600, 840)
        self.move(0, 200)   
        self.show()

    @property
    def scroll_area(self):
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollarea.setWidget(self.widget)
        #self.canvas.events.mouse_move.connect(self.bkg_mouse_handler)
        l = QVBoxLayout()
        l.addWidget(self.canvas.native)
        l.addWidget(self.scrollArea)
        w = QWidget(self.widget)
        w.setLayout(l)
        return w

    
    @property
    def control_widget(self):
        lo = QVBoxLayout()
        self.sl = QSlider(Qt.Horizontal)
        self.sl.setMinimum(10)
        self.sl.setMaximum(30)
        self.sl.setValue(20)
        self.sl.setTickPosition(QSlider.TicksBelow)
        self.sl.setTickInterval(5)
        label = QLabel()
        label.setText("Control Window")
        label.setAlignment(Qt.AlignCenter)
        lo.addWidget(label)  
        lo.addWidget(self.sl)
        lo.setContentsMargins(0, 3, 3, 3)
        w = QWidget(self.widget)
        w.setLayout(lo)
        return w
    
    @property
    def main_control_widget(self):
        lo = QVBoxLayout()
        self.cb = QComboBox()
        self.cb.addItems(["BT038", "BT063", "BT073", "BT077", "BT087"])
        self.cb.activated.connect(self.updateLabel)
        self.cb.move(0,80)
        self.sl = QSlider(Qt.Horizontal)
        self.sl.setMinimum(10)
        self.sl.setMaximum(30)
        self.sl.setValue(20)
        self.sl.setTickPosition(QSlider.TicksBelow)
        self.sl.setTickInterval(5)
        self.sl_lab_min = QLabel()
        self.sl_lab_min.setText("10")
        self.sl_lab_min.setAlignment(Qt.AlignLeft)
        self.sl_lab_max = QLabel()
        self.sl_lab_max.setText("30")
        self.sl_lab_max.setAlignment(Qt.AlignRight)
        #self.sl_lab_max.move(50,50)
        self.sli = QSlider(Qt.Horizontal)
        self.sli.setMinimum(00)
        self.sli.setMaximum(40)
        self.sli.setValue(20)
        self.sli.setTickPosition(QSlider.TicksBelow)
        self.sli.setTickInterval(5) 
        self.sli_lab_min = QLabel()
        self.sli_lab_min.setText("00")
        self.sli_lab_min.setAlignment(Qt.AlignLeft)
        self.sli_lab_max = QLabel()
        self.sli_lab_max.setText("40")
        self.sli_lab_max.setAlignment(Qt.AlignRight) 

        self.slid = QSlider(Qt.Horizontal)
        self.slid.setMinimum(00)
        self.slid.setMaximum(100)
        self.slid.setValue(50)
        self.slid.setTickPosition(QSlider.TicksBelow)
        self.slid.setTickInterval(5) 
        self.slid_lab_min = QLabel()
        self.slid_lab_min.setText("00")
        self.slid_lab_min.setAlignment(Qt.AlignLeft)
        self.slid_lab_max = QLabel()
        self.slid_lab_max.setText("100")
        self.slid_lab_max.setAlignment(Qt.AlignRight)

        label = QLabel()
        label.setText("Control Panel")
        label.setAlignment(Qt.AlignCenter)
         
        #label.move(65,0) 
        lo.addWidget(label)  
        lo.addWidget(self.cb)
        lo.addWidget(self.sl)
        lo.addWidget(self.sl_lab_min)
        lo.addWidget(self.sl_lab_max)
        lo.addWidget(self.sli)
        lo.addWidget(self.sli_lab_min)
        lo.addWidget(self.sli_lab_max)
        lo.addWidget(self.slid)
        lo.addWidget(self.slid_lab_min)
        lo.addWidget(self.slid_lab_max)

        lo.setContentsMargins(3, 3, 3, 3)
        w = QWidget(self.widget)   
        w.setLayout(lo)
        w.setMaximumWidth(300)
        return w

    @property
    def draw(self):
        lo = QVBoxLayout()
        sc = MplCanvas(self, width=5, height=4, dpi=100)
        sc.axes.plot([0,1,2,3,4], [10,1,20,3,40])
        toolbar = NavigationToolbar(sc,self)
        lo.addWidget(toolbar)
        lo.addWidget(sc)
        w = QWidget(self.widget)
        w.setLayout(lo)
        return w
    
          
    def openImage(self, checked=False):
        imagePath, _ = QFileDialog.getOpenFileName()
        pixmap = QPixmap(imagePath)
        #print(pixmap.size())
        self.clm.setChecked(False)
        self.p1.visible = False
        self.label.setPixmap(pixmap)
        self.resize(pixmap.size())
        self.adjustSize()

    def toggleMenu(self, state):
        if state:
            self.label.clear()
            self.p1.visible = True 
            self.statusbar.show()
        else:
            self.statusbar.hide()
    
    def updateLabel(self):
        self.statusbar.showMessage(self.cb.currentText())
        if self.cb.currentText() == "BT073":
            print("Selcted " + self.cb.currentText())
        return self.cb.currentText()
        
 
    def plot(self):
        ''' plot some random stuff '''
        # random data
        data = [random.random() for i in range(10)]

        # create an axis
        ax = self.figure.add_subplot(111)

        # discards the old graph
        ax.clear()

        # plot data
        ax.plot(data, '*-')

        # refresh canvas
        self.canvas_plot.draw()


        
        
if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    ex = basicMenubar()
    sys.exit(app.exec_())
