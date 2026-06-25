# \# Robotic 3D Environment Mapping with RoboDK

# 

# !\[RoboDK](https://img.shields.io/badge/RoboDK-6.0-blue)

# !\[Robot](https://img.shields.io/badge/Robot-Doosan%20M0609-lightgrey)

# !\[Camera](https://img.shields.io/badge/Camera-Intel%20RealSense-green)

# !\[Python](https://img.shields.io/badge/Python-Embedded%20RoboDK-yellow)

# !\[Status](https://img.shields.io/badge/Status-Final%20Product-success)

# 

# \---

# 

# \## Overview

# 

# This repository contains the final files for the \*\*Robotic 3D Environment Mapping\*\* project.

# 

# The project uses \*\*RoboDK\*\*, a \*\*Doosan Robotics M0609 robot\*\*, and an \*\*Intel RealSense camera\*\* to scan the inside of a cabinet, process 3D point cloud data, align the scanned environment, export/import RoboDK-compatible files, and generate robot movement paths.

# 

# The complete workflow is divided into six Python programs that must be executed in order.

# 

# \---

# 

# \## Project Information

# 

# | Item          | Information                                                                       |

# | ------------- | --------------------------------------------------------------------------------- |

# | Project name  | Robotic 3D Environment Mapping                                                    |

# | Robot         | Doosan Robotics M0609                                                             |

# | Software      | RoboDK version 6.0                                                                |

# | Camera        | Intel RealSense camera                                                            |

# | License       | RoboDK USB dongle license                                                         |

# | Main workflow | `1.main.py` → `2.main.py` → `3.main.py` → `4.main.py` → `5.main.py` → `6.main.py` |

# 

# \---

# 

# \## System Workflow Design

# 

# ```mermaid

# flowchart TD

# &#x20;   A\[Start RoboDK] --> B\[Load Doosan Robotics M0609 Station]

# &#x20;   B --> C\[Activate RoboDK USB Dongle License]

# &#x20;   C --> D\[Prepare Physical Robot]

# &#x20;   D --> E\[Mount Intel RealSense Camera]

# &#x20;   E --> F\[Connect Laptop to Robot using Ethernet]

# &#x20;   F --> G\[Connect RoboDK to Robot IP]

# &#x20;   G --> H\[Accept Transfer Control on Robot Tablet]

# &#x20;   H --> I\[Install Required Python Libraries]

# &#x20;   I --> J\[Import Python Files into RoboDK]

# &#x20;   J --> K\[Run 1.main.py - Adaptive Inside Box Scanner]

# &#x20;   K --> L\[Run 2.main.py - RoboDK Scan Alignment]

# &#x20;   L --> M\[Run 3.main.py - RoboDK Export Converter]

# &#x20;   M --> N\[Run 4.main.py - RoboDK File Importer OOP]

# &#x20;   N --> O\[Run 5.main.py - Camera Neck Follow]

# &#x20;   O --> P\[Run 6.main.py - Angled Tip Path]

# &#x20;   P --> Q\[Disconnect Robot Properly]

# &#x20;   Q --> R\[Workflow Completed]

# ```

# 

# \---

# 

# \## Repository Structure

# 

# ```text

# Robotic-3D-Environment-Mapping/

# │

# ├── 1. Final Product/

# │   ├── Python Code/

# │   │   ├── 1. adaptive\_inside\_box\_scanner/

# │   │   │   ├── 1.main.py

# │   │   │   ├── auto\_box\_detector.py

# │   │   │   ├── auto\_centering\_service.py

# │   │   │   ├── config.py

# │   │   │   ├── point\_cloud\_service.py

# │   │   │   ├── pose\_generator.py

# │   │   │   ├── realsense\_camera.py

# │   │   │   ├── robot\_controller.py

# │   │   │   ├── scanning\_service.py

# │   │   │   └── transform\_utils.py

# │   │   │

