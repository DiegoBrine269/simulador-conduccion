/*
 * File:   Encoder.c
 * Author: Ismael Cervantes de Anda
 * Circuito  para leer los pulsos de un encoder
 * Created on 15 de marzo de 2024, 11:10 AM
 */

// PIC18F4550 Configuration Bit Settings

// 'C' source line config statements

// CONFIG1L
#pragma config PLLDIV = 1       // PLL Prescaler Selection bits (No prescale (4 MHz oscillator input drives PLL directly))
#pragma config CPUDIV = OSC1_PLL2// System Clock Postscaler Selection bits ([Primary Oscillator Src: /1][96 MHz PLL Src: /2])
#pragma config USBDIV = 1       // USB Clock Selection bit (used in Full-Speed USB mode only; UCFG:FSEN = 1) (USB clock source comes directly from the primary oscillator block with no postscale)

// CONFIG1H
#pragma config FOSC = XT_XT     // Oscillator Selection bits (XT oscillator (XT))
#pragma config FCMEN = OFF      // Fail-Safe Clock Monitor Enable bit (Fail-Safe Clock Monitor disabled)
#pragma config IESO = OFF       // Internal/External Oscillator Switchover bit (Oscillator Switchover mode disabled)

// CONFIG2L
#pragma config PWRT = ON        // Power-up Timer Enable bit (PWRT enabled)
#pragma config BOR = ON         // Brown-out Reset Enable bits (Brown-out Reset enabled in hardware only (SBOREN is disabled))
#pragma config BORV = 3         // Brown-out Reset Voltage bits (Minimum setting 2.05V)
#pragma config VREGEN = OFF     // USB Voltage Regulator Enable bit (USB voltage regulator disabled)

// CONFIG2H
#pragma config WDT = OFF        // Watchdog Timer Enable bit (WDT disabled (control is placed on the SWDTEN bit))
#pragma config WDTPS = 32768    // Watchdog Timer Postscale Select bits (1:32768)

// CONFIG3H
#pragma config CCP2MX = ON      // CCP2 MUX bit (CCP2 input/output is multiplexed with RC1)
#pragma config PBADEN = ON      // PORTB A/D Enable bit (PORTB<4:0> pins are configured as analog input channels on Reset)
#pragma config LPT1OSC = OFF    // Low-Power Timer 1 Oscillator Enable bit (Timer1 configured for higher power operation)
#pragma config MCLRE = ON       // MCLR Pin Enable bit (MCLR pin enabled; RE3 input pin disabled)

// CONFIG4L
#pragma config STVREN = ON      // Stack Full/Underflow Reset Enable bit (Stack full/underflow will cause Reset)
#pragma config LVP = OFF        // Single-Supply ICSP Enable bit (Single-Supply ICSP disabled)
#pragma config XINST = OFF      // Extended Instruction Set Enable bit (Instruction set extension and Indexed Addressing mode disabled (Legacy mode))

// CONFIG5L
#pragma config CP0 = ON         // Code Protection bit (Block 0 (000800-001FFFh) is not code-protected)
#pragma config CP1 = ON         // Code Protection bit (Block 1 (002000-003FFFh) is not code-protected)
#pragma config CP2 = ON         // Code Protection bit (Block 2 (004000-005FFFh) is not code-protected)
#pragma config CP3 = ON         // Code Protection bit (Block 3 (006000-007FFFh) is not code-protected)

// CONFIG5H
#pragma config CPB = OFF         // Boot Block Code Protection bit (Boot block (000000-0007FFh) is not code-protected)
#pragma config CPD = ON          // Data EEPROM Code Protection bit (Data EEPROM is not code-protected)

// CONFIG6L
#pragma config WRT0 = OFF       // Write Protection bit (Block 0 (000800-001FFFh) is not write-protected)
#pragma config WRT1 = OFF       // Write Protection bit (Block 1 (002000-003FFFh) is not write-protected)
#pragma config WRT2 = OFF       // Write Protection bit (Block 2 (004000-005FFFh) is not write-protected)
#pragma config WRT3 = OFF       // Write Protection bit (Block 3 (006000-007FFFh) is not write-protected)

