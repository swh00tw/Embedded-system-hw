/* ----------------------------------------------------------------------
** Include Files
** ------------------------------------------------------------------- */
#include "mbed.h"
#include "arm_math.h"
#include "math_helper.h"
#include "iostream"

// Sensors drivers present in the BSP library
#include "stm32l475e_iot01_tsensor.h"
#include "stm32l475e_iot01_hsensor.h"
#include "stm32l475e_iot01_psensor.h"
#include "stm32l475e_iot01_magneto.h"
#include "stm32l475e_iot01_gyro.h"
#include "stm32l475e_iot01_accelero.h"

#if defined(SEMIHOSTING)
#include <stdio.h>
#endif


/* ----------------------------------------------------------------------
** Macro Defines
** ------------------------------------------------------------------- */

#define TEST_LENGTH_SAMPLES  320
/*
This SNR is a bit small. Need to understand why
this example is not giving better SNR ...
*/
#define SNR_THRESHOLD_F32    75.0f
#define BLOCK_SIZE            32

#if defined(ARM_MATH_MVEF) && !defined(ARM_MATH_AUTOVECTORIZE)
/* Must be a multiple of 16 */
#define NUM_TAPS_ARRAY_SIZE              32
#else
#define NUM_TAPS_ARRAY_SIZE              29
#endif

#define NUM_TAPS              29

/* -------------------------------------------------------------------
 * Declare Test output buffer
 * ------------------------------------------------------------------- */

static float32_t testOutput[TEST_LENGTH_SAMPLES];

/* -------------------------------------------------------------------
 * Declare State buffer of size (numTaps + blockSize - 1)
 * ------------------------------------------------------------------- */
#if defined(ARM_MATH_MVEF) && !defined(ARM_MATH_AUTOVECTORIZE)
static float32_t firStateF32[2 * BLOCK_SIZE + NUM_TAPS - 1];
#else
static float32_t firStateF32[BLOCK_SIZE + NUM_TAPS - 1];
#endif 

/* ----------------------------------------------------------------------
** FIR Coefficients buffer generated using fir1() MATLAB function.
** fir1(28, 6/24)
** ------------------------------------------------------------------- */

// ------------ original one -----------------
// #if defined(ARM_MATH_MVEF) && !defined(ARM_MATH_AUTOVECTORIZE)
// const float32_t firCoeffs32[NUM_TAPS_ARRAY_SIZE] = {
//   -0.0018225230f, -0.0015879294f, +0.0000000000f, +0.0036977508f, +0.0080754303f, +0.0085302217f, -0.0000000000f, -0.0173976984f,
//   -0.0341458607f, -0.0333591565f, +0.0000000000f, +0.0676308395f, +0.1522061835f, +0.2229246956f, +0.2504960933f, +0.2229246956f,
//   +0.1522061835f, +0.0676308395f, +0.0000000000f, -0.0333591565f, -0.0341458607f, -0.0173976984f, -0.0000000000f, +0.0085302217f,
//   +0.0080754303f, +0.0036977508f, +0.0000000000f, -0.0015879294f, -0.0018225230f, 0.0f,0.0f,0.0f
// };
// #else
// const float32_t firCoeffs32[NUM_TAPS_ARRAY_SIZE] = {
//   -0.0018225230f, -0.0015879294f, +0.0000000000f, +0.0036977508f, +0.0080754303f, +0.0085302217f, -0.0000000000f, -0.0173976984f,
//   -0.0341458607f, -0.0333591565f, +0.0000000000f, +0.0676308395f, +0.1522061835f, +0.2229246956f, +0.2504960933f, +0.2229246956f,
//   +0.1522061835f, +0.0676308395f, +0.0000000000f, -0.0333591565f, -0.0341458607f, -0.0173976984f, -0.0000000000f, +0.0085302217f,
//   +0.0080754303f, +0.0036977508f, +0.0000000000f, -0.0015879294f, -0.0018225230f
// };
// #endif

