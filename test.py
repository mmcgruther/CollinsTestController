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
        print("TEST CONNECTION")
        QTest.mouseClick(self.main_window.refresh_button, Qt.LeftButton)
        QTest.qWait(10000)
        
        self.assertEqual(self.main_window.controller_model.equipment_model.get_connected("TCPIP::192.168.1.1::10001::SOCKET"), 1)
        self.assertEqual(self.main_window.controller_model.equipment_model.get_connected("TCPIP::192.168.1.2::10001::SOCKET"), 1)
        self.assertEqual(self.main_window.controller_model.equipment_model.get_connected("TCPIP::192.168.1.3::10001::SOCKET"), 1)

    def test_execution(self):
        print("TEST EXECUTION")
        QTest.mouseClick(self.main_window.refresh_button, Qt.LeftButton)
        QTest.qWait(1000)
        QTest.keyClicks(self.main_window.xlabel_lineedit, "test X label")
        QTest.mouseClick(self.main_window.execute_button, Qt.LeftButton)
        QTest.qWait(220000)
        self.assertEqual(len(self.main_window.controller_model.output_manager.df.index), 10)
        self.assertEqual(self.main_window.controller_model.output_manager.params["xlabel"], "test X label")

    def test_abort(self):
        print("TEST ABORT")
        QTest.mouseClick(self.main_window.refresh_button, Qt.LeftButton)
        QTest.qWait(1000)
        QTest.mouseClick(self.main_window.execute_button, Qt.LeftButton)
        QTest.qWait(30000)
        QTest.mouseClick(self.main_window.abort_button, Qt.LeftButton)
        QTest.qWait(10000)
        self.assertEqual(len(self.main_window.controller_model.output_manager.df.index), 2)
        self.main_window.close()

if __name__ == "__main__":
    unittest.main()