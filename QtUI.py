#This is part of Blather
# -- this code is licensed GPLv3
# Copyright 2013 Jezra
import sys
import gi
from gi.repository import GObject

# Qt stuff
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QVBoxLayout
from PyQt5.QtWidgets import QLabel, QPushButton, QCheckBox, QAction

from PyQt5.QtGui import QIcon

class UI(GObject.GObject):
	__gsignals__ = {
		'command' : (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_STRING,))
	}

	def __init__(self,args,continuous):
		self.continuous = continuous
		GObject.GObject.__init__(self)
		#start by making our app
		self.app = QApplication(args)
		#make a window
		self.window = QMainWindow()
		#give the window a name
		self.window.setWindowTitle("BlatherQt")
		self.window.setMaximumSize(400,200)
		center = QWidget()
		self.window.setCentralWidget(center)

		layout = QVBoxLayout()
		center.setLayout(layout)
		#make a listen/stop button
		self.listen_button = QPushButton("Listen")
		layout.addWidget(self.listen_button)
		#make a continuous button
		self.ccheckbox = QCheckBox("Continuous Listen")
		layout.addWidget(self.ccheckbox)

		#connect the buttons
		self.listen_button.clicked.connect(self.listen_button_clicked)
		self.ccheckbox.clicked.connect(self.ccheckbox_clicked)

		#add a label to the UI to display the last command
		self.label = QLabel()
		layout.addWidget(self.label)

		#add the actions for quiting
		quit_action = QAction(self.window)
		quit_action.setShortcut('Ctrl+Q')
		quit_action.triggered.connect(self.accel_quit)
		self.window.addAction(quit_action)

	def accel_quit(self):
		#emit the quit
		self.emit("command", "quit")

	def ccheckbox_clicked(self):
		checked = self.ccheckbox.isChecked()
		if checked:
			#disable listen_button
			self.listen_button.setEnabled(False)
			self.listen_button_stopped()
			self.emit('command', "continuous_listen")
			self.set_icon_active()
		else:
			self.listen_button.setEnabled(True)
			self.emit('command', "continuous_stop")
			self.set_icon_inactive()

	def listen_button_stopped(self):
		self.listen_button.setText("Listen")

	def listen_button_clicked(self):
		val = self.listen_button.text()
		if val == "Listen":
			self.emit("command", "listen")
			self.listen_button.setText("Stop")
			#clear the label
			self.label.setText("")
			self.set_icon_active()
		else:
			self.listen_button_stopped()
			self.emit("command", "stop")
			self.set_icon_inactive()

	def run(self):
		self.set_icon_inactive()
		self.window.show()
		if self.continuous:
			self.set_icon_active()
			self.ccheckbox.setCheckState(Qt.Checked)
			self.ccheckbox_clicked()
		self.app.exec_()
		self.emit("command", "quit")

	def finished(self, text):
		#if the continuous isn't pressed
		if not self.ccheckbox.isChecked():
			self.listen_button_stopped()
			self.set_icon_inactive()
		self.label.setText(text)

	def set_icon(self, icon):
		self.window.setWindowIcon(QIcon(icon))

	def set_icon_active_asset(self, i):
		self.icon_active = i

	def set_icon_inactive_asset(self, i):
		self.icon_inactive = i

	def set_icon_active(self):
		self.window.setWindowIcon(QIcon(self.icon_active))

	def set_icon_inactive(self):
		self.window.setWindowIcon(QIcon(self.icon_inactive))

