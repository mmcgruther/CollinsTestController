import json

class Equipment_Model:
    """
    data:
    {
        addr:
        {
            --index: -1
            --connected: 0
            names: [...]
            equipment: [...]
        }
    }
    """
    def __init__(self, file=None):
        self.data = {}
        if file is not None:
            self.load_json(file)

    def load_json(self, file):
        infile = open(file, 'r')
        json_obj = json.load(infile)
        for item in json_obj:
            address = json_obj[item]['address']
            if address not in self.data:
                self.data[address] = { 'index': -1, 'connected': 0, 'equipment': [], 'names': []}
            self.data[address]['equipment'].append(json_obj[item])
            self.data[address]['names'].append(item)

    def get_equipment_address(self, equipment_name):
        for addr in self.data:
            if equipment_name == self.data[addr]['names'][self.data[addr]['index']]:
                if self.data[addr]['connected']:
                    return addr
        return None

    def get_IP_table_data(self):
        addr_list = list(self.data)
        name_list = []
        connected_list = []
        for addr in addr_list:
            name_list.append(self.data[addr]['equipment'][self.data[addr]['index']]['idn'])
            connected_list.append(self.data[addr]['connected'])

        return [addr_list, name_list, connected_list]
    
    def get_addr_list(self):
        return list(self.data)

    def set_worker(self, worker, addr):
        self.data[addr]['worker'] = worker

    def get_worker(self, addr):
        return self.data[addr]['worker']

    def reset_index(self, addr):
        self.data[addr]['index'] = -1

    def increment_equipment(self, addr):
        self.data[addr]['index'] += 1
        valid_index = self.data[addr]['index'] < len(self.data[addr]['equipment'])
        if not valid_index:
            self.reset_index(addr)
        return not valid_index

    def get_equipment_idn(self, addr):
        return self.data[addr]['equipment'][self.data[addr]['index']]['idn']

    def get_equipment_idn_cmd(self, addr):
        return self.data[addr]['equipment'][self.data[addr]['index']]['idn_cmd']

    def get_connected(self, addr):
        return self.data[addr]['connected']

    def set_connected(self, addr, value):
        self.data[addr]['connected'] = value

    def get_connected_equipment(self, addr):
        if self.data[addr]['connected']:
            return self.data[addr]['equipment']