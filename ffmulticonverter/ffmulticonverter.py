#!/usr/bin/python
# -*- coding: utf-8 -*-
# Program: FF Multi Converter
# Purpose: GUI application to convert multiple file formats
#
# Copyright (C) 2011-2012 Ilias Stamatis <stamatis.iliass@gmail.com>
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
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals
from __init__ import __version__

from PyQt4.QtCore import (QSettings, QTimer, QLocale, QTranslator,
                  QT_VERSION_STR, PYQT_VERSION_STR)
from PyQt4.QtGui import (QApplication, QMainWindow, QWidget, QGridLayout,
                  QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QToolButton,
                  QCheckBox, QRadioButton, QPushButton, QTabWidget, QIcon,
                  QKeySequence, QFileDialog, QMessageBox)

import os
import sys
import platform
import tabs

import pyqttools
import preferences_dlg
import presets_dlgs

try:
    import PythonMagick
except ImportError:
    pass


class ValidationError(Exception): pass

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.home = os.getenv('HOME')
        self.fname = ''
        self.output = ''

        select_label = QLabel(self.tr('Select file:'))
        output_label = QLabel(self.tr('Output folder:'))
        self.fromLineEdit = QLineEdit()
        self.fromLineEdit.setReadOnly(True)
        self.toLineEdit = QLineEdit()
        self.toLineEdit.setReadOnly(True)
        self.fromToolButton = QToolButton()
        self.fromToolButton.setText('...')
        self.toToolButton = QToolButton()
        self.toToolButton.setText('...')
        grid1 = pyqttools.add_to_grid(QGridLayout(),
                        [select_label, self.fromLineEdit, self.fromToolButton],
                        [output_label, self.toLineEdit, self.toToolButton])

        self.audiovideo_tab = tabs.AudioVideoTab(self)
        self.image_tab = tabs.ImageTab(self)
        self.document_tab = tabs.DocumentTab(self)

        self.tabs = [self.audiovideo_tab, self.image_tab, self.document_tab]
        tab_names = [self.tr('Audio/Video'), self.tr('Images'),
                                                          self.tr('Documents')]
        self.TabWidget = QTabWidget()
        for num, tab in enumerate(tab_names):
            self.TabWidget.addTab(self.tabs[num], tab)
        self.TabWidget.setCurrentIndex(0)

        self.folderCheckBox = QCheckBox(self.tr(
                                          'Convert all files\nin this folder'))
        self.recursiveCheckBox = QCheckBox(self.tr(
                                                 'Convert files\nrecursively'))
        self.deleteCheckBox = QCheckBox(self.tr('Delete original'))
        layout1 = pyqttools.add_to_layout(QHBoxLayout(),self.folderCheckBox,
                             self.recursiveCheckBox, self.deleteCheckBox, None)

        self.typeRadioButton = QRadioButton(self.tr('Same type'))
        self.typeRadioButton.setEnabled(False)
        self.typeRadioButton.setChecked(True)
        self.extRadioButton = QRadioButton(self.tr('Same extension'))
        self.extRadioButton.setEnabled(False)
        layout2 = pyqttools.add_to_layout(QHBoxLayout(), self.typeRadioButton,
                                                     self.extRadioButton, None)
        layout3 = pyqttools.add_to_layout(QVBoxLayout(), layout1, layout2)

        self.convertPushButton = QPushButton(self.tr('&Convert'))
        layout4 = pyqttools.add_to_layout(QHBoxLayout(), None,
                                                        self.convertPushButton)
        final_layout = pyqttools.add_to_layout(QVBoxLayout(), grid1,
                                        self.TabWidget, layout3, None, layout4)

        self.statusBar = self.statusBar()
        self.dependenciesLabel = QLabel()
        self.statusBar.addPermanentWidget(self.dependenciesLabel, stretch=1)

        Widget = QWidget()
        Widget.setLayout(final_layout)
        self.setCentralWidget(Widget)

        c_act = pyqttools.create_action
        openAction = c_act(self, self.tr('Open'), QKeySequence.Open, None,
                                        self.tr('Open a file'), self.open_file)
        convertAction = c_act(self, self.tr('Convert'), 'Ctrl+C', None,
                               self.tr('Convert files'), self.start_conversion)
        quitAction = c_act(self, self.tr('Quit'), 'Ctrl+Q', None, self.tr(
                                                           'Quit'), self.close)
        presetsAction = c_act(self, self.tr('Edit Presets'), 'Ctrl+P', None,
                                         self.tr('Edit Presets'), self.presets)
        importAction = c_act(self, self.tr('Import'), None, None,
                                self.tr('Import presets'), self.import_presets)
        exportAction = c_act(self, self.tr('Export'), None, None,
                                self.tr('Export presets'), self.export_presets)

        clearAction = c_act(self, self.tr('Clear'), None, None,
                                             self.tr('Clear form'), self.clear)
        preferencesAction = c_act(self, self.tr('Preferences'), 'Alt+Ctrl+P',
                                None, self.tr('Preferences'), self.preferences)
        aboutAction = c_act(self, self.tr('About'), 'Ctrl+?', None,
                                                  self.tr('About'), self.about)

        fileMenu = self.menuBar().addMenu(self.tr('File'))
        editMenu = self.menuBar().addMenu(self.tr('Edit'))
        presetsMenu = editMenu.addMenu(self.tr('Presets'))
        helpMenu = self.menuBar().addMenu(self.tr('Help'))
        pyqttools.add_actions(fileMenu, [openAction, convertAction, None,
                                                                   quitAction])
        pyqttools.add_actions(presetsMenu, [presetsAction, importAction,
                                                                 exportAction])
        pyqttools.add_actions(editMenu, [clearAction, None, preferencesAction])
        pyqttools.add_actions(helpMenu, [aboutAction])


        self.TabWidget.currentChanged.connect(self.resize_window)
        self.TabWidget.currentChanged.connect(self.checkboxes_clicked)
        self.fromToolButton.clicked.connect(self.open_file)
        self.toToolButton.clicked.connect(self.open_dir)
        self.convertPushButton.clicked.connect(convertAction.triggered)
        self.folderCheckBox.clicked.connect(
                                     lambda: self.checkboxes_clicked('folder'))
        self.recursiveCheckBox.clicked.connect(
                                  lambda: self.checkboxes_clicked('recursive'))


        self.resize(660, 378)
        self.setWindowTitle('FF Multi Converter')

        QTimer.singleShot(0, self.check_for_dependencies)
        QTimer.singleShot(0, self.set_settings)

    def checkboxes_clicked(self, data=None):
        """Manages the behavior of checkboxes and radiobuttons.

        Keywords arguments:
        data -- a string to show from which CheckBox the signal emitted.
        """
        # data default value is None because the method can also be called
        # when TabWidget's tab change.
        if data == 'folder' and self.recursiveCheckBox.isChecked():
            self.recursiveCheckBox.setChecked(False)
        elif data == 'recursive' and self.folderCheckBox.isChecked():
            self.folderCheckBox.setChecked(False)

        enable = self.recursiveCheckBox.isChecked() or \
                                                self.folderCheckBox.isChecked()
        self.extRadioButton.setEnabled(enable)
        if enable and self.current_tab().name == 'Documents':
            # set typeRadioButton disabled when type == document files,
            # because it is not possible to convert every file format to any
            # other file format.
            self.typeRadioButton.setEnabled(False)
            self.extRadioButton.setChecked(True)
        else:
            self.typeRadioButton.setEnabled(enable)

    def clear(self):
        """Clears the form.

        Clears line edits and unchecks checkboxes and radio buttons.
        """
        self.fromLineEdit.clear()
        self.fname = ''
        if self.output is not None:
            self.toLineEdit.clear()
            self.output = ''
        boxes = [self.folderCheckBox, self.recursiveCheckBox,
                                                           self.deleteCheckBox]
        for box in boxes:
            box.setChecked(False)
        self.checkboxes_clicked()

        self.audiovideo_tab.clear()
        self.image_tab.clear()
        
    def resize_window(self):
        """Hides widgets of AudioVideo tab and resizes the window."""
        self.tabs[0].moreButton.setChecked(False)    
    
    def current_tab(self):
        """Returns current tab."""
        for i in self.tabs:
            if self.tabs.index(i) == self.TabWidget.currentIndex():
                return i       
                
    def set_settings(self):
        """Sets program settings"""
        settings = QSettings()
        self.saveto_output = settings.value('saveto_output').toBool()
        self.rebuild_structure = settings.value('rebuild_structure').toBool()
        self.overwrite_existing = settings.value('overwrite_existing').toBool()
        self.default_output = unicode(
                                   settings.value('default_output').toString())
        self.prefix = unicode(settings.value('prefix').toString())
        self.suffix = unicode(settings.value('suffix').toString())

        if self.saveto_output:
            if self.output is None or self.toLineEdit.text() == '':
                self.output = self.default_output
                self.toLineEdit.setText(self.output)
            self.toLineEdit.setEnabled(True)
        else:
            self.toLineEdit.setEnabled(False)
            self.toLineEdit.setText(self.tr(
                                           'Each file to its original folder'))
            self.output = None                

    def open_file(self):
        """Uses standard QtDialog to get file name."""
        all_files = '*'
        audiovideo_files = ' '.join(
                                 ['*.'+i for i in self.audiovideo_tab.formats])
        img_formats = self.image_tab.formats[:]
        img_formats.extend(self.image_tab.extra_img)
        image_files = ' '.join(['*.'+i for i in img_formats])
        document_files = ' '.join(['*.'+i for i in self.document_tab.formats])
        formats = [all_files, audiovideo_files, image_files, document_files]
        strings = [self.tr('All Files'), self.tr('Audio/Video Files'),
                   self.tr('Image Files'), self.tr('Document Files')]

        filters = ''
        for string, extensions in zip(strings, formats):
            filters += string + ' ({0});;'.format(extensions)
        filters = filters[:-2] # remove last ';;'

        fname = QFileDialog.getOpenFileName(self, 'FF Multi Converter - ' + \
                                    self.tr('Choose File'), self.home, filters)
        fname = unicode(fname)
        if fname:
            self.fname = fname
            self.fromLineEdit.setText(self.fname)

    def open_dir(self):
        """Uses standard QtDialog to get directory name."""
        if self.toLineEdit.isEnabled():
            output = QFileDialog.getExistingDirectory(self, 'FF Multi '
              'Converter - ' + self.tr('Choose output destination'), self.home)
            output = unicode(output)
            if output:
                self.output = output
                self.toLineEdit.setText(self.output)
        else:
            return QMessageBox.warning(self, 'FF Multi Converter - ' + \
                    self.tr('Save Location!'), self.tr(
                   'You have chosen to save every file to its original folder.'
                   '\nYou can change this from preferences.'))

    def preferences(self):
        """Opens the preferences dialog."""
        dialog = preferences_dlg.Preferences()
        if dialog.exec_():
            self.set_settings()

    def presets(self):
        dialog = presets_dlgs.ShowPresets()
        dialog.exec_()

    def import_presets(self):
        print 'import'

    def export_presets(self):
        print 'export'

    def ok_to_continue(self):
        """Checks if everything is ok to continue with conversion.

        Checks if:
        - Theres is no given file or no given output destination
        - Given file exists and output destination exists

        Returns: boolean
        """
        try:
            if self.fname == '':
                raise ValidationError(self.tr(
                                         'You must choose a file to convert!'))
            elif not os.path.exists(self.fname):
                raise ValidationError(self.tr(
                                         'The selected file does not exists!'))
            elif self.output is not None and self.output == '':
                raise ValidationError(self.tr(
                                          'You must choose an output folder!'))
            elif self.output is not None and not os.path.exists(self.output):
                raise ValidationError(self.tr(
                                             'Output folder does not exists!'))
            if not self.current_tab().ok_to_continue():
                return False
            return True

        except ValidationError as e:
            QMessageBox.warning(self, 'FF Multi Converter - ' + \
                                                 self.tr('Error!'), unicode(e))
            return False


    def start_conversion(self):
        if not self.ok_to_continue():
            return
        print 'CONVERT!!!'

    def about(self):
        """Shows an About dialog using qt standard dialog."""
        link = 'https://sites.google.com/site/ffmulticonverter/'
        msg = self.tr('Convert among several file types to other extensions')
        QMessageBox.about(self, self.tr('About') + ' FF Multi Converter',
            '''<b> FF Multi Converter {0} </b>
            <p>{1}
            <p><a href="{2}">FF Multi Converter - Home Page</a>
            <p>Copyright &copy; 2011-2012 Ilias Stamatis
            <br>License: GNU GPL3
            <p>Python {3} - Qt {4} - PyQt {5} on {6}'''
            .format(__version__, msg, link, platform.python_version()[:5],
            QT_VERSION_STR, PYQT_VERSION_STR, platform.system()))

    def is_installed(self, program):
        """Checks if program is installed."""
        for path in os.getenv('PATH').split(os.pathsep):
            fpath = os.path.join(path, program)
            if os.path.exists(fpath) and os.access(fpath, os.X_OK):
                return True
        return False

    def check_for_dependencies(self):
        """Checks if dependencies are installed and set dependenciesLabel
        status."""
        missing = []
        if self.is_installed('ffmpeg'):
            self.ffmpeg = True
        else:
            self.ffmpeg = False
            missing.append('FFmpeg')
        if self.is_installed('unoconv'):
            self.unoconv = True
        else:
            self.unoconv = False
            missing.append('unoconv')
        try:
            PythonMagick # PythonMagick has imported earlier
            self.pmagick = True
        except NameError:
            self.pmagick = False
            missing.append('PythonMagick')

        missing = ', '.join(missing) if missing else self.tr('None')
        status = self.tr('Missing dependencies:') + ' ' + missing
        self.dependenciesLabel.setText(status)


def main():
    app = QApplication(sys.argv)
    app.setOrganizationName('ffmulticonverter')
    app.setOrganizationDomain('sites.google.com/site/ffmulticonverter/')
    app.setApplicationName('FF Muli Converter')
    app.setWindowIcon(QIcon(':/ffmulticonverter.png'))

#    locale = QLocale.system().name()
#    qtTranslator = QTranslator()
#    if qtTranslator.load('qt_' + locale, ':/'):
#        app.installTranslator(qtTranslator)
#    appTranslator = QTranslator()
#    if appTranslator.load('ffmulticonverter_' + locale, ':/'):
#        app.installTranslator(appTranslator)

    converter = MainWindow()
    converter.show()
    app.exec_()

if __name__ == '__main__':
    main()
