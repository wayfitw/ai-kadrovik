# LibreOffice headless behind unoserver (XML-RPC on :2004). Used in block 2.3 for
# DOCX → PDF. Kept as a separate container so the API image stays small.
FROM python:3.12-slim

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
        libreoffice-writer libreoffice-calc python3-uno fonts-dejavu fonts-liberation netcat-openbsd \
 && rm -rf /var/lib/apt/lists/*

# unoserver must run with the system python that has the uno bindings.
RUN /usr/bin/python3 -m pip install --break-system-packages --no-cache-dir "unoserver>=2.2,<3"

EXPOSE 2004
CMD ["/usr/bin/python3", "-m", "unoserver.server", "--interface", "0.0.0.0", "--port", "2004", "--uno-port", "2002"]
