# objloader inspired from:
# http://www.pygame.org/wiki/OBJFileLoader
# installing glut for init at
# https://www.lfd.uci.edu/gohlke/pythonlibs/#pyopengl
# LMB + move: rotate
# RMB + move: pan
# Scroll wheel: zoom in/out

'''
sauvegarder la pos x y z,
axe rotation y ou z en haut dans l'animation
'''
import sys, pygame
from pygame.locals import *
from pygame.constants import *
from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt5.Qt import QMainWindow, QApplication, QMenu, QAction, QIcon, qApp, QLCDNumber, QSlider, Qt, QLabel, QTimer
# from PyQt5 import QtCor QtGui, QtWidgets
# from pyquaternion import Quaternion
from objloader import *
from stereoCamera import StereoCamera
from time import sleep
import time

pygame.init()
sC = StereoCamera()


class Application:
    def __init__(self):
        iO = pygame.display.Info()
        viewport = (iO.current_w - 200, iO.current_h - 200)
        pygame.display.gl_set_attribute(pygame.GL_STEREO, 1)
        pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE, 1)
        # srf = pygame.display.set_mode(viewport, DOUBLEBUF)
        pygame.display.set_mode(viewport, OPENGL | DOUBLEBUF | pygame.OPENGLBLIT | RESIZABLE)

        self.animationAngle = 0.0
        self.angleStep = 1
        self.frameRate = 120
        self.isAnimating = False
        self.stereoMode = "SHUTTER"
        self.rx, self.ry = (0, 0)
        self.tx, self.ty = (0, 0)
        self.zpos = 5
        self.rotate = self.move = False
        # LOAD OBJECT AFTER PYGAME INIT
        # obj = OBJ('cube.obj', swapyz=True)
        self.donut = OBJ('models/cube.obj', swapyz=False)
        # ------- OpenGL specification
        glLightfv(GL_LIGHT0, GL_POSITION, (-40, 200, 100, 0.0))
        glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.5, 0.5, 0.5, 1.0))
        # glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, [0.2, 0.2, 0.2, 1])
        glEnable(GL_LIGHT0)
        glEnable(GL_LIGHTING)
        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_DEPTH_TEST)  # further color are shown over further ones
        glShadeModel(GL_SMOOTH)  # most obj files expect to be smooth-shaded
        width, height = viewport
        gluPerspective(90.0, width / float(height), 1, 100.0)
        # ------- stereo camera specification
        # The smaller the aperture(ouverture), the greater the depth of field.
        # The larger the aperture, the shallower(mince) the depth of field.
        sC.aperture = 40.0
        # Using a wide-angle lens or zooming out increases depth of field.
        # Using a long lens or zooming in decreases it
        sC.focalLength = 10.0
        sC.centerPosition[0], sC.centerPosition[1], sC.centerPosition[2] = \
            0.0, 0.0, 5.0
        sC.viewingDirection[0], sC.viewingDirection[1], sC.viewingDirection[2] = \
            0.0, 0.0, -1.0
        # Distance in the scene from the camera to the near plane.
        sC.near = sC.focalLength / 500.0
        # Distance in the scene from the camera to the far plane.
        sC.far = 1000
        sC.eyeSeparation = sC.focalLength / 200.0
        sC.whRatio = \
            float(iO.current_w) / iO.current_h
        sC.update()
        # xQuat=Quaternion(axis=[1, 0, 0], angle=ry)
        # yQuat=Quaternion(axis=[0, 1, 0], angle=rx)
    '''
    ########## draw 3D text
    def drawText(self, position, textString):
        font = pygame.font.Font (None, 64)
        textSurface = font.render(
            textString, True, (255,255,255,255), (0,0,0,255))
        textData = pygame.image.tostring(textSurface, "RGBA", True)
        glRasterPos3d(*position)
        glDrawPixels(
            textSurface.get_width(),
            textSurface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, textData)
    '''

    def _animationStep(self):
        """Update animated parameters."""
        self.animationAngle += self.angleStep
        if self.animationAngle > 360:
            self.animationAngle -= 360
        #sleep(1 / float(self.frameRate))

    def _render(self, side):
        iO = pygame.display.Info()
        glViewport(
            0, 0, iO.current_w, iO.current_h)
        if side == GL_BACK_LEFT:
            frust = sC.frustumLeft
            look = sC.lookAtLeft
        else:
            frust = sC.frustumRight
            look = sC.lookAtRight
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glFrustum(frust[0], frust[1], frust[2], frust[3], frust[4], frust[5])
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(
            look[0], look[1], look[2], look[3],
            look[4], look[5], look[6], look[7], look[8])
        
        glTranslate(self.tx / 20., self.ty / 20., -self.zpos)
        if self.isAnimating:
            # glRotatef(self.animationAngle, 0, 1, 0)
            # glRotatef(self.animationAngle, 0.2, 0.7, 0.3)
            # glRotatef(
            #    self.animationAngle, self.tx / 20, self.ty / 20, - self.zpos)
            glRotatef( time.time() % (1.0) / 1 * -360, 0.2,0.7,0.3)
        else:
            glRotatef(self.ry * 360.0 / iO.current_h, 1, 0, 0)
            glRotatef(self.rx * 360.0 / iO.current_w, 0, 1, 0)

        # CALL LIST OF LOADED OBJ
        # glCallList(obj.gl_list)
        glCallList(self.donut.gl_list)

        # self._animationStep()
        '''
        pos=(100,100,50)
        self.drawText(pos,"texte")
        '''
        # print("quaternion: xQuat: {} \n yQuat: {}".format(xQuat, yQuat))
        # glRotatef(2 * math.acos(rx) * 180.00/math.pi, -1*1, 0, 0)

    def _run(self, window):
        # clock = pygame.time.Clock()
        # while 1:
        #   clock.tick(120)
        for e in pygame.event.get():
            if e.type == QUIT:
                sys.exit()
            elif e.type == KEYDOWN and e.key == K_ESCAPE:
                sys.exit()
            elif e.type == KEYDOWN and e.key == K_SPACE:
                if self.isAnimating:
                    self.isAnimating = False
                else:
                    self.isAnimating = True
            elif e.type == KEYDOWN and e.key == K_KP_PLUS:
                self.angleStep += 0.1
                self.frameRate += 5
            elif e.type == KEYDOWN and e.key == K_KP_MINUS:
                self.angleStep -= 0.1
                self.frameRate -= 5
            elif e.type == MOUSEBUTTONDOWN:
                '''
                1-left click 2-middle click
                3-right click 4-scroll up
                5-scroll down
                '''
                if e.button == 4:
                    self.zpos = max(1, self.zpos - 3)
                elif e.button == 5:
                    self.zpos += 3
                elif e.button == 1:
                    if self.isAnimating:
                        self.isAnimating = False
                    self.rotate = True
                elif e.button == 3:
                    if self.isAnimating:
                        self.isAnimating = False
                    self.move = True
            elif e.type == MOUSEBUTTONUP:
                if e.button == 1:
                    self.rotate = False
                elif e.button == 3:
                    self.move = False
            elif e.type == MOUSEMOTION:
                # return amount of movement in X and Y since previous call
                i, j = e.rel
                if self.rotate:
                    self.rx += i
                    self.ry += j
                if self.move:
                    self.tx += i
                    self.ty -= j
        if self.stereoMode == "SHUTTER":
            glDrawBuffer(GL_BACK_LEFT)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            self._render(GL_BACK_LEFT)
            glDrawBuffer(GL_BACK_RIGHT)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            self._render(GL_BACK_RIGHT)
        else:
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glDrawBuffer(GL_BACK_LEFT)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            # setLightColor("white")
            self._render(GL_BACK_LEFT)
        pygame.display.flip()

        return False
        '''
        gl_util.view_push()
        gl_util.set_view_2D((0,0,viewport[0],viewport[1]))
        glEnable(GL_TEXTURE_2D)
        glDisable(GL_DEPTH_TEST)
        glDepthMask(False)
        # draw
        for ui_component in self.ui_components:
            ui_component.draw()
        glDepthMask(True)
        glEnable(GL_DEPTH_TEST)
        glDisable(GL_TEXTURE_2D)
        gl_util.view_pop()
        '''


