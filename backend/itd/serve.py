"""Run the API, with HTTPS/TLS when certificates exist.   python -m itd.serve [--port 8443]
TLS: the default Python server context accepts TLS 1.2 or higher only."""
import argparse
import os
import uvicorn


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=0)
    ap.add_argument("--cert", default="certs/cert.pem")
    ap.add_argument("--key", default="certs/key.pem")
    ap.add_argument("--host", default="127.0.0.1")
    a = ap.parse_args()
    tls = os.path.exists(a.cert) and os.path.exists(a.key)
    port = a.port or (8443 if tls else 8000)
    if tls:
        print(f"HTTPS on https://{a.host}:{port}  (set VITE_API_BASE to this address for the dashboard)")
        uvicorn.run("itd.api:app", host=a.host, port=port, ssl_certfile=a.cert, ssl_keyfile=a.key)
    else:
        print("No certificates found: serving plain HTTP for development. Run: python scripts/make_cert.py")
        uvicorn.run("itd.api:app", host=a.host, port=port)


if __name__ == "__main__":
    main()
