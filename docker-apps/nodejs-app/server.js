const http = require("node:http");

const port = 3000;
const page = `<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Node.js Hello World</title>
    <style>
      body { font-family: system-ui, sans-serif; max-width: 42rem; margin: 15vh auto; padding: 2rem; background: #f3f7fb; color: #17202a; }
      main { background: white; border-left: 6px solid #3c873a; padding: 2rem; box-shadow: 0 8px 30px #0001; }
    </style>
  </head>
  <body><main><h1>Hello World from Node.js!</h1><p>Served from a Docker container.</p></main></body>
</html>`;

const server = http.createServer((request, response) => {
  if (request.url !== "/") {
    response.writeHead(404, { "content-type": "text/plain; charset=utf-8" });
    response.end("Not found\n");
    return;
  }

  response.writeHead(200, { "content-type": "text/html; charset=utf-8" });
  response.end(page);
});

server.listen(port, "0.0.0.0", () => {
  console.log(`Node.js app listening on port ${port}`);
});