class Slider(QMainWindow):
    def __init__(self, application):
        super().__init__()
        self._init_ui()
        self._initPygame(application)
        self.setWindowTitle('Settings')

    # allow slider to handle float
    def _valueHandler(self, value):
        # type of "value" is int so you need to convert it to float
        # in order to get float type for "scaledValue"
        scaledValue = float(value) / 100
        print(scaledValue, type(scaledValue))

    def _animate(self):
        if self.application.isAnimating:
            self.application.isAnimating = False
        else:
            self.application.isAnimating = True

    def _init_ui(self):
        self.statusBar().showMessage('Ready')
        # ------- FILE MENU
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('File')

        impMenu = QMenu('Import', self)
        impAct = QAction('Import obj', self)
        impMenu.addAction(impAct)

        newAct = QAction('New', self)

        fileMenu.addAction(newAct)
        fileMenu.addMenu(impMenu)
        # ------- Icon exit and animate
        exitAct = QAction(
            QIcon('models/icon_exit.png'),
            'Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.triggered.connect(qApp.quit)

        animationButton = QAction(
            QIcon('models/icon_play.png'),
            'Animate', self)
        animationButton.setShortcut('Space')
        animationButton.triggered.connect(self._animate)
        # self.action.setShortcut("ESC")
        # ------- Display slider value
        lcdAperture = QLCDNumber(self)
        lcdFocalLength = QLCDNumber(self)
        # lcdNear = QLCDNumber(self)
        lcdFar = QLCDNumber(self)
        # ------- Slider creation and connection to lcd
        self.sldAperture = QSlider(Qt.Horizontal, self)
        self.sldAperture.setTickPosition(QSlider.TicksBothSides)
        self.sldFocalLength = QSlider(Qt.Horizontal, self)
        self.sldFocalLength.setTickPosition(QSlider.TicksBothSides)
        '''
        self.sldNear = QSlider(Qt.Horizontal, self)
        self.sldNear.setTickPosition(QSlider.TicksBothSides)
        '''
        self.sldFar = QSlider(Qt.Horizontal, self)
        self.sldFar.setTickPosition(QSlider.TicksBothSides)
        # ------- Connect slider to lcd
        self.sldAperture.valueChanged.connect(lcdAperture.display)
        self.sldFocalLength.valueChanged.connect(lcdFocalLength.display)
        '''
        self.sldNear.valueChanged.connect(lcdNear.display)
        '''
        self.sldFar.valueChanged.connect(lcdFar.display)
        # ------- Slider parameter and specifications
        # self.sldAperture.setMinimum(0)
        # self.sldAperture.setMaximum(80)
        self.sldAperture.setValue(sC.aperture)
        self.sldAperture.setRange(10, 100)
        self.sldFocalLength.setValue(sC.focalLength)
        self.sldFocalLength.setRange(1, 15)
        self.sldFocalLength.valueChanged.connect(self._valueHandler)
        '''
        self.sldNear.setValue(sC.near)
        self.sldNear.setRange(0,10)
        self.sldNear.valueChanged.connect(self._valueHandler)
        '''
        self.sldFar.setValue(sC.far)
        self.sldFar.setRange(50, 150)
        # ------- Show slide bar
        self.exitToolbar = self.addToolBar('exit')
        self.exitToolbar.addAction(exitAct)
        self.exitToolbar.addAction(animationButton)
        # ------- Go back to line
        self.addToolBarBreak()
        self.lcdToolbar = self.addToolBar('lcd')
        self.lcdToolbar.addWidget(lcdAperture)
        self.apertureToolbar = self.addToolBar('aperture')
        self.apertureToolbar.addWidget(self.sldAperture)
        self.apertureToolbar.addWidget(QLabel("Aperture"))
        self.addToolBarBreak()
        self.lcdToolbar2 = self.addToolBar('lcd2')
        self.lcdToolbar2.addWidget(lcdFocalLength)
        self.focalLengthToolbar = self.addToolBar('focalLength')
        self.focalLengthToolbar.addWidget(self.sldFocalLength)
        self.focalLengthToolbar.addWidget(QLabel("focalLength *100"))
        self.addToolBarBreak()
        '''
        self.lcdToolbarNear = self.addToolBar('lcd2')
        self.lcdToolbarNear.addWidget(lcdNear)
        self.nearToolbar = self.addToolBar('near')
        self.nearToolbar.addWidget(self.sldNear)
        self.nearToolbar.addWidget(QLabel("near(/100)"))
        self.addToolBarBreak()
        '''
        self.lcdToolbarFar = self.addToolBar('lcdFar')
        self.lcdToolbarFar.addWidget(lcdFar)
        self.farToolbar = self.addToolBar('far')
        self.farToolbar.addWidget(self.sldFar)
        self.farToolbar.addWidget(QLabel("far"))
        # ------- required to display
        self.setGeometry(600, 600, 600, 600)
        self.show()

    def _initPygame(self, application):
        # https://stackoverflow.com/questions/46656634/pyqt5-qtimer-count-until-specific-seconds
        self.application = application
        self.timer = QTimer()
        self.timer.timeout.connect(self._pygame_loop)
        self.timer.start(0)

    def _uiUpdate(self):
        sC.aperture = self.sldAperture.value()
        sC.focalLength = self.sldFocalLength.value()
        # sC.near = self.sldNear.value()
        sC.far = self.sldFar.value()
        sC.update()

    def _pygame_loop(self):
        self._uiUpdate()
        if self.application._run(self):
            self.close()


def main():
    application = Application()
    app = QApplication(sys.argv)
    win = Slider(application)
    win.show()
    sys.exit(app.exec_())

    pygame.quit()


if __name__ == '__main__':
    main()
