#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <stdlib.h>
#include <signal.h>
#include <stdint.h>

int main() {
    char input[32] = {0};

    // Fuzzer input
    ssize_t n = read(0, input, 31);
    if (n < 8) return 0;

    // ========================================================================
    // 1: 32-bit (Block Casting) + XOR
    // ========================================================================
    // 'M'(0x4D), 'a'(0x61), 'n'(0x6E), 'h'(0x68). 
    // Little-Endian 0x686E614D. 0x686E614D ^ 0xDEADBEEF = 0xB6C3DFA2
    uint32_t *block1 = (uint32_t *)input;
    if ((*block1 ^ 0xDEADBEEF) == 0xB6C3DFA2) {
        printf("[+] Access Granted: Path 1 (Manh). Triggering SIGABRT...\n");
        abort(); 
    }

    // ========================================================================
    // 2 (Linear Equation System)
    // ========================================================================
    // Nghiệm mong muốn: 'V' (86) và 'N' (78)
    // 86 + 78 = 164;  86 - 78 = 8
    if (input[0] == 'U' && input[1] == 'E' && input[2] == 'T') {
        if (input[3] + input[4] == 164 && input[3] - input[4] == 8) {
            printf("[+] Access Granted: Path 2 (UETVN). Triggering SIGSEGV...\n");
            raise(SIGSEGV);
        }
    }

    // ========================================================================
    // 3 (Checksum / Accumulator)
    // ========================================================================
    if (n >= 10 && memcmp(input, "SECURE", 6) == 0) {
        //'B'(66), 'U'(85), 'G'(71) -> 66 + 85 + 71 = 222
        if (input[6] + input[7] + input[8] == 222) {
            if (input[6] == 'B' && (input[7] ^ 0x11) == 0x44) { // 0x44 ^ 0x11 = 0x55 ('U')
                printf("[+] Access Granted: Path 3 (SECUREBUG). Triggering SIGILL...\n");
                raise(SIGILL);
            }
        }
    }

    return 0;
}
