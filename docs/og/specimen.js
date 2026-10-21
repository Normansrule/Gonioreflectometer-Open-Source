/* The raking-light specimen: three strips (PTFE, mirror, printed black ABS) under one lamp that follows the pointer.
   Shading is the same Lambert + GGX (Schlick Fresnel, height-correlated Smith) model as
   software/src/opengonio/brdf/models.py. PTFE and the mirror use the simulator's materials (sim.py: Lambert 0.99;
   GGX base 0.9, roughness 0.1, metallic 1); the printed-ABS values and its bead texture are illustrative, not measured.
   It is a rendering, and the page says so.
   SPDX-License-Identifier: GPL-3.0-or-later */
(function () {
  const VERT = `attribute vec2 p; void main(){ gl_Position = vec4(p, 0.0, 1.0); }`;
  const FRAG = `
#ifdef GL_OES_standard_derivatives
#extension GL_OES_standard_derivatives : enable
#endif
precision highp float;
uniform vec2 uRes; uniform float uShift; uniform vec3 uLamp; uniform vec3 uCam; uniform vec3 uGround; uniform vec3 uLightCol;
uniform float uFov; uniform float uExposure;
const float PI = 3.14159265;
float hash(float n){ return fract(sin(n) * 43758.5453); }
float noise(vec2 x){ vec2 i = floor(x), f = fract(x); f = f*f*(3.0-2.0*f);
  float n = i.x + i.y*57.0;
  return mix(mix(hash(n), hash(n+1.0), f.x), mix(hash(n+57.0), hash(n+58.0), f.x), f.y); }
float ggxD(float ch, float a){ float a2 = a*a; float d = ch*ch*(a2-1.0)+1.0; return a2/(PI*d*d); }
float smithG2(float ci, float co, float a){ float a2 = a*a;
  float li = co*sqrt(ci*ci*(1.0-a2)+a2), lo = ci*sqrt(co*co*(1.0-a2)+a2); return 2.0*ci*co/(li+lo); }
// models.py ggx_brdf, per channel base colour
vec3 brdf(vec3 n, vec3 wi, vec3 wo, vec3 base, float rough, float metal){
  float ci = dot(n, wi), co = dot(n, wo); if (ci <= 0.0 || co <= 0.0) return vec3(0.0);
  vec3 h = normalize(wi + wo); float a = max(rough*rough, 1e-4);
  vec3 f0 = mix(vec3(0.04), base, metal);
  vec3 F = f0 + (1.0 - f0) * pow(1.0 - clamp(dot(wi, h), 0.0, 1.0), 5.0);
  vec3 spec = ggxD(max(dot(h, n), 0.0), a) * smithG2(ci, co, a) * F / (4.0*ci*co);
  vec3 diff = (1.0 - metal) * (1.0 - F) * base / PI;
  return diff + spec; }
vec3 aces(vec3 x){ return clamp((x*(2.51*x+0.03))/(x*(2.43*x+0.59)+0.14), 0.0, 1.0); }
void main(){
  vec2 uv = (gl_FragCoord.xy - 0.5*uRes) / uRes.y; uv.x -= uShift;   // uShift: specimen centre moved right of the canvas centre
  vec3 fw = normalize(-uCam), rt = normalize(cross(fw, vec3(0.0, 0.0, 1.0))), up = cross(rt, fw);
  vec3 rd = normalize(fw + (uv.x*rt + uv.y*up) * tan(uFov*0.5)*2.0);
  vec3 col = uGround;
  if (rd.z < 0.0) {
    float t = -uCam.z / rd.z; vec3 P = uCam + rd*t;
    vec3 n = vec3(0.0, 0.0, 1.0); vec3 base; float rough, metal, inside = 1.0, lambertOnly = 0.0;
    float x = P.x, y = P.y;
    if (abs(y) > 1.15 || abs(x) > 1.62) inside = 0.0;
    if (x < -0.53) {                         // PTFE: the white reference, almost perfectly diffuse
      if (x > -0.56) inside = 0.0;
      base = vec3(0.99); rough = 1.0; metal = 0.0; lambertOnly = 1.0;
      float g = noise(P.xy*120.0) - 0.5;
      n = normalize(vec3(0.05*g, 0.05*(noise(P.yx*110.0) - 0.5), 1.0));
    } else if (x < 0.53) {                   // mirror: polished, with a faint long-wave roll
      if (x < -0.5 || x > 0.5) inside = 0.0;
      base = vec3(0.9); rough = 0.1; metal = 1.0;
      n = normalize(vec3(0.006*sin(y*7.0 + 1.3) + 0.002*sin(y*31.0), 0.004*sin(x*9.0), 1.0));
    } else {                                 // printed black ABS: 0.2 mm beads along y, shown up by grazing light
      if (x < 0.56) inside = 0.0;
      float pitch = 0.03, k = x / pitch, cell = floor(k), u = fract(k)*2.0 - 1.0;
      float w = 0.85 + 0.3*hash(cell);
      float s = -u / sqrt(max(1.0 - u*u, 0.05)) * 0.6 * w;
      #ifdef GL_OES_standard_derivatives
      s *= clamp(1.5 - fwidth(k)*1.6, 0.0, 1.0);   // fade beads smaller than a pixel instead of aliasing
      #endif
      float seam = smoothstep(0.8, 1.0, abs(u));
      n = normalize(vec3(s, 0.12*(noise(vec2(cell*3.1, y*24.0)) - 0.5), 1.0));
      base = vec3(0.035, 0.034, 0.032) * (1.0 - 0.4*seam); rough = 0.3; metal = 0.0;
    }
    if (inside > 0.5) {
      vec3 L = uLamp - P; float d2 = dot(L, L); vec3 wi = L / sqrt(d2); vec3 wo = normalize(uCam - P);
      vec3 E = uLightCol * 9.0 / d2 * max(dot(n, wi), 0.0);
      vec3 f = lambertOnly > 0.5 ? (dot(n, wi) > 0.0 && dot(n, wo) > 0.0 ? base / PI : vec3(0.0)) : brdf(n, wi, wo, base, rough, metal);
      col = f * E * uExposure;
      col = pow(aces(col), vec3(1.0/2.2));
    }
  }
  gl_FragColor = vec4(col, 1.0);
}`;

  function make(canvas, opts) {
    const gl = canvas.getContext("webgl", { antialias: false, preserveDrawingBuffer: !!opts.keep, alpha: false });
    if (!gl) return null;
    gl.getExtension("OES_standard_derivatives");
    const sh = (type, src) => { const s = gl.createShader(type); gl.shaderSource(s, src); gl.compileShader(s);
      if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(s)); return s; };
    const prog = gl.createProgram();
    gl.attachShader(prog, sh(gl.VERTEX_SHADER, VERT)); gl.attachShader(prog, sh(gl.FRAGMENT_SHADER, FRAG));
    gl.linkProgram(prog); if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(prog));
    gl.useProgram(prog);
    const buf = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, buf);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
    const loc = gl.getAttribLocation(prog, "p"); gl.enableVertexAttribArray(loc); gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
    const U = n => gl.getUniformLocation(prog, n);
    const u = { shift: U("uShift"), res: U("uRes"), lamp: U("uLamp"), cam: U("uCam"), ground: U("uGround"), light: U("uLightCol"), fov: U("uFov"), exp: U("uExposure") };
    const CAM_DEG = 35;                                // the fixed camera: 35 degrees from the sample normal
    return {
      CAM_DEG,
      draw(thetaDeg, phiDeg, sx = 0) {   // sx: centre the specimen this fraction of the width right of centre
        const dpr = Math.min(window.devicePixelRatio || 1, 1.75), w = Math.round(canvas.clientWidth * dpr), h = Math.round(canvas.clientHeight * dpr);
        if (!w || !h) return;
        if (canvas.width !== w || canvas.height !== h) { canvas.width = w; canvas.height = h; }
        gl.viewport(0, 0, w, h);
        const aspect = w / h, fov = 30 * Math.PI / 180;
        const room = aspect * 2 * (sx > 0 ? Math.min(0.5 - sx, sx + 0.1) : 0.5), need = Math.max(1.85 / (Math.tan(fov / 2) * room), 1.3 / Math.tan(fov / 2));   // fit the three strips
        const c = CAM_DEG * Math.PI / 180, th = thetaDeg * Math.PI / 180, ph = phiDeg * Math.PI / 180, r = 3.2;
        const K = OG.tokens();
        gl.uniform2f(u.res, w, h); gl.uniform1f(u.shift, sx * aspect);
        gl.uniform3f(u.cam, 0, -need * Math.sin(c), need * Math.cos(c));
        gl.uniform3f(u.lamp, r * Math.sin(th) * Math.cos(ph), r * Math.sin(th) * Math.sin(ph), r * Math.cos(th));
        gl.uniform3fv(u.ground, OG.rgb(K.ground));
        gl.uniform3f(u.light, 1.0, 0.74, 0.45);       // 3000 K, linear
        gl.uniform1f(u.fov, fov); gl.uniform1f(u.exp, 1.15);
        gl.drawArrays(gl.TRIANGLES, 0, 3);
        this.view = { cam: [0, -need * Math.sin(c), need * Math.cos(c)], fov, w: canvas.clientWidth, h: canvas.clientHeight, sx };
      },
      /* world point on the sample plane -> CSS pixels in the canvas (for labels under each strip) */
      project(x, y) {
        const v = this.view; if (!v) return null;
        const C = v.cam, n = Math.hypot(...C), fw = C.map(q => -q / n), rt = [1, 0, 0];
        const up = [rt[1] * fw[2] - rt[2] * fw[1], rt[2] * fw[0] - rt[0] * fw[2], rt[0] * fw[1] - rt[1] * fw[0]];
        const d = [x - C[0], y - C[1], -C[2]], z = d[0] * fw[0] + d[1] * fw[1] + d[2] * fw[2];
        const k = 1 / (Math.tan(v.fov / 2) * 2 * z);
        const sx = (d[0] * rt[0] + d[1] * rt[1] + d[2] * rt[2]) * k, sy = (d[0] * up[0] + d[1] * up[1] + d[2] * up[2]) * k;
        return [v.w / 2 + v.sx * v.w + sx * v.h, v.h / 2 - sy * v.h];
      },
    };
  }
  window.Specimen = { make };
})();