// CONFIG6H
#pragma config WRTC = OFF       // Configuration Register Write Protection bit (Configuration registers (300000-3000FFh) are not write-protected)
#pragma config WRTB = OFF       // Boot Block Write Protection bit (Boot block (000000-0007FFh) is not write-protected)
#pragma config WRTD = OFF       // Data EEPROM Write Protection bit (Data EEPROM is not write-protected)

// CONFIG7L
#pragma config EBTR0 = OFF      // Table Read Protection bit (Block 0 (000800-001FFFh) is not protected from table reads executed in other blocks)
#pragma config EBTR1 = OFF      // Table Read Protection bit (Block 1 (002000-003FFFh) is not protected from table reads executed in other blocks)
#pragma config EBTR2 = OFF      // Table Read Protection bit (Block 2 (004000-005FFFh) is not protected from table reads executed in other blocks)
#pragma config EBTR3 = OFF      // Table Read Protection bit (Block 3 (006000-007FFFh) is not protected from table reads executed in other blocks)

// CONFIG7H
#pragma config EBTRB = OFF      // Boot Block Table Read Protection bit (Boot block (000000-0007FFh) is not protected from table reads executed in other blocks)

// #pragma config statements should precede project file includes.
// Use project enums instead of #define for ON and OFF.

#include <xc.h>
#include <pic18f4550.h>

#define _XTAL_FREQ 4000000

#define SenPres PORTAbits.RA0
#define LedInt LATAbits.LATA3
#define LedIzq LATAbits.LATA4
#define LedDer LATAbits.LATA5

#define EncoderA PORTBbits.RB7
#define EncoderB PORTBbits.RB6

#define RxUART PORTCbits.RC7
#define TxUART LATCbits.LATC6

#define EEPGD EECON1bits.EEPGD
#define WR EECON1bits.WR
#define WREN EECON1bits.WREN
#define RD EECON1bits.RD
#define EEIE PIE2bits.EEIE
#define EEIF PIR2bits.EEIF

#define SPEN RCSTAbits.SPEN
#define CREN RCSTAbits.CREN
#define RCIE PIE1bits.RCIE
#define TXIE PIE1bits.TXIE
#define TXIF PIR1bits.TXIF
#define RCIF PIR1bits.RCIF
#define TRMT TXSTAbits.TRMT

#define RBIF INTCONbits.RBIF
#define RBIE INTCONbits.RBIE
#define RBIP INTCON2bits.RBIP

#define ADIF PIR1bits.ADIF
#define ADIE PIE1bits.ADIE
#define ADIP IPR1bits.ADIP
#define GO_DONE ADCON0bits.GO_DONE

#define RCIP IPR1bits.RCIP
#define IPEN RCONbits.IPEN

#define GIE INTCONbits.GIE
#define PEIE INTCONbits.PEIE

char TempPORTB;
char FinRx;
char BanderaRx;
char TxUSART;
char tempoActivado;
char BanderaRx;

char BanGiro;
char MovEncoder;
char Giro;
int TiempoGiro;
char PulsosA;
char PulsosB;
char NumRevoluciones;
char PosInicial;

char BanderaADC;
char SupSenPedal;
char InfSenPedal;
char TempCHS;
char VarCHS;

char MensajeRx[] = "xxx\n";

