# Usage

1. Import new project from https://os.mbed.com/teams/ST/code/DISCO_L475VG_IOT01-Sensors-BSP/
2. replace old main.cpp by our main.cpp
3. add mbed_app.json into project
4. Add library mbed-dsp to the project: https://os.mbed.com/teams/mbed-official/code/mbed-dsp
5. add a #define __CC_ARM before line 43 at file mbed-dsp/cmsis_dsp/TransformFunctions/arm_bitreversal2.S
6. run and compile. 
7. The input is z-axis acceleration data of STM node, store in testInput.
8. The output is input after low pass filter, store in testOutput.
