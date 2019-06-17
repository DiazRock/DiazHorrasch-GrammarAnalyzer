from PyQt5.QtCore import (QFile, QFileInfo, QPoint, QRect, QSettings, QSize,
        Qt, QTextStream)
from PyQt5.QtGui import QIcon, QKeySequence, QFont, QStaticText, QTextBlock, QTextObject, QTextDocument
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog, QMainWindow,
        QMessageBox, QTextEdit, QTabWidget, QTabBar, QLabel, QComboBox)
import PyQt5

from Parser import GrammarClass, NoTerminal
from AuxiliarMethods import cleanGrammar

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.curFile = ''
        self.textEdit = QTextEdit()
        self.setCentralWidget(self.textEdit)

        self.createActions()
        self.createMenus()
        self.createToolBars()
        self.createStatusBar()

        self.readSettings()

        self.textEdit.document().contentsChanged.connect(self.documentWasModified)

        self.setCurrentFile('')

    def createActions(self):
        root = QFileInfo(__file__).absolutePath()
        self.newAct = QAction(QIcon(root + '/images/new.png'), "&New", self,
                shortcut=QKeySequence.New, statusTip="Create a new file",
                triggered=self.newFile)
        self.openAct = QAction(QIcon(root + '/images/open.png'), "&Open...",
                self, shortcut=QKeySequence.Open,
                statusTip="Open an existing file", triggered=self.open)

        self.saveAct = QAction(QIcon(root + '/images/save.png'), "&Save", self,
                shortcut=QKeySequence.Save,
                statusTip="Save the document to disk", triggered=self.save)

        self.saveAsAct = QAction("Save &As...", self,
                shortcut=QKeySequence.SaveAs,
                statusTip="Save the document under a new name",
                triggered=self.saveAs)

        self.exitAct = QAction("E&xit", self, shortcut="Ctrl+Q",
                statusTip="Exit the application", triggered=self.close)

        self.actionAct = QAction(QIcon(root + '/images/play.svg'),"&Actions", 
        self, shortcut = "Ctrl + P", 
        statusTip = "Execute the grammar analyzer", triggered = self.actionEvent)


    def newFile(self):
        if self.maybeSave():
            self.textEdit.clear()
            self.setCurrentFile('')

    def open(self):
        if self.maybeSave():
            fileName, _ = QFileDialog.getOpenFileName(self)
            if fileName:
                self.loadFile(fileName)

    def save(self):
        if self.curFile:
            return self.saveFile(self.curFile)

        return self.saveAs()

    def saveAs(self):
        fileName, _ = QFileDialog.getSaveFileName(self)
        if fileName:
            return self.saveFile(fileName)

        return False
    
    def closeEvent(self, event):
        if self.maybeSave():
            self.writeSettings()
            event.accept()
        else:
            event.ignore()

    def actionEvent(self):
        self.response = Response(self, self.textEdit.toPlainText())                
        self.response.show()
        pass
    
    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addAction(self.newAct)    
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addAction(self.saveAct)
        self.fileMenu.addAction(self.saveAsAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)


    def maybeSave(self):
        if self.textEdit.document().isModified():
            ret = QMessageBox.warning(self, "Application",
                    "The document has been modified.\nDo you want to save "
                    "your changes?",
                    QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)

            if ret == QMessageBox.Save:
                return self.save()

            if ret == QMessageBox.Cancel:
                return False

        return True

    def createToolBars(self):
        self.fileToolBar = self.addToolBar("File")
        self.fileToolBar.addAction(self.newAct)
        self.fileToolBar.addAction(self.openAct)
        self.fileToolBar.addAction(self.saveAct)

        self.actionToolBar = self.addToolBar("Actions")
        self.actionToolBar.addAction(self.actionAct)

    def createStatusBar(self):
        
        pass

    def readSettings(self):
        settings = QSettings("DiazRock Codes", "Grammar Analyzer")
        pos = settings.value("pos", QPoint(200, 200))
        size = settings.value("size", QSize(400, 400))
        self.resize(size)
        self.move(pos)

    def setCurrentFile(self, fileName):
        self.curFile = fileName
        self.textEdit.document().setModified(False)
        self.setWindowModified(False)

        if self.curFile:
            shownName = self.strippedName(self.curFile)
        else:
            shownName = 'untitled.txt'

        self.setWindowTitle("%s[*] - Application" % shownName)

    def documentWasModified(self):
        self.setWindowModified(self.textEdit.document().isModified())
   
    def writeSettings(self):
        settings = QSettings("DiazRock Codes", "Grammar Analyzer")
        settings.setValue("pos", self.pos())
        settings.setValue("size", self.size())


class Response(QMainWindow):
    def __init__(self, parent, text):
        super().__init__()        
        nonTerminals_productions = {}
        splitText = text.split('\n')
        initial_symbol = splitText[0].split('-->')[0].split( ) [0]     
        for line in splitText:
            leftPart, rightPart = line.split('-->')
            leftPart = leftPart.split()[0]
            nonTerminals_productions.update({ leftPart : [] } )                
            for prod in rightPart.split( '|' ):
                nonTerminals_productions[NoTerminal (leftPart)].append(prod.split())

        terminals = {x for x in prod.split() for prod in nonTerminals_productions.values() if not x in nonTerminals_productions}
        self.grammar = GrammarClass(terminals = terminals, nonTerminals = nonTerminals_productions, initialSymbol = initial_symbol)
        self.setFont(QFont('SansSerif', 12))

        #La parte presentar la gramática.
        self.OutPutBox = QTextEdit( self )         
        self.OutPutBox.setText( repr(self.grammar) )
        (width, height) = (len (repr(self.grammar)), len (repr(self.grammar))) if len (repr(self.grammar)) > 256 else (256, 256)        
        self.rect = QRect(20, 50, width, height)        
        self.OutPutBox.setGeometry(self.rect)
        self.OutPutBox.setReadOnly (True)
        self.Label = QLabel("Gramática original:", parent = self)
        self.Label.setGeometry(10, 10, 256, 32)
        self.Label.show()

        not_generable, not_reachable = cleanGrammar( self.grammar )
        if not not_generable and not not_reachable:
            self.message_good_grammar = QLabel("La gramática no posee elementos innecesarios", parent= self)
            self.message_good_grammar.setGeometry(90, 90, 128, 128)
            self.message_good_grammar.show()

if __name__ == '__main__':
    
    import sys

    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
