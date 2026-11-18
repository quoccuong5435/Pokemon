// Static server for the render check: / -> index.html, /viewer.min.js -> mdx-m3-viewer (installed in
// C:\Users\quocc\fxrender_pkg), /assets/... -> out/render_assets/..., /tex/<path> -> a texture by its model path
// (lower case; a missing one -> an 8x8 white TGA so particles that use game textures still show).
//   node analysis/render/server.js 8765
const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = parseInt(process.argv[2] || '8765', 10);
const HERE = __dirname;
const WORK = path.dirname(path.dirname(HERE));
const ASSETS = path.join(WORK, 'out', 'render_assets');
const VIEWER = path.join('C:\\Users\\quocc\\fxrender_pkg', 'node_modules', 'mdx-m3-viewer', 'dist', 'umd', 'viewer.min.js');
// 8x8 white 32-bit TGA (the viewer has a TGA handler, not a PNG one)
const WHITE = Buffer.concat([Buffer.from([0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 0, 8, 0, 32, 8]), Buffer.alloc(8 * 8 * 4, 255)]);

function send(res, code, type, body) {
  res.writeHead(code, { 'Content-Type': type, 'Access-Control-Allow-Origin': '*' });
  res.end(body);
}

http.createServer((req, res) => {
  const url = decodeURIComponent(req.url.split('?')[0]);
  try {
    if (url === '/' || url === '/index.html') {
      return send(res, 200, 'text/html', fs.readFileSync(path.join(HERE, 'index.html')));
    }
    if (url === '/viewer.min.js') {
      return send(res, 200, 'application/javascript', fs.readFileSync(VIEWER));
    }
    if (url.startsWith('/tex/')) {
      const p = path.join(ASSETS, 'tex', url.slice(5).toLowerCase());
      if (p.startsWith(ASSETS) && fs.existsSync(p)) {
        return send(res, 200, 'application/octet-stream', fs.readFileSync(p));
      }
      return send(res, 200, 'application/octet-stream', WHITE);
    }
    if (url.startsWith('/assets/')) {
      const p = path.join(ASSETS, url.slice(8));
      if (p.startsWith(ASSETS) && fs.existsSync(p)) {
        const type = p.endsWith('.json') ? 'application/json' : 'application/octet-stream';
        return send(res, 200, type, fs.readFileSync(p));
      }
    }
    send(res, 404, 'text/plain', 'not found');
  } catch (e) {
    send(res, 500, 'text/plain', String(e));
  }
}).listen(PORT, '127.0.0.1', () => console.log('render server on http://localhost:' + PORT));
