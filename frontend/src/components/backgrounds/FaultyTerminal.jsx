import React, { useEffect, useRef } from 'react';

export default function FaultyTerminal() {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const gl = canvas.getContext('webgl', { alpha: false });
    if (!gl) return;

    gl.clearColor(0, 0, 0, 1);

    const vertexShader = `
      attribute vec2 position;
      attribute vec2 uv;
      varying vec2 vUv;
      void main() {
        vUv = uv;
        gl_Position = vec4(position, 0.0, 1.0);
      }
    `;

    const fragmentShader = `
      precision mediump float;
      varying vec2 vUv;
      uniform float iTime;
      uniform vec2 iResolution;
      uniform vec3 uTint;

      uniform vec2 uMouse;
      
      float hash21(vec2 p) {
        p = fract(p * 234.56);
        p += dot(p, p + 34.56);
        return fract(p.x * p.y);
      }
      
      float noise(vec2 p) {
        return sin(p.x * 10.0) * sin(p.y * (3.0 + sin(iTime * 0.090909))) + 0.2; 
      }
      
      mat2 rotate(float angle) {
        float c = cos(angle);
        float s = sin(angle);
        return mat2(c, -s, s, c);
      }
      
      float fbm(vec2 p) {
        p *= 1.1;
        float f = 0.0;
        float amp = 0.5;
        
        mat2 modify0 = rotate(iTime * 0.02);
        f += amp * noise(p);
        p = modify0 * p * 2.0;
        amp *= 0.454545;
        
        mat2 modify1 = rotate(iTime * 0.02);
        f += amp * noise(p);
        p = modify1 * p * 2.0;
        amp *= 0.454545;
        
        mat2 modify2 = rotate(iTime * 0.08);
        f += amp * noise(p);
        
        return f;
      }
      
      float pattern(vec2 p, out vec2 q, out vec2 r) {
        vec2 offset1 = vec2(1.0);
        vec2 offset0 = vec2(0.0);
        mat2 rot01 = rotate(0.1 * iTime);
        mat2 rot1 = rotate(0.1);
        
        q = vec2(fbm(p + offset1), fbm(rot01 * p + offset1));
        r = vec2(fbm(rot1 * q + offset0), fbm(q + offset0));
        return fbm(p + r);
      }
      
      float digit(vec2 p){
          vec2 grid = vec2(15.0, 7.5);
          vec2 s = floor(p * grid) / grid;
          p = p * grid;
          vec2 q, r;
          float intensity = pattern(s * 0.1, q, r) * 1.3 - 0.03;
          
          p = fract(p);
          p *= 1.2;
          
          float px5 = p.x * 5.0;
          float py5 = (1.0 - p.y) * 5.0;
          float x = fract(px5);
          float y = fract(py5);
          
          float i = floor(py5) - 2.0;
          float j = floor(px5) - 2.0;
          float n = i * i + j * j;
          float f = n * 0.0625;
          
          float isOn = step(0.1, intensity - f);
          float brightness = isOn * (0.2 + y * 0.8) * (0.75 + x * 0.25);
          
          return step(0.0, p.x) * step(p.x, 1.0) * step(0.0, p.y) * step(p.y, 1.0) * brightness;
      }
      
      void main() {
          vec2 uv = vUv;
          vec2 p = uv * 2.0 - 1.0;
          p.x *= iResolution.x / iResolution.y;
          p += (uMouse - 0.5) * 0.08;
          
          vec2 mouse = uMouse;
          vec2 toMouse = p - (mouse * 2.0 - 1.0);
          float dist = length(toMouse);
          float mouseEffect = smoothstep(0.3, 0.0, dist) * 0.4;
          
          vec2 q, r;
          float charVal = pattern(p * 0.1, q, r);
          float glyph = digit(fract(p * 15.0)) * 0.8;
          
          float base = charVal * 0.6 + glyph * 0.4;
          base += mouseEffect;
          
          float scan = sin(uv.y * iResolution.y * 1.0 - iTime * 4.0) * 0.5 + 0.5;
          scan = pow(scan, 4.0);
          base += scan * 0.15;
          
          vec3 color = uTint * base * 0.8 + vec3(0.05);
          
          gl_FragColor = vec4(color, 1.0);
      }
    `;

    function compileShader(type, source) {
      const shader = gl.createShader(type);
      gl.shaderSource(shader, source);
      gl.compileShader(shader);
      if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
        throw new Error(`Shader compile error: ${gl.getShaderInfoLog(shader)}`);
      }
      return shader;
    }

    const vertShader = compileShader(gl.VERTEX_SHADER, vertexShader);
    const fragShader = compileShader(gl.FRAGMENT_SHADER, fragmentShader);
    
    const program = gl.createProgram();
    gl.attachShader(program, vertShader);
    gl.attachShader(program, fragShader);
    gl.linkProgram(program);
    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
      throw new Error(`Program link error: ${gl.getProgramInfoLog(program)}`);
    }
    gl.useProgram(program);

    const positionBuffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, positionBuffer);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([
      -1, -1,  0, 0,
       1, -1,  1, 0,
      -1,  1,  0, 1,
      -1,  1,  0, 1,
       1, -1,  1, 0,
       1,  1,  1, 1
    ]), gl.STATIC_DRAW);

    const positionLoc = gl.getAttribLocation(program, 'position');
    const uvLoc = gl.getAttribLocation(program, 'uv');
    gl.enableVertexAttribArray(positionLoc);
    gl.vertexAttribPointer(positionLoc, 2, gl.FLOAT, false, 16, 0);
    gl.enableVertexAttribArray(uvLoc);
    gl.vertexAttribPointer(uvLoc, 2, gl.FLOAT, false, 16, 8);

    const uTime = gl.getUniformLocation(program, 'iTime');
    const uResolution = gl.getUniformLocation(program, 'iResolution');
    const uTint = gl.getUniformLocation(program, 'uTint');
    const uMouse = gl.getUniformLocation(program, 'uMouse');

    gl.uniform3f(uTint, 0.0, 1.0, 1.0); // Cyan

    const targetMouse = { x: 0.5, y: 0.5 };
    const smoothMouse = { x: 0.5, y: 0.5 };
    
    const onPointerMove = (event) => {
      targetMouse.x = event.clientX / Math.max(window.innerWidth, 1);
      targetMouse.y = 1 - event.clientY / Math.max(window.innerHeight, 1);
    };
    window.addEventListener('pointermove', onPointerMove);

    function resize() {
      const dpr = Math.min(window.devicePixelRatio || 1, 1.5);
      canvas.width = window.innerWidth * dpr;
      canvas.height = window.innerHeight * dpr;
      gl.viewport(0, 0, canvas.width, canvas.height);
      gl.uniform2f(uResolution, canvas.width, canvas.height);
    }
    window.addEventListener('resize', resize);
    resize();

    let start = performance.now();
    let animId;
    function update() {
      animId = requestAnimationFrame(update);
      const t = (performance.now() - start) * 0.001;
      gl.uniform1f(uTime, t * 0.6);
      smoothMouse.x += (targetMouse.x - smoothMouse.x) * 0.07;
      smoothMouse.y += (targetMouse.y - smoothMouse.y) * 0.07;
      gl.uniform2f(uMouse, smoothMouse.x, smoothMouse.y);
      gl.drawArrays(gl.TRIANGLES, 0, 6);
    }
    update();

    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener('resize', resize);
      window.removeEventListener('pointermove', onPointerMove);
    };
  }, []);

  return (
    <div id="faultyTerminal" style={{ position: 'fixed', inset: 0, zIndex: 0, pointerEvents: 'none' }}>
      <canvas ref={canvasRef} style={{ display: 'block', width: '100%', height: '100%', opacity: 0.65 }} />
    </div>
  );
}
