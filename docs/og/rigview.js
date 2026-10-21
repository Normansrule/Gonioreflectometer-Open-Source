/* The four-axis view: the CAD assembly (og/model/rig.js, from tools/cad/assembly.py) drawn in WebGL and moved with the
   same rotations as the CAD clash check (tools/cad/poses.py), lit by its own lamp. Plays the axes in turn; the
   sliders drive it by hand. Angles shown use the software's kinematics (opengonio/gantry/kinematics.py).
   SPDX-License-Identifier: GPL-3.0-or-later */
(function () {
  const VERT = `
attribute vec3 aPos; attribute vec3 aNrm; attribute float aGroup; attribute float aColor;
uniform mat4 uVP; uniform mat4 uG[5]; uniform float uScale;
varying vec3 vN; varying vec3 vW; varying float vC; varying float vG;
mat4 pick(float g){ if (g < 0.5) return uG[0]; if (g < 1.5) return uG[1]; if (g < 2.5) return uG[2]; if (g < 3.5) return uG[3]; return uG[4]; }
void main(){
  mat4 M = pick(aGroup);
  vec4 w = M * vec4(aPos * uScale, 1.0);
  vW = w.xyz; vN = normalize(mat3(M) * aNrm); vC = aColor; vG = aGroup;
  gl_Position = uVP * w;
}`;
  const FRAG = `
precision highp float;
varying vec3 vN; varying vec3 vW; varying float vC; varying float vG;
uniform vec3 uPal[4]; uniform vec3 uLamp; uniform vec3 uEye; uniform vec3 uLampCol; uniform vec3 uFill;
uniform float uHi[5]; uniform vec3 uHiCol; uniform float uOn;
const float PI = 3.14159265;
vec3 aces(vec3 x){ return clamp((x*(2.51*x+0.03))/(x*(2.43*x+0.59)+0.14), 0.0, 1.0); }
float ggx(float nh, float a){ float a2 = a*a; float d = nh*nh*(a2-1.0)+1.0; return a2/(PI*d*d); }
void main(){
  vec3 base = vC < 0.5 ? uPal[0] : vC < 1.5 ? uPal[1] : vC < 2.5 ? uPal[2] : uPal[3];
  vec3 n = normalize(vN); vec3 v = normalize(uEye - vW);
  if (dot(n, v) < 0.0) n = -n;                                  // thin or open faces
  vec3 L = uLamp - vW; float d2 = dot(L, L); vec3 l = L / sqrt(d2); vec3 h = normalize(l + v);
  float nl = max(dot(n, l), 0.0), nh = max(dot(n, h), 0.0), vh = max(dot(v, h), 0.0);
  float rough = vC < 0.5 ? 0.42 : 0.32;
  float F = 0.04 + 0.96 * pow(1.0 - vh, 5.0);
  float spec = ggx(nh, rough*rough) * F / max(4.0 * nl * max(dot(n, v), 0.05), 0.05) * nl;
  vec3 E = uLampCol * uOn * 260000.0 / d2;                         // the arm's own lamp, inverse square
  vec3 key = (base / PI * nl + spec) * E;
  vec3 fill = base * (0.28 + 0.22 * max(n.z, 0.0)) * uFill + 0.035 * uFill * pow(1.0 - max(dot(n, v), 0.0), 3.0);
  float hi = vG < 0.5 ? uHi[0] : vG < 1.5 ? uHi[1] : vG < 2.5 ? uHi[2] : vG < 3.5 ? uHi[3] : uHi[4];
  vec3 rim = uHiCol * hi * 0.55 * pow(1.0 - max(dot(n, v), 0.0), 2.0);
  vec3 c = aces((key + fill) * 1.15 + rim);
  gl_FragColor = vec4(pow(c, vec3(1.0/2.2)), 1.0);
}`;
  const GLOW_V = `attribute vec2 p; uniform vec2 uC; uniform vec2 uR; varying vec2 vP; void main(){ vP = p; gl_Position = vec4(uC + p * uR, 0.0, 1.0); }`;
  const GLOW_F = `precision mediump float; varying vec2 vP; uniform vec3 uCol; uniform float uA;
void main(){ float r = length(vP); float a = exp(-r*r*5.0) * uA + smoothstep(0.16, 0.08, r) * uA; gl_FragColor = vec4(uCol * a, a); }`;

  /* ---------- small matrix kit (column-major, like WebGL) ---------- */
  const I4 = () => [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1];
  function mul(a, b) { const o = new Array(16).fill(0);
    for (let c = 0; c < 4; c++) for (let r = 0; r < 4; r++) for (let k = 0; k < 4; k++) o[c * 4 + r] += a[k * 4 + r] * b[c * 4 + k]; return o; }
  function rotAbout(p, d, deg) {                              // rotation by deg about the line through p along unit d
    const a = deg * Math.PI / 180, c = Math.cos(a), s = Math.sin(a), C = 1 - c, [x, y, z] = d;
    const R = [c + x * x * C, y * x * C + z * s, z * x * C - y * s, 0, x * y * C - z * s, c + y * y * C, z * y * C + x * s, 0,
               x * z * C + y * s, y * z * C - x * s, c + z * z * C, 0, 0, 0, 0, 1];
    const T = (t) => [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, t[0], t[1], t[2], 1];
    return mul(T(p), mul(R, T(p.map(q => -q))));
  }
  function apply(m, v) { return [0, 1, 2].map(r => m[r] * v[0] + m[4 + r] * v[1] + m[8 + r] * v[2] + m[12 + r]); }
  function lookAt(eye, at, up) {
    const z = norm(sub(eye, at)), x = norm(cross(up, z)), y = cross(z, x);
    return [x[0], y[0], z[0], 0, x[1], y[1], z[1], 0, x[2], y[2], z[2], 0, -dot(x, eye), -dot(y, eye), -dot(z, eye), 1];
  }
  function persp(fov, asp, n, f) { const t = 1 / Math.tan(fov / 2);
    return [t / asp, 0, 0, 0, 0, t, 0, 0, 0, 0, (f + n) / (n - f), -1, 0, 0, 2 * f * n / (n - f), 0]; }
  const sub = (a, b) => a.map((x, i) => x - b[i]), dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
  const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
  const norm = a => { const l = Math.hypot(...a) || 1; return a.map(x => x / l); };

  /* ---------- pose -> group matrices (tools/cad/poses.py) and BRDF angles (kinematics.py) ---------- */
  function groupMatrices(R, pose) {
    const ang = { M1: pose.M1 - R.shown.M1, M2: R.shown.M2 - pose.M2, M3: pose.M3 - R.shown.M3, M4: pose.M4 - R.shown.M4 };
    return R.groups.map(g => {
      let M = I4();
      R.order.forEach(k => { const ax = R.axes[k]; if (ax.moves.includes(g) && Math.abs(ang[k]) > 1e-9) M = mul(rotAbout(ax.point, ax.dir, ang[k]), M); });
      return M;
    });
  }
  function angles(pose) {
    const r = d => d * Math.PI / 180, c = Math.cos, s = Math.sin;
    const m3 = r(pose.M3), m2 = r(-pose.M2), m1 = r(pose.M1);
    // first column of Rz(M3) Ry(-M2) Rx(M1): the sample normal
    const n = [c(m3) * c(m2), s(m3) * c(m2), -s(m2)];
    const l = [c(r(pose.M4)), s(r(pose.M4)), 0], cam = [1, 0, 0];
    const deg = x => Math.acos(Math.max(-1, Math.min(1, x))) * 180 / Math.PI;
    void m1;
    return { ti: deg(dot(n, l)), tr: deg(dot(n, cam)) };
  }

  async function inflate(b64) {
    const bin = Uint8Array.from(atob(b64), ch => ch.charCodeAt(0));
    const ds = new DecompressionStream("deflate");
    return new Uint8Array(await new Response(new Blob([bin]).stream().pipeThrough(ds)).arrayBuffer());
  }

  async function make(canvas, R) {
    const gl = canvas.getContext("webgl", { antialias: true, alpha: false, preserveDrawingBuffer: false });
    if (!gl || typeof DecompressionStream === "undefined" || !gl.getExtension("OES_element_index_uint")) return null;
    const raw = await inflate(R.data);
    const nv = R.vertices, vbytes = nv * 12;
    const sh = (t, src) => { const s = gl.createShader(t); gl.shaderSource(s, src); gl.compileShader(s);
      if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(s)); return s; };
    const prog = (v, f) => { const p = gl.createProgram(); gl.attachShader(p, sh(gl.VERTEX_SHADER, v)); gl.attachShader(p, sh(gl.FRAGMENT_SHADER, f));
      gl.linkProgram(p); if (!gl.getProgramParameter(p, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(p)); return p; };
    const P = prog(VERT, FRAG), G = prog(GLOW_V, GLOW_F);
    const vb = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, vb); gl.bufferData(gl.ARRAY_BUFFER, raw.subarray(0, vbytes), gl.STATIC_DRAW);
    const ib = gl.createBuffer(); gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, ib);
    gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, new Uint32Array(raw.buffer.slice(raw.byteOffset + vbytes, raw.byteOffset + raw.byteLength)), gl.STATIC_DRAW);
    const nIdx = (raw.byteLength - vbytes) / 4;
    const quad = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, quad); gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]), gl.STATIC_DRAW);
    const U = (p, n) => gl.getUniformLocation(p, n);
    const loc = { pos: gl.getAttribLocation(P, "aPos"), nrm: gl.getAttribLocation(P, "aNrm"), grp: gl.getAttribLocation(P, "aGroup"), col: gl.getAttribLocation(P, "aColor") };
    const pal = [];
    for (let i = 0; i < 4; i++) { const c = R.palette[i] || [0.5, 0.5, 0.5];
      pal.push(...(c[0] < 0.2 ? [0.075, 0.075, 0.08] : c));    // printed parts: matte black ABS, as built
    }
    gl.enable(gl.DEPTH_TEST);
    const [lo, hi] = R.bbox, centre = [(lo[0] + hi[0]) / 2 - 40, (lo[1] + hi[1]) / 2, 150];
    const radius = Math.hypot(hi[0] - lo[0], hi[1] - lo[1]) / 2;
    return {
      draw(pose, view, opts) {
        const dpr = Math.min(window.devicePixelRatio || 1, 2), w = Math.round(canvas.clientWidth * dpr), h = Math.round(canvas.clientHeight * dpr);
        if (!w || !h) return;
        if (canvas.width !== w || canvas.height !== h) { canvas.width = w; canvas.height = h; }
        gl.viewport(0, 0, w, h);
        const K = OG.tokens(), bg = OG.rgb(K.ground);
        gl.clearColor(bg[0], bg[1], bg[2], 1); gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
        const yaw = view.yaw * Math.PI / 180, pit = view.pitch * Math.PI / 180, dist = radius * view.zoom / Math.tan(0.31) / Math.min(1, w / h / 1.25);   // whole machine in frame at any aspect
        const eye = [centre[0] + dist * Math.cos(pit) * Math.cos(yaw), centre[1] + dist * Math.cos(pit) * Math.sin(yaw), centre[2] + dist * Math.sin(pit)];
        const VP = mul(persp(0.62, w / h, 20, 6000), lookAt(eye, centre, [0, 0, 1]));
        const Ms = groupMatrices(R, pose);
        const lamp = apply(Ms[R.groups.indexOf("arm")], R.lamp);
        gl.useProgram(P);
        gl.bindBuffer(gl.ARRAY_BUFFER, vb); gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, ib);
        gl.enableVertexAttribArray(loc.pos); gl.vertexAttribPointer(loc.pos, 3, gl.SHORT, false, 12, 0);
        gl.enableVertexAttribArray(loc.nrm); gl.vertexAttribPointer(loc.nrm, 3, gl.BYTE, true, 12, 6);
        gl.enableVertexAttribArray(loc.grp); gl.vertexAttribPointer(loc.grp, 1, gl.BYTE, false, 12, 9);
        gl.enableVertexAttribArray(loc.col); gl.vertexAttribPointer(loc.col, 1, gl.UNSIGNED_BYTE, false, 12, 10);
        gl.uniformMatrix4fv(U(P, "uVP"), false, VP);
        gl.uniformMatrix4fv(U(P, "uG"), false, Ms.flat());
        gl.uniform1f(U(P, "uScale"), R.scale);
        gl.uniform3fv(U(P, "uPal"), pal);
        gl.uniform3fv(U(P, "uLamp"), lamp); gl.uniform3fv(U(P, "uEye"), eye);
        gl.uniform3f(U(P, "uLampCol"), 1.0, 0.74, 0.45);
        const light = K.theme === "light";
        gl.uniform3fv(U(P, "uFill"), light ? [0.9, 0.9, 0.92] : [0.42, 0.45, 0.55]);
        gl.uniform1fv(U(P, "uHi"), R.groups.map(g => (opts.hi || []).includes(g) ? 1 : 0));
        gl.uniform3fv(U(P, "uHiCol"), OG.rgb(K.light));
        gl.uniform1f(U(P, "uOn"), 1);
        gl.drawElements(gl.TRIANGLES, nIdx, gl.UNSIGNED_INT, 0);
        // the lamp's glow, drawn over everything at the COB
        const clip = (() => { const v = VP, p = lamp; const x = v[0] * p[0] + v[4] * p[1] + v[8] * p[2] + v[12], y = v[1] * p[0] + v[5] * p[1] + v[9] * p[2] + v[13],
          ww = v[3] * p[0] + v[7] * p[1] + v[11] * p[2] + v[15]; return [x / ww, y / ww]; })();
        gl.disableVertexAttribArray(loc.nrm); gl.disableVertexAttribArray(loc.grp); gl.disableVertexAttribArray(loc.col);
        gl.useProgram(G); gl.disable(gl.DEPTH_TEST); gl.enable(gl.BLEND); gl.blendFunc(gl.ONE, gl.ONE);
        gl.bindBuffer(gl.ARRAY_BUFFER, quad); const gp = gl.getAttribLocation(G, "p");
        gl.enableVertexAttribArray(gp); gl.vertexAttribPointer(gp, 2, gl.FLOAT, false, 0, 0);
        const rpx = 34 * dpr; gl.uniform2f(U(G, "uC"), clip[0], clip[1]); gl.uniform2f(U(G, "uR"), rpx / w * 2, rpx / h * 2);
        gl.uniform3f(U(G, "uCol"), 1.0, 0.82, 0.55); gl.uniform1f(U(G, "uA"), light ? 0.55 : 0.9);
        gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
        gl.disable(gl.BLEND); gl.enable(gl.DEPTH_TEST);
        return { lamp, clip };
      },
    };
  }
  window.RigView = { make, angles };
})();