# │   │   ├── 2. robodk\_scan\_alignment/

# │   │   │   ├── 2.main.py

# │   │   │   ├── config.py

# │   │   │   ├── convert\_pcd\_to\_robodk\_stl.py

# │   │   │   ├── deviation\_reporter.py

# │   │   │   ├── edge\_deviation\_plotter.py

# │   │   │   ├── plane\_detector.py

# │   │   │   ├── point\_cloud\_processor.py

# │   │   │   ├── scan\_aligner.py

# │   │   │   ├── scan\_filter.py

# │   │   │   └── visualizer.py

# │   │   │

# │   │   ├── 3. robodk\_export\_converter/

# │   │   │   ├── 3.main.py

# │   │   │   ├── cad\_exporter.py

# │   │   │   ├── color\_material\_service.py

# │   │   │   ├── colored\_scan\_exporter.py

# │   │   │   ├── colored\_voxel\_obj\_writer.py

# │   │   │   ├── config.py

# │   │   │   ├── point\_cloud\_scaler.py

# │   │   │   └── robodk\_conversion\_service.py

# │   │   │

# │   │   ├── 4. robodk\_file\_importer\_oop/

# │   │   │   ├── 4.main.py

# │   │   │   ├── config.py

# │   │   │   ├── file\_validator.py

# │   │   │   ├── robodk\_import\_service.py

# │   │   │   └── robodk\_item\_service.py

# │   │   │

# │   │   ├── 5. camera\_neck\_follow/

# │   │   │   ├── 5.main.py

# │   │   │   ├── camera\_calibration.py

# │   │   │   ├── camera\_neck\_follow\_service.py

# │   │   │   ├── camera\_pose\_builder.py

# │   │   │   ├── config.py

# │   │   │   ├── debug\_target\_service.py

# │   │   │   ├── look\_line\_generator.py

# │   │   │   ├── robot\_controller.py

# │   │   │   └── transform\_utils.py

# │   │   │

# │   │   └── 6. angled\_tip\_path/

# │   │       ├── 6.main.py

# │   │       ├── angled\_tcp\_pose\_builder.py

# │   │       ├── angled\_tip\_path\_service.py

# │   │       ├── camera\_calibration.py

# │   │       ├── config.py

# │   │       ├── debug\_target\_service.py

# │   │       ├── robot\_controller.py

# │   │       ├── seam\_path\_generator.py

# │   │       └── transform\_utils.py

# │   │

# │   └── Python Code.zip

# │

# ├── CAD Model/

# │   ├── 4. Cabinet Correct Measurements.STL

# │   ├── 5. Cabinet Correct Measurements.STL

# │   ├── 6. Cabinet Correct Measurements.STL

# │   ├── 7. Cabinet Correct Measurements.STL

# │   ├── 8. Cabinet Correct Measurements.STL

# │   ├── Box.SLDPRT

# │   ├── Box 2.SLDPRT

# │   └── Box 3.SLDPRT

# │

# ├── RoboDK/

# │   ├── 4. Semi-Final Product.rdk

# │   ├── 5. Final Product.rdk

# │   ├── New Station (1).rdk

# │   └── import\_stl\_to\_robodk.py

# │

# └── RoboDK Export/

# &#x20;   ├── 02\_scan\_cleaned\_inside\_stl\_range\_ROBODK\_MM.stl

# &#x20;   ├── 02\_scan\_cleaned\_inside\_stl\_range\_ROBODK\_MM\_COLORED.mtl

# &#x20;   ├── 02\_scan\_cleaned\_inside\_stl\_range\_ROBODK\_MM\_COLORED.obj

# &#x20;   ├── 04\_aligned\_cabinet\_ROBODK.stl

# &#x20;   ├── 04\_aligned\_cabinet\_ROBODK\_MM.stl

# &#x20;   └── 05\_cad\_to\_robot\_base\_transform.txt

# ```

# 

# \---

# 

# \## Requirements

# 

