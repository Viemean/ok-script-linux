#include <stdint.h>
#include <stddef.h>

void ab30_to_bgr24(const uint32_t *src, uint8_t *dst, int width, int height, int stride_pixels) {
    for (int y = 0; y < height; y++) {
        const uint32_t *__restrict__ row_src = src + (size_t)y * stride_pixels;
        uint8_t *__restrict__ row_dst = dst + (size_t)y * width * 3;
        for (int x = 0; x < width; x++) {
            uint32_t p = row_src[x];
            row_dst[x * 3 + 0] = (uint8_t)((p >> 22) & 0xFF);        // B: (p >> 20) >> 2
            row_dst[x * 3 + 1] = (uint8_t)(((p >> 10) & 0x3FF) >> 2); // G
            row_dst[x * 3 + 2] = (uint8_t)((p & 0x3FF) >> 2);        // R
        }
    }
}
