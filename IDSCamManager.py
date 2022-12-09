from imswitch.imcommon.model import initLogger
from .DetectorManager import DetectorManager, DetectorAction, DetectorNumberParameter, DetectorListParameter

class IDSCamManager(DetectorManager):
    def __init__(self, detectorInfo, name, **_lowLevelManagers):
        self.__logger = initLogger(self, instanceName=name)
        self._camera = self._getCamObj()

        model = self._camera.model
        self._running = False

        for propertyName, propertyValue in detectorInfo.managerProperties['idscam'].items():
            self._camera.setPropertyValue(propertyName, propertyValue)

        fullShape = (self._camera.getPropertyValue('image_width'),
                     self._camera.getPropertyValue('image_height'))

        # Prepare parameters
        parameters = {
            'exposure': DetectorNumberParameter(group='Misc', value=100, valueUnits='ms',
                                                editable=True),
            'gain': DetectorNumberParameter(group='Misc', value=1, valueUnits='arb.u.',
                                            editable=True),
            'image_width': DetectorNumberParameter(group='Misc', value=fullShape[0], valueUnits='arb.u.',
                                                   editable=False),
            'image_height': DetectorNumberParameter(group='Misc', value=fullShape[1], valueUnits='arb.u.',
                                                    editable=False)
                                                    }

        # Prepare actions
        actions = {
            'More properties': DetectorAction(group='Misc',
                                              func=self._camera.openPropertiesGUI)
        }

        super().__init__(detectorInfo, name, fullShape=fullShape, supportedBinnings=[1], model=model, parameters=parameters, actions=actions, croppable=True)

    def startAcquisition(self):
        if not self._running:
            self._camera.start_live()
            self._running = True
            self.__logger.debug('startlive')

    def stopAcquisition(self):
        if self._running:
            self._running = False
            self._camera.suspend_live()
            self.__logger.debug('suspendlive')

    def _getCamObj(self):
        try:
            from imswitch.imcontrol.model.interfaces.idscam import IDSCam
            self.__logger.debug("Initializing IDS Camera")
            camera = IDSCam()
        except Exception as e:
            print("Failed to initialize IDS Camera, " + str(e))
            from imswitch.imcontrol.model.interfaces.tiscamera_mock import MockCameraTIS
            camera = MockCameraTIS()

        self.__logger.info(f'Initialized camera, model: {camera.model}')
        return camera

    def crop(self, hpos, vpos, hsize, vsize):
        pass

    def flushBuffers(self):
        pass

    def getChunk(self):
        pass

    def getLatestFrame(self):
        self._camera.start_live()


    def pixelSizeUm(self):
        pass