# Before running the project, make sure the following items are available:

# 

# | Requirement               | Description                                        |

# | ------------------------- | -------------------------------------------------- |

# | Windows laptop or PC      | Used to run RoboDK and the Python scripts          |

# | RoboDK 6.0                | Robot simulation and robot control software        |

# | RoboDK USB dongle license | Required to use the licensed RoboDK environment    |

# | Git                       | Used to clone the repository                       |

# | Python                    | Used by the project scripts                        |

# | Ethernet cable            | Used to connect the laptop to the robot            |

# | Ethernet-to-USB adapter   | Needed if the laptop has no Ethernet port          |

# | Doosan Robotics M0609     | Physical robot used for the project                |

# | Doosan robot tablet       | Used to control and accept RoboDK transfer control |

# | Intel RealSense camera    | Used for 3D scanning                               |

# | 3D printed camera mount   | Used to attach the camera to the robot             |

# | Camera cable              | Used to connect the camera to the laptop or PC     |

# 

# \---

# 

# \## Install RoboDK

# 

# 1\. Download RoboDK version 6.0 from:

# 

# ```text

# https://robodk.com/download

# ```

# 

# 2\. Run the installer.

# 3\. Follow the installation steps.

# 4\. Open RoboDK after installation.

# 

# \---

# 

# \## Download the Doosan Robotics M0609 Station

# 

# 1\. Open RoboDK.

# 2\. Click \*\*File\*\*.

# 3\. Click \*\*Open Sample Stations\*\*.

# 4\. Go to the robot library.

# 5\. Search for:

# 

# ```text

# Doosan Robotics M0609

# ```

# 

# 6\. Download the Doosan Robotics M0609 robot station.

# 7\. Move the downloaded station to the RoboDK local library.

# 8\. Open the station in RoboDK.

# 

# \---

# 

# \## Activate the RoboDK USB Dongle License

# 

# 1\. Plug the RoboDK USB dongle into the laptop.

# 2\. Open RoboDK.

# 3\. Click \*\*Help\*\*.

# 4\. Click \*\*License\*\*.

# 5\. Select \*\*USB Dongle\*\*.

# 6\. Confirm that the license is active.

# 

# The RoboDK title bar should show an education or licensed version instead of the free version.

# 

# \---

# 

# \## Prepare the Physical Robot

# 

# \### Switch on the robot control box

# 

# 1\. Go to the robot control box.

# 2\. Find the power switch under the control box.

# 3\. Switch on the robot.

# 4\. Wait until the control box has started.

# 

# \### Switch on the robot tablet

# 

# 1\. Go to the robot tablet.

# 2\. Press the power button at the upper-left part of the tablet.

# 3\. Wait until the robot tablet has fully started.

# 

# \---

# 

# \## Attach the Intel RealSense Camera

# 

# 1\. Make sure the 3D printed camera mount is attached to the robot.

# 2\. Place the Intel RealSense camera on the mount.

# 3\. Screw the camera onto the mount.

# 4\. Check that the camera is firmly attached.

# 5\. Connect the camera cable to the camera.

# 6\. Connect the other end of the cable to the laptop or PC.

# 7\. Make sure the cable does not block the robot movement path.

# 

# Do not continue if the camera is loose, the cable is not connected, or the cable is inside the robot movement path.

# 

# \---

# 

# \## Connect RoboDK to the Physical Robot

# 

# \### Open the robot connection window

# 

# 1\. In RoboDK, click the \*\*Doosan Robotics M0609\*\* robot in the station tree.

# 2\. Right-click the robot.

# 3\. Click \*\*Connect to Robot\*\*.

# 

# \### Find the robot IP address

# 

# 1\. Go to the Doosan robot tablet.

# 2\. Click \*\*Settings\*\*.

# 3\. Click \*\*Network\*\*.

# 4\. Enter the password:

# 

# ```text

# admin

# ```

# 