void __interrupt(high_priority) VectorInterrupcion(void)
{
    if (EEIF == 1) {
        EEIF = 0;
    }                                                  //interrupción por fin de escritura en EEPROM
    if (RBIF == 1)  {
        if (TempPORTB == 0)    
            PosInicial = 0;
        if (TempPORTB == 192)   
            PosInicial = 1;
        if (TempPORTB == 128) 
            PosInicial = 2;
        if (TempPORTB == 64)
            PosInicial = 2;
        if (EncoderA == PosInicial) {}
                                            else    {   if (PosInicial == 2)    {}
                                                        else    {   Giro = 'I';
                                                                    LedDer = 1;
                                                                    LedIzq = 0;
                                                                    PulsosA = PulsosA + 1;
                                                                    if (PulsosA == 20)  {   PulsosA = 0;
                                                                                            NumRevoluciones = NumRevoluciones + 1;}
                                                                    PulsosB = 0;
                                                                    MovEncoder = 1;
                                                                    BanGiro = 1;
                                                                    TiempoGiro = 0;
                                                                }
                                                    }
                        if (EncoderB == PosInicial) {}
                                            else    {   if (PosInicial == 2)    {}
                                                        else    {   Giro = 'D';
                                                                    LedIzq = 1;
                                                                    LedDer = 0;
                                                                    PulsosB = PulsosB + 1;
                                                                    if (PulsosB == 20)  {   PulsosB = 0;
                                                                                            NumRevoluciones = NumRevoluciones + 1;}
                                                                    PulsosA = 0;
                                                                    MovEncoder = 1;
                                                                    BanGiro = 1;
                                                                    TiempoGiro = 0;
                                                                }
                                                    }
                        TempPORTB = PORTB & 0B11000000;
                        RBIF = 0;
                        GIE = 1;
                    }
    if (RCIF == 1)                                                              //Interrupción por uso de UART (RS-232)
                    {   MensajeRx[BanderaRx] = RCREG;
                        BanderaRx = BanderaRx + 1;
                        if (BanderaRx != 0) {   tempoActivado = 1;}
                        if (BanderaRx == 2) {   BanderaRx = 0;                  //Recepciona la cantidad de 2 Bytes
                                                FinRx = 1;
                                                tempoActivado = 0;
                                            }
                        RCIF = 0;                                               //Limpia la bandera de interrupción por recepción
                        GIE = 1;                                                //Activa las interrupciones
                    }
    if (ADIF == 1)  {   
        SupSenPedal = ADRESH;    //Interrupción por ADC
        InfSenPedal = ADRESL;
        BanderaADC = 1;
        ADIF = 0;
        GIE = 1;                //Activación general de interrupciones
    }
}

void ConfigPIC(void)
{
    TRISA = 0B00000111;         //Puerto A
    TRISB = 0B11000111;         //Puerto B
    TRISC = 0B10111111;         //Bits 6 salida demás como entradas del puerto C
    TRISD = 0B00000000;
    IPEN = 1;                   //Activa los niveles de prioridad en las interrupciones
    LATB = 0;
    ADCON1 = 0X0F;              //Configura los pines del puerto A y B (que tienen acceso a los A/D) como Entradas/Salidas digitales
    CMCON = 0X07;               //Configura los pines del puerto A (que tienen acceso a comparadores de voltaje) como Entradas/Salidas digitales
    
    PosInicial = 2;
    BanGiro = 0;
    MovEncoder = 0;
    FinRx = 0;
    BanderaRx = 0;
}

void ConfigPIC2(void)
{   
    TempPORTB = PORTB & 0B11000000;
    RBIF = 0;                   //Limpia bandera
    RBIE = 1;                   //Activa las interrupciones para detectar cambio de estado en las terminales 7, 6, 5 y 4 del puerto B (para emplearse en la detección de los pulsos del encoder)
    RBIP = 1;                   //Asigna alta prioridad en la interrupción pro cambio de estado en las terminales del nibble superior del puerto B
    
    GIE = 1;                    //Activar habilitador general de interrupciones.
    PEIE = 1;                   //Activar habilitador general de interrupciones por perifericos.
    
    //ComienzoGiro = 1;
    PulsosA = 0;
    PulsosB = 0;
}

void ConfigADC(void)
{   ADCON0 = 0B00000001;        //Activa el módulo ADC
    ADCON1 = 0B00001100;        //Configurar las terminales de AN0 ,AN1 y AN2 de acceso al ADC como analógicas demas terminales como digitales
    ADCON2 = 0B10100001;        //Justifica a la derecha, 8TDA, Fosc/8
    ADIP = 1;                   //Alta prioridad
    ADIE = 1;                   //Activación de interrupción por ADC
    ADIF = 0;
    GIE = 1;                    //Activación de interrpciones
    PEIE = 1;                   //Activación de interrupciones por periférico
}

void ConfigUSART(void)          //Configuracion_USART  9600 BPS, sin bit de paridad, 1 bit stop
{
	TXSTA = 0B00100110;
    RCSTA = 0B10010000;
                                //Este bit es parte del registro RCSTA    SPEN =1;                    //Habilitacion del puerto de comunicacion serial
                                //Este bit es parte del registro RCSTA    CREN = 1;                   //Activa la recepcion continua
    BAUDCON = 0B00000010;
    SPBRG = 25;
    TXIE = 0;                   //Desactiva interrupción por fin de transmición por usart.
    RCIP = 1;                   //Asigna alta prioridad a la interrupción por recepción por usart
    TXIF = 0;
    RCIF = 0;
    RCIE = 1;                   //Activar interrupción por fin de recepción por usart.
    GIE = 1;                    //Activar habilitador general de interrupciones.
    PEIE = 1;                   //Activar habilitador general de interrupciones por perifericos.
    RCREG = 0;
}

