/*
 * Copyright (c) 2014-2020 Arm Limited and affiliates.
 * SPDX-License-Identifier: Apache-2.0
 */

#include "ThisThread.h"
#include "Thread.h"
#include "mbed.h"
#include "mbed_power_mgmt.h"
#include <cstdio>
#include <iostream>
#include <string.h>
#include <iomanip>

// Adjust pin name to your board specification.
// You can use LED1/LED2/LED3/LED4 if any is connected to PWM capable pin,
// or use any PWM capable pin, and see generated signal on logical analyzer.
PwmOut led(PWM_OUT);
using namespace std;

int main()
{
    int length;
    const int unit_time = 1;
    int arr[10] = {0,1,2,3,4,5,6,7,8,9};
    int index = 0;
    int num;
    int period;
    int active;

    while(1) {
        num = arr[(index % 10)];
        
        led.period_ms(unit_time);
        led.pulsewidth_ms(0);
        ThisThread::sleep_for(unit_time);
        
        period = unit_time * (num + 1) *2;
        active = unit_time * (num + 1);
        led.period_ms(period);
        led.pulsewidth_ms(period);
        ThisThread::sleep_for(period*1.01);
        
        led.period_ms(unit_time);
        led.pulsewidth_ms(0);
        ThisThread::sleep_for(unit_time);
        
        index++;
    }
 
}
