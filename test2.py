import sys

from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont
import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PIL import Image, ImageOps, ImageFilter
from PIL.ImageQt import ImageQt
import os
import time
import shutil
import pandas as pd
import matplotlib as plt
from pdf2 import sav2im
import json
from PIL import Image
from PIL import ImageOps
import pytesseract
from model_made import create_model_2
import torchvision.transforms as T
from pdf2image import convert_from_path
import time
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from make_datab import form_database

class Box_point(QPushButton):

    def __init__(self, parent=None, x=0, y=0):
        super(Box_point, self).__init__(parent=parent)
        self.move(x, y)
        self.setStyleSheet(
            "QPushButton{border-image: url(C:/Users/Миша/PycharmProjects/pythonProject4/st_icons/icon1.png)}")

    def mousePressEvent(self, event):
        self.__mousePressPos = None
        self.__mouseMovePos = None
        if event.button() == Qt.LeftButton:
            self.__mousePressPos = event.globalPos()
            self.__mouseMovePos = event.globalPos()

        super(Box_point, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            # adjust offset from clicked point to origin of widget
            currPos = self.mapToGlobal(self.pos())
            globalPos = event.globalPos()
            diff = globalPos - self.__mouseMovePos
            newPos = self.mapFromGlobal(currPos + diff)
            self.move(newPos)
            self.__mouseMovePos = globalPos

        super(Box_point, self).mouseMoveEvent(event)


class Box(QWidget):
    def __init__(self, parent=None, x1=0, y1=0, x2=200, y2=200, child = None):
        super(Box, self).__init__()
        self.child = child
        # self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.move(x1, y1)
        self.point1 = Box_point(x=x1-25, y=y1-15)
        self.point2 = Box_point(x=x2, y=y2)
        a = parent.addWidget(self.point1)
        b = parent.addWidget(self.point2)
        a.setZValue(1)
        b.setZValue(1)


class screener(QWidget):
    def __init__(self, parent=None, img=0, scalfac=1):
        super(screener, self).__init__(parent=parent)
        self.img = img
        self.scalfac = scalfac
        self.parent = parent
        self.blocked = []
        graphicsView = QGraphicsView(self)
        self.working_file = ''
        self.scene = QGraphicsScene()
        self.cur_width = 0
        self.cur_height = 0
        self.boxes = []
        self.pixmap = QGraphicsPixmapItem()
        self.scene.addItem(self.pixmap)
        but5 = QPushButton('Add box', self)
        but5.clicked.connect(self.add_box)
        self.scene.addWidget(but5)
        but5 = QPushButton('Delete selected', self)
        but5.clicked.connect(self.delete_boxes)
        self.scene.addWidget(but5)
        but5.move(0, 40)
        graphicsView.setScene(self.scene)
        graphicsView.resize(app.desktop().screenGeometry().width(), app.desktop().screenGeometry().height() - 100)

    def add_boxes(self):
        flag = 0
        for k in self.boxes:
            k.point1.deleteLater()
            k.point2.deleteLater()
        self.boxes = []
        if 'page-' + str(self.img) + '.png' in self.blocked:
            return
        if len(os.listdir(path=r'C:\Users\Миша\PycharmProjects\pythonProject4\boxes')) != 0:
            with open(r'C:\Users\Миша\PycharmProjects\pythonProject4\boxes\key_res.json') as f:
                boxes = json.load(f)
            if self.working_file in list(boxes.keys()):
                for box in boxes[self.working_file]:
                    if box['page'] == 'page-' + str(self.img) + '.png':
                        flag = 1
                        boxes = box['boxes']
                        pat = os.path.join(r'C:\Users\Миша\PycharmProjects\pythonProject4\imgs',
                                           'page-' + str(self.img) + '.png')
                        im = Image.open(pat)
                        (width, height) = im.size
                        break
                    else:
                        boxes = []
                for k in boxes:
                    box1 = Box(self.scene, x1=int(k[0] / self.scalfac), y1=int(k[1] / self.scalfac),
                               x2=int(k[2] / self.scalfac), y2=int(k[3] / self.scalfac))
                    self.boxes.append(box1)
        else:
            pass

    def add_box(self):
        box1 = Box(self.scene, x1=100, y1=100,
                   x2=300, y2=300)
        if 'page-' + str(self.img) + '.png' in self.blocked:
            self.blocked.remove('page-' + str(self.img) + '.png')
        self.boxes.append(box1)
        self.show_boxes()

    def delete_boxes(self):
        for box in self.boxes:
            if box.child.isSelected():
                self.boxes.remove(box)
                box.point1.deleteLater()
                box.point2.deleteLater()
        self.show_boxes()


    def show_boxes(self):
        n = QGraphicsRectItem()
        for item in self.scene.items():
            if type(item) == type(n):
                self.scene.removeItem(item)
        pen = QPen(QColor("salmon"))
        pen.setWidth(3)
        for box in self.boxes:
            x1 = box.point1.x()+25
            y1 = box.point1.y()+15
            x2 = box.point2.x()
            y2 = box.point2.y()
            rect_item = QGraphicsRectItem(QRectF(x1, y1, x2-x1, y2-y1))
            box.child = rect_item
            rect_item.setFlag(QGraphicsItem.ItemIsSelectable, True)
            box.point1.clicked.connect(self.show_boxes)
            box.point2.clicked.connect(self.show_boxes)
            rect_item.setPen(pen)
            self.scene.addItem(rect_item)
        self.parent.change_color_2()


class Crops_text(QWidget):
    def __init__(self, parent=None, img = None):
        super(Crops_text, self).__init__(parent=parent)
        table = QTableWidget(self)
        table.setColumnCount(1)
        table.setRowCount(3)
        table.setHorizontalHeaderLabels(["Компании"])
        w = table.width()
        h = table.height()
        self.resize(w, h)

class graph_wid(QGraphicsView):
    def __init__(self, parent=None, way = None):
        super(graph_wid, self).__init__(parent=parent)
        self.rubberband = QRubberBand(
            QRubberBand.Rectangle, self)
        self.setMouseTracking(True)

    def mousePressEvent(self, event):
        self.origin = event.pos()
        self.rubberband.setGeometry(
            QRect(self.origin, QSize()))
        self.rubberband.show()
        super(graph_wid, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.rubberband.isVisible():
            self.rubberband.setGeometry(
                QRect(self.origin, event.pos()).normalized())
        super(graph_wid, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.rubberband.isVisible():
            self.rubberband.hide()
        super(graph_wid, self).mouseReleaseEvent(event)

class mdem(QGraphicsScene):
    def __init__(self, parent=None, way = None):
        super(mdem, self).__init__(parent=parent)
        self.rubberband = QGraphicsRectItem()
        self.rubberband.hide()
        self.addItem(self.rubberband)
        self.way = way
        self.parent=parent

    def mousePressEvent(self, event):
        if event.scenePos().x() > 200 or event.scenePos().x() < 0:
            super(mdem, self).mousePressEvent(event)
            return
        self.origin = event.scenePos()
        self.rubberband.setPos(self.origin)
        self.rubberband.show()
        super(mdem, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.rubberband.isVisible():
            self.rubberband.setRect(self.origin.x(), self.origin.y(), event.pos().x()-self.origin.x(), event.pos().y()-self.origin.y())
        super(mdem, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.rubberband.isVisible():
            self.rubberband.setRect(self.origin.x(), self.origin.y(), event.scenePos().x() - self.origin.x(),
                                    event.scenePos().y() - self.origin.y())
            self.rubberband.hide()
            box1 = [self.origin.x(), self.origin.y(), event.scenePos().x(), event.scenePos().y()]
            if (abs(event.scenePos().x()-self.origin.x())) < 80 or abs((event.scenePos().y()-self.origin.y())< 10):
                super(mdem, self).mouseReleaseEvent(event)
                return
            self.way.add_box(box1)
            super(mdem, self).mouseReleaseEvent(event)
        else:
            super(mdem, self).mouseReleaseEvent(event)

class edit_help(QLineEdit):
    def __init__(self, parent=None, way=None, child=None):
        super(edit_help, self).__init__(parent)
        self.way = way
        self.x = 0
        self.y = 0
        self.child = child

    def mousePressEvent(self, event):
        for item in self.way.buts:
            item.hide()
        self.child.show()
        super(edit_help, self).mouseReleaseEvent(event)

    def fill_text(self):
        self.setText(self.child.widget().text())



class Crops(QWidget):
    def __init__(self, parent=None, working_file=None, img=0, scalfac=1):
        super(Crops, self).__init__(parent=parent)
        self.graphicsView = graph_wid(self)
        self.working_file = working_file
        self.scene = mdem(way=self)
        self.crop = ''
        self.rrr = {}
        self.setMouseTracking(True)
        self.img = 0
        self.tab_wid = 0
        self.num_crops = len(os.listdir(os.path.join(r'C:\Users\Миша\PycharmProjects\pythonProject4\crops',
                                                     self.working_file)))
        self.initUI()

    def initUI(self):
        self.buts = []
        self.scene = mdem(way=self)
        print(self.working_file)
        if self.working_file:
            city = ['bronx', 'queens', 'brooklyn', 'manhattan', 'staten']
            for cit in city:
                if cit in self.working_file.lower():
                    kon = pd.read_excel(r'C:\Users\Миша\PycharmProjects\pythonProject4\database\database.xlsx', sheet_name=cit)
                    kon1 = kon['ind'].to_list()
                    if len(kon1) > 100:
                        self.firms = kon1
                    else:
                        self.firms = pd.read_excel(r'C:\Users\Миша\PycharmProjects\pythonProject4\companies.xlsx')
                        self.firms['Companies'] = self.firms['Companies'].str.strip()
                        self.firms = list(self.firms['Companies'])
            self.num_crops = len(os.listdir(os.path.join(r'C:\Users\Миша\PycharmProjects\pythonProject4\crops',
                                                     self.working_file)))
        print(1)
        if self.working_file:
            self.pat1 = os.path.join(r'C:\Users\Миша\PycharmProjects\pythonProject4\crops', self.working_file)
            width = 0
            with open(os.path.join(r'C:\Users\Миша\PycharmProjects\pythonProject4\database\data.json')) as f:
                data1 = json.load(f)
                if self.working_file in data1.keys() and str(self.img) in data1[self.working_file].keys():
                    data = data1[self.working_file]
                    title = str(self.img)
                else:
                    with open(os.path.join(r'C:\Users\Миша\PycharmProjects\pythonProject4\processed', self.working_file + '.json')) as f:
                        data = json.load(f)
                    title = self.working_file + '_'+str(self.img)
            self.rects = []
            self.pixmap = QGraphicsPixmapItem()
            img = QPixmap(os.path.join(self.pat1, self.working_file + '_'+str(self.img) + '.png'))
            self.pixmap.setPixmap(img)
            self.scene.addItem(self.pixmap)
            i=0
            n = {}
            for c in range(len(data[title]['text'])):
                box = data[title]['boxes'][c]
                n[c] = box[1]
            self.sorted_keys = sorted(n, key=n.get)
            for hj in range(len(data[title]['text'])):
                box = data[title]['boxes'][self.sorted_keys[hj]]
                rect_item = QGraphicsRectItem(QRectF(width+box[0], box[1], box[2]-box[0], box[3] - box[1]))
                rect_item.setFlag(QGraphicsItem.ItemIsSelectable, True)
                self.scene.addItem(rect_item)
                tex = self.find_sim(data[title]['text'][self.sorted_keys[hj]])
                oao = QPushButton(tex[0])
                ooo = self.scene.addWidget(oao)
                ooo.hide()
                self.buts.append(ooo)
                d = edit_help(way=self, child=ooo)
                d.setText(data[title]['text'][self.sorted_keys[hj]])
                d.createStandardContextMenu()
                compl = QCompleter(self.firms)
                d.setCompleter(compl)
                a = self.scene.addWidget(d)
                a.setPos(-1 * a.size().width(), box[1])
                oao.clicked.connect(d.fill_text)
                ooo.setPos(-1 * a.size().width()-oao.width(), box[1])
                self.rects.append([rect_item, a])
            self.pixmap.moveBy(0, 0)
        but1 = QPushButton('Remove selected', self)
        but1.clicked.connect(self.remove_selected)
        a = self.scene.addWidget(but1)
        self.graphicsView.setScene(self.scene)
        self.graphicsView.resize(app.desktop().screenGeometry().width(), app.desktop().screenGeometry().height() - 100)

    def remove_selected(self):
        for item in self.rects:
            if item[0].isSelected():
                self.scene.removeItem(item[0])
                self.scene.removeItem(item[1])
                self.rects.remove(item)

    def add_box(self, box):
        rect_item = QGraphicsRectItem(QRectF(box[0], box[1], box[2] - box[0], box[3] - box[1]))
        rect_item.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.scene.addItem(rect_item)
        rect_item.setZValue(2)
        nnn=self.define_text(box)
        tex = self.find_sim(nnn)
        oao = QPushButton(tex[0])
        ooo = self.scene.addWidget(oao)
        ooo.hide()
        self.buts.append(ooo)
        d = edit_help(way=self, child=ooo)
        d.setText(nnn)
        d.createStandardContextMenu()
        compl = QCompleter(self.firms)
        d.setCompleter(compl)
        a = self.scene.addWidget(d)
        a.setPos(-1 * a.size().width(), box[1])
        oao.clicked.connect(d.fill_text)
        ooo.setPos(-1 * a.size().width() - oao.width(), box[1])
        self.rects.append([rect_item, a])


    def define_text(self, box):
        d = Image.open(os.path.join(self.pat1, self.working_file + '_'+str(self.img)+'.png'))
        siz = d.size
        self.width1 = 0
        tr = d.crop((box[0], box[1], box[2], box[3]))
        g = self.get_text(tr)
        if g.isspace() or g == '':
            tr = d.crop((box[0] - 3 -self.width1, box[1] - 3, box[2] + 3 -self.width1, box[3] + 3))
            g = self.get_text(tr)
        if g.isspace() or g == '':
            tr = d.crop((box[0]-self.width1, box[1], box[2]-self.width1, box[3]))
            width, height = tr.size
            tr1 = Image.new(tr.mode, (width + 40, height + 40), (255, 255, 255))
            tr1.paste(tr, (20, 20))
            g = self.get_text(tr1)
        if g.isspace() or g == '':
            tr = d.crop((box[0] - 3-self.width1, box[1] - 3, box[2] + 3-self.width1, box[3] + 3))
            width, height = tr.size
            tr1 = Image.new(tr.mode, (width + 40, height + 40), (255, 255, 255))
            tr1.paste(tr, (20, 20))
            g = self.get_text(tr1)
        return g

    def get_text(self, img):
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'
        string = pytesseract.image_to_string(img, lang='eng')
        return string

    def find_sim(self, comp):
        a = process.extractOne(comp, self.firms)
        return a


class process_work_dir(QThread):
    def __init__(self, parent=None, dir1 = r'C:\Users\Миша\PycharmProjects\pythonProject4\working', data=dict()):
        super(process_work_dir, self).__init__(parent)
        self.data = data
        self.parent = parent
        self.dir1 = dir1

    def run(self):
        value = 0
        for file in os.listdir(self.dir1):
            if file[:-4] not in list(self.data.keys()):
                a = os.path.join(self.dir1, file)
                boxes = self.parent.make_boxes(a, dir=0)
                self.data[file[:-4]] = boxes
                with open(r'C:\Users\Миша\PycharmProjects\pythonProject4\boxes\key_res.json', 'w') as f:
                    json.dump(self.data, f)
            value+=(100/len(os.listdir(self.dir1)))
            self.parent.bar.setValue(int(value))


class process_crops(QThread):
    def __init__(self, parent=None, dir1 = r'C:\Users\Миша\PycharmProjects\pythonProject4\crops'):
        super(process_crops, self).__init__(parent)
        self.parent = parent
        self.dir1 = dir1

    def run(self):
        value = len(set(os.listdir(self.dir1)).intersection([
            os.listdir(r'C:\Users\Миша\PycharmProjects\pythonProject4\processed')[i][:-4]
            for i in range(len(os.listdir(r'C:\Users\Миша\PycharmProjects\pythonProject4\processed')))]))*100/len(
            os.listdir(self.dir1))
        for file in os.listdir(self.dir1):
            if file+'.json' not in os.listdir(r'C:\Users\Миша\PycharmProjects\pythonProject4\processed'):
                a = os.path.join(self.dir1, file)
                boxes = self.parent.find_companies(a)
                value+=(100/len(os.listdir(self.dir1)))
                self.parent.bar3.setValue(int(value))
                with open(os.path.join(r'C:\Users\Миша\PycharmProjects\pythonProject4\processed', file + '.json'), 'w') as f:
                    json.dump(boxes, f)

class take_it_easy(QThread):
    def __init__(self, parent=None):
        super(take_it_easy, self).__init__(parent)
        self.parent = parent

    def run(self):
        fileName = os.path.join(r'C:\Users\Миша\PycharmProjects\pythonProject4\working', os.listdir(
            r'C:\Users\Миша\PycharmProjects\pythonProject4\working')[1])
        sav2im(fileName)


class Example(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setAcceptDrops(True)
        self.num = len([name for name in os.listdir(r'C:\Users\Миша\PycharmProjects\pythonProject4\imgs')])
        self.model = create_model_2(r'C:\Users\Миша\PycharmProjects\pythonProject4\model\model1_5.pth', 2)
        self.model.eval()
        self.model2 = create_model_2(r'C:\Users\Миша\PycharmProjects\pythonProject4\model\model_new_2_9.pth', classes=3)
        self.model2.eval()
        self.val = 0
        with open(r'C:\Users\Миша\PycharmProjects\pythonProject4\meta.json', 'rb') as f:
            dat = json.load(f)
        self.img = dat['page']
        self.category = dat['category']
        self.working_shape = [0, 0]
        self.working_file = dat['file']
        self.total = len(os.listdir(r'C:\Users\Миша\PycharmProjects\pythonProject4\working'))
        self.processed = []
        self.initUI()
        self.play()
        self.createActions()
        self.createMenus()

    def initUI(self):
        pageLayout = QHBoxLayout()
        button_layout = QVBoxLayout()
        self.stacklayout = QStackedLayout()
        self.setGeometry(600, 600, 600, 800)

        self.graphicsView = screener(self)
        self.stacklayout.addWidget(self.graphicsView)
        pageLayout.addLayout(self.stacklayout)

        self.setWindowTitle('Test')

        self.bar4 = QProgressBar()
        self.bar4.setMaximumWidth(250)
        button_layout.addWidget(self.bar4)
        self.bar4.setValue(0)

        self.lcd4 = QLCDNumber(self)
        self.lcd4.display(0)
        button_layout.addWidget(self.lcd4)

        button = QPushButton('Вперёд', self)
        button.clicked.connect(self.forward)
        button.clicked.connect(self.play)
        button_layout.addWidget(button)

        button1 = QPushButton('Назад', self)
        button1.clicked.connect(self.backward)
        button1.clicked.connect(self.play)
        button_layout.addWidget(button1)

        self.button2 = QPushButton('Сохранить', self)
        self.button2.clicked.connect(self.save_boxes)
        self.button2.clicked.connect(self.change_color)
        self.button2.clicked.connect(self.change_processed)
        self.button2.clicked.connect(self.forward)
        self.button2.clicked.connect(self.play)
        button_layout.addWidget(self.button2)

        button3 = QPushButton('Закончить', self)
        button3.clicked.connect(self.end_work)
        button_layout.addWidget(button3)

        button4 = QPushButton('Перейти к кускам', self)
        button4.clicked.connect(self.change_to_crops)
        button_layout.addWidget(button4)

        button5= QPushButton('Обработать рабочую директорию', self)
        button5.clicked.connect(self.process_work_dir)
        button_layout.addWidget(button5)

        button6 = QPushButton('Обработать отдельные куски', self)
        button6.clicked.connect(self.done_crops)
        button_layout.addWidget(button6)

        button7 = QPushButton('Найти категорию', self)
        button7.clicked.connect(self.find_category)
        button_layout.addWidget(button7)

        self.bar = QProgressBar()
        self.bar.setMaximumWidth(250)
        button_layout.addWidget(self.bar)

        self.bar2 = QProgressBar()
        self.bar2.setMaximumWidth(250)
        button_layout.addWidget(self.bar2)

        self.bar3 = QProgressBar()
        self.bar3.setMaximumWidth(250)
        button_layout.addWidget(self.bar3)

        self.lcd = QLCDNumber(self)
        self.lcd.display(1)
        button_layout.addWidget(self.lcd)

        self.lcd1 = QLCDNumber(self)
        self.lcd1.display(self.num)
        button_layout.addWidget(self.lcd1)

        pageLayout.addLayout(button_layout)

        self.widget = QWidget()
        self.widget.setLayout(pageLayout)
        self.setCentralWidget(self.widget)

        self.showMaximized()

    def find_category(self):
        a = []
        t = self.make_mask()
        for b in list(t.keys()):
            if t[b] == 0:
                a.append(b)
        self.graphicsView.blocked = a
        self.play()

    def forward(self):
        if self.img != self.num - 1:
            self.img += 1
        else:
            self.img = 0
        self.graphicsView.img = self.img

    def change_color(self):
        self.button2.setStyleSheet("QPushButton"
                             "{"
                             "background-color : green;"
                             "}"
                             )

    def change_color_2(self):
        self.button2.setStyleSheet("QPushButton"
                             "{"
                             "background-color : red;"
                             "}"
                             )

    def change_processed(self):
        if self.img not in self.processed:
            self.processed.append(self.img)
            self.bar2.setValue(int(len(self.processed)*100/self.num))

    def backward(self):
        if self.img != 0:
            self.img -= 1
        else:
            self.img = self.num - 1
        self.graphicsView.img = self.img

    def play(self):
        self.lcd.display(self.img + 1)
        b = 'page-' + str(self.img) + '.png'
        d = os.path.join(r'C:\Users\Миша\PycharmProjects\pythonProject4\imgs', b)
        img = QPixmap(d)
        self.working_shape = [img.width(), img.height()]
        sc_fac = max([img.width() / app.desktop().screenGeometry().width(),
                      img.height() / app.desktop().screenGeometry().height()]) + 0.4
        self.graphicsView.cur_width = int(img.width() / sc_fac)
        self.graphicsView.cur_height = int(img.height() / sc_fac)
        img = img.scaled(int(img.width() / sc_fac), int(img.height() / sc_fac))
        self.graphicsView.scalfac = sc_fac
        self.graphicsView.img = self.img
        self.graphicsView.working_file = self.working_file
        self.graphicsView.pixmap.setPixmap(img)
        self.graphicsView.add_boxes()
        self.graphicsView.show_boxes()
        if self.img in self.processed:
            self.change_color()

    def open(self):
        options = QFileDialog.Options()
        # fileName = QFileDialog.getOpenFileName(self, "Open File", QDir.currentPath())
        fileName, _ = QFileDialog.getOpenFileName(self, 'QFileDialog.getOpenFileName()', '',
                                                  '*.pdf', options=options)
        self.working_file = os.path.basename(fileName)[:-4]
        if fileName:
            self.num = sav2im(fileName, path1=r'C:\Users\Миша\PycharmProjects\pythonProject4\imgs')
        self.num = len([name for name in os.listdir(r'C:\Users\Миша\PycharmProjects\pythonProject4\imgs')])
        self.lcd1.display(self.num)
        self.img = 0
        self.processed = []
        self.play()

    def createActions(self):
        self.openAct = QAction("&Open...", self, shortcut="Ctrl+O", triggered=self.open)

    def createMenus(self):
        self.fileMenu = QMenu("&File", self)
        self.fileMenu.addAction(self.openAct)
        self.menuBar().addMenu(self.fileMenu)

    def save_boxes(self):
        cur_boxes = self.graphicsView.boxes
        with open(r'C:\Users\Миша\PycharmProjects\pythonProject4\boxes\key_res.json') as f:
            data = json.load(f)
        file_name = self.working_file
        new_boxes = []
        for box in cur_boxes:
            x1 = (box.point1.x()+25)* self.graphicsView.scalfac
            y1 = (box.point1.y()+15)* self.graphicsView.scalfac
            x2 = box.point2.x() * self.graphicsView.scalfac
            y2 = box.point2.y() * self.graphicsView.scalfac
            box1 = [x1, y1, x2, y2]
            new_boxes.append(box1)
        for k in data[file_name]:
            if k['page'] == 'page-' + str(self.img) + '.png':
                k['boxes'] = new_boxes
        with open(r'C:\Users\Миша\PycharmProjects\pythonProject4\boxes\key_res.json', "w") as fp:
            json.dump(data, fp)

    def end_work(self):
        self.rename()
        pat1 = os.path.join(r'C:\Users\Миша\PycharmProjects\pythonProject4\crops', str(self.working_file))
        if self.working_file not in os.listdir(r'C:\Users\Миша\PycharmProjects\pythonProject4\crops'):
            os.mkdir(os.path.join(r'C:\Users\Миша\PycharmProjects\pythonProject4\crops', str(self.working_file)))
        else:
            for filename in os.listdir(pat1):
                file_path1 = os.path.join(pat1, filename)
                try:
                    if os.path.isfile(file_path1) or os.path.islink(file_path1):
                        os.unlink(file_path1)
                except:
                    pass
        with open(r'C:\Users\Миша\PycharmProjects\pythonProject4\boxes\key_res.json', "rb") as fp:
            boxes = json.load(fp)
        i = 0
        for k in boxes[self.working_file]:
            box2 = k['boxes']
            img = Image.open(os.path.join(r'C:\Users\Миша\PycharmProjects\pythonProject4\Future', k['page']))
            for box in box2:
                img1 = img.crop((box[0], box[1], box[2], box[3]))
                img1.save(os.path.join(pat1, str(self.working_file) + '_' + str(i) + '.png'))
                i += 1
        self.val += 100/self.total
        self.lcd4.display(self.lcd4.value()+1)
        self.bar4.setValue(int(self.val))
        self.go_next()

    def go_next(self):
        if self.working_file + '.pdf' in os.listdir(r'C:\Users\Миша\PycharmProjects\pythonProject4\working'):
            os.remove(os.path.join(r'C:\Users\Миша\PycharmProjects\pythonProject4\working', self.working_file+ '.pdf'))
        if len(os.listdir(r'C:\Users\Миша\PycharmProjects\pythonProject4\working'))>0:
            self.working_file = os.listdir(
                r'C:\Users\Миша\PycharmProjects\pythonProject4\working')[0][:-4]
            self.num = len([name for name in os.listdir(r'C:\Users\Миша\PycharmProjects\pythonProject4\imgs')])
            self.lcd1.display(self.num)
            self.bar2.setValue(0)
            self.img = 0
            self.processed = []
            self.graphicsView.blocked = []
            self.play()
        else:
            pass
        if len(os.listdir(r'C:\Users\Миша\PycharmProjects\pythonProject4\working'))>1:
            new_thread_2 = take_it_easy(parent=self)
            new_thread_2.start()

    def rename(self):
        os.rename(r'C:\Users\Миша\PycharmProjects\pythonProject4\imgs',
                   r'C:\Users\Миша\PycharmProjects\pythonProject4\past')
        os.rename(r'C:\Users\Миша\PycharmProjects\pythonProject4\Future',
                   r'C:\Users\Миша\PycharmProjects\pythonProject4\imgs')
        os.rename(r'C:\Users\Миша\PycharmProjects\pythonProject4\past',
                   r'C:\Users\Миша\PycharmProjects\pythonProject4\Future')

    def change_to_crops(self):
        pageLayout = QHBoxLayout()
        button_layout = QVBoxLayout()
        self.done = set()
        self.stacklayout = QStackedLayout()
        self.setGeometry(600, 600, 600, 800)

        wf = os.listdir(r'C:\Users\Миша\PycharmProjects\pythonProject4\processed')[0][:-5]
        while len(os.listdir(os.path.join(r'C:\Users\Миша\PycharmProjects\pythonProject4\crops', wf))) == 0:
            self.deal_with_empty(wf)
            if len(os.listdir(r'C:\Users\Миша\PycharmProjects\pythonProject4\crops')) > 0:
                wf = os.listdir(r'C:\Users\Миша\PycharmProjects\pythonProject4\crops')[0]

        self.graphicsView = Crops(self, working_file=wf)
        self.stacklayout.addWidget(self.graphicsView)
        pageLayout.addLayout(self.stacklayout)

        self.setWindowTitle('Test')

        self.lcd2 = QLCDNumber(self)
        self.lcd2.display(0)
        button_layout.addWidget(self.lcd2)

        button2 = QPushButton('Вперёд', self)
        button2.clicked.connect(self.next_crop)
        button_layout.addWidget(button2)
        pageLayout.addLayout(button_layout)

        button3 = QPushButton('Назад', self)
        button3.clicked.connect(self.prev_crop)
        button_layout.addWidget(button3)
        pageLayout.addLayout(button_layout)

        button4 = QPushButton('Сохранить', self)
        button4.clicked.connect(self.save_firms)
        button4.clicked.connect(self.next_crop)
        button_layout.addWidget(button4)
        pageLayout.addLayout(button_layout)

        button1 = QPushButton('Закончить', self)
        button1.clicked.connect(self.next_file_crops)
        button_layout.addWidget(button1)
        pageLayout.addLayout(button_layout)

        button = QPushButton('К файлам', self)
        button.clicked.connect(self.initUI)
        button.clicked.connect(self.play)
        button_layout.addWidget(button)

        button5 = QPushButton('Сформировать файл с базой', self)
        button5.clicked.connect(self.form_file)
        button_layout.addWidget(button5)

        self.bar = QProgressBar()
        self.bar.setMaximumWidth(250)
        button_layout.addWidget(self.bar)

        self.lcd = QLCDNumber(self)
        self.lcd.display(1)
        button_layout.addWidget(self.lcd)

        self.lcd1 = QLCDNumber(self)
        self.lcd1.display(self.graphicsView.num_crops)
        button_layout.addWidget(self.lcd1)

        self.widget = QWidget()
        self.widget.setLayout(pageLayout)
        self.setCentralWidget(self.widget)

        self.showMaximized()

    def del_crop(self):
        a = self.graphicsView.img
        k = 0
        path1= os.path.join(r'C:\Users\Миша\PycharmProjects\pythonProject4\crops', self.graphicsView.working_file)
        b = os.listdir(path1)
        with open(os.path.join(r'C:\Users\Миша\PycharmProjects\pythonProject4\processed', self.graphicsView.working_file+'.json'), 'rb') as f:
            data = json.load(f)
        for file in b:
            if k < a:
                k+=1
                continue
            elif k==a:
                os.remove(os.path.join(path1, file))
                k+=1
                del data[file[:-4]]
                continue
            elif k>a:
                os.rename(os.path.join(path1, file), os.path.join(path1, self.graphicsView.working_file + '_'+str(k-1)+'.png'))
                data[self.graphicsView.working_file + '_'+str(k-1)] = data.pop(file[:-4])
                k+=1
                continue
        with open(os.path.join(r'C:\Users\Миша\PycharmProjects\pythonProject4\processed', self.graphicsView.working_file+'.json'), 'w') as f:
            json.dump(data, f)
        self.graphicsView.initUI()

    def form_file(self):
        form_database()

    def next_crop(self):
        if self.graphicsView.img == self.graphicsView.num_crops-1:
            self.graphicsView.img = 0
            self.graphicsView.initUI()
        else:
            self.graphicsView.img = self.graphicsView.img + 1
            self.graphicsView.initUI()
        self.lcd.display(self.graphicsView.img+1)

    def prev_crop(self):
        if self.graphicsView.img > 0:
            self.graphicsView.img = self.graphicsView.img - 1
            self.graphicsView.initUI()
        else:
            self.graphicsView.img = self.graphicsView.num_crops-1
            self.graphicsView.initUI()
        self.lcd.display(self.graphicsView.img + 1)

    def next_file_crops(self):
        if self.bar.value() != 100:
            return
        self.lcd2.display(self.lcd2.value()+1)
        if len(os.listdir(r'C:\Users\Миша\PycharmProjects\pythonProject4\crops')) > 1:
            os.remove(os.path.join(r'C:\Users\Миша\PycharmProjects\pythonProject4\processed',
                                       os.listdir(r'C:\Users\Миша\PycharmProjects\pythonProject4\processed')[0]))
            wk = os.listdir(r'C:\Users\Миша\PycharmProjects\pythonProject4\crops')[0]
            path = os.path.join(r'C:\Users\Миша\PycharmProjects\pythonProject4\crops', wk)
            shutil.move(path, r'C:\Users\Миша\PycharmProjects\pythonProject4\database_learn')
        if len(os.listdir(r'C:\Users\Миша\PycharmProjects\pythonProject4\crops')) > 0:
            working_file = os.listdir(r'C:\Users\Миша\PycharmProjects\pythonProject4\crops')[0]
            while len(os.listdir(os.path.join(r'C:\Users\Миша\PycharmProjects\pythonProject4\crops', working_file)))==0:
                self.deal_with_empty(working_file)
                if len(os.listdir(r'C:\Users\Миша\PycharmProjects\pythonProject4\crops')) > 0:
                    working_file = os.listdir(r'C:\Users\Миша\PycharmProjects\pythonProject4\crops')[0]
                else:
                    return
            self.graphicsView.working_file = working_file
            self.graphicsView.rrr = {}
            self.graphicsView.img = 0
            self.graphicsView.tab_wid = 0
            self.lcd.display(1)
            self.done = set()
            self.bar.setValue(0)
            self.lcd1.display(self.graphicsView.num_crops)
            self.graphicsView.num_crops = len(os.listdir(os.path.join(r'C:\Users\Миша\PycharmProjects\pythonProject4\crops',
                                                         self.graphicsView.working_file)))
            self.graphicsView.initUI()
            self.lcd1.display(self.graphicsView.num_crops)

    def deal_with_empty(self, working_file):
        with open(r'C:\Users\Миша\PycharmProjects\pythonProject4\database\data.json', 'rb') as f:
            data = json.load(f)
        data[working_file] = {}
        with open(r'C:\Users\Миша\PycharmProjects\pythonProject4\database\data.json', 'w') as f:
            json.dump(data, f)
        if len(os.listdir(r'C:\Users\Миша\PycharmProjects\pythonProject4\crops')) > 1:
            os.remove(os.path.join(r'C:\Users\Миша\PycharmProjects\pythonProject4\processed',
                                       os.listdir(r'C:\Users\Миша\PycharmProjects\pythonProject4\processed')[0]))
            wk = os.listdir(r'C:\Users\Миша\PycharmProjects\pythonProject4\crops')[0]
            path = os.path.join(r'C:\Users\Миша\PycharmProjects\pythonProject4\crops', wk)
            shutil.move(path, r'C:\Users\Миша\PycharmProjects\pythonProject4\database_learn')

    def rework(self, preds):
        d = {}
        k=0
        for b in preds['scores']:
            if b > 0.9:
                k+=1
            else:
                break
        d['boxes'] = preds['boxes'].tolist()[:k]
        d['labels'] = preds['labels'].tolist()[:k]
        d['scores'] = preds['scores'].tolist()[:k]
        return d

    def make_boxes(self, file, dir = 0):
        k = T.ToTensor()
        r = 0
        a = []
        m = {}
        if dir == 0:
            images = convert_from_path(file, poppler_path=r'C:\Users\Миша\Desktop\poppler-0.68.0\bin')
            for t in images:
                text = self.get_text(t)
                j = k(t)
                preds = self.model([j])[0]
                preds = self.rework(preds)
                preds['page'] = 'page-' + str(r)+'.png'
                m['page-' + str(r)+'.png'] = text
                r+=1
                a.append(preds)
        else:
            for b in os.listdir(file):
                j = Image.open(os.path.join(file, b))
                text = self.get_text(j)
                j = k(j)
                preds = self.model([j])[0]
                preds = self.rework(preds)
                preds['page'] = b
                m[b] = text
                a.append(preds)
        part1 = r'C:\Users\Миша\PycharmProjects\pythonProject4\texts'
        part2 = os.path.basename(file)[:-4] + '.json'
        part3 = os.path.join(part1, part2)
        with open(part3, 'w') as fn:
            json.dump(m, fn)
        return a

    def find_companies(self, file):
        k = T.ToTensor()
        r = 0
        a = {}
        for b in os.listdir(file):
            d = Image.open(os.path.join(file, b))
            j = k(d)
            preds = self.model2([j])[0]
            preds = self.rework(preds)
            preds['text'] = []
            for comp in preds['boxes']:
                tr = d.crop((comp[0], comp[1], comp[2], comp[3]))
                g = self.get_text(tr)
                if g.isspace() or g == '':
                    tr = d.crop((comp[0]-3, comp[1]-3, comp[2]+3, comp[3]+3))
                    g = self.get_text(tr)
                if g.isspace() or g == '':
                    tr = d.crop((comp[0], comp[1], comp[2], comp[3]))
                    width, height = tr.size
                    tr1 = Image.new(tr.mode, (width+40, height+40), (255, 255, 255))
                    tr1.paste(tr, (20, 20))
                    g = self.get_text(tr1)
                if g.isspace() or g == '':
                    tr = d.crop((comp[0]-3, comp[1]-3, comp[2]+3, comp[3]+3))
                    width, height = tr.size
                    tr1 = Image.new(tr.mode, (width+40, height+40), (255, 255, 255))
                    tr1.paste(tr, (20, 20))
                    g = self.get_text(tr1)
                preds['text'].append(g)
            a[b[:-4]] = preds
        return a

    def done_crops(self):
        new_thread_1 = process_crops(parent=self)
        new_thread_1.start()

    def get_text(self, img):
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'
        string = pytesseract.image_to_string(img, lang='eng')
        return string

    def save_firms(self):
        self.done.add(self.graphicsView.img)
        self.bar.setValue(int(100*len(self.done)/self.graphicsView.num_crops))
        n = QGraphicsProxyWidget()
        r = QLineEdit()
        results = []
        boxes = []
        for item in self.graphicsView.rects:
            results.append(item[1].widget().text())
            a = item[0].boundingRect()
            boxes.append([a.x(), a.y(), a.x()+a.width(), a.y()+a.height()])
        with open(r'C:\Users\Миша\PycharmProjects\pythonProject4\database\data.json', 'rb') as f:
            data = json.load(f)
        if self.graphicsView.working_file not in data.keys():
            data[self.graphicsView.working_file] = {}
        if self.graphicsView.img not in data[self.graphicsView.working_file].keys():
            data[self.graphicsView.working_file][self.graphicsView.img] = {}
        data[self.graphicsView.working_file][self.graphicsView.img]['text'] = results
        data[self.graphicsView.working_file][self.graphicsView.img]['boxes'] = boxes
        with open(r'C:\Users\Миша\PycharmProjects\pythonProject4\database\data.json', 'w') as f:
            json.dump(data, f)

        companies = pd.read_excel(r'C:\Users\Миша\PycharmProjects\pythonProject4\companies.xlsx')
        a = pd.DataFrame(results, columns=['Companies'])
        a = pd.concat([companies, a])
        a = a.drop_duplicates()
        a.to_excel(r'C:\Users\Миша\PycharmProjects\pythonProject4\companies.xlsx', index=False)

    def process_work_dir(self):
        path=r'C:\Users\Миша\PycharmProjects\pythonProject4\working'
        with open(r'C:\Users\Миша\PycharmProjects\pythonProject4\boxes\key_res.json') as f:
            data = json.load(f)
        new_thread = process_work_dir(parent=self, data=data)
        new_thread.start()

    def make_mask(self):
        with open(os.path.join(r'C:\Users\Миша\PycharmProjects\pythonProject4\texts', self.working_file+'.json')) as f:
            data = json.load(f)
        n = {}
        for text in list(data.keys()):
            k = data[text].lower().count(self.category.lower())
            n[text] = k
        return n

    def closeEvent(self, event):
        d = {}
        d['page'] = self.img
        d['file'] = self.working_file
        d['category'] = self.category
        with open(r'C:\Users\Миша\PycharmProjects\pythonProject4\meta.json', 'w') as fp:
            json.dump(d, fp)
        close = QMessageBox()
        close.setText("You sure?")
        close.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        close = close.exec()

        if close == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


app = QApplication(sys.argv)
window = Example()
app.exec()
sys.exit()