# 5\. Look for the robot IP address.

# 

# The normal robot IP address is:

# 

# ```text

# 192.168.137.50

# ```

# 

# \### Connect the laptop to the robot

# 

# 1\. Connect the laptop to the robot using the Ethernet cable.

# 2\. Use the Ethernet-to-USB adapter if the laptop has no Ethernet port.

# 3\. Make sure the cable is connected properly.

# 

# \### Enter the IP address in RoboDK

# 

# 1\. Go back to the RoboDK robot connection window.

# 2\. In the \*\*Robot IP/COM\*\* field, enter:

# 

# ```text

# 192.168.137.50

# ```

# 

# 3\. Click \*\*Connect\*\*.

# 

# \### Accept transfer control

# 

# 1\. After clicking \*\*Connect\*\* in RoboDK, check the robot tablet.

# 2\. Look for the \*\*Transfer Control\*\* window.

# 3\. Press \*\*OK\*\*.

# 

# RoboDK can now control the physical robot.

# 

# \### Confirm the connection

# 

# The connection is successful when:

# 

# \* The connection status is green.

# \* The status says \*\*Ready\*\*.

# \* A clicking sound can be heard from the robot joints.

# 

# \---

# 

# \## Install Required Python Libraries

# 

# RoboDK uses its own embedded Python environment.

# Install the required libraries inside the RoboDK embedded Python version, not only in the normal system Python.

# 

# Open Command Prompt and run:

# 

# ```cmd

# "C:\\RoboDK\\Python-Embedded\\python.exe" -m pip install open3d

# ```

# 

# Then run:

# 

# ```cmd

# "C:\\RoboDK\\Python-Embedded\\python.exe" -m pip install pyrealsense2

# ```

# 

# These libraries are needed for:

# 

# \* Point cloud processing

# \* Intel RealSense camera functionality

# \* 3D scan processing

# \* File conversion and alignment

# 

# \---

# 

# \## Clone the Repository

# 

# Open a terminal in the folder where you want to save the project.

# 

# ```cmd

# git clone https://github.com/DarylGenove/Robotic-3D-Environment-Mapping.git

# ```

# 

# Go into the project folder:

# 

# ```cmd

# cd Robotic-3D-Environment-Mapping

# ```

# 

# If needed, switch to the develop branch:

# 

# ```cmd

# git checkout develop

# ```

# 

# \---

# 

# \## Go to the Python Code Folder

# 

# The main Python programs are located in:

# 

# ```text

# Robotic-3D-Environment-Mapping\\1. Final Product\\Python Code

# ```

# 

# Inside this folder, there are six main subfolders.

# 

# \---

# 

# \## Main Python Programs

# 

# | Step | Program                     | Folder                           | Main file   | Purpose                                                    |

# | ---- | --------------------------- | -------------------------------- | ----------- | ---------------------------------------------------------- |

# | 1    | Adaptive Inside Box Scanner | `1. adaptive\_inside\_box\_scanner` | `1.main.py` | Scans the inside of the cabinet using the robot and camera |

# | 2    | RoboDK Scan Alignment       | `2. robodk\_scan\_alignment`       | `2.main.py` | Processes and aligns the scanned point cloud data          |

# | 3    | RoboDK Export Converter     | `3. robodk\_export\_converter`     | `3.main.py` | Converts processed scan data into RoboDK-compatible files  |

# | 4    | RoboDK File Importer OOP    | `4. robodk\_file\_importer\_oop`    | `4.main.py` | Imports converted files back into RoboDK                   |

# | 5    | Camera Neck Follow          | `5. camera\_neck\_follow`          | `5.main.py` | Creates camera-follow movement behavior                    |

# | 6    | Angled Tip Path             | `6. angled\_tip\_path`             | `6.main.py` | Generates and executes the final angled tip path           |

# 

# \---

# 

# \## Import Python Files into RoboDK

# 

# The Python files must be imported into RoboDK one by one.

