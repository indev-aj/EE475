# EE475 - Development of centralised controls for microscopic elements using ImSwitch and Jetson Nano

This repository consist of multiple files written for final year project @ University of Strathclyde.
Software and hardware used in this project: 
- Jetson Nano
- ESP32
- IDS Imaging Camera
- Microscopic Laser
- Microscopic Stage


## Abstract
The use of several microscopic elements from different manufacturers will need to use specific software for each of the elements. It also induces time loss in completing readings as there is the need to change software when dealing with elements from different manufacturers.

This project is aimed to develop a centralized controls graphical user interface (GUI) for microscopic elements using Nvidia Jetson Nano and ImSwitch library. Currently, a user will have to control each of microscope’s element by hand, including turning on and off lasers, and controlling MEMS mirrors. Changing camera will also need to change the software used as each manufacturer has their specific software.

The GUI is built on currently in development library, ImSwitch. The software communicate with Jetson Nano and Jetson Nano will decide where to execute the commands. Jetson Nano will directly control the imaging device and will control other elements through communication with ESP32.
