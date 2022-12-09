import numpy

from ids_peak import ids_peak as peak
from ids_peak_ipl import ids_peak_ipl

from imswitch.imcommon.model import initLogger


class IDSCam:
    def __init__(self):
        super().__init__()
        self.__logger = initLogger(self, tryInheritParent=True)

        # Initialize library
        peak.Library.Initialize()

        self.model = "IDSCamera"
        self.camera = None

        # camera parameters
        self.exposure_time = 0

        if not self.open_camera():
            # error
            self.__logger.error("Camera Error")
    
        if not self.prepare_acquisition():
            # error
            self.__logger.error("Prepare Error")
        
        if not self.set_roi(16, 16, 256, 256):
            # error
            self.__logger.error("ROI Error")
        
        if not self.alloc_and_announce_buffers():
            # error
            self.__logger.error("Alloc Error")
        
        if not self.start_acquisition():
            # error
            self.__logger.error("Start Acquisition Error")

    def open_camera(self):
        global m_device, m_node_map_remote_device

        try:
            # Create instance of the device manager
            device_manager = peak.DeviceManager.Instance()

            # Update the device manager
            device_manager.Update()

            # Return if no device was found
            if device_manager.Devices().empty():
                return False

            # open the first openable device in the device manager's device list
            device_count = device_manager.Devices().size()
            for i in range(device_count):
                if device_manager.Devices()[i].IsOpenable():
                    m_device = device_manager.Devices()[i].OpenDevice(
                        peak.DeviceAccessType_Control)

                    # Get NodeMap of the RemoteDevice for all accesses to the GenICam NodeMap tree
                    m_node_map_remote_device = m_device.RemoteDevice().NodeMaps()[
                        0]

                    self.camera = m_node_map_remote_device

                    return True
        except Exception as e:
            self.__logger.error(e)

        return False

    def set_roi(self, x, y, width, height):
        try:
            # Get the minimum ROI and set it. After that there are no size restrictions anymore
            x_min = m_node_map_remote_device.FindNode("OffsetX").Minimum()
            y_min = m_node_map_remote_device.FindNode("OffsetY").Minimum()
            w_min = m_node_map_remote_device.FindNode("Width").Minimum()
            h_min = m_node_map_remote_device.FindNode("Height").Minimum()

            m_node_map_remote_device.FindNode("OffsetX").SetValue(x_min)
            m_node_map_remote_device.FindNode("OffsetY").SetValue(y_min)
            m_node_map_remote_device.FindNode("Width").SetValue(w_min)
            m_node_map_remote_device.FindNode("Height").SetValue(h_min)

            # Get the maximum ROI values
            x_max = m_node_map_remote_device.FindNode("OffsetX").Maximum()
            y_max = m_node_map_remote_device.FindNode("OffsetY").Maximum()
            w_max = m_node_map_remote_device.FindNode("Width").Maximum()
            h_max = m_node_map_remote_device.FindNode("Height").Maximum()

            if (x < x_min) or (y < y_min) or (x > x_max) or (y > y_max):
                return False
            elif (width < w_min) or (height < h_min) or ((x + width) > w_max) or ((y + height) > h_max):
                return False
            else:
                # Now, set final AOI
                m_node_map_remote_device.FindNode("OffsetX").SetValue(x)
                m_node_map_remote_device.FindNode("OffsetY").SetValue(y)
                m_node_map_remote_device.FindNode("Width").SetValue(width)
                m_node_map_remote_device.FindNode("Height").SetValue(height)

                return True
        except Exception as e:
            # ...
            self.__logger.error(e)

        return False

    def prepare_acquisition(self):
        global m_dataStream
        try:
            data_streams = m_device.DataStreams()
            if data_streams.empty():
                # no data streams available
                return False

            m_dataStream = m_device.DataStreams()[0].OpenDataStream()

            return True
        except Exception as e:
            self.__logger.error(e)

        return False

    def alloc_and_announce_buffers(self):
        try:
            if m_dataStream:
                # Flush queue and prepare all buffers for revoking
                m_dataStream.Flush(peak.DataStreamFlushMode_DiscardAll)

                # Clear all old buffers
                for buffer in m_dataStream.AnnouncedBuffers():
                    m_dataStream.RevokeBuffer(buffer)

                payload_size = m_node_map_remote_device.FindNode(
                    "PayloadSize").Value()

                # Get number of minimum required buffers
                num_buffers_min_required = m_dataStream.NumBuffersAnnouncedMinRequired()

                # Alloc buffers
                for count in range(num_buffers_min_required):
                    buffer = m_dataStream.AllocAndAnnounceBuffer(payload_size)
                    m_dataStream.QueueBuffer(buffer)

                return True
        except Exception as e:
            self.__logger.error(e)

        return False

    def start_acquisition(self):
        try:
            m_dataStream.StartAcquisition(
                peak.AcquisitionStartMode_Default, peak.DataStream.INFINITE_NUMBER)
            m_node_map_remote_device.FindNode("TLParamsLocked").SetValue(1)
            m_node_map_remote_device.FindNode("AcquisitionStart").Execute()

            return True
        except Exception as e:
            # ...
            self.__logger.error(e)

        return False

    def stop_acquisition(self):
        pass  # TODO: self.camera.stop_live()

    def close(self):
        pass  # TODO: self.camera.close()

    def start_live(self):
        try:
            buffer = m_dataStream.WaitForFinishedBuffer(5000)
            img = ids_peak_ipl.Image_CreateFromSizeAndBuffer(
            buffer.PixelFormat(), buffer.BasePtr(), buffer.Size(), buffer.Width(), buffer.Height()
            )

            img = img.ConvertTo(ids_peak_ipl.PixelFormatName_BGRa8, ids_peak_ipl.ConversionMode_Fast)
            m_dataStream.QueueBuffer(buffer)

            np_img = numpy.array(img)
            return np_img

        except Exception as e:
            self.__logger.error(e)

    def setPropertyValue(self, property_name, property_value):
        # Check if the property exists.
        if property_name == "gain":
            self.set_analog_gain(property_value)
        elif property_name == "exposure":
            self.set_exposure_time(property_value)
        else:
            self.__logger.warning(f'Property {property_name} does not exist')
            return False
        return property_value

    def getPropertyValue(self, property_name):
        # Check if the property exists.
        if property_name == "gain":
            property_value = self.camera.gain
        elif property_name == "exposure":
            property_value = self.camera.gain
        elif property_name == "image_width":
            property_value = self.camera.FindNode("Width").Value()
        elif property_name == "image_height":
            property_value = self.camera.FindNode("Height").Value()
        else:
            self.__logger.warning(f'Property {property_name} does not exist')
            return False
        return property_value

    def set_analog_gain(self, value):
        try:
            min = m_node_map_remote_device.FindNode("Gain").Minimum()
            m_node_map_remote_device.FindNode("Gain").SetValue(min)
        except Exception as e:
            print(str(e))

    def set_exposure_time(self, value):
        try:
            min = m_node_map_remote_device.FindNode("ExposureTime").Minimum()
            m_node_map_remote_device.FindNode("ExposureTime").SetValue(min)
        except Exception as e:
            print(str(e))

    

    def openPropertiesGUI(self):
        pass

    def crop():
        pass

    def flushBuffers():
        pass