# 

# 1\. Open RoboDK.

# 2\. Click \*\*File\*\*.

# 3\. Click \*\*Open\*\*.

# 4\. Browse to:

# 

# ```text

# Robotic-3D-Environment-Mapping\\1. Final Product\\Python Code

# ```

# 

# 5\. Open the correct numbered folder.

# 6\. Select the numbered Python file.

# 7\. Click \*\*Open\*\*.

# 8\. The Python file should appear in the RoboDK station tree.

# 

# Repeat this process for all six main Python files.

# 

# \---

# 

# \## Recommended Run Method

# 

# The recommended way to run each Python file is through the RoboDK script editor.

# 

# 1\. In the RoboDK station tree, find the imported Python file.

# 2\. Right-click the Python file.

# 3\. Click \*\*Edit Python Script\*\*.

# 4\. At the top of the code window, click \*\*Run\*\*.

# 5\. Click \*\*Run Module\*\*.

# 

# This method is recommended because it shows more detailed messages and possible errors while the script is running.

# 

# \---

# 

# \## Alternative Run Method

# 

# You can also double-click the Python file in the RoboDK station tree.

# 

# This starts the script directly, but it may show less detailed information compared to the script editor method.

# 

# \---

# 

# \## Correct Running Order

# 

# Run the programs in this exact order:

# 

# ```text

# 1.main.py → 2.main.py → 3.main.py → 4.main.py → 5.main.py → 6.main.py

# ```

# 

# Do not start the next script until the current script has finished.

# 

# | Order | File        |

# | ----- | ----------- |

# | 1     | `1.main.py` |

# | 2     | `2.main.py` |

# | 3     | `3.main.py` |

# | 4     | `4.main.py` |

# | 5     | `5.main.py` |

# | 6     | `6.main.py` |

# 

# \---

# 

# \## Expected Result

# 

# When everything is executed correctly:

# 

# 1\. RoboDK opens the Doosan Robotics M0609 robot station.

# 2\. RoboDK connects to the physical Doosan robot.

# 3\. The robot status becomes green and says \*\*Ready\*\*.

# 4\. The Intel RealSense camera is attached and connected.

# 5\. The required Python libraries are installed in RoboDK embedded Python.

# 6\. The scanning workflow starts.

# 7\. The point cloud data is processed and aligned.

# 8\. The scan data is exported or converted.

# 9\. The converted files are imported back into RoboDK.

# 10\. Camera-follow movement is generated.

# 11\. The angled tip path is executed as the final movement.

# 

# \---

# 

# \## Common Issues and Fixes

# 

# | Issue                                | Fix                                                                                                            |

# | ------------------------------------ | -------------------------------------------------------------------------------------------------------------- |

# | RoboDK is still in Free mode         | Check whether the USB dongle license is plugged in. Then go to \*\*Help → License → USB Dongle\*\*.                |

# | Doosan robot station cannot be found | Check whether the downloaded Doosan Robotics M0609 station was moved into the RoboDK local library.            |

# | Robot or tablet does not turn on     | Check the control box switch under the robot control box and the tablet power button.                          |

# | RoboDK cannot connect to the robot   | Check the Ethernet cable, robot IP address, robot tablet, transfer control permission, and network connection. |

# | Connection status is not green       | Check whether the robot IP address is correct. The normal IP address is `192.168.137.50`.                      |

# | Camera is not detected               | Check whether the camera is screwed onto the mount and the cable is connected to the camera and PC.            |

# | Python file does not start           | Check whether the file was imported into RoboDK correctly.                                                     |

# | Missing `open3d` library             | Run `"C:\\RoboDK\\Python-Embedded\\python.exe" -m pip install open3d`.                                            |

# | Missing `pyrealsense2` library       | Run `"C:\\RoboDK\\Python-Embedded\\python.exe" -m pip install pyrealsense2`.                                      |

