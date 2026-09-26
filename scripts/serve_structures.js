// Serves the files of a directory as a read-only SOyA repository:
// GET /<Name> returns the JSON-LD structure <Name>.
const http = require('http');
const fs = require('fs');
const path = require('path');

const dir = path.resolve(process.argv[2] || 'build/structures');
const port = Number(process.argv[3] || 9000);

http.createServer((req, res) => {
  const name = decodeURIComponent((req.url || '/').split('?')[0].replace(/^\/+/, ''));
  const file = path.join(dir, path.basename(name));
  if (!name || !fs.existsSync(file)) {
    res.writeHead(404, { 'Content-Type': 'application/json' });
    return res.end('{"error":"not found"}');
  }
  res.writeHead(200, { 'Content-Type': 'application/json' });
  return fs.createReadStream(file).pipe(res);
}).listen(port, '127.0.0.1');
