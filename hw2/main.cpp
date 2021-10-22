/* Sockets Example
 * Copyright (c) 2016-2020 ARM Limited
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

// Sensors drivers present in the BSP library
// #include "stm32l475e_iot01_tsensor.h"
// #include "stm32l475e_iot01_hsensor.h"
// #include "stm32l475e_iot01_psensor.h"
// #include "stm32l475e_iot01_magneto.h"
#include "stm32l475e_iot01_gyro.h"
#include "stm32l475e_iot01_accelero.h"
#include <cstdio>
#include <cstring>
#include <iostream>
#define SCALE_MULTIPLIER    0.004


#include "mbed.h"
#include "wifi_helper.h"
#include "mbed-trace/mbed_trace.h"

#if MBED_CONF_APP_USE_TLS_SOCKET
#include "root_ca_cert.h"

#ifndef DEVICE_TRNG
#error "mbed-os-example-tls-socket requires a device which supports TRNG"
#endif
#endif // MBED_CONF_APP_USE_TLS_SOCKET

class SocketDemo {
    static constexpr size_t MAX_NUMBER_OF_ACCESS_POINTS = 10;
    static constexpr size_t MAX_MESSAGE_RECEIVED_LENGTH = 100;

#if MBED_CONF_APP_USE_TLS_SOCKET
    static constexpr size_t REMOTE_PORT = 443; // tls port
#else
    static constexpr size_t REMOTE_PORT = 3005; // standard HTTP port
#endif // MBED_CONF_APP_USE_TLS_SOCKET

public:
    SocketDemo() : _net(NetworkInterface::get_default_instance())
    {
    }

    ~SocketDemo()
    {
        if (_net) {
            _net->disconnect();
        }
    }

    void run()
    {
        if (!_net) {
            printf("Error! No network interface found.\r\n");
            return;
        }

        /* if we're using a wifi interface run a quick scan */
        if (_net->wifiInterface()) {
            /* the scan is not required to connect and only serves to show visible access points */
            wifi_scan();

            /* in this example we use credentials configured at compile time which are used by
             * NetworkInterface::connect() but it's possible to do this at runtime by using the
             * WiFiInterface::connect() which takes these parameters as arguments */
        }

        /* connect will perform the action appropriate to the interface type to connect to the network */

        printf("Connecting to the network...\r\n");

        nsapi_size_or_error_t result = _net->connect();
        if (result != 0) {
            printf("Error! _net->connect() returned: %d\r\n", result);
            return;
        }

        print_network_info();

        /* opening the socket only allocates resources */
        result = _socket.open(_net);
        if (result != 0) {
            printf("Error! _socket.open() returned: %d\r\n", result);
            return;
        }

#if MBED_CONF_APP_USE_TLS_SOCKET
        result = _socket.set_root_ca_cert(root_ca_cert);
        if (result != NSAPI_ERROR_OK) {
            printf("Error: _socket.set_root_ca_cert() returned %d\n", result);
            return;
        }
        _socket.set_hostname(MBED_CONF_APP_HOSTNAME);
#endif // MBED_CONF_APP_USE_TLS_SOCKET

        /* now we have to find where to connect */

        SocketAddress address;

        if (!resolve_hostname(address)) {
            return;
        }

        address.set_port(REMOTE_PORT);

        /* we are connected to the network but since we're using a connection oriented
         * protocol we still need to open a connection on the socket */

        printf("Opening connection to remote port %d\r\n", REMOTE_PORT);

        result = _socket.connect(address);
        if (result != 0) {
            printf("Error! _socket.connect() returned: %d\r\n", result);
            return;
        }

        /* exchange an HTTP request and response */

        if (!send_message()) {
            return;
        }

        // if (!receive_http_response()) {
        //     return;
        // }


        printf("Demo concluded successfully \r\n");
    }

