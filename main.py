#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Created on Wed Feb 26 01:54:04 2020
# @author: Fernando Camussi
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

""" Main """

from blackboard import Blackboard, Mode
from counting_file import CountingFile
from segmentation import segmentation
from morphology import morphology
from rows_orientation import rows_orientation
from rotation import rotation
from descriptors import Descriptors
from model import Model
from counting import counting
from PyQt5.QtWidgets import (QApplication,
                             QMainWindow,
                             QHBoxLayout,
                             QWidget,
                             QLabel,
                             QFileDialog,
                             QScrollArea,
                             QAction,
                             QVBoxLayout,
                             QListWidget,
                             QPushButton,
                             QMessageBox,
                             QPlainTextEdit,
                             QInputDialog)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import (Qt,
                          pyqtSignal,
                          QRunnable,
                          QThreadPool,
                          QObject,
                          QDir)
import sys
import cv2 as cv


def getFileNameDialog(self, save_mode, filter, suffix=None):
    dialog = QFileDialog(self)
    dialog.setNameFilter(filter)
    dialog.setDirectory(QDir.currentPath())
    if save_mode:
        dialog.setWindowTitle('Guardar como')
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        if suffix is not None:
            dialog.setDefaultSuffix(suffix)
    else:
        dialog.setWindowTitle('Abrir')
        dialog.setFileMode(QFileDialog.ExistingFile)
    if dialog.exec_() == QFileDialog.Accepted:
        file = dialog.selectedFiles()[0]
    else:
        file = ""
    return file


def windowGeometry(window, width, height):
    r = app.screens()[0].availableGeometry()
    window.setGeometry(int((r.width()-width)/2), int((r.height()-height)/2),
                       width, height)


class Worker(QRunnable):

    class Signals(QObject):
        finished = pyqtSignal(object)

    def __init__(self, fun, *args):
        super().__init__()
        self.signals = self.Signals()
        self.fun = fun
        self.args = args

    def run(self):
        self.fun(*self.args)


