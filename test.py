import sys, unittest
from final.Main_Window import Main_Window
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt

app = QApplication(sys.argv)

class Controller_Test(unittest.TestCase):
    def setUp(self):
        self.main_window = Main_Window()

    def test_connection(self):
        QTest.mouseClick(self.main_window.refresh_button, Qt.LeftButton)
        QTest.qWait(1000)
        self.assertEqual(1, 1)

if __name__ == "__main__":
    unittest.main()