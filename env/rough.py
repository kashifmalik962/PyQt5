import sys
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTextEdit, QSplitter
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineProfile
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor

class WebEnginePage(QWebEnginePage):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window

    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceId):
        self.main_window.handle_console_message(level, message, lineNumber, sourceId)



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt5 WebEngine Console and Network Example")
        self.setGeometry(100, 100, 800, 800)

        self.web_view = QWebEngineView(self)
        self.web_page = WebEnginePage(self, self.web_view)
        self.web_view.setPage(self.web_page)

        self.console_output = QTextEdit(self)
        self.console_output.setReadOnly(True)


        splitter = QSplitter(self)
        splitter.setOrientation(Qt.Vertical)
        splitter.addWidget(self.web_view)

        bottom_splitter = QSplitter(Qt.Horizontal)
        bottom_splitter.addWidget(self.console_output)
        splitter.addWidget(bottom_splitter)

        self.setCentralWidget(splitter)

        self.web_view.setUrl(QUrl("https://en.wikipedia.org/wiki/Empire"))


    def handle_console_message(self, level, message, line_number, source_id):
        console_message = f"Console message: {message} (Source: {source_id}, Line: {line_number})"
        self.console_output.append(console_message)
        print(console_message)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())