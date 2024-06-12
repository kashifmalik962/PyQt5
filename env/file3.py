# Importing required libraries for Selenium
import ast
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium import webdriver


# Importing required libraries for PyQt5
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
    def __init__(self,url, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # Set up the browser
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl(url))
        self.browser.urlChanged.connect(self.update_urlbar)
        # self.browser.loadFinished.connect(self.on_load_finished)
        # print(current url)

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
        play_btn.setStatusTip("Selenium Script")
        play_btn.triggered.connect(self.SeleniumScript)
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
        print(f"Recording state: {recording}")  # Print True if recording, False if not
        self.on_load_finished()  # Call the on_load_finished function

    def on_load_finished(self):
        if recording:
            self.inject_javascript()
        else:
            self.remove_javascript()

    def inject_javascript(self):
        print("Injecting JavaScript because recording is ON")
        js_code_qwebchannel = """
        (function() {
            function loadScript(url, callback) {
                var script = document.createElement('script');
                script.type = 'text/javascript';
                script.src = url;
                script.onload = callback;
                document.head.appendChild(script);
            }

            // Load jQuery
            loadScript('https://code.jquery.com/jquery-3.6.0.min.js', function() {
                // Load qwebchannel.js after jQuery is loaded
                loadScript('qrc:///qtwebchannel/qwebchannel.js', function() {
                    new QWebChannel(qt.webChannelTransport, function(channel) {
                        window.qt = channel.objects.qt;

                        if (typeof window.recordingEventListener !== 'undefined') {
                            $(document).off('click', window.recordingEventListener);
                        }

                        window.recordingEventListener = function(event) {
                            var element = event.target;
                            var xpath = getXPath(element);
                            var Link = clickLink(element);
                            var Text = getText(element);
                            window.qt.processXPath(xpath, Text, Link);
                        };

                        $(document).on('click', window.recordingEventListener);

                        function getXPath(element) {
                            var xpath = '';
                            for (; element && element.nodeType == 1; element = element.parentNode) {
                                var tagName = element.tagName.toLowerCase();
                                var siblingIndex = getSiblingIndex(element);
                                xpath = '/' + tagName + siblingIndex + xpath;
                            }
                            return xpath;
                        }

                        function getSiblingIndex(element) {
                            var siblings = element.parentNode ? element.parentNode.children : [];
                            var sameTagSiblings = Array.from(siblings).filter(sibling => sibling.tagName === element.tagName);
                            var index = sameTagSiblings.indexOf(element) + 1;
                            return sameTagSiblings.length > 1 ? '[' + index + ']' : '';
                        }

                        var input_prev = [];
                        function getText() {
                            const inputs = document.getElementsByTagName('input');
                            let input_data = [];

                            for (var i = 0; i < inputs.length; i++) {
                                if (inputs[i].value !== '') {
                                    let path = getXPath(inputs[i]); // Calculate XPath inside the loop

                                    if (!input_prev.some(([prevPath, prevValue]) => prevPath === path && prevValue === inputs[i].value)){
                                        input_prev.push([path, inputs[i].value]);
                                        input_data.push([path, inputs[i].value]);
                                    }
                                }
                            }
                            return input_data.toString();
                        }

                        
                        function clickLink(target){
                            const eleTarget = target;
                            if (eleTarget.href){
                                return eleTarget.href;
                            } else {
                                return "";
                            }
                        }
                    });
                });
            });
        })();
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
                Text = list(Text.split(','))
                print("text=",Text, "*******************************************")
                def pair_elements(input_list):
                    list_of_list = [input_list[i:i+2] for i in range(0, len(input_list), 2)]
                    lst = []
                    for list in list_of_list:
                        if list[1] not in ['on', 'Special:Search', 'Search archives']:
                            lst.append(list)
                    return lst
                Text = pair_elements(Text)

            if Link == '' or Link not in '/':
                Link = []

            print(xpath)
            file.write(f"{[xpath.replace('/input',''), Text, Link]},\n")

    def update_urlbar(self, q):
        self.urlbar.setText(q.toString())
        self.urlbar.setCursorPosition(0)

    def navigate_to_url(self):
        q = QUrl(self.urlbar.text())
        if q.scheme() == "":
            q.setScheme("http")
        self.browser.setUrl(q)

                                    # Selenium Script

    def SeleniumScript(self):
        # Set Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome()
        # Now you can use the driver for testing with the extension pre-loaded in headless mode
        txt = open("path.txt")

        step=ast.literal_eval('[' + txt.read() + ']')
        txt.close()
        driver.get(url)
        page_source = driver.page_source
        actions = ActionChains(driver)
        wait = WebDriverWait(driver, 10)
        for i in step:
            print(i[0], "---------------------------------------------")
            wait.until(EC.element_to_be_clickable((By.XPATH, i[0]))).click()
            print(i[0], "---------------------------------------------")
            if len(i[1]) >=1 :
                for j in i[1]:
                    # print(j)
                    inputValue =  j[0]
                    string = j[1]
                    print(inputValue,"==",string)
                    wait.until(EC.element_to_be_clickable((By.XPATH,inputValue))).click()
                    actions.send_keys(string)
                    actions.perform()
                    # input()
            if i[2] != []:
                print(i[2],"++++++++++++++++++++++++++++++++++++++++++++++++")
                driver.get(i[2])
                
        print("script Execute Successfully")

# Creating a PyQt5 application
app = QApplication(sys.argv)

# Setting name to the application
app.setApplicationName("Geek Browser")

# Creating a main window object
url = "https://en.wikipedia.org/"
window = MainWindow(url)

# Loop
app.exec_()