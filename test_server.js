const http = require('http');
const { exec } = require('child_process');
const url = require('url');
const querystring = require('querystring');

const port = 3000;

const server = http.createServer((req, res) => {
  const parsedUrl = url.parse(req.url);
  const query = querystring.parse(parsedUrl.query);
  
  // Get Python code from URL parameter
  const pythonCode = query.code;
  
  if (!pythonCode) {
    res.statusCode = 400;
    res.end('Error: Missing "code" parameter');
    return;
  }
  
  // Execute the Python code
  exec(`./python.exe -c "${pythonCode.replace(/"/g, '\\"')}"`, (error, stdout, stderr) => {
    res.setHeader('Content-Type', 'text/plain');
    
    if (error) {
      res.statusCode = 500;
      res.end(`Error: ${stderr}`);
      return;
    }
    
    res.statusCode = 200;
    res.end(`Output:\n${stdout}`);
  });
});

server.listen(port, () => {
  console.log(`Server running at http://localhost:${port}/`);
  console.log('Use it like: http://localhost:3000/?code=print("Hello%20World!")');
});
