import folium
import geopy
import joblib
import linecache
import os
import pandas as pd
import paths
import requests
import shutil
import sys
import tensorflow as tf
import time

# used by mainw.ui
import resources
from PyQt6 import QtWebEngineWidgets

from crypt import decrypt, encrypt
from geopy.extra.rate_limiter import RateLimiter
from html2image import html2image
from instagrapi.exceptions import ChallengeError, ClientError
from maps import LocoutMaps
from OSMPythonTools.overpass import Overpass
from paths import cl, DUMP_JSON, HND_BLACK, HND_BOLD, HND_LIGHT, HND_REG, KEY, MAP, MAP_HTML, MAP_PNG, USER_JSON, \
    MAINW, LOGIN, JOB, MODEL
from PyQt6 import QtCore, QtWidgets, uic
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor, QFont, QIcon, QMovie, QPalette, QColor
from scrape import location_data, user_posts
from sklearn.tree import DecisionTreeClassifier


class Login(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.dragPos = None
        self.password = None
        self.username = None
        self.MainWindow = None
        self.splashM = QMovie(':/Resource/img/loading.gif')
        self.timer = QtCore.QTimer(self)
        self.setWindowIcon(QIcon(':/Resource/img/nigelico.png'))
        uic.loadUi(LOGIN, self)
        self.login_text.setFont(QFont(HND_BLACK, 24))
        self.label_username.setFont(QFont(HND_LIGHT, 24))
        self.label_password.setFont(QFont(HND_LIGHT, 24))
        self.frame.hide()
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.WindowMinMaxButtonsHint |
                            QtCore.Qt.WindowType.WindowCloseButtonHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.Splash()

    def Splash(self):
        self.splashM.start()
        self.timer.singleShot(3000, self.Splash_trans)
        self.loading.setMovie(self.splashM)
        self.loading.setScaledContents(True)

    def Splash_trans(self):
        self.splash_frame.hide()
        self.splashM.stop()
        self.timer.stop()
        decrypt()
        try:
            if os.path.exists(DUMP_JSON and USER_JSON):
                cl.delay_range = [1, 3]
                username = linecache.getline(USER_JSON, 1).rstrip('\n')
                password = linecache.getline(USER_JSON, 2)
                paths.USERNAME = username
                paths.PASSWORD = password
                encrypt()
                self.MainWindow = Recognizance()
                # noinspection PyTypeChecker
                cl.load_settings(DUMP_JSON)
                cl.login(username, password)
                cl.get_timeline_feed()
                self.MainWindow.show()
                self.hide()
            else:
                self.frame.show()
                self.initUI()

        except ClientError as e:
            QtWidgets.QMessageBox.information(self, 'Login', f"Instagram has logged you out due to API limitations. It"
                                                             f" is recommended to log in again only after a few minutes"
                                                             f" to avoid being flagged. ({e})")
            if os.path.exists(USER_JSON):
                os.remove(USER_JSON)
                os.remove(DUMP_JSON)
                os.remove(KEY)
            self.close()
            sys.exit(0)

    def toggle_pass(self):
        if self.lineedit_password.echoMode() == QtWidgets.QLineEdit.EchoMode.Password:
            self.lineedit_password.setEchoMode(QtWidgets.QLineEdit.EchoMode.Normal)
            self.show_pw.setStyleSheet('QToolButton { '
                                       'border-image:url(:/Resource/img/eye_open.png);'
                                       '}'
                                       'QToolButton:hover { '
                                       'border-image:url(:/Resource/img/eye_close.png);'
                                       '}'
                                       'QToolButton:pressed {'
                                       'border-image:url(:/Resource/img/eye_close.png);'
                                       '}')
        else:
            self.lineedit_password.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
            self.show_pw.setStyleSheet('QToolButton { '
                                       'border-image:url(:/Resource/img/eye_close.png);'
                                       '}'
                                       'QToolButton:hover { '
                                       'border-image:url(:/Resource/img/eye_open.png);'
                                       '}'
                                       'QToolButton:pressed {'
                                       'border-image:url(:/Resource/img/eye_open.png);'
                                       '}')

    def initUI(self):
        if os.path.exists(USER_JSON):
            os.remove(USER_JSON)
            os.remove(DUMP_JSON)
            os.remove(KEY)
        self.lineedit_password.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.close_butt.clicked.connect(self.Close_app)
        self.min_butt.clicked.connect(self.showMinimized)
        self.button_login.clicked.connect(self.login)
        self.button_login.setShortcut('Return')
        self.show_pw.clicked.connect(self.toggle_pass)
        vbox = QtWidgets.QVBoxLayout()
        self.setLayout(vbox)

    def Close_app(self):
        if os.path.exists(MAP_PNG):
            os.remove(MAP_PNG)
        if os.path.exists(MAP_HTML):
            os.remove(MAP_HTML)
        if os.path.exists('cache'):
            shutil.rmtree('cache')
        self.close()
        sys.exit(0)

    def mousePressEvent(self, event):
        if event.buttons() == QtCore.Qt.MouseButton.LeftButton:
            self.dragPos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if hasattr(self, 'dragPos'):
            if event.buttons() & QtCore.Qt.MouseButton.LeftButton:
                self.move(self.pos() + event.globalPosition().toPoint() - self.dragPos)
                self.dragPos = event.globalPosition().toPoint()
                event.accept()

    def manual_input_code(self, username: str, choice=None):
        code = None
        while True:
            code = QtWidgets.QInputDialog.getText(self, "Login", f"Enter code (6 digits) for "
                                                                 f"{self.username} ({choice}): ",
                                                  QtWidgets.QLineEdit.EchoMode.Normal)[0]
            if code and code.isdigit():
                break
        return code

    def login(self):
        self.username = self.lineedit_username.text()
        self.password = self.lineedit_password.text()

        cl.delay_range = [1, 3]
        cl.challenge_code_handler = self.manual_input_code

        paths.USERNAME = self.username
        paths.PASSWORD = self.password

        try:
            cl.login(self.username, self.password)

        except ClientError:
            if self.username == '' or self.password == '':
                QtWidgets.QMessageBox.information(self, 'Login', 'Please enter both username and password!')
            else:
                QtWidgets.QMessageBox.information(self, 'Login', 'Instagram error: Resolve by logging in to Instagram'
                                                                 ' on your browser or on the mobile app.')
        except ChallengeError:
            QtWidgets.QMessageBox.information(self, 'Login', 'Your account requires additional verification, resolve'
                                                             'this by logging in to the Instagram site on your'
                                                             'browser or on the mobile app.')
        except requests.HTTPError as e:
            if e.response.status_code == 429:
                time.sleep(int(e.response.headers['Retry-After']))

        else:
            # noinspection PyTypeChecker
            cl.dump_settings(DUMP_JSON)
            f = open(USER_JSON, 'w')
            f.write(self.username + '\n')
            f.write(self.password)
            f.close()
            encrypt()
            self.MainWindow = Recognizance()
            self.MainWindow.show()
            self.hide()


class Recognizance(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon(':/Resource/img/nigelico.png'))
        self.blister = None
        self.businesslist = None
        self.loci = None
        self.geocode = None
        self.locations = None
        self.lat = None
        self.location = None
        self.lng = None
        self.userlist2 = None
        self.userlist1 = None
        self.check = None
        self.radius = None
        self.map = None
        self.data = None
        self.chc = None
        self.locs = None
        self.geolocator = None
        self.geocoder_result = None
        self.amen = None
        self.login = None
        self.dragPos = None
        self.trans = QMovie(':/Resource/img/input_trans.webp')
        self.timer = QtCore.QTimer(self)
        self.backy = QMovie(':/Resource/img/back_trans.webp')
        self.dashy = QMovie(':/Resource/img/dashy.gif')
        self.outy = QMovie(':/Resource/img/output_trans.webp')
        self.bouty = QMovie(':/Resource/img/outback_trans.webp')
        self.inputty = QMovie(':/Resource/img/inputty.gif')
        self.outin = QMovie(':/Resource/img/outin.gif')
        uic.loadUi(MAINW, self)
        self.start_butt.setFont(QFont(HND_BLACK, 72))
        self.welcome.setFont(QFont(HND_REG, 20))
        self.label.setFont(QFont(HND_BLACK, 48))
        if os.path.exists(USER_JSON and KEY):
            decrypt()
            username = linecache.getline(USER_JSON, 1).rstrip('\n')
            self.welcome.setText(f"Welcome, {username}!")
            encrypt()
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.WindowMinMaxButtonsHint |
                            QtCore.Qt.WindowType.WindowCloseButtonHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.centralwidget.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.mainframe.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAutoFillBackground(True)
        self.dash_wid.hide()
        self.prodframe.hide()
        self.locframe.hide()
        self.netframe.hide()
        self.mainframe.show()
        self.start_wid.show()
        self.start_butt.setShortcut('Return')
        self.start_butt.clicked.connect(self.Dashboard)
        self.close_butt.clicked.connect(self.Close_app)
        self.min_butt.clicked.connect(self.showMinimized)
        self.button_logout.clicked.connect(self.Logout)

    def Dashboard(self):
        self.backy.stop()
        self.start_wid.hide()
        self.prodframe.hide()
        self.locframe.hide()
        self.netframe.hide()
        self.transition.hide()
        self.dash_no.setFont(QFont(HND_BLACK, 48))
        self.dash_title.setFont(QFont(HND_BOLD, 30))
        self.locbutt.setFont(QFont(HND_BLACK, 16))
        self.netbutt.setFont(QFont(HND_BLACK, 16))
        self.back_butt.setFont(QFont(HND_BLACK, 30))
        self.dash_close.clicked.connect(self.Close_app)
        self.dash_min.clicked.connect(self.showMinimized)
        self.back_butt.clicked.connect(self.Back)
        self.dashy.start()
        self.dash_graphic.setMovie(self.dashy)
        self.dash_graphic.setScaledContents(True)
        self.locbutt.clicked.connect(self.locIn_trans)
        self.netbutt.clicked.connect(self.netIn_trans)
        self.mainframe.show()
        self.dash_wid.show()

    def Input(self):
        self.trans.stop()
        self.bouty.stop()
        self.timer.stop()
        self.output_wid.hide()
        self.mainframe.hide()
        self.locframe.hide()
        self.prodframe.show()
        self.input_wid.show()
        self.input_title.setFont(QFont(HND_BOLD, 30))
        self.input_HT.setFont(QFont(HND_BLACK, 30))
        self.input_no.setFont(QFont(HND_BLACK, 48))
        self.input_no_2.setFont(QFont(HND_BLACK, 48))
        self.input_prodbutt.setFont(QFont(HND_BLACK, 16))
        self.back_butt_3.setFont(QFont(HND_BLACK, 30))
        self.next_butt.setFont(QFont(HND_BLACK, 30))
        self.inputty.start()
        self.input_graphic.setMovie(self.inputty)
        self.input_graphic.setScaledContents(True)
        self.next_butt.setShortcut('Return')
        self.input_close.clicked.connect(self.Close_app)
        self.input_min.clicked.connect(self.showMinimized)
        self.back_butt_3.clicked.connect(self.toDash_trans)
        self.next_butt.clicked.connect(self.toOutput_trans)
        self.transition.hide()
        self.out_transition.hide()
        self.back_transition.hide()
        self.to_outtrans.hide()

    def locInput(self):
        self.process.lower()
        self.trans.stop()
        self.bouty.stop()
        self.timer.stop()
        self.locin_outtrans.hide()
        self.locback_trans.hide()
        self.dash_wid.hide()
        self.mainframe.hide()
        self.prodframe.hide()
        self.netframe.hide()
        self.locframe.show()
        self.locin_wid.show()
        self.locin_title.setFont(QFont(HND_BOLD, 20))
        self.locin_title_2.setFont(QFont(HND_BOLD, 20))
        self.locin_title_3.setFont(QFont(HND_BOLD, 20))
        self.locin_no1.setFont(QFont(HND_BLACK, 48))
        self.locin_no2.setFont(QFont(HND_BLACK, 48))
        self.locin_locbutt.setFont(QFont(HND_BLACK, 16))
        self.locin_text.setFont(QFont(HND_LIGHT, 12))
        self.locin_combo.setFont(QFont(HND_LIGHT, 16))
        self.locin_backbutt.setFont(QFont(HND_BLACK, 30))
        self.locin_nextbutt.setFont(QFont(HND_BLACK, 30))
        self.locin_nextbutt.setEnabled(False)
        self.locin_combo.currentIndexChanged[int].connect(self.onComboIndexChanged)
        self.locin_radius.valueChanged.connect(self.onRadiusChanged)
        self.inputty.start()
        self.locin_graphic.setMovie(self.inputty)
        self.locin_graphic.setScaledContents(True)
        self.locin_nextbutt.setShortcut('Return')
        self.locin_close.clicked.connect(self.Close_app)
        self.locin_min.clicked.connect(self.showMinimized)
        self.locin_backbutt.clicked.connect(self.locDash_trans)
        self.locin_nextbutt.clicked.connect(self.raise_process)
        self.locback_trans.hide()
        self.locin_outtrans.hide()

    def onRadiusChanged(self):
        value = self.locin_radius.value()
        self.locin_title_3.setText(f"Radius: {value}m")

    def raise_process(self):
        self.process.raise_()
        self.timer = QtCore.QTimer(self)
        self.timer.singleShot(1000, self.locOutput_trans)

    def netInput(self):
        self.n_process.lower()
        self.trans.stop()
        self.bouty.stop()
        self.timer.stop()
        self.transition.hide()
        self.netin_outtrans.hide()
        self.netin_backtrans.hide()
        self.netout_wid.hide()
        self.dash_wid.hide()
        self.mainframe.hide()
        self.prodframe.hide()
        self.locframe.hide()
        self.netframe.show()
        self.netin_wid.show()
        self.netin_title.setFont(QFont(HND_BOLD, 30))
        self.netin_no1.setFont(QFont(HND_BLACK, 48))
        self.netin_no2.setFont(QFont(HND_BLACK, 48))
        self.netin_netbutt.setFont(QFont(HND_BLACK, 16))
        self.netin_text.setFont(QFont(HND_LIGHT, 12))
        self.netin_backbutt.setFont(QFont(HND_BLACK, 30))
        self.netin_nextbutt.setFont(QFont(HND_BLACK, 30))
        self.netin_nextbutt.setEnabled(False)
        self.netin_text.textChanged[str].connect(lambda:
                                                 self.netin_nextbutt.setEnabled(True) if self.netin_text.text() != ""
                                                 else self.netin_nextbutt.setEnabled(False))
        self.inputty.start()
        self.netin_graphic.setMovie(self.inputty)
        self.netin_graphic.setScaledContents(True)
        self.netin_nextbutt.setShortcut('Return')
        self.netin_close.clicked.connect(self.Close_app)
        self.netin_min.clicked.connect(self.showMinimized)
        self.netin_backbutt.clicked.connect(self.netDash_trans)
        self.netin_nextbutt.clicked.connect(self.raise_netprocess)

    def raise_netprocess(self):
        self.n_process.raise_()
        self.timer = QtCore.QTimer(self)
        self.timer.singleShot(1000, self.netOutput_trans)

    def Output(self):
        self.outy.stop()
        self.timer.stop()
        self.back_transition.hide()
        self.output_wid.show()
        self.input_wid.hide()
        self.out_no_1.setFont(QFont(HND_BLACK, 48))
        self.out_no_2.setFont(QFont(HND_BLACK, 48))
        self.out_prodbutt.setFont(QFont(HND_BLACK, 16))
        self.analysis_title.setFont(QFont(HND_BOLD, 30))
        self.rec_title.setFont(QFont(HND_BOLD, 30))
        self.outback_butt.setFont(QFont(HND_BLACK, 30))
        self.out_next_butt.setFont(QFont(HND_BLACK, 30))
        self.outin.start()
        self.out_graphic.setMovie(self.outin)
        self.out_graphic.setScaledContents(True)
        self.input_txt.setFont(QFont(HND_BLACK, 25))
        hashtag = self.input_text.text()
        self.input_txt.setText(f"#{hashtag}")
        self.outback_butt.clicked.connect(self.Outback_trans)
        self.out_next_butt.clicked.connect(self.BackMain)
        self.out_close.clicked.connect(self.Close_app)
        self.out_min.clicked.connect(self.showMinimized)
        self.out_transition.hide()

    def locOutput(self):
        self.outy.stop()
        self.timer.stop()
        self.locback_trans.hide()
        self.locout_wid.show()
        self.locin_wid.hide()
        self.locout_type.setFont(QFont(HND_LIGHT, 20))
        self.locout_locy.setFont(QFont(HND_LIGHT, 20))
        self.locout_tit1.setFont(QFont(HND_BOLD, 30))
        self.locout_tit2.setFont(QFont(HND_BOLD, 30))
        self.locout_locy.setText(f"{self.locin_text.text()}")
        self.locout_type.setText(self.locin_combo.currentText())
        self.locout_no1.setFont(QFont(HND_BLACK, 48))
        self.locout_no2.setFont(QFont(HND_BLACK, 48))
        self.locout_locbutt.setFont(QFont(HND_BLACK, 16))
        self.locout_rec.setFont(QFont(HND_BOLD, 30))
        self.locout_backbutt.setFont(QFont(HND_BLACK, 30))
        self.locout_nextbutt.setFont(QFont(HND_BLACK, 30))
        self.locout_map.setStyleSheet(f"background-image: url({MAP_PNG});"
                                      " background-position: center; border: none;")
        self.locout_map.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.locout_map.clicked.connect(self.ShowMap)
        self.outin.start()
        self.locout_graphic.setMovie(self.outin)
        self.locout_graphic.setScaledContents(True)
        self.locout_backbutt.clicked.connect(self.locOutback_trans)
        self.locout_nextbutt.clicked.connect(self.BackMain)
        self.locout_close.clicked.connect(self.Close_app)
        self.locout_min.clicked.connect(self.showMinimized)
        self.locout_trans.hide()

    def netOutput(self):
        self.outy.stop()
        self.timer.stop()
        self.netin_backtrans.hide()
        self.netout_trans.hide()
        self.netout_wid.show()
        self.netin_wid.hide()
        self.netout_anal.setFont(QFont(HND_BOLD, 30))
        self.netout_rec.setFont(QFont(HND_BOLD, 30))
        self.netout_no1.setFont(QFont(HND_BLACK, 48))
        self.netout_no2.setFont(QFont(HND_BLACK, 48))
        self.netout_netbutt.setFont(QFont(HND_BLACK, 16))
        self.netout_backbutt.setFont(QFont(HND_BLACK, 30))
        self.netout_nextbutt.setFont(QFont(HND_BLACK, 30))
        self.netout_rectxt.setFont(QFont(HND_LIGHT, 16))
        self.netout_user.setFont(QFont(HND_LIGHT, 12))
        self.netout_txt.setFont(QFont(HND_LIGHT, 25))
        self.netout_user.setAutoFillBackground(False)
        self.netout_user.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        palette = self.netout_user.palette()
        palette.setColor(QPalette.ColorRole.Base, QColor(0, 0, 0, 0))
        self.netout_user.setPalette(palette)
        self.netout_txt.setText(f"{self.netin_text.text()}")
        self.netout_map.setStyleSheet(f"background-image: url({MAP_PNG});"
                                      " "
                                      "background-position: center; border: none;")
        self.netout_backbutt.clicked.connect(self.netOutback_trans)
        self.netout_nextbutt.clicked.connect(self.BackMain)
        self.netout_close.clicked.connect(self.Close_app)
        self.netout_min.clicked.connect(self.showMinimized)

    def onComboIndexChanged(self, index):
        self.locin_nextbutt.setEnabled(index != -1)

    def ShowMap(self):
        self.map = LocoutMaps()
        self.map.blist.setHtml(self.blister)
        self.map.show()

    def get_dashy(self):
        return self.dashy

    def BackMain(self):
        if os.path.exists(MAP_PNG):
            os.remove(MAP_PNG)
        if os.path.exists(MAP_HTML):
            os.remove(MAP_HTML)
        self.outin.stop()
        self.output_wid.hide()
        self.locout_wid.hide()
        self.locframe.hide()
        self.prodframe.hide()
        self.mainframe.show()
        self.start_wid.show()

    def Back(self):
        if os.path.exists(MAP_PNG):
            os.remove(MAP_PNG)
        if os.path.exists(MAP_HTML):
            os.remove(MAP_HTML)
        self.dash_wid.hide()
        self.start_wid.show()
        self.get_dashy().stop()

    def Back_dash(self):
        self.dashy.stop()
        self.backy.stop()
        self.timer.stop()
        self.back_transition.hide()
        self.dash_wid.show()
        self.input_wid.hide()
        self.Dashboard()

    def toOutput_trans(self):
        self.inputty.stop()
        self.to_outtrans.show()
        self.timer = QtCore.QTimer(self)
        self.timer.singleShot(1000, self.Output)
        self.outy.start()
        self.outy.setSpeed(50)
        self.to_outtrans.setMovie(self.outy)
        self.to_outtrans.setScaledContents(True)

    def locOutput_trans(self):
        try:
            self.geolocator = geopy.Nominatim(user_agent="Recognizance")
            self.locs = self.locin_text.text()
            self.chc = self.locin_combo.currentText()
            self.radius = self.locin_radius.value()
            self.amen = None
            cl.delay_range = [1, 3]
            cl.get_timeline_feed()

            if self.chc == "Restaurant":
                self.amen = "restaurant"
            elif self.chc == "Cafe":
                self.amen = "cafe"
            elif self.chc == "Bar":
                self.amen = "bar"
            elif self.chc == "Fast Food":
                self.amen = "fast_food"

            self.geocode = RateLimiter(self.geolocator.geocode, min_delay_seconds=1)
            self.geocoder_result = self.geocode(self.locs)

            if self.geocoder_result is None:
                self.locout_txt.setText("The address you entered doesn't exist, please go back and try again.")

            else:
                lat = self.geocoder_result.latitude
                lng = self.geocoder_result.longitude

                self.loci = cl.location_search(lat, lng)
                posts_csv = user_posts(cl, self.loci)

                data = pd.read_csv(posts_csv)

                overpass = Overpass()

                result = overpass.query(f"""
                    node(around:{self.radius}, {lat}, {lng})["amenity"="{self.amen}"];
                    out center;
                """)

                amenities = []

                m = folium.Map(location=[lat, lng], zoom_start=40)

                folium.Marker([lat, lng], icon=folium.Icon(color="red"), popup=folium.Popup(
                    '<a href="' + f"https://www.google.com/maps?q=&layer=c&cbll={lat},{lng}" + '">' + str(self.locs) +
                    '</a>', max_width=200)).add_to(m)

                counts = 0
                if result.nodes() is not None:
                    for amenity in result.nodes():
                        if amenity.tag('name') != "None":
                            name = amenity.tag('name')
                            lat = amenity.lat()
                            lng = amenity.lon()
                            amenities.append((lat, lng, name))
                            counts += 1

                # business = {'business_type': self.chc,
                #             'count': len(amenities)}

                self.businesslist = ""
                for lat, lng, name in amenities:
                    street_view_link = f"https://www.google.com/maps?q=&layer=c&cbll={lat},{lng}"
                    folium.Marker([lat, lng], popup=folium.Popup('<a href="' + street_view_link + '">' + name + '</a>',
                                                                 max_width=200)).add_to(m)
                    self.businesslist += name + "\n"

                self.blister = "<table>"
                for i, name in enumerate(self.businesslist.split("\n")):
                    if i % 2 == 0:
                        self.blister += "<tr><td>" + name + "</td>"
                    else:
                        self.blister += "<td>" + name + "</td></tr>"
                self.blister += "</table>"

                # training data for decision weighting
                competitors = [5, 6, 4, 4, 2, 4, 13, 16, 5, 30, 5, 6, 4, 73, 20, 4, 13, 102, 5, 2]
                engagement_rates = [10000, 9999, 10000, 9999, 11532, 98, 4053, 8456, 1, 36405, 345, 80, 9032, 30250,
                                    12130, 7234, 95003, 7045, 8632, 124800]

                encoded_recommendations = [0, 1, 2, 3, 2, 3, 1, 1, 1, 2, 1, 1, 3, 0, 0, 3, 0, 1, 1, 2]

                decision_tree = DecisionTreeClassifier()
                decision_tree.fit(list(zip(competitors, engagement_rates)), encoded_recommendations)

                joblib.dump(decision_tree, JOB)
                model = joblib.load(JOB)

                new_competitors = counts
                data['combined_total'] = data['likes'] + data['comments']
                new_engagement_rate = data['combined_total'].sum()
                new_prediction = model.predict([[new_competitors, new_engagement_rate]])

                if new_prediction[0] == 0:
                    self.locout_txt.setText("A saturated market can be daunting, but with high engagement, you can "
                                            "differentiate your business from the competition. Focus on your unique "
                                            "selling points and provide excellent customer service.")

                elif new_prediction[0] == 1:
                    self.locout_txt.setText("A less receptive audience and a crowded market can make it difficult to "
                                            "succeed. However, with careful planning and execution, you can still find "
                                            "success. Identify your target market and develop a marketing strategy that"
                                            " resonates with them.")

                elif new_prediction[0] == 2:
                    self.locout_txt.setText("A receptive market with less competition means that your business has a "
                                            "good chance of success. With high engagement, you can build a strong brand"
                                            " and loyal customer base.")

                elif new_prediction[0] == 3:
                    self.locout_txt.setText("While the engagements online and the number of competitors are low in the"
                                            " location, it may come with unique opportunities for business expansion. "
                                            "It might be challenging to attract customers, but through conducting "
                                            "market analysis and strategies, you can establish your business as a "
                                            "frontrunner in the market.")

                if os.path.exists(MAP_HTML):
                    os.remove(MAP_HTML)
                m.save(MAP_HTML)
                hti = html2image.Html2Image(custom_flags=['--virtual-time-budget=10000'])
                hti.screenshot(html_file=MAP_HTML, save_as=MAP)
                os.replace(MAP, MAP_PNG)

            self.inputty.stop()
            self.locin_outtrans.show()
            self.timer = QtCore.QTimer(self)
            self.timer.singleShot(1000, self.locOutput)
            self.outy.start()
            self.outy.setSpeed(50)
            self.locin_outtrans.setMovie(self.outy)
            self.locin_outtrans.setScaledContents(True)

        except ClientError as e:
            QtWidgets.QMessageBox.critical(self, 'Error', 'Error: ' + str(e) + '\n\nPlease try again later.')
            self.close()
            sys.exit(0)

    def netOutput_trans(self):
        try:
            cl.delay_range = [1, 3]
            geolocator = geopy.Nominatim(user_agent="Recognizance")

            self.location = self.netin_text.text()

            self.geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
            self.geocoder_result = self.geocode(self.location)

            if self.geocoder_result is None:
                self.netout_rectxt.setText("Location not found. Please try again.")

            else:
                lat = self.geocoder_result.latitude
                lng = self.geocoder_result.longitude

                self.locations = cl.location_search(lat, lng)

                m = folium.Map(location=[lat, lng], zoom_start=40)

                folium.Marker([lat, lng], icon=folium.Icon(color="red")).add_to(m)

                m.save(MAP_HTML)
                hti = html2image.Html2Image(custom_flags=['--virtual-time-budget=10000'])
                hti.screenshot(html_file=MAP_HTML, save_as=MAP)
                os.replace(MAP, MAP_PNG)

                # Load the data from the CSV file
                users_csv = location_data(cl, self.locations)

                data = pd.read_csv(users_csv)

                # Filter the data based on follower_count > 500 and collab == 1
                filtered_data = data[(data['follower_count'] > 500) & (data['collab'] == 1)].copy()

                # Filter the data based on follower_count < 500 and collab == 0 or 1
                user_data = \
                    data[(data['follower_count'] < 500) & ((data['collab'] == 0) | (data['collab'] == 1))].copy()

                X = user_data[['follower_count', 'like_count', 'comment_count']]
                y = user_data['collab']

                neomodel = tf.keras.models.load_model(MODEL)

                # Predict the labels for all data points
                y_pred = neomodel.predict(X)

                # Add the predicted labels to user_data
                user_data['accuracy'] = y_pred

                # Get the top 5 users based on accuracy
                top_users = user_data.sort_values('accuracy', ascending=False).head(5)

                # Create a combined_total column that sums the likes, comments, and follower_count
                filtered_data['combined_total'] = filtered_data['like_count'] + filtered_data['comment_count'] + \
                                                  filtered_data['follower_count']

                # Group the filtered data by username and sum the combined_total
                grouped_data = filtered_data.groupby('username')['combined_total'].sum().reset_index()

                # Sort the data by combined_total in descending order
                sorted_data = grouped_data.sort_values('combined_total', ascending=False)

                # Select the top 10 usernames with the highest combined total
                top_usernames = sorted_data['username'].head(10).tolist()

                # Print the recommended usernames
                self.netout_rectxt.setText(
                    "To improve your promotion, consider reaching out and connect with these top Instagram users "
                    "who have recently been in the area.")

                self.netout_user.setOpenExternalLinks(True)

                html = """
                <html>
                    <head>
                        <style>
                            .column {{
                                float: left;
                                width: 50%;
                            }}
                            .row:after {{
                                content: "";
                                display: table;
                                clear: both;
                            }}
                        </style>
                    </head>
                    <body>
                        <div class="row">
                            <div class="column">
                                <h3>Most Recommended:<br></h3>
                                {}
                            </div>
                            <div class="column">
                                <h3>Other Recommendations:<br></h3>
                                {}
                            </div>
                        </div>
                    </body>
                </html>
                """

                top_users['bio'] = top_users['bio'].fillna(value="No bio available.")

                most_recommended = ""
                other_recommendations = ""

                for username in top_usernames:
                    follower_count = filtered_data[filtered_data['username'] == username]['follower_count'].values[0]
                    bio = filtered_data[filtered_data['username'] == username]['bio'].values[0]
                    most_recommended += f'<a href="https://www.instagram.com/{username}/">@{username}</a>' \
                                        f' - {follower_count} Followers<br> Bio: {bio}<br><br>'

                for username in top_users['username']:
                    follower_count = top_users[top_users['username'] == username]['follower_count'].values[0]
                    bio = top_users[top_users['username'] == username]['bio'].values[0]
                    other_recommendations += f'<a href="https://www.instagram.com/{username}/">@{username}</a>' \
                                             f' - {follower_count} Followers<br> Bio: {bio}<br><br>'

                self.netout_user.setHtml(html.format(most_recommended, other_recommendations))

            self.inputty.stop()
            self.netin_outtrans.show()
            self.timer = QtCore.QTimer(self)
            self.timer.singleShot(1000, self.netOutput)
            self.outy.start()
            self.outy.setSpeed(50)
            self.netin_outtrans.setMovie(self.outy)
            self.netin_outtrans.setScaledContents(True)

        except ClientError as e:
            QtWidgets.QMessageBox.critical(self, 'Error', 'Error: ' + str(e) + '\n\nPlease try again later.')
            self.close()
            sys.exit(0)

    def Outback_trans(self):
        self.outin.stop()
        self.out_transition.show()
        self.timer = QtCore.QTimer(self)
        self.timer.singleShot(1000, self.Input)
        self.bouty.start()
        self.bouty.setSpeed(40)
        self.out_transition.setMovie(self.bouty)
        self.out_transition.setScaledContents(True)

    def locOutback_trans(self):
        if os.path.exists(MAP_PNG):
            os.remove(MAP_PNG)
        if os.path.exists(MAP_HTML):
            os.remove(MAP_HTML)
        self.outin.stop()
        self.locout_trans.show()
        self.timer = QtCore.QTimer(self)
        self.timer.singleShot(1000, self.locInput)
        self.bouty.start()
        self.bouty.setSpeed(40)
        self.locout_trans.setMovie(self.bouty)
        self.locout_trans.setScaledContents(True)

    def netOutback_trans(self):
        self.outin.stop()
        self.netout_trans.show()
        self.timer = QtCore.QTimer(self)
        self.timer.singleShot(1000, self.netInput)
        self.bouty.start()
        self.bouty.setSpeed(40)
        self.netout_trans.setMovie(self.bouty)
        self.netout_trans.setScaledContents(True)

    def toInput_trans(self):
        self.dashy.stop()
        self.transition.show()
        self.timer = QtCore.QTimer(self)
        self.timer.singleShot(1000, self.Input)
        self.trans.start()
        self.trans.setSpeed(50)
        self.transition.setMovie(self.trans)
        self.transition.setScaledContents(True)

    def locIn_trans(self):
        self.dashy.stop()
        self.transition.show()
        self.timer = QtCore.QTimer(self)
        self.timer.singleShot(1000, self.locInput)
        self.trans.start()
        self.trans.setSpeed(50)
        self.transition.setMovie(self.trans)
        self.transition.setScaledContents(True)

    def netIn_trans(self):
        self.dashy.stop()
        self.transition.show()
        self.timer = QtCore.QTimer(self)
        self.timer.singleShot(1000, self.netInput)
        self.trans.start()
        self.trans.setSpeed(50)
        self.transition.setMovie(self.trans)
        self.transition.setScaledContents(True)

    def toDash_trans(self):
        self.inputty.stop()
        self.timer.singleShot(1000, self.Back_dash)
        self.back_transition.show()
        self.backy.start()
        self.backy.setSpeed(50)
        self.back_transition.setMovie(self.backy)
        self.back_transition.setScaledContents(True)

    def locDash_trans(self):
        self.inputty.stop()
        self.timer.singleShot(1000, self.Back_dash)
        self.locback_trans.show()
        self.backy.start()
        self.backy.setSpeed(50)
        self.locback_trans.setMovie(self.backy)
        self.locback_trans.setScaledContents(True)

    def netDash_trans(self):
        self.inputty.stop()
        self.timer.singleShot(1000, self.Back_dash)
        self.netin_backtrans.show()
        self.backy.start()
        self.backy.setSpeed(50)
        self.netin_backtrans.setMovie(self.backy)
        self.netin_backtrans.setScaledContents(True)

    def Close_app(self):
        if os.path.exists(MAP_PNG):
            os.remove(MAP_PNG)
        if os.path.exists(MAP_HTML):
            os.remove(MAP_HTML)
        if os.path.exists('cache'):
            shutil.rmtree('cache')
        self.close()
        sys.exit(0)

    def Logout(self):
        cl.delay_range = [1, 3]
        self.login = Login()
        cl.logout()
        os.remove(USER_JSON)
        os.remove(DUMP_JSON)
        os.remove(KEY)
        self.hide()
        self.login.show()

    def mousePressEvent(self, event):
        if event.buttons() == QtCore.Qt.MouseButton.LeftButton:
            self.dragPos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if hasattr(self, 'dragPos'):
            if event.buttons() & QtCore.Qt.MouseButton.LeftButton:
                if self.dragPos is not None:
                    self.move(self.pos() + event.globalPosition().toPoint() - self.dragPos)
                self.dragPos = event.globalPosition().toPoint()
                event.accept()
