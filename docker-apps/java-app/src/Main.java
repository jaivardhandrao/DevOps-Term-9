import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpServer;
import java.io.IOException;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;

public class Main {
    private static final byte[] PAGE = """
        <!doctype html>
        <html lang="en">
          <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>Java Hello World</title>
            <style>
              body { font-family: system-ui, sans-serif; max-width: 42rem; margin: 15vh auto; padding: 2rem; background: #eef4f7; color: #202830; }
              main { background: white; border-bottom: 6px solid #e76f00; padding: 2rem; box-shadow: 0 8px 30px #0001; }
            </style>
          </head>
          <body><main><h1>Hello World from Java!</h1><p>Served from a Docker container.</p></main></body>
        </html>
        """.getBytes(StandardCharsets.UTF_8);

    public static void main(String[] args) throws IOException {
        HttpServer server = HttpServer.create(new InetSocketAddress("0.0.0.0", 8080), 0);
        server.createContext("/", Main::handleRequest);
        server.start();
        System.out.println("Java app listening on port 8080");
    }

    private static void handleRequest(HttpExchange exchange) throws IOException {
        if (!exchange.getRequestURI().getPath().equals("/")) {
            exchange.sendResponseHeaders(404, -1);
            exchange.close();
            return;
        }

        exchange.getResponseHeaders().add("Content-Type", "text/html; charset=utf-8");
        exchange.sendResponseHeaders(200, PAGE.length);
        exchange.getResponseBody().write(PAGE);
        exchange.close();
    }
}
