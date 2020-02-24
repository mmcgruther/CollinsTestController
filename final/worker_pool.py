from PyQt5 import QtCore
from final.Visa_Worker import Visa_Worker

class Worker_Pool(QtCore.QObject):
   
    def __init__(self, parent, backend):
        super(Worker_Pool, self).__init__()
        self.init = False
        self.pool = {}
        self.backend = backend

    def is_init(self):
        return self.init

    def set_init(self, state):
        self.init = state
    
    def create_worker(self, addr):
        w = Visa_Worker(addr, self.backend)
        w.w_thread = QtCore.QThread()
        w.w_thread.start()

        w.signal_connect.connect(w.slot_connect)
        w.signal_write.connect(w.slot_write)

        #Signals to worker
        w.signal_start.connect(w.slot_start)
        w.signal_query.connect(w.slot_query)
        w.signal_stop.connect(w.slot_stop)

        w.moveToThread(w.w_thread)
        self.pool[addr] = w
        return w
    
    def get_worker(self, addr):
        return self.pool[addr]

    def __del__(self):
        if self.init:  
            for key in self.pool.keys():
                self.pool[key].w_thread.terminate()
                #self.get_worker(addr).w_thread.terminate()