// ------------ self designed -----------------
#if defined(ARM_MATH_MVEF) && !defined(ARM_MATH_AUTOVECTORIZE)
const float32_t firCoeffs32[NUM_TAPS_ARRAY_SIZE] = {
0.00516516454302776f,
0.00592820768243009f,
0.00815503499250421f,
0.0117456327507358f,
0.0165288970204929f,
0.0222711447846357f,
0.0286879389594637f,
0.0354586185100425f,
0.0422427786903709f,
0.0486978400932577f,
0.0544967845816832f,
0.0593451246895173f,
0.0629962114730087f,
0.0652640721110309f,
0.0660330982355974f,
0.0652640721110309f,
0.0629962114730087f,
0.0593451246895173f,
0.0544967845816832f,
0.0486978400932577f,
0.0422427786903709f,
0.0354586185100425f,
0.0286879389594637f,
0.0222711447846357f,
0.0165288970204929f,
0.0117456327507358f,
0.00815503499250421f,
0.00592820768243009f,
0.00516516454302776f,
0.0f,
0.0f,
0.0f
};
#else
const float32_t firCoeffs32[NUM_TAPS_ARRAY_SIZE] = {
0.00516516454302776f,
0.00592820768243009f,
0.00815503499250421f,
0.0117456327507358f,
0.0165288970204929f,
0.0222711447846357f,
0.0286879389594637f,
0.0354586185100425f,
0.0422427786903709f,
0.0486978400932577f,
0.0544967845816832f,
0.0593451246895173f,
0.0629962114730087f,
0.0652640721110309f,
0.0660330982355974f,
0.0652640721110309f,
0.0629962114730087f,
0.0593451246895173f,
0.0544967845816832f,
0.0486978400932577f,
0.0422427786903709f,
0.0354586185100425f,
0.0286879389594637f,
0.0222711447846357f,
0.0165288970204929f,
0.0117456327507358f,
0.00815503499250421f,
0.00592820768243009f,
0.00516516454302776f
};
#endif

/* ------------------------------------------------------------------
 * Global variables for FIR LPF Example
 * ------------------------------------------------------------------- */

uint32_t blockSize = BLOCK_SIZE;
uint32_t numBlocks = TEST_LENGTH_SAMPLES/BLOCK_SIZE;

float32_t  snr;

/* ----------------------------------------------------------------------
 * FIR LPF Example
 * ------------------------------------------------------------------- */
int main()
{
    /* ----------------------------------------------------------------------
    ** Get testInput data from sensor (sample 320 at rate 48kHz)
    ** ------------------------------------------------------------------- */
    float sensor_value = 0;
    int16_t pDataXYZ[3] = {0};
    float pGyroDataXYZ[3] = {0};
    int j=0;

    float32_t testInput[320];

    printf("Start sensor init\n");

    BSP_TSENSOR_Init();
    BSP_HSENSOR_Init();
    BSP_PSENSOR_Init();

    BSP_MAGNETO_Init();
    BSP_GYRO_Init();
    BSP_ACCELERO_Init();

    while(j<320) {
        // printf("\nNew loop, LED1 should blink during sensor read\n");
        printf("\n-------------------------------------------\n");

        BSP_ACCELERO_AccGetXYZ(pDataXYZ);
        printf("\nACCELERO_X = %d\n", pDataXYZ[0]); 
        printf("ACCELERO_Y = %d\n", pDataXYZ[1]);
        printf("ACCELERO_Z = %d\n", pDataXYZ[2]);

        // led = 0;
        // ms
        testInput[j] = pDataXYZ[2]; // use z-axis accelerate data as observe target
        ThisThread::sleep_for(2.08/100);
        //ThisThread::sleep_for(100);
        j++;
    }
    printf("\n---------------------END------------------\n");

    // FIR example
    uint32_t i;
    arm_fir_instance_f32 S;
    arm_status status;
    float32_t  *inputF32, *outputF32;

    /* Initialize input and output buffer pointers */
    inputF32 = &testInput[0];
    outputF32 = &testOutput[0];

    /* Call FIR init function to initialize the instance structure. */
    arm_fir_init_f32(&S, NUM_TAPS, (float32_t *)&firCoeffs32[0], &firStateF32[0], blockSize);

    /* ----------------------------------------------------------------------
    ** Call the FIR process function for every blockSize samples
    ** ------------------------------------------------------------------- */

    for(i=0; i < numBlocks; i++)
    {
        arm_fir_f32(&S, inputF32 + (i * blockSize), outputF32 + (i * blockSize), blockSize);
    }

    /* ----------------------------------------------------------------------
    ** result in testOutput
    ** input in testInput
    ** ------------------------------------------------------------------- */
    printf("\n----------start print output signal-------------\n");
    printf("\nidx:   OUTPUT:         INPUT:   \n");
    for (size_t k=0;k<320;k++){
        printf("%d", k);
        printf("    %f", testOutput[k]);
        printf("    %f", testInput[k]);
        printf("\n");
    }
}
