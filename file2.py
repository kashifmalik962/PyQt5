# Importing required libraries
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWebChannel import QWebChannel
import sys

# Declare the global variable
recording = False

# Creating main window class
class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # Set up the browser
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("https://www.geeksforgeeks.org/"))
        self.browser.urlChanged.connect(self.update_urlbar)
        self.browser.loadFinished.connect(self.on_load_finished)

        self.setCentralWidget(self.browser)
        self.status = QStatusBar()
        self.setStatusBar(self.status)

        # Navigation toolbar
        navtb = QToolBar("Navigation")
        self.addToolBar(navtb)

        # Record button
        self.record_btn = QAction("Record", self)
        self.record_btn.setStatusTip("Toggle recording")
        self.record_btn.triggered.connect(self.toggle_recording)
        navtb.addAction(self.record_btn)

        # Play button
        play_btn = QAction("Play", self)
        play_btn.setStatusTip("Reload page")
        play_btn.triggered.connect(self.browser.reload)
        navtb.addAction(play_btn)

        # Separator
        navtb.addSeparator()

        # URL bar
        self.urlbar = QLineEdit()
        self.urlbar.returnPressed.connect(self.navigate_to_url)
        navtb.addWidget(self.urlbar)

        # Stop button
        stop_btn = QAction("Stop", self)
        stop_btn.setStatusTip("Stop loading current page")
        stop_btn.triggered.connect(self.browser.stop)
        navtb.addAction(stop_btn)

        self.show()

        # Set up QWebChannel for communication
        self.channel = QWebChannel()
        self.browser.page().setWebChannel(self.channel)

        # Register the 'qt' object
        self.channel.registerObject('qt', self)

    @pyqtSlot()
    def toggle_recording(self):
        global recording
        recording = not recording
        current_url = self.browser.url().toString()
        print(f"Recording state: {recording}, Current URL: {current_url}")  # Print True if recording, False if not
        self.on_load_finished()  # Call the on_load_finished function

    def on_load_finished(self):
        if recording:
            self.inject_javascript()
        else:
            self.remove_javascript()

    def inject_javascript(self):
        print("Injecting JavaScript because recording is ON")
        
        # This is a placeholder. Replace the content with the actual content of qwebchannel.js.
        qwebchannel_js_content = """
        // Content of qwebchannel.js goes here.
        // Download from https://code.qt.io/cgit/qt/qtwebchannel.git/tree/src/qtwebchannel/qwebchannel.js
        """

        js_code_qwebchannel = f"""
        (function() {{
            function loadScript(url, callback) {{
                var script = document.createElement('script');
                script.type = 'text/javascript';
                script.src = url;
                script.onload = callback;
                document.head.appendChild(script);
            }}

            // Load jQuery
            loadScript('https://code.jquery.com/jquery-3.6.0.min.js', function() {{
                {qwebchannel_js_content}

                new QWebChannel(qt.webChannelTransport, function(channel) {{
                    window.qt = channel.objects.qt;

                    if (typeof window.recordingEventListener !== 'undefined') {{
                        $(document).off('click', window.recordingEventListener);
                    }}

                    window.recordingEventListener = function(event) {{
                        var element = event.target;
                        var xpath = getXPath(element);
                        var Link = clickLink(element);
                        var Text = getText(element);
                        window.qt.processXPath(xpath, Text, Link);
                    }};

                    $(document).on('click', window.recordingEventListener);

                    function getXPath(element) {{
                        var xpath = '';
                        for (; element && element.nodeType == 1; element = element.parentNode) {{
                            var id = $(element.parentNode).children(element.tagName).index(element) + 1;
                            id = id > 1 ? '[' + id + ']' : '';
                            xpath = '/' + element.tagName.toLowerCase() + id + xpath;
                        }}
                        return xpath;
                    }}

                    var input_prev = [];
                    function getText() {{
                        const inputs = document.getElementsByTagName('input');
                        let input_data = [];

                        for (var i = 0; i < inputs.length; i++) {{
                            if (inputs[i].value !== '') {{
                                let path = getXPath(inputs[i]); // Calculate XPath inside the loop

                                if (!input_prev.some(([prevPath, prevValue]) => prevPath === path && prevValue === inputs[i].value)){{
                                    input_prev.push([path, inputs[i].value]);
                                    input_data.push([path, inputs[i].value]);
                                }}
                            }}
                        }}
                        return input_data.toString();
                    }}

                    function clickLink(target){{
                        const eleTarget = target;
                        if (eleTarget.href){{
                            return eleTarget.href;
                        }} else {{
                            return "";
                        }}
                    }}
                }});
            }});
        }})();
        """

        self.browser.page().runJavaScript(js_code_qwebchannel)

    def remove_javascript(self):
        print("Removing JavaScript because recording is OFF")
        js_code_remove_listener = """
        (function() {
            if (typeof window.recordingEventListener !== 'undefined') {
                $(document).off('click', window.recordingEventListener);
            }
        })();
        """
        self.browser.page().runJavaScript(js_code_remove_listener)

    @pyqtSlot(str, str, str)
    def processXPath(self, xpath, Text, Link):
        # Write the clicked element's details to a file
        with open('path.txt', 'a') as file:
            if Text == '':
                Text = []
            else:
                Text = Text.split(',')

            if Link == '':
                Link = []
            else:
                Link = Link.split(',')
            file.write(f"{[xpath, Text, Link]},\n")

    def update_urlbar(self, q):
        self.urlbar.setText(q.toString())
        self.urlbar.setCursorPosition(0)

    def navigate_to_url(self):
        q = QUrl(self.urlbar.text())
        if q.scheme() == "":
            q.setScheme("http")
        self.browser.setUrl(q)

# Creating a PyQt5 application
app = QApplication(sys.argv)

# Setting name to the application
app.setApplicationName("Geek Browser")

# Creating a main window object
window = MainWindow()

# Running the application
app.exec_()
