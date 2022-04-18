"""
Handles interfacing the map tile manager with the GUI data pipeline
"""

from Modules.MapTileManager.map_tile_manager import MapTileManager

from constants import Constants

from Modules.data_interface_core import ThreadedModuleCore


class MapInterface(ThreadedModuleCore):
    """
    Generates random data for testing
    """

    def __init__(self):
        super(MapInterface, self).__init__()

        self.tile_manager = MapTileManager()

        self.data_dictionary[Constants.map_tile_manager_key] = self.tile_manager

    def getDataDictionary(self):
        """Don't want it to copy every loop"""
        return self.data_dictionary

    def spin(self):
        try:
            self.tile_manager.process_requests()
        except Exception as e:
            print("Error getting map tiles {}".format(e))