class MainWindow(QMainWindow):

    PROG_NAME = 'Conteo de plantas de girasol'

    def __init__(self):
        super().__init__()
        self.initUI()
        self.show()
        self.counting_file = None

    def resizeEvent(self, event):
        [w,h] = [event.size().width(), event.size().height()]
        [lp_w,lp_h] = [300,100]
        self.label_processing.setGeometry(int((w-lp_w)/2), int((h-lp_h)/2),
                                          lp_w, lp_h)
        QMainWindow.resizeEvent(self, event)

    def initMenu(self):
        for menu in self.menu_list:
            menu.setEnabled(True)
        self.save_act.setEnabled(True)
        self.export_act.setEnabled(True)
        self.extr_descr_act.setEnabled(True)
        self.apply_model_act.setEnabled(True)
        self.mark_act.setChecked(False)
        self.ROI_act.setChecked(True)
        self.view_image_act.setChecked(True)
        self.view_mask_act.setChecked(False)

    def openFile(self):
        filter = 'Counting (*.counting)'
        file = getFileNameDialog(self, False, filter)
        if file:
            self.counting_file = CountingFile(file)
            self.image = CountingFile.cvImageToQPixmap(
                self.counting_file.getImage())
            points = self.counting_file.getPoints()
            self.blackboard.setImage(self.image)
            self.blackboard.setPoints(points)
            self.blackboard.mode = Mode.ROI
            self.initMenu()
            self.label_ppm.setText(str(self.counting_file.getPPM()))
            self.addInfoText('Se abrió el archivo %s.\n' % file)

    def saveFile(self):
        if self.counting_file.getFile() is None:
            filter = 'Counting (*.counting)'
            file = getFileNameDialog(self, True, filter, 'counting')
            if file:
                self.counting_file.setPoints(self.blackboard.getPoints())
                self.counting_file.saveFile(file)
                self.addInfoText('Se creó el archivo %s.\n' % file)
        else:
            self.counting_file.setPoints(self.blackboard.getPoints())
            self.counting_file.saveFile(self.counting_file.getFile())
            self.addInfoText('Se guardó el archivo %s.\n' %
                                 self.counting_file.getFile())

    def importImage(self):

        def fun(cv_image, ppm):
            cv_mask = segmentation(cv_image)
            cv_mask = morphology(cv_mask, ppm)
            orientation = rows_orientation(cv_mask)
            if orientation is None:
                cv_image = None
            else:
                cv_image = rotation(cv_image, -orientation)
                cv_mask = segmentation(cv_image)
                cv_mask = morphology(cv_mask, ppm)
            self.worker.signals.finished.emit((cv_image,cv_mask,
                                               orientation,ppm))

        def fun_finished(arg):
            (cv_image,cv_mask,orientation,ppm) = arg
            self.hideProcessingMsg()
            if cv_image is None:
                msg = QMessageBox()
                msg.setWindowTitle(self.PROG_NAME)
                msg.setText("Falló la detección de la orientación.")
                msg.exec_()
            else:
                self.counting_file = CountingFile()
                self.counting_file.setImage(cv_image)
                self.counting_file.setMask(cv_mask)
                self.counting_file.setPPM(ppm)
                self.image = CountingFile.cvImageToQPixmap(cv_image)
                self.blackboard.setImage(self.image)
                self.blackboard.mode = Mode.ROI
                self.blackboard.setPoints([])
                self.initMenu()
                self.label_ppm.setText(str(self.counting_file.getPPM()))
                self.addInfoText('Se importó la imagen %s' % image_file)
                self.addInfoText('La imagen se rotó %.2f grados.\n' %
                                     -orientation)

        filter = 'Imágenes (*.jpeg *.jpg *.png *.tif *.tiff)'
        image_file = getFileNameDialog(self, False, filter)
        if image_file:
            ppm,ok = QInputDialog.getInt(self,
                                         self.PROG_NAME,
                                         'Ingrese pixeles por metro',
                                         1, 1)
            if ok:
                cv_image = cv.imread(image_file, cv.IMREAD_COLOR)
                if not CountingFile.isRGB(cv_image):
                    msg = QMessageBox()
                    msg.setWindowTitle(self.PROG_NAME)
                    msg.setText("La imagen no es RGB.")
                    msg.exec_()
                else:
                    self.showProcessingMsg()
                    self.worker = Worker(fun, cv_image, ppm)
                    self.threadpool = QThreadPool()
                    self.worker.signals.finished.connect(fun_finished)
                    self.threadpool.start(self.worker)

    def exportImage(self):
        filter = 'Imágenes PNG (*.png)'
        image_file = getFileNameDialog(self, True, filter, 'png')
        if image_file:
            self.blackboard.getPixmap().save(image_file)

    def zoomIn(self):
        self.blackboard.zoomIn()

    def zoomOut(self):
        self.blackboard.zoomOut()

    def mark(self):
        if self.mark_act.isChecked():
            self.blackboard.mode = Mode.MARKER
            self.ROI_act.setChecked(False)
        else:
            self.mark_act.setChecked(True)

    def ROI(self):
        if self.ROI_act.isChecked():
            self.blackboard.mode = Mode.ROI
            self.mark_act.setChecked(False)
        else:
            self.ROI_act.setChecked(True)

    def viewImage(self):
        if self.view_image_act.isChecked():
            self.image = CountingFile.cvImageToQPixmap(
                self.counting_file.getImage())
            self.blackboard.changeImage(self.image)
            self.view_mask_act.setChecked(False)
        else:
            self.view_image_act.setChecked(True)

    def viewMask(self):
        if self.view_mask_act.isChecked():
            self.image = CountingFile.cvImageToQPixmap(
                self.counting_file.getMask())
            self.blackboard.changeImage(self.image)
            self.view_image_act.setChecked(False)
        else:
            self.view_mask_act.setChecked(True)

    def extractDescriptors(self):

        def fun(descr_file, ppm):
            cv_mask = self.counting_file.getMask()
            contours,_ = cv.findContours(cv_mask, cv.RETR_EXTERNAL,
                                         cv.CHAIN_APPROX_NONE)
            descr_df = Descriptors.compute(contours, ppm,
                                           self.blackboard.getPoints())
            self.worker.signals.finished.emit((descr_file,descr_df))

        def fun_finished(arg):
            (descr_file,descr_df) = arg
            Descriptors.save(descr_file, descr_df)
            self.hideProcessingMsg()
            self.addInfoText('Se creó el archivo de descriptores %s.\n' %
                                 descr_file)

        if not self.blackboard.getPoints():
            msg = QMessageBox()
            msg.setWindowTitle(self.PROG_NAME)
            msg.setText("No hay puntos marcados.")
            msg.exec_()
            return

        filter = 'Descriptores (*.csv)'
        descr_file = getFileNameDialog(self, True, filter, "csv")
        if descr_file:
            self.showProcessingMsg()
            self.worker = Worker(fun, descr_file, self.counting_file.getPPM())
            self.threadpool = QThreadPool()
            self.worker.signals.finished.connect(fun_finished)
            self.threadpool.start(self.worker)

    def generateModel(self):
        model_window.show()

    def applyModel(self):

        def fun(model_file, ppm):
            mask = self.counting_file.getMask()
            args = counting(mask, model_file, ppm)
            self.worker.signals.finished.emit(args)

        def fun_finished(args):
            total_plants,rects,total_rows,lines = args
            self.hideProcessingMsg()
            self.blackboard.addLines(lines)
            self.addInfoText('Se aplicó el modelo %s.' % model_file)
            self.addInfoText('Cantidad de hileras: %d' % total_rows)
            self.blackboard.addRectangles(rects)
            self.addInfoText('Cantidad de grupos: %d' % len(rects))
            self.addInfoText('Cantidad de plantas: %d\n' % total_plants)

        filter = 'Imágenes (*.model)'
        model_file = getFileNameDialog(self, False, filter)
        if model_file:
            self.showProcessingMsg()
            self.worker = Worker(fun, model_file, self.counting_file.getPPM())
            self.threadpool = QThreadPool()
            self.worker.signals.finished.connect(fun_finished)
            self.threadpool.start(self.worker)

    def ROIselected(self, ROI, points):
        self.ROI = ROI
        p1 = ROI.topLeft()
        points = list(map(lambda p: p - p1, points)) # resto top-left
        ROI_window.blackboard.setImage(self.image.copy(ROI))
        ROI_window.blackboard.setPoints(points)
        ROI_window.show()

    def pointsMarked(self, n_points):
        self.label_points.setText(str(n_points))

    def ROIwindowClosed(self, points, cropped):
        if cropped:
            [x,y,w,h] = self.ROI.getRect()
            cv_image = self.counting_file.getImage()
            cv_mask = self.counting_file.getMask()
            cv_image = cv_image[y:y+h,x:x+w]
            cv_mask = segmentation(cv_image)
            ppm = self.counting_file.getPPM()
            cv_mask = morphology(cv_mask, ppm)
            self.counting_file = CountingFile()
            self.counting_file.setImage(cv_image)
            self.counting_file.setMask(cv_mask)
            self.counting_file.setPPM(ppm)
            if self.view_mask_act.isChecked():
                self.image = CountingFile.cvImageToQPixmap(cv_mask)
            else:
                self.image = CountingFile.cvImageToQPixmap(cv_image)
            self.blackboard.setImage(self.image)
            self.blackboard.setPoints([])
            self.ROI.setX(0)
            self.ROI.setY(0)
        p1 = self.ROI.topLeft()
        points = list(map(lambda p: p + p1, points)) # sumo top-left
        points2 = self.blackboard.getPoints()
        old_ROI_points = list(filter(self.ROI.contains, points2))
        for p in old_ROI_points:
            points2.remove(p)
        points2.extend(points)
        self.blackboard.setPoints(points2)

    def showProcessingMsg(self):
        self.blackboard.setEnabled(False)
        self.menu_list_enabled = []
        for menu in self.menu_list:
            self.menu_list_enabled.append(menu.isEnabled())
            menu.setEnabled(False)
        self.label_processing.setVisible(True)

    def hideProcessingMsg(self):
        self.blackboard.setEnabled(True)
        for menu,menu_enabled in zip(self.menu_list,self.menu_list_enabled):
            menu.setEnabled(menu_enabled)
        self.label_processing.setVisible(False)

    def addInfoText(self, text):
        self.text_info.appendPlainText(text)

    def initUI(self):
        # Barra de menu
        menubar = self.menuBar()
        self.menu_list = []
        self.file_menu = menubar.addMenu('Fichero')
        self.menu_list.append(self.file_menu)
        load_act = QAction('Abrir...', self)
        load_act.triggered.connect(self.openFile)
        self.file_menu.addAction(load_act)
        self.save_act = QAction('Guardar', self)
        self.save_act.setShortcut('Ctrl+S')
        self.save_act.triggered.connect(self.saveFile)
        self.save_act.setEnabled(False)
        self.file_menu.addAction(self.save_act)
        self.import_act = QAction('Importar imagen...', self)
        self.import_act.triggered.connect(self.importImage)
        self.file_menu.addAction(self.import_act)
        self.export_act = QAction('Exportar imagen...', self)
        self.export_act.triggered.connect(self.exportImage)
        self.export_act.setEnabled(False)
        self.file_menu.addAction(self.export_act)
        exit_act = QAction('Salir', self)
        exit_act.setShortcut('Ctrl+E')
        exit_act.triggered.connect(self.close)
        self.file_menu.addAction(exit_act)
        self.view_menu = menubar.addMenu('Ver')
        self.menu_list.append(self.view_menu)
        self.view_menu.setEnabled(False)
        zoom_in_act = QAction('Ampliar', self)
        zoom_in_act.setShortcut('Ctrl++')
        zoom_in_act.triggered.connect(self.zoomIn)
        self.view_menu.addAction(zoom_in_act)
        zoom_out_act = QAction('Reducir', self)
        zoom_out_act.setShortcut('Ctrl+-')
        zoom_out_act.triggered.connect(self.zoomOut)
        self.view_menu.addAction(zoom_out_act)
        self.view_menu.addSeparator()
        self.view_image_act = QAction('Imagen', self, checkable=True)
        self.view_image_act.triggered.connect(self.viewImage)
        self.view_mask_act = QAction('Máscara', self, checkable=True)
        self.view_mask_act.triggered.connect(self.viewMask)
        self.view_menu.addAction(self.view_image_act)
        self.view_menu.addAction(self.view_mask_act)
        self.mode_menu = menubar.addMenu('Modo')
        self.menu_list.append(self.mode_menu)
        self.mode_menu.setEnabled(False)
        self.mark_act = QAction('Marcar', self, checkable=True)
        self.mark_act.setShortcut('Ctrl+M')
        self.mark_act.triggered.connect(self.mark)
        self.ROI_act = QAction('ROI', self, checkable=True)
        self.ROI_act.setShortcut('Ctrl+R')
        self.ROI_act.triggered.connect(self.ROI)
        self.mode_menu.addAction(self.mark_act)
        self.mode_menu.addAction(self.ROI_act)
        prediction_menu = menubar.addMenu('Predicción')
        self.menu_list.append(prediction_menu)
        self.extr_descr_act = QAction('Extraer descriptores...', self)
        self.extr_descr_act.triggered.connect(self.extractDescriptors)
        self.extr_descr_act.setEnabled(False)
        prediction_menu.addAction(self.extr_descr_act)
        gen_model_act = QAction('Generar modelo...', self)
        gen_model_act.triggered.connect(self.generateModel)
        prediction_menu.addAction(gen_model_act)
        self.apply_model_act = QAction('Aplicar modelo...', self)
        self.apply_model_act.triggered.connect(self.applyModel)
        self.apply_model_act.setEnabled(False)
        prediction_menu.addAction(self.apply_model_act)

        # Resto de la ventana
        self.setWindowTitle(self.PROG_NAME)
        self.blackboard = Blackboard()
        self.blackboard.ROI_selected.connect(self.ROIselected)
        self.blackboard.points_marked.connect(self.pointsMarked)
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.blackboard)
        self.label_points_text = QLabel("| puntos: ")
        self.label_points = QLabel()
        self.label_ppm_text = QLabel("| ppm: ")
        self.label_ppm = QLabel()
        self.statusBar().addPermanentWidget(self.label_ppm_text, 0)
        self.statusBar().addPermanentWidget(self.label_ppm, 0)
        self.statusBar().addPermanentWidget(self.label_points_text, 0)
        self.statusBar().addPermanentWidget(self.label_points, 0)
        widget = QWidget()
        self.setCentralWidget(widget)
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll_area)
        self.text_info = QPlainTextEdit()
        self.text_info.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.text_info.setFixedWidth(200)
        layout.addWidget(self.text_info)
        self.label_processing = QLabel(widget)
        self.label_processing.setText("Procesando")
        self.label_processing.setFont(QFont("Times", 24, QFont.Bold))
        self.label_processing.setAlignment(Qt.AlignCenter)
        self.label_processing.setStyleSheet("border: 3px solid black; " +
                                            "background-color: lightgray;")
        self.label_processing.setVisible(False)
        windowGeometry(self, 1000, 800)