private:
    bool resolve_hostname(SocketAddress &address)
    {
        const char hostname[] = MBED_CONF_APP_HOSTNAME;

        /* get the host address */
        printf("\nResolve hostname %s\r\n", hostname);
        nsapi_size_or_error_t result = _net->gethostbyname(hostname, &address);
        if (result != 0) {
            printf("Error! gethostbyname(%s) returned: %d\r\n", hostname, result);
            return false;
        }

        printf("%s address is %s\r\n", hostname, (address.get_ip_address() ? address.get_ip_address() : "None") );

        return true;
    }

    bool send_http_request()    {
        /* loop until whole request sent */
        const char buffer[] = "GET / HTTP/1.1\r\n"
                              "Host: 140.112.150.20\r\n"
                              "Connection: close\r\n"
                              "\r\n";

        nsapi_size_t bytes_to_send = strlen(buffer);
        nsapi_size_or_error_t bytes_sent = 0;

        printf("\r\nSending message: \r\n%s", buffer);

        while (bytes_to_send) {
            bytes_sent = _socket.send(buffer + bytes_sent, bytes_to_send);
            if (bytes_sent < 0) {
                printf("Error! _socket.send() returned: %d\r\n", bytes_sent);
                return false;
            } else {
                printf("sent %d bytes\r\n", bytes_sent);
            }

            bytes_to_send -= bytes_sent;
        }

        printf("Complete message sent\r\n");

        return true;
    }

    bool receive_http_response()
    {
        char buffer[MAX_MESSAGE_RECEIVED_LENGTH];
        int remaining_bytes = MAX_MESSAGE_RECEIVED_LENGTH;
        int received_bytes = 0;

        /* loop until there is nothing received or we've ran out of buffer space */
        nsapi_size_or_error_t result = remaining_bytes;
        while (result > 0 && remaining_bytes > 0) {
            result = _socket.recv(buffer + received_bytes, remaining_bytes);
            if (result < 0) {
                printf("Error! _socket.recv() returned: %d\r\n", result);
                return false;
            }

            received_bytes += result;
            remaining_bytes -= result;
        }

        /* the message is likely larger but we only want the HTTP response code */

        printf("received %d bytes:\r\n%.*s\r\n\r\n", received_bytes, strstr(buffer, "\n") - buffer, buffer);

        return true;
    }


    bool send_sensor_data(){

        nsapi_error_t response;

        int16_t pDataXYZ[3] = {0};
        char recv_buffer[9];
        char acc_json[64];
        int sample_num = 0;

        printf("start sending sensor data\r\n");

        _socket.set_blocking(1);
        while (1){
            ++sample_num;
            BSP_ACCELERO_AccGetXYZ(pDataXYZ);
            float x = pDataXYZ[0]*SCALE_MULTIPLIER, y = pDataXYZ[1]*SCALE_MULTIPLIER, z = pDataXYZ[2]*SCALE_MULTIPLIER;
            int len = sprintf(acc_json,"{\"x\":%f,\"y\":%f,\"z\":%f,\"s\":%d}",(float)(int(x*10000))/10000,
                                        (float)(int(y*10000))/10000, (float)(int(z*10000))/10000, sample_num);

            
            response = _socket.send(acc_json,len);
            if (0 >= response){
                printf("Error sending: %d\n", response);
                break;
            }
            ThisThread::sleep_for(5000);
    

        }   


        printf("Complete message sent\r\n");
        _socket.close();

        return true;
    }

    bool send_message()
    {
        float sensor_value = 0;
        int16_t pDataXYZ[3] = {0};
        float pGyroDataXYZ[3] = {0};

        printf("Start sensor init\n");
        BSP_GYRO_Init();
        BSP_ACCELERO_Init();

        while(true){
        

            char buffer[] = "{\r\n";
            char endline[] = "\r\n";

            BSP_ACCELERO_AccGetXYZ(pDataXYZ);
            int acc_x = int(pDataXYZ[0]);
            int acc_y = int(pDataXYZ[1]);
            int acc_z = int(pDataXYZ[2]);
            
            BSP_GYRO_GetXYZ(pGyroDataXYZ);
            int gyro_x = int(pGyroDataXYZ[0]);
            int gyro_y = int(pGyroDataXYZ[1]);
            int gyro_z = int(pGyroDataXYZ[2]);

            //printf("%d\r\n",gyro_x);
            //printf("%d\r\n",gyro_y);
            //printf("%d\r\n",gyro_z);

            

            // int to char[]
            //acc
            string value_acc_x = to_string(acc_x);
            int value_length_x = value_acc_x.length();
            char chararray_acc_x[value_length_x+1];
            strcpy(chararray_acc_x, value_acc_x.c_str());
            strcat(chararray_acc_x,endline);

            string value_acc_y = to_string(acc_y);
            int value_length_y = value_acc_y.length();
            char chararray_acc_y[value_length_y+1];
            strcpy(chararray_acc_y, value_acc_y.c_str());
            strcat(chararray_acc_y,endline);

            string value_acc_z = to_string(acc_z);
            int value_length_z = value_acc_z.length();
            char chararray_acc_z[value_length_z+1];
            strcpy(chararray_acc_z, value_acc_z.c_str());
            strcat(chararray_acc_z,endline);

            //gyro
            string value_gyro_x = to_string(gyro_x);
            int value_length_gyro_x = value_gyro_x.length();
            char chararray_gyro_x[value_length_gyro_x+1];
            strcpy(chararray_gyro_x, value_gyro_x.c_str());
            strcat(chararray_gyro_x,endline);

            string value_gyro_y = to_string(gyro_y);
            int value_length_gyro_y = value_gyro_y.length();
            char chararray_gyro_y[value_length_gyro_y+1];
            strcpy(chararray_gyro_y, value_gyro_y.c_str());
            strcat(chararray_gyro_y,endline);

            string value_gyro_z = to_string(gyro_z);
            int value_length_gyro_z = value_gyro_z.length();
            char chararray_gyro_z[value_length_gyro_z+1];
            strcpy(chararray_gyro_z, value_gyro_z.c_str());
            strcat(chararray_gyro_z,endline);

            
            strcat(buffer, chararray_acc_x);
            strcat(buffer, chararray_acc_y);
            strcat(buffer, chararray_acc_z);

            // cout << chararray_acc_x;
            // cout << chararray_acc_y;
            // cout << chararray_acc_z;

            strcat(buffer, chararray_gyro_x);
            strcat(buffer, chararray_gyro_y);
            strcat(buffer, chararray_gyro_z);

            //cout << chararray_gyro_x;
            //cout << chararray_gyro_y;
            //cout << chararray_gyro_z;

            char buffer_2[] = "}";
            strcat(buffer, buffer_2);

            nsapi_size_t bytes_to_send = strlen(buffer);
            nsapi_size_or_error_t bytes_sent = 0;
            while (bytes_to_send) {
                bytes_sent = _socket.send(buffer + bytes_sent, bytes_to_send);
                bytes_to_send -= bytes_sent;
            }
            // printf("Finish sending\n");
            ThisThread::sleep_for(100);
        };
        return true;
    }
    
    void wifi_scan()
    {
        WiFiInterface *wifi = _net->wifiInterface();

        WiFiAccessPoint ap[MAX_NUMBER_OF_ACCESS_POINTS];

        /* scan call returns number of access points found */
        int result = wifi->scan(ap, MAX_NUMBER_OF_ACCESS_POINTS);

        if (result <= 0) {
            printf("WiFiInterface::scan() failed with return value: %d\r\n", result);
            return;
        }

        printf("%d networks available:\r\n", result);

        for (int i = 0; i < result; i++) {
            printf("Network: %s secured: %s BSSID: %hhX:%hhX:%hhX:%hhx:%hhx:%hhx RSSI: %hhd Ch: %hhd\r\n",
                   ap[i].get_ssid(), get_security_string(ap[i].get_security()),
                   ap[i].get_bssid()[0], ap[i].get_bssid()[1], ap[i].get_bssid()[2],
                   ap[i].get_bssid()[3], ap[i].get_bssid()[4], ap[i].get_bssid()[5],
                   ap[i].get_rssi(), ap[i].get_channel());
        }
        printf("\r\n");
    }

    void print_network_info()
    {
        /* print the network info */
        SocketAddress a;
        _net->get_ip_address(&a);
        printf("IP address: %s\r\n", a.get_ip_address() ? a.get_ip_address() : "None");
        _net->get_netmask(&a);
        printf("Netmask: %s\r\n", a.get_ip_address() ? a.get_ip_address() : "None");
        _net->get_gateway(&a);
        printf("Gateway: %s\r\n", a.get_ip_address() ? a.get_ip_address() : "None");
    }

private:
    NetworkInterface *_net;

#if MBED_CONF_APP_USE_TLS_SOCKET
    TLSSocket _socket;
#else
    TCPSocket _socket;
#endif // MBED_CONF_APP_USE_TLS_SOCKET
};

int main() {
    printf("\r\nStarting socket demo\r\n\r\n");

#ifdef MBED_CONF_MBED_TRACE_ENABLE
    mbed_trace_init();
#endif

    SocketDemo *example = new SocketDemo();
    MBED_ASSERT(example);
    example->run();

    return 0;
}