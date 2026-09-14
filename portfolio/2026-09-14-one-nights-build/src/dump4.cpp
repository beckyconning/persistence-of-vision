// descent: escape-count fields of the Misiurewicz point M(23,2) at 32 zooms (x1.18 each), 200x200, one file
#include "cpu_render.h"
#include "shaders/perturb_step.hlsli"
#include <cmath>
#include <cstdio>
#include <fstream>
int main(int argc, char **argv) {
    std::ifstream in(argv[1]); std::string line; std::getline(in, line);
    std::string name = line.substr(0, line.find(' '));
    View base; uint32_t it; location_parse(line.substr(name.size()), base, it);
    const int W = 200, H = 200, F = 32;
    FILE *f = fopen(argv[2], "wb");
    for (int k = 0; k < F; ++k) {
        View v = base;
        view_set_zoom(v, 1e40 * std::pow(1.18, k));
        RefOrbit o; ref_compute(o, v.re, v.im, limbs_for_spacing(view_spacing(v, H)), 65537);
        std::vector<CpuPixel> px; cpu_render_perturb(o, v, W, H, 65536, px);
        uint32_t mx = 0; for (auto &p : px) { float val = p.status == 1 ? (float)p.n + p.frac : -1.0f; fwrite(&val, 4, 1, f); if (p.status == 1 && p.n > mx) mx = p.n; }
        fprintf(stderr, "frame %d zoom %.3g max n %u\n", k, v.zoom, mx);
    }
    fclose(f);
}