class ROIwindow(QMainWindow):

    ROI_closed = pyqtSignal(list, bool)

    def __init__(self):
        super().__init__()
        self.initUI()
        self.cropped = False

    def closeEvent(self, event):
        self.ROI_closed.emit(self.blackboard.getPoints(), self.cropped)
        self.cropped = False

    def zoomIn(self):
        self.blackboard.zoomIn()

    def zoomOut(self):
        self.blackboard.zoomOut()

    def removeMarks(self):
        self.blackboard.setPoints([])

    def cropROI(self):
        self.cropped = True
        self.close()

    def initUI(self):
        # Barra de menu
        menubar = self.menuBar()
        view_menu = menubar.addMenu('Ver')
        zoom_in_act = QAction('Ampliar', self)
        zoom_in_act.setShortcut('Ctrl++')
        zoom_in_act.triggered.connect(self.zoomIn)
        view_menu.addAction(zoom_in_act)
        zoom_out_act = QAction('Reducir', self)
        zoom_out_act.setShortcut('Ctrl+-')
        zoom_out_act.triggered.connect(self.zoomOut)
        view_menu.addAction(zoom_out_act)
        remove_menu = menubar.addMenu('Borrar')
        remove_marks_act = QAction('Borrar marcas', self)
        remove_marks_act.setShortcut('Ctrl+B')
        remove_marks_act.triggered.connect(self.removeMarks)
        remove_menu.addAction(remove_marks_act)
        crop_menu = menubar.addMenu('Cortar')
        crop_ROI_act = QAction('Cortar ROI', self)
        crop_ROI_act.triggered.connect(self.cropROI)
        crop_menu.addAction(crop_ROI_act)

        # Resto de la ventana
        self.setWindowTitle('ROI')
        self.setWindowModality(Qt.ApplicationModal)
        self.blackboard = Blackboard()
        self.blackboard.mode = Mode.MARKER
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.blackboard)
        self.setCentralWidget(scroll_area)
        windowGeometry(self, 600, 600)


class ModelWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()
        #self.show()

    def showEvent(self, event):
        self.list_widget.clear()
        QMainWindow.showEvent(self, event)

    def addButtonClicked(self):
        filter = 'CSV (*.csv)'
        descr_file = getFileNameDialog(self, False, filter)
        if descr_file:
            if not self.list_widget.findItems(descr_file,
                                              Qt.MatchFixedString |
                                              Qt.MatchCaseSensitive):
                self.list_widget.addItem(descr_file)

    def removeButtonClicked(self):
        row = self.list_widget.currentRow()
        if row > -1:
            self.list_widget.takeItem(row)

    def generateButtonClicked(self):
        if self.list_widget.count() > 0:
            filter = 'Model (*.model)'
            file = getFileNameDialog(self, True, filter, 'model')
            if file:
                descr_files = [self.list_widget.item(row).text()
                               for row in range(self.list_widget.count())]
                descr_list = Descriptors.load(descr_files)
                model,info = Model.generate(descr_list)
                Model.save(file, model)
                main_window.addInfoText('Se creó el archivo de modelo %s.' %
                                            file)
                main_window.addInfoText('R^2: %.2f\n' % info['R2'])

    def initUI(self):
        self.setWindowTitle('Modelo')
        self.setWindowModality(Qt.ApplicationModal)
        widget = QWidget()
        self.setCentralWidget(widget)
        layout = QVBoxLayout(widget)
        self.list_widget = QListWidget()
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.list_widget)
        label = QLabel("Ficheros descriptores:")
        label.adjustSize()
        add_button = QPushButton("Agregar")
        remove_button = QPushButton("Remover")
        generate_button = QPushButton("Generar modelo")
        layout.addWidget(label)
        layout.addWidget(scroll_area)
        layout.addWidget(add_button)
        add_button.clicked.connect(self.addButtonClicked)
        layout.addWidget(remove_button)
        remove_button.clicked.connect(self.removeButtonClicked)
        layout.addWidget(generate_button)
        generate_button.clicked.connect(self.generateButtonClicked)
        windowGeometry(self, 600, 600)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    ROI_window = ROIwindow()
    ROI_window.ROI_closed.connect(main_window.ROIwindowClosed)
    model_window = ModelWindow()
    sys.exit(app.exec_())
