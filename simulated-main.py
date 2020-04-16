from final.Main_Window import Main_Window
from PyQt5.QtWidgets import QApplication
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = Main_Window("testfiles/equipment.json", "testfiles/tests.json", "testfiles/simulated_devices.yaml@sim")
    sys.exit(app.exec_())
