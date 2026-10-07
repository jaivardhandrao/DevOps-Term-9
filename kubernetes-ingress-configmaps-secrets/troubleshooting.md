# Configuration and Ingress troubleshooting

An Ingress is an API object describing HTTP routing. An Ingress controller watches those
objects and implements the routing. Creating `ingress.yaml` without a compatible controller
does not create a working proxy. This lab uses the Minikube Nginx controller and `nginx` class.

For a route failure, inspect class, host, path, Service name/port, ready endpoints, and then
application response. The [session 12 recording script](../scripts/run-coursework-labs.py)
deliberately points `/api` at a nonexistent Service, captures the failed response, restores
the manifest, and verifies the recovered API. It also verifies configuration and Secret
presence inside the Pod without printing the Secret.

The instructor's trailing-newline case is a byte mismatch: `echo` normally adds a newline;
`printf '%s'` does not. Use a public example to reproduce it:

```python
import base64
expected = b'classroom-demo'
broken = base64.b64encode(expected + b'\n')
fixed = base64.b64encode(expected)
assert base64.b64decode(broken) != expected
assert base64.b64decode(fixed) == expected
print('before: comparison failed; after: comparison passed')
```

This is an encoding demonstration, not evidence of an actual PostgreSQL authentication
incident. Base64 suffixes are not a reliable validation rule; compare the intended decoded
bytes without logging credentials. The final project exercises real PostgreSQL separately.

Sources: [Ingress](https://kubernetes.io/docs/concepts/services-networking/ingress/),
[Secrets](https://kubernetes.io/docs/concepts/configuration/secret/).
