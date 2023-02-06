# image processing libraries
import numpy as np

# import IDS libraries
from ids_peak import ids_peak as peak
from ids_peak_ipl import ids_peak_ipl
from ids_peak import ids_peak_ipl_extension

from imswitch.imcommon.model import initLogger


class IDSCamera:
    def __init__(self):
        super().__init__()
        self.__logger = initLogger(self, tryInheritParent=False)

        
        self.model = "IDS Camera"
        
        # TODO get camera parameters
        # TODO convert global variable to 'self'
        

        self.m_device = None
        self.m_dataStream = None
        self.m_node_map_remote_device = None
        self.camera = self.openCamera()


    def start_live(self):
        try:
            self.m_dataStream.StartAcquisition(peak.AcquisitionStartMode_Default, peak.DataStream.INFINITE_NUMBER)
            self.m_node_map_remote_device.FindNode("TLParamsLocked").SetValue(1)
            self.m_node_map_remote_device.FindNode("AcquisitionStart").Execute()
            
            return True
        except Exception as e:
            self.__logger.error(e)
        
        return False
        
         
    def stop_live(self):
        self.camera.release()
        self.camera_is_open = False

    def suspend_live(self):
        self.camera.release()
        self.camera_is_open = False

    def prepare_live(self):
        pass

    def close(self):
        self.camera.release()
        self.camera_is_open = False
        
    def set_value(self ,feature_key, feature_value):
        # Need to change acquisition parameters?
        try:
            feature = self.camera.feature(feature_key)
            feature.value = feature_value
        except Exception as e:
            self.__logger.error(e)
            self.__logger.error(feature_key)
            self.__logger.debug("Value not available?")
    

    def set_exposure_time(self,exposure_time):
        self.exposure_time = exposure_time
        self.set_value("ExposureTime", self.exposure_time*1000)

    def set_analog_gain(self,analog_gain):
        self.analog_gain = analog_gain
        self.set_value("Gain", self.analog_gain)
        
    def set_blacklevel(self,blacklevel):
        self.blacklevel = blacklevel
        self.set_value("BlackLevel", blacklevel)

    def set_pixel_format(self,format):
        self.pixelformat = format
        self.set_value("PixelFormat", format)
        
    def getLast(self):
        # get frame and save
        try:
            buffer = self.m_dataStream.WaitForFinishedBuffer(5000)
            ipl_image = ids_peak_ipl_extension.BufferToImage(buffer)
            converted_ipl_image = ipl_image.ConvertTo(ids_peak_ipl.PixelFormatName_BGRa8)

            self.m_dataStream.QueueBuffer(buffer)
            image_np_array = converted_ipl_image.get_numpy_1D()

            frame = np.mean(image_np_array)

        except peak.Exception as e:
            self.__error_counter += 1
            self.__logger.error(e)

        return frame

    def getLastChunk(self):
        try:
            # Get buffer from device's DataStream
            buffer = self.m_data_stream.WaitForFinishedBuffer(5000)
        
            if buffer.HasChunks():
                self.m_node_map_remote_device.UpdateChunkNodes(buffer)
                exposure_time = self.m_node_map_remote_device.FindNode("ChunkExposureTime").Value()
        
            # Create IDS peak IPL image for debayering and convert it to RGBa8 format
            image = ids_peak_ipl.Image_CreateFromSizeAndBuffer(
                buffer.PixelFormat(),
                buffer.BasePtr(),
                buffer.Size(),
                buffer.Width(),
                buffer.Height()
            )
            image = image.ConvertTo(ids_peak_ipl.PixelFormatName.BGRa8)
        
            # Queue buffer so that it can be used again
            self.m_data_stream.QueueBuffer(buffer)
        except Exception as e:
            self.__logger.error(e)
       
    def setROI(self, x, y, width, height):
        try:
            # Get the minimum ROI and set it. After that there are no size restrictions anymore
            x_min = self.m_node_map_remote_device.FindNode("OffsetX").Minimum()
            y_min = self.m_node_map_remote_device.FindNode("OffsetY").Minimum()
            w_min = self.m_node_map_remote_device.FindNode("Width").Minimum()
            h_min = self.m_node_map_remote_device.FindNode("Height").Minimum()
        
            self.m_node_map_remote_device.FindNode("OffsetX").SetValue(x_min)
            self.m_node_map_remote_device.FindNode("OffsetY").SetValue(y_min)
            self.m_node_map_remote_device.FindNode("Width").SetValue(w_min)
            self.m_node_map_remote_device.FindNode("Height").SetValue(h_min)
        
            # Get the maximum ROI values
            x_max = self.m_node_map_remote_device.FindNode("OffsetX").Maximum()
            y_max = self.m_node_map_remote_device.FindNode("OffsetY").Maximum()
            w_max = self.m_node_map_remote_device.FindNode("Width").Maximum()
            h_max = self.m_node_map_remote_device.FindNode("Height").Maximum()
        
            if (x < x_min) or (y < y_min) or (x > x_max) or (y > y_max):
                self.__logger.error("Offset value is wrong!")
                return False
            elif (width < w_min) or (height < h_min) or ((x + width) > w_max) or ((y + height) > h_max):
                self.__logger.error("ROI size is wrong!")
                return False
            else:
                # Now, set final AOI
                self.m_node_map_remote_device.FindNode("OffsetX").SetValue(x)
                self.m_node_map_remote_device.FindNode("OffsetY").SetValue(y)
                self.m_node_map_remote_device.FindNode("Width").SetValue(width)
                self.m_node_map_remote_device.FindNode("Height").SetValue(height)
        
                return True
        except Exception as e:
            # ...
            self.__logger.error(e)
        
        return False

    def setPropertyValue(self, property_name, property_value):
        pass

    def getPropertyValue(self, property_name):
        pass

    def openPropertiesGUI(self):
        pass

    def openCamera(self):
        try:
            device_manager = peak.DeviceManager.Instance()
            device_manager.Update()

            if device_manager.Devices().empty():
                self.__logger.Debug("No IDS camera found!")

            device_count = device_manager.Devices().size()
            for i in range(device_count):
                if device_manager.Devices()[i].IsOpenable():
                    m_device = device_manager.Devices()[i].OpenDevice(peak.DeviceAccessType_Control)
        
                    # Get NodeMap of the RemoteDevice for all accesses to the GenICam NodeMap tree
                    self.m_node_map_remote_device = m_device.RemoteDevice().NodeMaps()[0]
    
            self.camera = m_device

            if not self.prepare_acquisition():
                # error
                self.__logger.error("Error occured! Couldn't prepare acquisition")
            
            if not self.set_roi(16, 16, 128, 128):
                # error
                self.__logger.error("Error occured! Couldn't set roi")
            
            if not self.alloc_and_announce_buffers():
                # error
                self.__logger.error("Error occured! Couldn't allocate buffer")
        except Exception as e:
            self.__logger.error(e)
        
    
    def prepare_acquisition(self):
        try:
            data_streams = self.m_device.DataStreams()
            # no data streams available
            if data_streams.empty():
                return False
        
            self.m_dataStream = self.m_device.DataStreams()[0].OpenDataStream()
        
            return True
        except Exception as e:
            self.__logger.error(e)
        
        return False
    

    def alloc_and_announce_buffers(self):
        try:
            if self.m_dataStream:
                # Flush queue and prepare all buffers for revoking
                self.m_dataStream.Flush(peak.DataStreamFlushMode_DiscardAll)
        
                # Clear all old buffers
                for buffer in self.m_dataStream.AnnouncedBuffers():
                    self.m_dataStream.RevokeBuffer(buffer)
        
                payload_size = self.m_node_map_remote_device.FindNode("PayloadSize").Value()
        
                # Get number of minimum required buffers
                num_buffers_min_required = self.m_dataStream.NumBuffersAnnouncedMinRequired()
        
                # Alloc buffers
                for count in range(num_buffers_min_required):
                    buffer = self.m_dataStream.AllocAndAnnounceBuffer(payload_size)
                    self.m_dataStream.QueueBuffer(buffer)
        
                return True
        except Exception as e:
            self.__logger.error(e)
        
        return False

