from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


PAGE = b"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Python Hello World</title>
    <style>
      body { font-family: system-ui, sans-serif; max-width: 42rem; margin: 15vh auto; padding: 2rem; background: #f8f5e9; color: #1f2933; }
      main { background: white; border-top: 6px solid #3776ab; padding: 2rem; box-shadow: 0 8px 30px #0001; }
    </style>
  </head>
  <body><main><h1>Hello World from Python!</h1><p>Served from a Docker container.</p></main></body>
</html>"""


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/":
            self.send_error(404)
            return

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(PAGE)))
        self.end_headers()
        self.wfile.write(PAGE)


if __name__ == "__main__":
    server = ThreadingHTTPServer(("0.0.0.0", 8000), RequestHandler)
    print("Python app listening on port 8000", flush=True)
    server.serve_forever()