# | RoboDK cannot find a project file    | Check whether the repository was cloned correctly and the correct folder path is used.                         |

# | Robot does not move                  | Check whether the robot connection status is green and says \*\*Ready\*\*.                                         |

# | Robot moves incorrectly              | Check the robot reference frame, tool frame, camera frame, and environment model position.                     |

# | Joint limit or movement error        | Stop the program and check whether the generated path is reachable for the robot.                              |

# 

# \---

# 

# \## Safety Notes

# 

# Before running the workflow on the physical robot:

# 

# 1\. Test all six Python programs in RoboDK simulation first.

# 2\. Make sure the robot path is safe and reachable.

# 3\. Keep the robot speed low during the first real test.

# 4\. Make sure the emergency stop is available.

# 5\. Keep people away from the robot working area.

# 6\. Stop the program immediately if the robot moves unexpectedly.

# 7\. Do not continue if RoboDK shows movement, frame, connection, or joint limit errors.

# 8\. Make sure the camera cable is not in the robot movement path.

# 9\. Make sure the camera is firmly attached before running the robot.

# 

# \---

# 

# \## Properly Disconnect the Robot

# 

# After finishing the workflow, disconnect the robot properly.

# 

# Do not unplug the Ethernet cable before disconnecting the robot inside RoboDK.

# 

# Correct disconnection steps:

# 

# 1\. Stop all running Python programs in RoboDK.

# 2\. In the RoboDK station tree, click the \*\*Doosan Robotics M0609\*\* robot.

# 3\. Right-click the robot.

# 4\. Click \*\*Connect to Robot\*\*.

# 5\. In the robot connection window, click \*\*Disconnect\*\*.

# 6\. Check that the connection status is no longer green and no longer says \*\*Ready\*\*.

# 7\. After RoboDK is disconnected from the robot, unplug the Ethernet cable.

# 8\. Remove the RoboDK USB dongle license if it is no longer needed.

# 9\. Disconnect the camera cable after the robot and program are fully stopped.

# 

# Correct disconnection order:

# 

# ```text

# Stop programs → Right-click robot → Connect to Robot → Disconnect → Check status → Unplug cable

# ```

# 

# \---

# 

# \## Quick Start

# 

# ```text

# 1\. Install RoboDK version 6.0.

# 2\. Download the Doosan Robotics M0609 robot station.

# 3\. Move the robot station into the RoboDK local library.

# 4\. Open the robot station in RoboDK.

# 5\. Plug in the RoboDK USB dongle license.

# 6\. Activate the license through Help → License → USB Dongle.

# 7\. Switch on the robot control box.

# 8\. Switch on the robot tablet.

# 9\. Attach the Intel RealSense camera to the robot.

# 10\. Connect the camera cable to the laptop or PC.

# 11\. Connect the laptop to the robot using Ethernet.

# 12\. Enter the robot IP address in RoboDK.

# 13\. Accept Transfer Control on the robot tablet.

# 14\. Confirm that the RoboDK connection status is green and says Ready.

# 15\. Install open3d and pyrealsense2 in RoboDK embedded Python.

# 16\. Clone this GitHub repository.

# 17\. Import the six Python files into RoboDK.

# 18\. Run the scripts in order from 1.main.py to 6.main.py.

# 19\. Disconnect the robot properly after finishing.

# ```

# 

# \---

# 

# \## Required Library Commands

# 

# ```cmd

# "C:\\RoboDK\\Python-Embedded\\python.exe" -m pip install open3d

# ```

# 

# ```cmd

# "C:\\RoboDK\\Python-Embedded\\python.exe" -m pip install pyrealsense2

# ```

# 

# \---

# 

# \## Recommended RoboDK Run Path

# 

# ```text

# Right-click Python file → Edit Python Script → Run → Run Module

# ```

# 

# \---

# 

# \## Author

# 

# \*\*Daryl Genove\*\*

# NHL Stenden University of Applied Sciences

# 

# \---