void Transmite(void)            //Transmite por RS-232 9600 BPS, sin bit de paridad, 1 bit stop
{
	TXSTA = 0B00100110;
    SPBRG = 25;
    TXREG = TxUSART;
    while(!TXIF);
    while(!TRMT);               //Esta bandera es la que funciona para detectar cuando se vacia el buffer de transmisión
}

void InicializaLeds(void)
{
    LedInt = 1;
    LedIzq = 1;
    LedDer = 1;
    __delay_ms(300);
    LedInt = 0;
    LedIzq = 0;
    LedDer = 0;
    __delay_ms(300);
    LedInt = 1;
    LedIzq = 1;
    LedDer = 1;
    __delay_ms(300);
    LedInt = 0;
    LedIzq = 0;
    LedDer = 0;
    __delay_ms(300);
    LedInt = 1;
    LedIzq = 1;
    LedDer = 1;
    __delay_ms(300);
    LedInt = 0;
    LedIzq = 0;
    LedDer = 0;
}

void PedalAcelerador (void)
{
    TxUSART = 'A';         //Transmite identificador de Encoder
    Transmite();
    __delay_us(10);
    TxUSART = InfSenPedal;
    Transmite();
    __delay_us(10);   
    TxUSART = SupSenPedal;
    Transmite();
    __delay_us(10);    
}
    
void PedalFreno (void)
{
    TxUSART = 'F';         //Transmite identificador de Encoder
    Transmite();
    __delay_us(10);
    TxUSART = InfSenPedal;
    Transmite();
    __delay_us(10);
    TxUSART = SupSenPedal;
    Transmite();
    __delay_us(10);    
}

void PedalClutch (void)
{
    TxUSART = 'C';         //Transmite identificador de Encoder
    Transmite();
    __delay_us(10);
    TxUSART = InfSenPedal;
    Transmite();
    __delay_us(10);       
    TxUSART = SupSenPedal;
    Transmite();
    __delay_us(10);    
}

void main(void)
{
    ConfigPIC();
    InicializaLeds();
    ConfigPIC2();
    ConfigADC();
    ConfigUSART();

    while (1)
    {   if (PosInicial == 2)    {}
        if ((PosInicial == 0||PosInicial == 1)&&MovEncoder == 1)   {   TxUSART = 'G';         //Transmite identificador de Encoder
                                                                    Transmite();
                                                                    __delay_us(10);
                                                                    TxUSART = Giro;
                                                                    Transmite();
                                                                    __delay_us(10);

                                                                    MovEncoder = 0;
                                                                }
        if (BanGiro == 1)   {   __delay_us(100);
                                TiempoGiro = TiempoGiro + 1;
                                if (TiempoGiro == 100)  {   BanGiro = 0;
                                                            TiempoGiro = 0;
                                                            MovEncoder = 0;
                                                            PulsosA = 0;
                                                            PulsosB = 0;
                                                            Giro = 0;
                                                            LedIzq = 0;
                                                            LedDer = 0;
                                                        }
                            }
        for(VarCHS = 0; VarCHS < 3; VarCHS++)   {   TempCHS = VarCHS << 2;              //Digitaliza los valores analógicos de los pedales
                                                    ADCON0 = TempCHS;
                                                    ADON = 1;
                                                    GO_DONE = 1;    //Iniciar la operación del ADC
                                                    while (BanderaADC == 0) {}  //Espera que termine proceso de digitalización del ADC
                                                    if (BanderaADC == 1)    {   BanderaADC = 0;}
                                                    switch  (VarCHS)    {   case 0: PedalAcelerador (); //Selecciona función de envio de información del pedal acelerador
                                                                            break;
                                                                            case 1: PedalFreno ();      //Selecciona función de envio de información del pedal freno
                                                                            break;
                                                                            case 2: PedalClutch ();     //Selecciona función de envio de información del pedal clutch
                                                                            break;
                                                                        }
                                                }
    }
    return;
}