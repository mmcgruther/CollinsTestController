import sys, unittest
from final.Main_Window import Main_Window
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt

app = QApplication(sys.argv)

class Controller_Test(unittest.TestCase):
    def setUp(self):
        self.main_window = Main_Window("testfiles/equipment.json", "testfiles/tests.json", "testfiles/simulated_devices.yaml@sim")

    def test_connection(self):
        QTest.mouseClick(self.main_window.refresh_button, Qt.LeftButton)
        QTest.qWait(1000)
        
        self.assertEqual(self.main_window.controller_model.equipment_model.get_connected("TCPIP::192.168.1.1::10001::SOCKET"), 1)
        self.assertEqual(self.main_window.controller_model.equipment_model.get_connected("TCPIP::192.168.1.2::10001::SOCKET"), 1)
        self.assertEqual(self.main_window.controller_model.equipment_model.get_connected("TCPIP::192.168.1.3::10001::SOCKET"), 1)

    def test_execution(self):
        QTest.mouseClick(self.main_window.refresh_button, Qt.LeftButton)
        QTest.qWait(1000)
        QTest.mouseClick(self.main_window.execute_button, Qt.LeftButton)
        QTest.qWait(12000)

if __name__ == "__main__":
    unittest.main()