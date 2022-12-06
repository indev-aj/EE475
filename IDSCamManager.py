class IDSCamManager():
  def _getCamObj(self):
    try:
      from idscam import IDSCamera
      self.__logger.debug("Initializing IDS Camera")
      camera = IDSCamera()
    except Exception as e:
      print("Failed to initialize IDS Camera, " + str(e))
      
