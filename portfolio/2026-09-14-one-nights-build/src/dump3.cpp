// dump n+frac for a location at W x H with the view centre shifted so the spiral sits at the left third
#include "cpu_render.h"
#include "shaders/perturb_step.hlsli"
#include <cstdio>
#include <fstream>
int main(int argc, char **argv) {
    std::ifstream in(argv[1]); std::string line; std::getline(in, line);
    std::string name = line.substr(0, line.find(' '));
    View v; uint32_t it; location_parse(line.substr(name.size()), v, it);
    const int W = 400, H = 400;


    RefOrbit o; ref_compute(o, v.re, v.im, limbs_for_spacing(view_spacing(v, H)), 4 * it + 1);
    std::vector<CpuPixel> px; cpu_render_perturb(o, v, W, H, 4 * it, px);
    FILE *f = fopen(argv[2], "wb");
    int capped = 0;
    for (auto &p : px) { float val = p.status == 1 ? (float)p.n + p.frac : -1.0f; if (p.status != 1) ++capped; fwrite(&val, 4, 1, f); }
    fclose(f);
    printf("%s zoom %.3g iters %u capped %d\n", name.c_str(), v.zoom, 4 * it, capped);
}
