// dump escape counts of a location line at W x H (CPU perturbation and direct parity summary)
#include "cpu_render.h"
#include "shaders/perturb_step.hlsli"
#include <cstdio>
#include <fstream>
#include <set>
int main(int argc, char **argv) {
    std::ifstream in(argv[1]); std::string line; std::getline(in, line);
    std::string name = line.substr(0, line.find(' '));
    View v; uint32_t it; location_parse(line.substr(name.size()), v, it);
    const int W = 192, H = 108;
    RefOrbit o; ref_compute(o, v.re, v.im, limbs_for_spacing(view_spacing(v, H)), it + 1);
    std::vector<CpuPixel> px; cpu_render_perturb(o, v, W, H, it, px);
    FILE *f = fopen(argv[2], "wb"); std::set<uint32_t> d;
    for (auto &p : px) { fwrite(&p.n, 4, 1, f); fwrite(&p.frac, 4, 1, f); if (p.status == 1) d.insert(p.n); }
    fclose(f);
    printf("%s iters %u reflen %u escaped distinct %zu min %u max %u\n", name.c_str(), it, o.length(), d.size(), d.empty()?0:*d.begin(), d.empty()?0:*d.rbegin());
}
