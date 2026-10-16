from __future__ import annotations

import base64
import csv
import io
import os
from typing import Any

import sys
import subprocess

print("Python utilizado:", sys.executable, flush=True)
subprocess.run(
    [sys.executable, "-m", "pip", "show", "psycopg2-binary"],
    check=False,
)

import psycopg2
print("Versão do psycopg2:", psycopg2.__version__, flush=True)
from psycopg2.extras import RealDictCursor
from nicegui import ui

# Configure DATABASE_URL nas variáveis de ambiente do Render.
DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("NEON_DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("Configure DATABASE_URL nas variáveis de ambiente do Render.")

PORT = int(os.getenv("PORT", "8080"))
TABLE_NAME = "convenios_publicos"

# Base completa anexada incorporada no próprio main.py.
EMBEDDED_TSV = base64.b64decode(
    "UEFTVEEJTk9NRQlDT05URcOaRE8JCVBhc3RhIERpZ2l0YWxpemFkYQ0KMCAxCUNvbnZlbmlvIEVzdGFkbyBkZSBTw6NvIFBhdWxvLAkiUEFWSU1FTlRBw4fDg08gQVNGw4FMVElDQSAKTkEgUlVBIElPR09TTMOBVklBIEpELkxJTElBTkUKTkEgUlVBIERPSVMsIFZJIFPDg08gSk9SR0UKTkEgUlVBIEPDgVNTSUEgSkQgQUxFR1JJQQpUUkVDSE9TIERBIEFWRU5JREEgClVCRVJMw4NORElBIEUgQVZFTklEQQpKQUNVVElNQkEiCQlodHRwczovL2RyaXZlLmdvb2dsZS5jb20vZHJpdmUvZm9sZGVycy8xR3NsZ19Ibld2WXBDQ1dFZkdjUFQtNU82bEpTc3hCWl8/dXNwPXNoYXJpbmcNCjAgMgkiTWFyY2VsbyBkYSBTaWx2YSBNb3RvYm95IOKAkyBNRSAKVGVybW8gQWRpdGl2byAwNSDigJMgQ29udHJhdG8gMDcwLzIwMTQKQ2FydGEgQ29udml0ZSDigJMgMDE5LzIwMTQKUHJvY2Vzc28gMjgzMS8yMDE0ClRlcm1vIGRlIFJlbm92YcOnw6NvIgkiUFJFU1RBw4fDg08gREUgU0VSVknDh08gCkRFIE1PVE9CT1kiCQlodHRwczovL2RyaXZlLmdvb2dsZS5jb20vZHJpdmUvZm9sZGVycy8xa0JhTUdjUWtsd0JPRDJZS0hqaXpkaS05UTdhYnFLUDk/dXNwPXNoYXJpbmcNCjAgMwkiQVBBRQpUZXJtbyBhZGl0aXZvIDAxLzIwMDkKQ29udHJhdG8gMDcwLzIwMDkKUHJvY2Vzc28gaW50ZXJubyA0NjUvMjAwOSIJUFJFU1RBw4fDg08gREUgQ09OVEFTCQlodHRwczovL2RyaXZlLmdvb2dsZS5jb20vZHJpdmUvZm9sZGVycy8xcWk3YlBIQW9aSm43ZExiZGlNbFdzUURoZWI5cWJGQUE/dXNwPXNoYXJpbmcNCjAgNAkiQ0lEQVAKQ0VOVFJPIERFIElOQ0xVU8ODTyAKRElHSVRBTCBFIEFQUkVORElaQUdFTQpQUk9GSVNTSU9OQUwiCSJJTVBMQU5UQcOHw4NPIERPIENFTlRSTyBERSBBQ0VTU08gRElHSVRBTCAKVFJBTlNNSVNTw4NPIExJTkhBIFRFTEVGw5ROSUNBIEUgTU9ERU0gREVTVElOQURPUyBQQVJBIApERSBEQURPUyBQQVJBIEFDRVNTTyDDgCBJTlRFUk5FVCBCQU5EQSBMQVJHQQpTUEVFRFkiCQlodHRwczovL2RyaXZlLmdvb2dsZS5jb20vZHJpdmUvZm9sZGVycy8xQVllYWw2QWw1cWpVQ2RTQ1ZQTXkzWnJMMUpuUGc5Y1A/dXNwPXNoYXJpbmcNCjAgNQkiQ09OVFJBVE8gREUgQ09NT0RBVE8KRVNQT1JURSBDTFVCRSBVTknDg08gClZFUkEgQ1JVWiBERSAKTUFMSEFTIEUgQk9DSEFTIgkiRnVuZGHDp8OjbyBMaW9ucyBkbyBkaXN0cml0byBMQy0yIChDZXNzw6NvIGRlIGRpcmVpdG9zIGRlCnN1cGVyZsOtY2llLCBwcm90b2NvbG8gMDAyNDYwIExpdnJvIDAyODIgUGFnaW5hcyAwNjUvMDY4KTsKSGVpdG9yIEhhcnRtYW5uIChkaXJlaXRvIGRlIHVzbyBkZSBsaW5oYSB0ZWxlZsO0bmljYSk7CkVzcG9ydGUgQ2x1YmUgVW5pw6NvIFZlcmEgQ3J1eiBkZSBNYWxoYXMgZSBCb2NoYXMKIChUZXJyZW5vIHBhcmEgY29uc3RydcOnw6NvIGRlIGR1YXMgcXVhZHJhcwpkZSBtYWxoYSwgZHVhcyBxdWFkcmFzIGRlIGJvY2hhIGUgdW1hIHNlZGUgc29jaWFsKTsKQXNmZnJpbyAoVGFucXVlIGVzdGFjaW9uw6FyaW8gcGFyYSBhcm1hemVuYWdlbQpkZSBhc2ZhbHRvIGF0aXZvIGZpeG8sIENvbnRyYXRvIDAyNzMpOwpWaXRvciBTYXBpZW56YSAoIFZlw61jdWxvIG1hcmNhIFdvbGtzd2FnZW4sIGNoYXNzaXMKOWJ3MXp6MjcxdHBvNTE4OTApOwpQcm9kZXNwOyIJCWh0dHBzOi8vZHJpdmUuZ29vZ2xlLmNvbS9kcml2ZS9mb2xkZXJzLzFPMkNCWHFJdFVRdUpSTWg1Zk9XcUo2ZUhEb1FidnVzXz91c3A9c2hhcmluZw0KMCA2CSJTRUNSRVRBUklBIERFIEhBQklUQcOHw4NPCkVTVEFETyBERSBTw4NPIFBBVUxPIgkiUHJvZ3JhbWEgTWluaGEgQ2FzYSBNaW5oYSBWaWRhIAooRnVuZG8gUGF1bGlzdGEgZGUgSGFiaXRhw6fDo28gZGUgSW50ZXJlc3NlIFNvY2lhbCDigJMgRlBISVMKWm9uYXMgRXNwZWNpYWlzIGRlIEludGVyZXNzZSBTb2NpYWwg4oCTIFpFSVMKRnVuZG8gZGUgQXJyZW5kYW1lbnRvIFJlc2lkZW5jaWFsIOKAkyBGQVIpOwpQcm9ncmFtYSBFc3RhZHVOw7pjbGVvcyBIYWJpdGFjaW9uYWlzIFByb2dyCkNpZGFkZSBMZWdhbGFsIGRlIFJlZ3VsYXJpemHDp8OjbyBkZSBDaWRhZGUgTGVnYWxhbCIJCWh0dHBzOi8vZHJpdmUuZ29vZ2xlLmNvbS9kcml2ZS9mb2xkZXJzLzFpbjJjVGxYczNudXhuYjF5YVF5ZU5mUjRnYl85RFpkLT91c3A9c2hhcmluZw0KMCA3CSJFTEVLVFJPClNFUlZJw4dPUyBTLkEiCSJDT0JSQU7Dh0EgREUgVkFMT1JFUyBERVNUSU5BRE9TIEEgQ09OVFJJQlVJw4fDg08gUEFSQSBDVVNURUlPIERPUyBTRVJWScOHT1MgREUgSUxVTUlOQcOHw4NPIFDDmkJMSUNBClZpZ8OqbmNpYSBkZSA0IGFub3MgYSBwYXJ0aXIgZGUgMTQgZGUgYWJyaWwgZGUgMjAwMzsKKENvbnRyYXRvIENPTi8zMy8xMjgzLzIwMDEKKFRlcm1vIGRlIGNvbXByb21pc3NvIEREQUZGLzEyNC8wMDgvOTIKSWx1bWluYcOnw6NvIHDDumJsaWNhIFBlZHJvIExlc3NhKSIJCWh0dHBzOi8vZHJpdmUuZ29vZ2xlLmNvbS9kcml2ZS9mb2xkZXJzLzFHMTlYNURFMi1Mc0s1SFBpQ1F0ZHNQVWFBVFZaYi04aj91c3A9c2hhcmluZw0KMCA4CSJHT1ZFUk5PIEZFREVSQUwKUFJFRkVJVFVSQSBERSBTw4NPIFBBVUxPClBSRUZFSVRVUkEgREUgRlJBTkNJU0NPIE1PUkFUTyIJSU5TVEFMQcOHw4NPIERPIENBUlTDk1JJTyBFTEVJVE9SQUwgREUgRlJBTkNJU0NPIE1PUkFUTwkJDQowIDkJIlRSSUJVTkFMIERFIENPTlRBUyAKTVVOSUPDjVBJTyBERSBTw4NPIFBBVUxPIgkiKFRlcm1vIGRlIGNvb3BlcmHDp8OjbyAxMC8yMDExCkNhcGFjaXRhw6fDo28gZG9zIHNlcnZpZG9yZXMgcHJlZmVpdHVyYSBtdW5pY2lwYWwgZGUgRnJhbmNpc2NvCk1vcmF0byBwb3IgbWVpbyBkYSBwYXJ0aWNpcGHDp8OjbyBub3MgY3Vyc29zCm1pbmlzdHJhZG9zIHBlbGEgZXNjb2xhIHN1cGVyaW9yIGNvbnNlbGhlaXJvIEV1csOtcGVkZXMgU2FsZXMpIgkJaHR0cHM6Ly9kcml2ZS5nb29nbGUuY29tL2RyaXZlL2ZvbGRlcnMvMUlaTWhZRkVaSkVDejdIS2liYVpySzJwdTFUQmhFUUpqP3VzcD1zaGFyaW5nDQoxMAlDRU5UUk8gUEFVTEEgU09VWkEJIihUZXJtbyBkZSBjb25jbHVzw6NvLCBlbmNlcnJhbWVudG8gZSBxdWl0YcOnw6NvIGRvIGNvbnbDqm5pbwpkZSBjb29wZXJhw6fDo28gdMOpY25pY28tZWR1Y2FjaW9uYWwuZGUgY29vcGVyYcOnw6NvIHTDqWNuaWNvLWVkdWNhY2lvbmFsLgpUZXJtbyBBZGl0aXZvIGRlIHJldGlmaWNhw6fDo28gYW8gY29udsOqbmlvIGRlIGNvb3BlcmHDp8OjbwowMy8wNy8yMDA4KUNvbnbDqm5pbyBkZSBjb29wZXJhw6fDo28gdMOpY25pY28tZWR1Y2FjaW9uYWwgCkNvbnbDqm5pbyBkZSBjb29wZXJhw6fDo28gdMOpY25pY28tZWR1Y2FjaW9uYWwiCQlodHRwczovL2RyaXZlLmdvb2dsZS5jb20vZHJpdmUvZm9sZGVycy8xNnF0eGhTWUpJYjhjVW5nUk9nbnllWWRDdlFfcTRnWGw/dXNwPXNoYXJpbmcNCjExCSJFVEMgCkNPUlJFSU8iCSIoQ29udHJhdG8gbcO6bHRpcGxvIGRlIHByZXN0YcOnw6NvIGRlIHNlcnZpw6dvcyBlIHZlbmRhIGRlIHByb2R1dG9zClZpZ8OqbmNpYSBkZSAxMiBtZXNlcyBhIHBhcnRpciBkZSAyNC8wNS8yMDEzCih0ZXJtb3MgYWRpdGl2b3MgYW8gY29udHJhdG8gOTkxMjIzNDc2OCkiCQlodHRwczovL2RyaXZlLmdvb2dsZS5jb20vZHJpdmUvZm9sZGVycy8xZW9vNldfZmZBRXNnQzZKdEJicTlqLWx5X3NHT051dDc/dXNwPXNoYXJpbmcNCjEyCUNQVE0JIihUZXJtbyBkZSBwZXJtaXNzw6NvIGRlIHVzbyBwYXJhIGZpbnMgZGl2ZXJzb3MgRkQvMDU0LzIwMDYKUHJvY2Vzc28gMDA3L0RGUFAvMjAwNikKKFRlcm1vIGRlIHBlcm1pc3PDo28gZGUgdXNvIHBhcmEgZmlucyBkaXZlcnNvcwpGRC8wMjIvMjAwOCBQcm9jZXNzbyA4NDY2NykiCQlodHRwczovL2RyaXZlLmdvb2dsZS5jb20vZHJpdmUvZm9sZGVycy8xeWRvbEktZFFMR3IzUlBqMldZaFhKMFdMYUtzWkhac2E/dXNwPXNoYXJpbmcNCjEzCSJURUxFU1AKTFVJWiBDQVJMT1MgRE9TIFJFSVMiCShUZXJtbyBkZSBwZXJtaXNzw6NvIGRlIHVzbyBkZSBwcsOzcHJpbyBtdW5pY2lwYWwJCWh0dHBzOi8vZHJpdmUuZ29vZ2xlLmNvbS9kcml2ZS9mb2xkZXJzLzFNclc1MnBJZ2cwQVBsNU5OXzVRMGx3a2p0MjB6aUJMbz91c3A9c2hhcmluZw0KMTQJIkFDRVNTQSBTw4NPIFBBVUxPCklORk9DRU5UUk8iCSIoQ29udsOqbmlvIGluc3RhbGHDp8OjbyBlIGZ1bmNpb25hbWVudG8gCkRvIHByb2dyYW1hIGFjZXNzYSBTw6NvIFBhdWxvIApEZWNyZXRvIG7CujUyLjg5NyIJCWh0dHBzOi8vZHJpdmUuZ29vZ2xlLmNvbS9kcml2ZS9mb2xkZXJzLzFZUm1LdlRHaVhMYl81QUo4ZzJuUWk2c190M0pGa1Azej91c3A9c2hhcmluZw0KMTUJUFJPREVTUAkiSW1wbGFudGHDp8OjbyBkb3Mgc2VydmnDp29zIHDDumJsaWNvcyBlbGV0csO0bmljb3MgYWNlc3PDrXZlaXMKbmEgcmVkZSBJbnRlcm5ldCwgbmEgcmVkZSBFeHRyYW5ldCBJbnRyYWdvdiBlIGRlbWFpcyBzZXJ2acOnb3MKcXVlIGludGVncmFtIG8gcHJvamV0byBpbnRpdHVsYWRvIFBvbnRvLlNQCiBBdGVuZGltZW50byBhbyBDaWRhZMOjbyBlbSBTZXJ2acOnb3MgVmlhIEludGVybmV0ClZpZ8OqbmNpYSBkZSA1IGFub3MgYSBwYXJ0aXIgZGUgMDEgZGUganVsaG8gZGUgMjAwNyIJCWh0dHBzOi8vZHJpdmUuZ29vZ2xlLmNvbS9kcml2ZS9mb2xkZXJzLzF1aUszN0lzcTZaZUhvY0ZSQXNfSVN5WDNxSGhYWnpkUj91c3A9c2hhcmluZw0KMTYJVFJJQlVOQUwgREUgSlVTVEnDh0EJQ2Vzc8OjbyBkZSBTZXJ2aWRvciBQw7pibGljbyBNdW5pY2lwYWwgcGFyYSBwcmVzdGFyIHNlcnZpw6dvcyBqdW50byBhbyBjZXNzaW9uw6FyaW8JCWh0dHBzOi8vZHJpdmUuZ29vZ2xlLmNvbS9kcml2ZS9mb2xkZXJzLzE0NXE2bHJ5dEhUS0tONG13NmJrZmZKWTRjMl9tTGRqVz91c3A9c2hhcmluZw0KMTcJIk1JTklTVMOJUklPIERBIFBSRVZJRMOKTkNJQQpFIEFTU0lTVMOKTkNJQSBTT0NJQUwiCSIoQ29udsOqbmlvIHBhcmEgYSBvcGVyYWNpb25hbGl6YcOnw6NvIGRhIGNvbXBlbnNhw6fDo28gcHJldmlkZW5jacOhcmlhKQpQcm9jZXNzbyA0NDAwMC4wMDEyNjMvMjAwMi04MSkKUFJFVmNpZGFkZSwgUHJvY2Vzc28gMzU0MDYuMDAwMDUwLzIwMDgtNzQsQ29udsOqbmlvIDAyLzIwMDgiCQlodHRwczovL2RyaXZlLmdvb2dsZS5jb20vZHJpdmUvZm9sZGVycy8xOXZ0NmtnT2dOdmx2SDNfTmJJX0pKVzEyRlpWWXNUZXM/dXNwPXNoYXJpbmcNCjE5CSJJTkRFU1AKSU5TVElUVVRPIE5BQ0lPTkFMIERFIApERVNFTlZPTFZJTUVOVE8gREUgREVTUE9SVE8iCSJDb252w6puaW8gdHJhbnNmZXLDqm5jaWEgZGUgcmVjdXJzb3MgUHJvZ3JhbWEgRVNQT1JURSBTT0xJRMOBUklPClByb2Nlc3NvIDIzMTMyLjAwMDQxNy85NS01MiAKQ29udsOqbmlvIDE5OS85NQpWaWfDqm5jaWEgZGUgMTUwIGRpYXMgYSBwYXJ0aXIgZGUgMjkgZGUgZGV6ZW1icm8gZGUgMTk5NQpBdXRvcml6YcOnw6NvIGRlIFVzbyBkbyBDZW50cm8gU29jaWFsIFVyYmFubyBkZSBGcmFuY2lzY28gTW9yYXRvIgkJaHR0cHM6Ly9kcml2ZS5nb29nbGUuY29tL2RyaXZlL2ZvbGRlcnMvMWt6amdkbEhNRkpFVDl4Z2Z5SVBLMVZQNkh2RzZybGpPP3VzcD1zaGFyaW5nDQoyMAlTQUJFU1AJIkRpcmVpdG8gZGUgZXhwbG9yYXIgYSBwcmVzdGHDp8OjbyBkb3Mgc2VydmnDp29zIHDDumJsaWNvcyBkZSBhYmFzdGVjaW1lbnRvIApEZSDDoWd1YSBlIGVzZ290YW1lbnRvIHNhbml0w6FyaW8uIgkJaHR0cHM6Ly9kcml2ZS5nb29nbGUuY29tL2RyaXZlL2ZvbGRlcnMvMWVXTXB0ZGxRWHJKa3QtRGM5d205TS1XQ3NZQVJWdE92P3VzcD1zaGFyaW5nDQoyMQkiU0FOVEEgQ0FTQQpMQVIgQVNTSVNURU5DSUFMIFPDg08gQkVORURJVE8iCSJUZXJtbyBhZGl0aXZvIDAxLzIwMDcsIENvbnRyYXRvIDE3LzIwMDksCkNvbnRyYXRhw6fDo28gZGUgMjAwIGFnZW50ZXMgY29tdW5pdGFyaW9zIGRlIHNhw7pkZSBBQ1MoY29udHJhdG8gMTYvMjAwOSkgKGNvbnbDqm5pbzAxLzIwMDIpICh0ZXJtbyBhZGl0aXZvIDAyLzIwMDIiCQlodHRwczovL2RyaXZlLmdvb2dsZS5jb20vZHJpdmUvZm9sZGVycy8xVjdQOXVaWjZORXNCMUhIdnVZUU1keklvNVBlU2JIUlk/dXNwPXNoYXJpbmcNCjIyCSJTQU1FIApMQVIgQVNTSVNURU5DSUFMIFPDg08gQkVORURJVE8iCVByb2Nlc3NvIDAxNi8yMDE0IFByb2Nlc3NvIDE0OC8yMDE1IGNvbnbDqm5pbyAwMS8yMDExCQlodHRwczovL2RyaXZlLmdvb2dsZS5jb20vZHJpdmUvZm9sZGVycy8xN3pfLUQ4YVBnQ2NiOGpNMkpwR0x4WUVUcGRhUHd2Rmc/dXNwPXNoYXJpbmcNCjIzCSJDSUEgQlJBU0lMRUlSQSBERSBQRVRST0xFTwpJUElSQU5HQSIJQ29udHJhdG8gMDM3IOKAkyBQUi8yMDA5IHJlZmVyZW50ZSBhbyBwcmVnw6NvIDAyLzIwMDkJCWh0dHBzOi8vZHJpdmUuZ29vZ2xlLmNvbS9kcml2ZS9mb2xkZXJzLzFJTkduaWdNVXZ1dVlJOXJkZHM5M0E5WlpvOWdrc0dnQj91c3A9c2hhcmluZw0KMjQJIlNFQ1JFVEFSSUEgREUgRVNQT1JURQpFIFRVUklTTU8KVkFMRElSIEFOVE9OSU8gTUFSVElOUyIJTWFudXRlbsOnw6NvIGUgZnVuY2lvbmFtZW50byBkbyBDZW50cm8gU29jaWFsIFVyYmFubwkJaHR0cHM6Ly9kcml2ZS5nb29nbGUuY29tL2RyaXZlL2ZvbGRlcnMvMUowa2RFYlc2OWhLZ2ItbzNoU1JScHplT3hHMUQ5dG9XP3VzcD1zaGFyaW5nDQoyNQkiQ8OCTUFSQSBNVU5JQ0lQQUwgCkZSQU5DSVNDTyBNT1JBVE8iCSJBdXRvcml6YcOnw6NvIHBhcmEgY29uc3RydcOnw6NvIGRvIHByw6lkaW8gb25kZSBmdW5jaW9uYSBhIGFzc2lzdMOqbmNpYSBTb2NpYWwgCkxlaSAxLjY1Mi85NiIJCWh0dHBzOi8vZHJpdmUuZ29vZ2xlLmNvbS9kcml2ZS9mb2xkZXJzLzFDUWc3SmM2MHd0N3RVUzkzSlpnRkxRRGRpTWtvMnNuZD91c3A9c2hhcmluZw0KMjYJIkNQVE0gCkNCVFUiCSJQcm90b2NvbG8gZGUgaW50ZW7Dp8O1ZXMgcGFyYSBjb29wZXJhw6fDo28gdMOpY25pY2EgZSBhcG9pbyBlIGFwb2lvIHJlY8OtcHJvY28gKHRlcm1vIGRlIHBlcm1pc3PDo28gCkRlIHVzbyBwYXJhIGZpbnMgZGl2ZXJzb3MgRkQvMDU0LzIwMDYKUHJvY2Vzc28gMDA3L0RGUFAvMjAwNiAoIFByb3RvY29sbyBkZSBpbnRlbsOnw6NvIENQVE0gODI3MzE3NDA4MTAwKQpQcm9jZXNzbyBpbnRlcm5vIDI1ODYvMjAxNyAoY29udsOqbmlvIDAwMS8yMDA1IgkJaHR0cHM6Ly9kcml2ZS5nb29nbGUuY29tL2RyaXZlL2ZvbGRlcnMvMUZlQ3Fubk9jSWNhMUlQUFRpcHRVdDdFQ2FHbUppRFR3P3VzcD1zaGFyaW5nDQoyNwkiQ09QRVJBVElWQSBFU1RBRE8gTVVOSUPDjVBJTwpQQVJBIENPTlNUUlXDh8ODTyBFU0NPTEFSRVMgClBBQyIJRGVzZW52b2x2aW1lbnRvIGRhIGVkdWNhw6fDo28gZGEgRWR1Y2HDp8OjbyBGREUgUHJvY2Vzc28gMjA4MC8yMDA1IC1TRQkJaHR0cHM6Ly9kcml2ZS5nb29nbGUuY29tL2RyaXZlL2ZvbGRlcnMvMVBFdWhxY1E2dmpCWGx0LWdwRGhEcElvcVdnWlBIR1puP3VzcD1zaGFyaW5nDQoyOAkiU0VDUkVUQVJJQSBEQSBBR1JJQ1VMVFVSQQpFIEFCQVNURUNJTUVOVE8iCSJ0ZXJtbyBkZSBjb252w6puaW8gb2JqZXRpdmFuZG8gYSBpbXBsYW50YcOnw6NvIGRvIHByb2dyYW1hIE1FTEhPUiBDQU1JTkhPIApQcm9jZXNzbyBTQUEgNzU3LzA4ClZpZ8OqbmNpYSBkZSAyOCBkZSBtYWlvIGRlIDIwMDgiCQlodHRwczovL2RyaXZlLmdvb2dsZS5jb20vZHJpdmUvZm9sZGVycy8xLXM0aGc3V2FYd1Z0WWdUdS1td3JwTWFnTUUyeEthQ04/dXNwPXNoYXJpbmcNCjMwCSJCRUzDiU0gVVJCQU5JWkFET1JBCk9MR0EgRUxFVVTDiVJJTyBEQSBTSUxWQQpPREFJUiBNSUFOSQpCSUFOQ0EgRVJNRUxJTkRBIERVQVJURSBEQSBTSUxWQQpNQVJDSU8gTlVDQ0kgTUFaWkVJCkJFTMOJTSBVUkJBTklaQURPUkEiCSJUZXJtb3MgZGUgYWNvcmRvIGUgZGVzYXByb3ByaWHDp8OjbyBhbWlnw6F2ZWwgQXV0b3JpemHDp8OjbyBCZWzDqW0gVXJiYW5pemFkb3JhIApNYXRyw61jdWxhcyA0MDgwIGUgNDA4MSBlIHRlcm1vcyBkZSBhY29yZG8gZGUgZGVzYXByb3ByaWHDp8OjbyBhbWlnw6F2ZWwgZGUgcXVlIApUcmF0YSBvIGRlY3JldG8gNDUgRy8yMDA0IgkJaHR0cHM6Ly9kcml2ZS5nb29nbGUuY29tL2RyaXZlL2ZvbGRlcnMvMTlVRkZKMGI1LUJ3Mjh5WTllTTlwWlBxS21qMHFENFBnP3VzcD1zaGFyaW5nDQozMQkiR1JJRk9OIEJSQVNJTApBU1NFU1NPUklBIExUREEgRVBQClJFTkFUQSBUT1JSRSBERSBTRU5FIgkiKFRlcm1vIGRlIGNvbnRyYXRvIDM2LzIwMjAgZGVjb3JyZW50ZSBkZSBkaXNwZW5zYSBkZSBsaWNpdGHDp8OjbykgClByb2Nlc3NvIGFkbWluaXN0cmF0aXZvIDkxMDEvMjAxOQpWaWfDqm5jaWEgZGUgMDEvMDIvMjAyMCBhIDMxLzAxLzIwMjEiCQlodHRwczovL2RyaXZlLmdvb2dsZS5jb20vZHJpdmUvZm9sZGVycy8xVjM4bnVkNVo5bkxrS0RmbUJjWDEwdjhPajdSQUVUMW4/dXNwPXNoYXJpbmcNCjMyCSJBU1NPQ0lBw4fDg08gREEgQ09SUE9SQcOHw4NPIApNVVNJQ0FMIFJPR8OJUklPIExFVk9SSU4iCSJBdGEgZGEgYXNzZW1ibGVpYSBleHRyYW9yZGluw6FyaWEgcGFyYSBhIGRlY2lzw6NvIGUgYXByb3Zhw6fDo28gCmRhIGFsdGVyYcOnw6NvIGRvIGVzdGF0dXRvIGRhIGFzc29jaWHDp8OjbyBkYSBjb3Jwb3Jhw6fDo28gbXVzaWNhbApSb2fDqXJpbyBMZXZvcmluIGRlIEZyYW5jaXNjbyBNb3JhdG8iCQlodHRwczovL2RyaXZlLmdvb2dsZS5jb20vZHJpdmUvZm9sZGVycy8xQ2dJNzVNQ3hqZWlHMnFETU1SX1dWOWNOTHdadmlBOEc/dXNwPXNoYXJpbmcNCjMzCSJNSU5JU1TDiVJJTyBETyBERVNFTlZPTFZJTUVOVE8KU09DSUFMIEUgQ09NQkFURSDDgCBGT01FIApBTkRSw4lBIENBVEhBUklOQSBQRUxJWkFSSSBQSU5UTyIJIlRlcm1vIGRlIGFkZXPDo28gYW8gcHJvZ3JhbWEgYm9sc2EgZmFtw61saWEgZSBhbyBjYWRhc3RybyDDum5pY28gZGUgcHJvZ3JhbWFzIHNvY2lhaXMKUG9ydGFyaWEgR00vTURTIDI0NiBkZSAyMCBkZSBtYWlvIGRlIDIwMDUKUHJvY2Vzc28gOTEwMDAuMDEwNjg3LzIwMDUtNTIKVGVybW8gZGUgYWRlc8OjbyAxODI4KSIJCWh0dHBzOi8vZHJpdmUuZ29vZ2xlLmNvbS9kcml2ZS9mb2xkZXJzLzFudXNLV3NVc0pjVEpmRVZlSTZBSEZJLU1QTTJRVzNMRj91c3A9c2hhcmluZw0KMzQJVEVSTU9TIERFIFBPU1NFIERPUyBQUkVGRUlUT1MJIlByb2N1cmHDp8O1ZXMgKGFudGlnYXMgZSBhdHVhaXMpIGRvcyBhZHZvZ2Fkb3MganVudG8gYW8gU3IgUHJlZmVpdG8KQ29tcHJvdmFudGVzIGRlIEluc2NyacOnw6NvIGUgZGUgc2l0dWHDp8OjbyBjYWRhc3RyYWwgZGEgUHJlZmVpdHVyYSIJCWh0dHBzOi8vZHJpdmUuZ29vZ2xlLmNvbS9kcml2ZS9mb2xkZXJzLzFfeDA5ckt6MGdYdGk0eUhWWV8yZnFhUDNNS0k5YWNvLT91c3A9c2hhcmluZw0KMzUJIkZVTkRBw4fDg08gTElPTlMgREUgU8ODTyBQQVVMTwpTRUNSRVRBUklBIERBIENVTFRVUkEKV2FsZGVzb24gQ2xhdWRpbm8gZGEgU2lsdmEiCSJDb252w6puaW8gcGFyYSBvIGRlc2Vudm9sdmltZW50byBkYSBiaWJsaW90ZWNhIHDDumJsaWNhIG11bmljaXBhbApGdW5kYcOnw6NvIExJT05TIGNlZGUgw6FyZWEgcGFyYSBhIGV4dHJhw6fDo28gZGUgY2FzY2FsaG8iCQlodHRwczovL2RyaXZlLmdvb2dsZS5jb20vZHJpdmUvZm9sZGVycy8xdEsxOHRxb2xaTnBydHJteDdwaVFvTWtSclVieGJ4bGE/dXNwPXNoYXJpbmcNCjM2CSJDRVNQIApMdWl6IENhcmxvcyBkb3MgUmVpcwpFTEVDVFJPCkpvc8OpIEFwYXJlY2lkbyIJIkxlaSBuwrogMi4wMDkvMjAwMiBkZSAyNyBkZSBEZXplbWJybyBkZSAyMDAyIApTdWJzdGl0dWnDp8OjbyBkZSBjb25qdW50b3MgZGUgbMOibXBhZGEgZGUgcmVkZSBkZSBpbHVtaW5hw6fDo28gcMO6YmxpY2EKKFRlcm1vIGRlIGNvbXByb21pc3NvIGUgYWNvcmRvIHBhcmEgcGFnYW1lbnRvIGRlIGTDqWJpdG8KRExBRi8xMjQvMTg0Lzk3KQooVGVybW8gZGUgYXV0b3JpemHDp8OjbyBlIGFqdXN0ZSBkZSBwYXJ0aWNpcGHDp8O1ZXMgZmluYW5jZWlyYXMg4oCTIDQ5MjcpIE9MTEYvMTI0LzEyMy85OApUQ0FQRC8xMjQvMDY5LzIwMDEtIOKAkyBDT1NJUCAtIApwcm9ncmFtYSBkZSBlZmljacOqbmNpYSBlbmVyZ8OpdGljYSDigJMgUEVFLzA1MDYvMDEyLzIwMDcsUEVFLzA1MDYvMTMwLzIwMDcKVGVybW8gZGUgY29udsOqbmlvIDIwMDMuMDYyLU9FIC0gCnByb2dyYW1hIG5hY2lvbmFsIGRlIGlsdW1pbmHDp8OjbyBww7pibGljYSBlZmljaWVudGUg4oCTIFJFTFVaCkNvbnRyYXRvIDEyNC9JUC8wMzEvMjAwNyIJCWh0dHBzOi8vZHJpdmUuZ29vZ2xlLmNvbS9kcml2ZS9mb2xkZXJzLzFvM216X1JMaUtiT2lEbzNVeVpDSXIyNExBXzN3dHBXaj91c3A9c2hhcmluZw0KMzcJQ0FJWEEJQ2Vzc8OjbyBkZSB1c28gZGUgw4FyZWEgZGUgaW3Ds3ZlbAkJaHR0cHM6Ly9kcml2ZS5nb29nbGUuY29tL2RyaXZlL2ZvbGRlcnMvMUZaNGF3RzBVR2VUSGhwS0phOEZoMFdnMy1kMjg4X2pIP3VzcD1zaGFyaW5nDQozOAlJTlNTCSJDb252w6puaW8gMDIvMjAwOCAtIFByb2Nlc3NvIDM1NDA2LjAwMDA1MC8yMDA4LTc0IApVbmlkYWRlIGRlIEF0ZW5kaW1lbnRvIFBSRVZDaWRhZGUiCQlodHRwczovL2RyaXZlLmdvb2dsZS5jb20vZHJpdmUvZm9sZGVycy8xZWR3OXJBWXZWdEExR0l0Q2JRUDFFczZCemp1cDhUaXk/dXNwPXNoYXJpbmcNCjM5CUNESFUJIlNpbHZlcmlvIEpvc2UgUGVsaXphcmkgQ29udHJhdG8gMTIwLjAwLjAwLzYuMC4wMC4wMC80OTMvOTUKUFAgNDUxMDAwMDYwMy0wMSAKTGVpIG7CuiAyLjM4My8yMDA5IGRlIDAxIGRlIGp1bGhvIGRlIDIwMDkgCkxlaSBuwrogMi4zNjAvMjAwOSBkZSAwNyBkZSBtYWlvIGRlIDIwMDkKTGVpIG7CuiAyLjM1MC8yMDA5IGRlIDEzIGRlIGZldmVyZWlybyBkZSAyMDA5CkNvbnRyYXRvIDEyMC4wMC4wMC82LjAuMDAuMDAvNDU4Lzk1IFBQIDQ1MTAwMDA2MDItMDEKKFBlcm1pc3PDo28gZGUgdXNvIDkuMDAuMDAuMDAvNS4wMC4wMC4wMC8wMDc3LzIwMTMgUHJvY2Vzc28gcHJvdmlzw7NyaW8gNTQuMTAuMDAuMDkuMDEKUHJvdG9jb2xvIDIwMjk1OC8xMiIJCWh0dHBzOi8vZHJpdmUuZ29vZ2xlLmNvbS9kcml2ZS9mb2xkZXJzLzFoT3BjM0cxQkdUTnRJcHhZS1o5Zi0xR3h1V2N2aWo1Rj91c3A9c2hhcmluZw0KNDAJTEFSIEFTU0lTVEVOQ0lBTCBBWkFSSUFTCSJQbGFubyBkZSB0cmFiYWxobyAyMDEyIOKAkyBQcm9qZXRvIGRvY2UgbGFyIGNhc2EgYWJyaWdvLCBDb252w6puaW8gMDA3LzIwMTEKQXRlbmRpbWVudG8gZGUgY3JpYW7Dp2FzIGNhcmVudGVzIHbDrXRpbWFzIGRlIHZpb2zDqm5jaWEgZG9tw6lzdGljYSwgbWF1cyB0cmF0b3MgZSBhYmFuZG9ubwpDb252w6puaW8gMDA2LzIwMDYsIENvbnbDqm5pbyAwMDUvMjAwNywgQ29udsOqbmlvIDAwMy8yMDA4LCBDb252w6puaW8gMDA1LzIwMDksIENvbnbDqm5pbyAwMDYvMjAwOSwgCkNvbnbDqm5pbyAwMDcvMjAwOSwgQ29udsOqbmlvIDAwNC8yMDEwLCBDb252w6puaW8gMDA3LzIwMTEsIENvbnbDqm5pbyAwMDYvMjAwNiwgQ29udsOqbmlvIDAwNS8yMDA5LApDb252w6puaW8gMDAxLzIwMTIiCQlodHRwczovL2RyaXZlLmdvb2dsZS5jb20vZHJpdmUvZm9sZGVycy8xSkZ0ZzVadVBwcEM2cjBLdFUtWUxzQWt1Zi0tVERmcTk/dXNwPXNoYXJpbmcNCjQxCVBSw5MgTU9SQVRPCUpvc8OpIEFwYXJlY2lkbyBCcmVzc2FuZTsgQW5kcmVhIENhdGhhcmluYSBQZWxpemFyaSBQaW50bwkJaHR0cHM6Ly9kcml2ZS5nb29nbGUuY29tL2RyaXZlL2ZvbGRlcnMvMVBaRFgwNGhoSXBhM3drWjJfYXpyRkl5bS1ZdnVtaUhNP3VzcD1zaGFyaW5nDQo0MglJTlNUSVRVVE8gTElSSU9TIERPIFZBTEUJIkNvbnbDqm5pbyAwMS8yMDEzClNlcnZpw6dvIGRlIGFjb2xoaW1lbnRvIGluc3RpdHVjaW9uYWwgcGFyYSBjcmlhbsOnYXMgZSBhZG9sZXNjZW50ZXMpIgkJaHR0cHM6Ly9kcml2ZS5nb29nbGUuY29tL2RyaXZlL2ZvbGRlcnMvMU1SeWNQT0VyV0hnVVp4UzVmUmczWlJyc0xLTDlubnd1P3VzcD1zaGFyaW5nDQo0MwlNSU5JU1TDiVJJTyBQw5pCTElDTwkiUHJvY2Vzc28gMzE2MS8yMDE3ClRlcm1vIGRlIHBlcm1pc3PDo28gZGUgdXNvLCBhIHRpdHVsbyBwcmVjYXJpbywgZGUgcHLDs3ByaW8gZGEgZmF6ZW5kYSBkbyBlc3RhZG8sCiBuYSBjb25mb3JtaWRhZGUgZG8gZGVjcmV0byA0MzI1NiBkZSAyOSBkZSBqdWxobyBkZSAxOTk4KQpPZsOtY2lvIG7CuiAxMzAvMjAxOSwgVGVybW8gZGUgY29udsOqbmlvIG7CuiAyNS8yMDE3IE1QU1AiCQlodHRwczovL2RyaXZlLmdvb2dsZS5jb20vZHJpdmUvZm9sZGVycy8xUlptUGU0RExoVXZNWnZlUnZDOGU4aVBuZzU3N0JVN2U/dXNwPXNoYXJpbmcNCjQ0CSJERVIgCkRlcGFydGFtZW50byBkZSBFc3RyYWRhcyBkZSBSb2RhZ2VtIgkiVGVybW8gZGUgY29udHJhdG8gcGFyYSBzZXJ2acOnbyBkZSBwYXZpbWVudGHDo28gZSBzZXJ2acOnb3MgY29tcGxlbWVudGFyZXMgZW0gdmlhcyB1cmJhbmFzKQpUZXJtbyBkZSBhZGVzw6NvIElTU1FOIDM0OC8yMDEwClNpc3RlbWEgZGUgcmV0ZW7Dp8OjbyBlIHJlcGFzc2UgZGUgaXNzcW4gQ29udsOqbmlvIDQxNjMgQXV0b3MgMjQ3LjI5My8yMDA3IApXYWxkZXNvbiBDbGF1ZGlubyBkYSBTaWx2YTsKQW5kcmVhIENhdGhhcmluYSBQZWxpemFyaSBQaW50byIJCWh0dHBzOi8vZHJpdmUuZ29vZ2xlLmNvbS9kcml2ZS9mb2xkZXJzLzFfXzNqYUhNYWxrNWRiLS1QMUlydS1uR3h5d21QUVEyZz91c3A9c2hhcmluZw0KNDUJIlNFQ1JFVEFSSUEgRE8gTUVJTyBBTUJJRU5URQpFU1RBRE8gREUgU8ODTyBQQVVMTyIJIlByb2pldG9zIGFtYmllbnRhaXMgRXN0cmF0w6lnaWNvcyAKUHJvdG9jb2xvIOKAkyBNdW5pY8OtcGlvIHZlcmRlIFRlcm1vIGRlIGFkZXPDo28KUGxhbm8gZGUgYcOnw6NvIGFtYmllbnRhbCBkbyBtdW5pY8OtcGlvCkRlY3JldG8gbsK6IDMwIEcgLzIwMDgKQW5kcmVhIENhdGhhcmluYSBQZWxpemFyaSBQaW50byIJCWh0dHBzOi8vZHJpdmUuZ29vZ2xlLmNvbS9kcml2ZS9mb2xkZXJzLzFxbDI0VDBjM3pETDlJZmhZVVJ0LThScHV5aE93MkE4Yz91c3A9c2hhcmluZw0KNDYJIkNPTlbDik5JTyBERSBGVU5DSU9Ow4FSSU8gCkRPIEbDk1JVTSIJIlRlcm1vIGRlIGNvbnbDqm5pbyBwYXJhIGEgY2Vzc8OjbyBkZSBzZXJ2aWRvciBww7pibGljbyBtdW5pY2lwYWwgCkFnaWxpemHDp8OjbyBkZSBleGVjdcOnw7VlcyBmaXNjYWlzIApQcsOpZGlvIGNvbXBvc3RvIHBlbGEgY2FzYSA5MiBlIHNhbMOjbyA5NiwgUnVhIE1hbm9lbCBWaWxhYm9pbQpKb3PDqSBBcGFyZWNpZG8gQnJlc3NhbmUsIFNpbHZlcmlvIEpvc2UgUGVsaXphcmkgUGludG8sIEFuZHJlYSBDYXRoYXJpbmEuIgkJaHR0cHM6Ly9kcml2ZS5nb29nbGUuY29tL2RyaXZlL2ZvbGRlcnMvMUZUSHlyc05EQllxa3o0U01Jb0loazdHc09KVVpyUDlZP3VzcD1zaGFyaW5nDQo0NwlERUxFR0FDSUEgREEgTVVMSEVSCSJJbnN0YWxhw6fDo28gZSBtYW51dGVuw6fDo28gZGEgRGVsZWdhY2lhIGRlIFBvbMOtY2lhIGRlIERlZmVzYSBkYSBNdWxoZXIgbmEgbG9jYWxpZGFkZQpDb252w6puaW8gMDA0LzIwMDYgCkNlc3PDo28gZGUgaW3Ds3ZlbCBwYXJhIGluc3RhbGHDp8OjbyBlIG1hbnV0ZW7Dp8OjbyBkYSBkZWxlZ2FjaWEgZGEgbXVsaGVyIG5lc3RlIG11bmljw61waW8KTGVpIDIuMTgzLzIwMDYKQ2Vzc8OjbyBkZSBmdW5jaW9uw6FyaW9zIGEgZGVsZWdhY2lhIGRhIG11bGhlciIJCWh0dHBzOi8vZHJpdmUuZ29vZ2xlLmNvbS9kcml2ZS9mb2xkZXJzLzFUWnVZaUx0ZFE0U2ZJRUJjWXhWNnczcVAtb0VlZHhaaT91c3A9c2hhcmluZw0KNDgJQ0VDQU0JIlJlbmF0YSBUb3JyZXMgZGUgU2VuZQpDZWNhbSBDb25zdWx0b3JpYSBlY29uw7RtaWNhLCBjb250w6FiaWwgZSBhZG1pbmlzdHJhdGl2YSAKbXVuaWNpcGFsIGx0ZGEsIGRlY29ycmVudGUgZG8gcHJlZ8OjbyAwMDcvMjAxOCDigJMgUHJvY2Vzc28gMjg1Ny8yMDE4IgkJaHR0cHM6Ly9kcml2ZS5nb29nbGUuY29tL2RyaXZlL2ZvbGRlcnMvMXF0bzBNNnF4RTZYcXNBWXFZVElRZmZVODJmX19rSnJ4P3VzcD1zaGFyaW5nDQo0OQlBVVRPIE9OSUJVUyBNT1JBVEVOU0UgTFREQQkiVGVybW8gZGUgY29udHJhdG8gMTMwLzIwMDYgZGVjb3JyZW50ZSBkZSBwcm9jZXNzbyBkZSBsaWNpdGHDp8OjbyAwNS8yMDA2CkNvbnRyYXRvIDA2Mi8yMDE3LCBDb250cmF0byAwMzAvMjAyMSwKUHJlc3Rhw6fDo28gZGUgc2VydmnDp29zIGRlIHRyYW5zcG9ydGUgZXNjb2xhcgpQcmVnw6NvIDAwOS8yMDE2IOKAkyBQcm9jZXNzbyAzMDI1LzIwMTYKVHJhbnNwb3J0ZSBlc2NvbGFyLCBmb3JuZWNpbWVudG8gZGUgYmlsaGV0ZXMgZWxldHLDtG5pY29zIGNvbSByZWNhcmdhIG1lbnNhbCIJCWh0dHBzOi8vZHJpdmUuZ29vZ2xlLmNvbS9kcml2ZS9mb2xkZXJzLzE5eUtHMHBoR05sbk03aVloY256QUgzVHRlUHcyb2ZwST91c3A9c2hhcmluZw0KNTAJIkFTU09DSUHDh8ODTyBCRU5FRklDRU5URQpEUi4gQ0VMU08gTEVNRSDigJMgU09CRU0iCSJMZWkgbsK6IDIuNDI0LzIwMTAgZGUgMjQgZGUgZmV2ZXJlaXJvIGRlIDIwMTAKVGVybW8gZGUgcGFyY2VyaWEgcGFyYSBmb3JuZWNlciBpbnN1bW9zIG5lY2Vzc8OhcmlvcyBhIGNvbnN0cnXDp8OjbyBkbyBtdXJvIGRlIGFycmltbwpubyBpbW92ZWwgZGUgcHJvcnBpZWRhZGUgZGEgU09CRU4sIHJ1YSB4YXZhbnRlcyAxOSBFTUVJIFBpbmdvIGRlIFNvbApDb252w6puaW8gNzM4Mzk4LzIwMTAKOCBudWNsZW9zIGRlIEVzcG9ydGUgRWR1Y2FjaW9uYWwiCQlodHRwczovL2RyaXZlLmdvb2dsZS5jb20vZHJpdmUvZm9sZGVycy8xRjZ3X3M1LXJYM3JRcFk0LWRCczZHMGp1QTFfdjNPRDE/dXNwPXNoYXJpbmcNCjUxCSJDT05TRUxITyBET1MgRVZBTkfDiUxJQ09TCkRFIEZSQU5DSVNDTyBNT1JBVE8iCUxlaSBuwrogMi42NzAvMjAxMiBkZSAxMGRlIHNldGVtYnJvIGRlIDIwMTIJCWh0dHBzOi8vZHJpdmUuZ29vZ2xlLmNvbS9kcml2ZS9mb2xkZXJzLzE5NUhhY1lZYjBqSTdkY1Y1dGYxa1VrdG5VQlp2MU1DUz91c3A9c2hhcmluZw0KNTIJIlBFTklURU5DScOBUklBIERFIApGUkFOQ08gREEgUk9DSEEiCSJMZWkgbsK6IDEuNzIwLzk3IGRlIDA4IGRlIGRlemVtYnJvIGRlIDE5OTcKVGVybW8gZGUgY29vcGVyYcOnw6NvIHZpc2FuZG8gYSBwcm9waWNpYXIgdHJhYmFsaG8gYSBwb3B1bGHDp8OjbyBjYXJjZXLDoXJpYSBlbSAKQ3VtcHJpbWVudG8gZGUgcGVuYSBwcml2YXRpdmEgZGUgbGliZXJkYWRlIHNvYiByZWdpbWUgU2VtaWFiZXJ0byIJCWh0dHBzOi8vZHJpdmUuZ29vZ2xlLmNvbS9kcml2ZS9mb2xkZXJzLzFDNnU4S3RTRE56WjdtU3BBZWExc2xlUlFHZkswY3kyNz91c3A9c2hhcmluZw0KNTMJRkFDRVNQCSJUZXJtbyBkZSBjb252w6puaW8gY29tIGEgcHJlZmVpdHVyYSBlIGZlZGVyYcOnw6NvIGRhcyBhc3NvY2lhw6fDo28gY29tZXJjaWFsIApEZSBmcmFuY2lzY28gTW9yYXRvIApUZXJtbyBkZSBSZXRpZmljYcOnw6NvIgkJaHR0cHM6Ly9kcml2ZS5nb29nbGUuY29tL2RyaXZlL2ZvbGRlcnMvMU9OT0pYZXdOZE50ZlhaVW50NDM5YzJoRmE2RC1DcXZlP3VzcD1zaGFyaW5nDQo1NAlHVUlNQSBDT05TRUNPCVByZWfDo28gbsK6MTIvMjAxNyBQcm9jZXNzbyBuwrozNTkvMjAxNwkJaHR0cHM6Ly9kcml2ZS5nb29nbGUuY29tL2RyaXZlL2ZvbGRlcnMvMW5RMEtKM3Z6Zk5tcDBxbGZpclAzSlNHeGRDYVJQbXpmP3VzcD1zaGFyaW5nDQo1NQkiRkVERVJBw4fDg08gTkFDSU9OQUwgREUgVU1CQU5EQQpFIENBTkRPTUJMw4kgRSBFTlRJREFERVMgCkRFIENVTFRPUyBBT1MgT1JJWMOBUyIJQ29udHJhdG8gZGUgY29uY2Vzc8OjbyBkZSBkaXJlaXRvIGRlIHVzby4JCWh0dHBzOi8vZHJpdmUuZ29vZ2xlLmNvbS9kcml2ZS9mb2xkZXJzLzFCMThjemVHbndZRktidFdHZ3QyUHN2YWx4NXVPeTZteT91c3A9c2hhcmluZw0KNTYJIlNJU1RFTUEgRVNUQURVQUwgREUgREVGRVNBIApET1MgQU5JTUFJUyBET03DiVNUSUNPUyIJVGVybW8gZGUgQWRlc8OjbwkJaHR0cHM6Ly9kcml2ZS5nb29nbGUuY29tL2RyaXZlL2ZvbGRlcnMvMURTbFpHOGdSR3FhY2p6ejlEekVyZWlaSzN4QzNteklzP3VzcD1zaGFyaW5nDQo1NwkiU0VDUkVUQVJJQSBEQSBBRE1JTklTVFJBw4fDg08gClBFTklURU5DScOBUklBIgkiSW1wbGVtZW50YcOnw6NvIGUgZXhlY3XDp8OjbyBjb250aW51YWRhIGRlIHByb2dyYW1hcyBkYSBjb29yZGVuYWRvcmlhIGRlIHJlaW50ZWdyYcOnw6NvClNvY2lhbCBlIGNpZGFkYW5pYSBlIGEgaW5zdGFsYcOnw6NvIGRhIHVuaWRhZGUgZGUgYXRlbmRpbWVudG8gZGUgcmVpbnRlZ3Jhw6fDo28gc29jaWFsIgkJaHR0cHM6Ly9kcml2ZS5nb29nbGUuY29tL2RyaXZlL2ZvbGRlcnMvMU1La3pyMnNQMkNlS1JsM2pIZ29MRFFoNE1hbXY3Tm4zP3VzcD1zaGFyaW5nDQo1OAkiTUlUUkEgRElPQ0VTQU5BIApERSBCUkFHQU7Dh0EgUEFVTElTVEEiCUNvbnRyYXRvIGRlIGNvbmNlc3PDo28gZGUgRGlyZWl0byBSZWFsIGRlIHVzbwkJaHR0cHM6Ly9kcml2ZS5nb29nbGUuY29tL2RyaXZlL2ZvbGRlcnMvMXJzdmpPVFIyU21JQlNXQnM3cHhlOWRlZEl1a3hRVDJkP3VzcD1zaGFyaW5nDQo1OQkiU09DSUVEQURFIEFNSUdPUyBETyBKQVJESU0gCkJBVElTVEEgR0VOTkFSSSIJIlByb2Nlc3NvIGludGVybm8gMDA4LzIwMDUsIENvbnRyYXRvIGRlIGNvbmNlc3PDo28gZGUgZGlyZWl0byBSZWFsIGRlIHVzbwpEZWNyZXRvIG7CuiAwNzMgRy8yMDAyIgkJaHR0cHM6Ly9kcml2ZS5nb29nbGUuY29tL2RyaXZlL2ZvbGRlcnMvMUM3V0xXVkJaMFUxSU02eWd2c201RDU4RFNEdEtfQ1pSP3VzcD1zaGFyaW5nDQo2MAkiQVNTRU1CTMOJSUEgREUgREVVUwpNSU5JU1TDiVJJTyBNQVJDSEEgREEgRsOJIgkiUHJvY2Vzc28gaW50ZXJubyAwMDMvMDQgLENvbmNlc3PDo28gZGUgZGlyZWl0byBSZWFsIGRlIHVzbwpBdGEgZGUgZnVuZGHDp8OjbwpNZW1vcmlhbCBEZXNjcml0aXZvIgkJaHR0cHM6Ly9kcml2ZS5nb29nbGUuY29tL2RyaXZlL2ZvbGRlcnMvMWw4WjJqcVVqdU5jajQzUWllWG0zZ2dSRURXTWs2T3VxP3VzcD1zaGFyaW5nDQo2MQkiQ0FTQSBERSBSRUNVUEVSQcOHw4NPCkpFU1VTIMOJIFZJREEiCSJQcm9jZXNzbyBpbnRlcm5vIDAwMi8yMDAyClNvbGljaXRhw6fDo28gZGUgRGlyZWl0byBSZWFsIGRlIHVzbyIJCWh0dHBzOi8vZHJpdmUuZ29vZ2xlLmNvbS9kcml2ZS9mb2xkZXJzLzFFc0dqZEpTOHNHZFlmZFhUM2w3TTRnLWNSZ29wYlhGZz91c3A9c2hhcmluZw0KNjIJIlBFTlRFQ09TVEFMIFBST05UTyAKU09DT1JSTyBERSBKRVNVUyIJQ29uY2Vzc8OjbyBkZSBEaXJlaXRvIGRlIHVzbyBSZWFsIGRvIEltw7N2ZWwJCWh0dHBzOi8vZHJpdmUuZ29vZ2xlLmNvbS9kcml2ZS9mb2xkZXJzLzE2UFlhTVdqYVZIRXhMSUdnUkctbDRmS0hnRHYwcm1Rbz91c3A9c2hhcmluZw0KNjMJIlBFTlRFQ09TVEFMIApQw4NPIERBIFZJREEiCUNvbnRyYXRvIGRlIGNvbmNlc3PDo28gZGUgRGlyZWl0byBSZWFsIGRlIFVzbwkJaHR0cHM6Ly9kcml2ZS5nb29nbGUuY29tL2RyaXZlL2ZvbGRlcnMvMV8zZWpfZU5uaTNXNzJYVlJmdXprY0psRU94QW1QaGtPP3VzcD1zaGFyaW5nDQo2NAkiUEVOVEVDT1NUQUwgClRFU1RFTVVOSEEgREUgSkVTVVMgQ1JJU1RPIgkiUHJvamV0byBkZSBMZWkgCkNvbmNlc3PDo28gZGUgRGlyZWl0byBSZWFsIGRlIHVzbyAxMS8wOS8yMDAwIgkJaHR0cHM6Ly9kcml2ZS5nb29nbGUuY29tL2RyaXZlL2ZvbGRlcnMvMTBKaUxyeE1uZXNWallrQWV2c3F0NExqYWFCX1p6eUYyP3VzcD1zaGFyaW5nDQo2NQkiU09DSUVEQURFIEFNSUdPUyBET1MgQkFJUlJPUwpKQVJESU0gU8ODTyBTRVZFUklOTwpWSUxBIEPDgVBVQSBFIEpBUkRJTSBTw4NPIEpPUkdFIgkiVmlsYSBDw6FwdWEgZSBKYXJkaW0gU8OjbyBKb3JnZSAKQ29udHJhdG8gZGUgY29uY2Vzc8OjbyBkZSBkaXJlaXRvIFJlYWwgZGUgdXNvIChjb25mLkxlaSBNdW5pY2lwYWwgbsK6IDEwMDkvODggMTkvMDUvODgpIgkJaHR0cHM6Ly9kcml2ZS5nb29nbGUuY29tL2RyaXZlL2ZvbGRlcnMvMS1QNXIwekhiZ1pYclI4bWJSREJ2dGstYVlGZGw3eXVYP3VzcD1zaGFyaW5nDQo2NgkiSUdSRUpBIEFTU0VNQkzDiUlBIERFIERFVVMKTUlOSVNUw4lSSU8gREUgRlJBTkNJU0NPIE1PUkFUTyIJIkxlaSBuwrogMS44MTYvOTkgZGUgMDggZGUganVuaG8gZGUgMTk5OQpDb250cmF0byBkZSBjb25jZXNzw6NvIGRlIGRpcmVpdG8gcmVhbCBkZSB1c28uIgkJaHR0cHM6Ly9kcml2ZS5nb29nbGUuY29tL2RyaXZlL2ZvbGRlcnMvMWd6aUtEaVhFSGV1S2xVWmowRHpPd29YREt5YWFtY0RwP3VzcD1zaGFyaW5nDQo2NwkiQ09OU1RSVcOHw4NPIERPIDI2wrogCkJBVEFMSMODTyBEQSBQT0zDjUNJQSBNSUxJVEFSIgkiTGVpIG7CuiAyLjA4OS8yMDA0IGRlIDIzIGRlIEFnb3N0byBkZSAyMDA0CkxlaSBuwrogMi4xMDAvMjAwNCBkZSAwOSBkZSBkZXplbWJybyBkZSAyMDA0CkNvbnRyYXRvIGRlIENvbmNlc3PDo28gZGUgZGlyZWl0byBSZWFsIGRlIHVzbyIJCWh0dHBzOi8vZHJpdmUuZ29vZ2xlLmNvbS9kcml2ZS9mb2xkZXJzLzFzdWI1OFJabFcxbHRfaXJaZ3M3eXM2QW4tRkdMNGlZVz91c3A9c2hhcmluZw0KNjgJIlNPQ0lFREFERSBBTUlHT1MgRE8gCkpBUkRJTSBOT1NTQSBTRU5IT1JBIEFQQVJFQ0lEQSIJIkxlaSBuwrogMS44MjgvOTkgZGUgMjMgZGUgQWdvc3RvIGRlIDE5OTkKQ29uY2Vzc8OjbyBkZSBkaXJlaXRvIFJlYWwgZGUgdXNvIgkJaHR0cHM6Ly9kcml2ZS5nb29nbGUuY29tL2RyaXZlL2ZvbGRlcnMvMVlHNkF3Q25LLW82X1ZrZVlKQ29vNlNlaUhLcHNXbTZmP3VzcD1zaGFyaW5nDQo2OQkiQVNTRU1CTMOJSUEgREUgREVVUwpJTlNUSVRVScOHw4NPIENVTFRVUkFMCkUgQVNTSVNURU5DSUFMIChOw4NPIExPQ0FMSVpBREEpIgkiTGVpIG7CuiAxLjg4Ny8yMDAwCkF1dMOzZ3JhZm8gMzgvMjAwMApDb250cmF0byBkZSBDb25jZXNzw6NvIGRlIGRpcmVpdG8gUmVhbCBkZSB1c28iCQkNCjcwCSJBU1NFTUJMw4lJQSBERSBERVVTCklOU1RJVFVJw4fDg08gQ1VMVFVSQUwKRSBBU1NJU1RFTkNJQUwiCSJMZWkgbsK6IDEuODg3LzIwMDAKQXV0w7NncmFmbyAzOC8yMDAwCkNvbnRyYXRvIGRlIENvbmNlc3PDo28gZGUgZGlyZWl0byBSZWFsIGRlIHVzbyIJCWh0dHBzOi8vZHJpdmUuZ29vZ2xlLmNvbS9kcml2ZS9mb2xkZXJzLzE1eTA5ZzZ4YUlMS196YmZUUXZlUVFHZkFPbUZJRDBiej91c3A9c2hhcmluZw0KNzEJIklNUExBTlRBw4fDg08gRE8gUFJPR1JBTUEKQVRJVklEQURFIERFTEVHQURBIgkiUHJvY2Vzc28gNjM5NS8yMDEyCkxlaSBuwrogMi42NDUvMjAxMgpDZXJ0aWTDo28iCQlodHRwczovL2RyaXZlLmdvb2dsZS5jb20vZHJpdmUvZm9sZGVycy8xRzM3QnJDV0FuWDhFYmczRms4RmVZSDhQdnJjNmZlaDY/dXNwPXNoYXJpbmcNCjcyCUNBUlTDk1JJTyBFTEVJVE9SQUwJVGVybW8gZGUgY29udsOqbmlvIFpvbmEgMzY3CQlodHRwczovL2RyaXZlLmdvb2dsZS5jb20vZHJpdmUvZm9sZGVycy8xZzE3bWVfSUtDT1dDTVFPVU9XUGY3dmwyS0E2T2oxX3Y/dXNwPXNoYXJpbmcNCjczCSJDSUNJCkNFTlRSTyBERSBJTlRFR1JBw4fDg08gCkUgQ0lEQURBTklBIglUZXJtbyBkZSBDb252w6puaW8sIFByb3RvY29sbyBkZSBpbnRlbsOnw7VlcwkJaHR0cHM6Ly9kcml2ZS5nb29nbGUuY29tL2RyaXZlL2ZvbGRlcnMvMXRIUXgya2FXQnJBSUVMT0hCS0swSHVBWnBqZU81TWo5P3VzcD1zaGFyaW5nDQo3NAkiUFJPQ09OCkZSQU5DSVNDTyBNT1JBVE8iCUNvbnbDqm5pbyBlbnRyZSBQcm9jb24gZSBQcmVmZWl0dXJhIGRlIEZyYW5jaXNjbyBNb3JhdG8JCWh0dHBzOi8vZHJpdmUuZ29vZ2xlLmNvbS9kcml2ZS9mb2xkZXJzLzFpNUozeWIxN01JYWxWSWNUc2ZJbF8xM0NZT1FmZF9tWj91c3A9c2hhcmluZw0KNzUJIkVTVEFETyBERSBTw4NPIFBBVUxPIApDw5NESUdPIERFIFRSQU5TSVRPIgkiTGVpIG7CuiA5LjUwMy85NyAKVGVybW8gZGUgY29udsOqbmlvIgkJaHR0cHM6Ly9kcml2ZS5nb29nbGUuY29tL2RyaXZlL2ZvbGRlcnMvMWVFZy1uZnlsemY3R2VNOWRJQUJHSnBnTHMyZllVRDAtP3VzcD1zaGFyaW5nDQo3NgkiRFJPR0FSSUEgCkVDT07DlE1JQ0EgRkFSTUEiCSJNYXJpYSBCZXTDom5pYSBCLiBCYXJib3NhIOKAkyBNRSAKQ29udsOqbmlvIG7CuiAwMDEvMjAwOSAKUHJvY2Vzc28gcHJvdG9jb2xhZG8gc29iOiAyMDA5LzY0NS0xIgkJaHR0cHM6Ly9kcml2ZS5nb29nbGUuY29tL2RyaXZlL2ZvbGRlcnMvMXRBc29tSF9WVzlHYVNBVEY5Nmw2TUhuNHpDM1RrUGZPP3VzcD1zaGFyaW5nDQo3NwlDSVJFVFJBTglSRUZPUk1BIFBSw4lESU8gQ0lSRVRSQU4g4oCTIElNTAkJaHR0cHM6Ly9kcml2ZS5nb29nbGUuY29tL2RyaXZlL2ZvbGRlcnMvMXlYY1dsR2xzbzF6al9PR0cxdlB2akxLOVo2U3hpbi1mP3VzcD1zaGFyaW5nDQo3OAlUUklCVU5BTCBERSBKVVNUScOHQQkiMcK6IFRFUk1PIERFIEFESVRBTUVOVE8KQ29udmVuaW8gbsK6IDAwMC4wOTIvMjAxNS9jdgpSZW5vdmHDp8OjbyBjb252w6puaW8gcHLDqWRpb3MiCQlodHRwczovL2RyaXZlLmdvb2dsZS5jb20vZHJpdmUvZm9sZGVycy8xQlJUWXZyemQzTkJtci1sUnJ3UmJwMWE0QURzU21aMWs/dXNwPXNoYXJpbmcNCjc5CURlcGFydGFtZW50byBFc3RhZHVhbCBkZSBUcmFuc2l0bwlDb25jZXNzw6NvIGRlIERpcmVpdG8gZGUgdXNvIFJlYWwgZG8gSW3Ds3ZlbAkJaHR0cHM6Ly9kcml2ZS5nb29nbGUuY29tL2RyaXZlL2ZvbGRlcnMvMVprNnRXRnI2TFBNWlJaQWdTRTBUN1gtWUxCSmJPTEIyP3VzcD1zaGFyaW5nDQo4MAlDQVJUw5NSSU8gREUgUkVHSVNUUk8gREUgSU1PVkVJUwkiVEVSTU8gREUgQ09OVkVOSU8gUVVFIENFTEVCUkFNIEZSQU5DSVNDTyBNT1JBVE8gCkUgTyBDQVJUT1JJTyBERSBSRUdJU1RSTyBERSBJTU9WRUlTIgkJaHR0cHM6Ly9kcml2ZS5nb29nbGUuY29tL2RyaXZlL2ZvbGRlcnMvMUhWTDBLSG1UdE1PcWhwQm5id0I1OEhic2hlRURhS3ZWP3VzcD1zaGFyaW5nDQo4MQkiQ09OVkVOSU8gRU5UUkUgQSBQUkVGRUlUVVJBIERFIApGUkFOQ0lTQ08gTU9SQVRPIEUgQSBQUk9DVVJBRE9SSUEtR0VSQUwgCkRBIEZBWkVOREEgTkFDSU9OQUwgLSBQR0ZOIgkiVEVSTU8gREUgQ09OVkVOSU8gUVVFIENFTEVCUkFNIEZSQU5DSVNDTyBNT1JBVE8gRSAKQSBQUk9DVVJBRE9SSUEgR0VSQUwgREEgRkFaRU5EQSBOQUNJT05BTCIJCWh0dHBzOi8vZHJpdmUuZ29vZ2xlLmNvbS9kcml2ZS9mb2xkZXJzLzF6MTFPUlNBWnZCblh5NmhTZm9OZFJseV8zVjVwZUtuWD91c3A9c2hhcmluZw0KODIJQ0VOVFJPIERFIFBST0ZFU1NPUkFETyBQQVVMSVNUQSDigJMgQ1BQCSJURVJNTyBERSBDT05Ww4pOSU8gUVVFIENFTEVCUkFNIEVOVFJFIEZSQU5DSVNDTyBNT1JBVE8gRSBPIENFTlRSTyBERSAKUFJPRkVTU09SQURPIFBBVUxJU1RBIENQUCIJCWh0dHBzOi8vZHJpdmUuZ29vZ2xlLmNvbS9kcml2ZS9mb2xkZXJzLzEya0Y1ZjE2c1hmMmRZbXQ4MktvaHVSdjZFbXhjTGttYj91c3A9c2hhcmluZw0KODMJVFJJQlVOQUwgREUgSlVTVEnDh0EJIlRFUk1PIERFIENPT1BFUkHDh8ODTyBUw4lDTklDQSBOwrogMDAwLjAwNiAyMDI1IOKAkyBGSVJNQU0gQSBJTlRFR1JBw4fDg08gRE8gUFJPQ0VTU08gREUgClRST0NBIERFIElORk9STUHDh8OVRVMgRU5UUkUgQVMgUEFSVEVTIEFUUkFWw4lTIERPIElOVEVSQ8OCTUJJTyBERSBEQURPUyIJCWh0dHBzOi8vZHJpdmUuZ29vZ2xlLmNvbS9kcml2ZS9mb2xkZXJzLzFfYkdITG1wbzFzWkI3OFpLVDlZempiMktNRWJCZzN3Qz91c3A9c2hhcmluZw0KODQJVFJUCSJURVJNTyBERSBDT05WRU5JTyBRVUUgQ0VMRUJSQU0gRlJBTkNJU0NPIE1PUkFUTyBFIE8gVFJUIERBIDLCuiBSRUdJw4NPIApQQVJBIE8gClNFUlZJw4dPIERFIEpVU1RJw4dBIElUSU5FUkFOVEUiCQlodHRwczovL2RyaXZlLmdvb2dsZS5jb20vZHJpdmUvZm9sZGVycy8xWXJHcVpPVDlYcGFtUXJVNHFZRFdLdHBLbEh6R2otc3I/dXNwPXNoYXJpbmcNCjg1CSJDT05WRU5JTyBFTlRSRSBBIFBSRUZFSVRVUkEgRSBPIEdPVkVSTk8gRE8gRVNUQURPIApERSBTUCAtIFNFSSIJVGVybW8gZGUgQ29vcGVyYcOnw6NvIFTDqWNuaWNhIG7CuiA3Ni0yMDI0IC0gQ29uc2VsaG8gTmFjaW9uYWwgZGUgSnVzdGnDp2EgZSBQcm9jdXJhZG9yaWEgZG8gRXN0YWRvIGRlIFNQCQlodHRwczovL2RyaXZlLmdvb2dsZS5jb20vZHJpdmUvZm9sZGVycy8xMEhlTGtmRk9OVlpMdkItdzVDcngyeFRxMXZRMGV5RFk/dXNwPXNoYXJpbmcNCjg2CSJDT05Ww4pOSU8g4oCTIElFUFRCIOKAkyBUQUJFTEnDg08gREUgTk9UQVMgCihFWEVDVcOHw4NPIEZJU0NBTCkiCSJDT05Ww4pOSU8gUVVFIENFTEVCUkFNIEVOVFJFIEZSQU5DSVNDTyBNT1JBVE8gRSBPIElOU1RJVFVUTyBERQogRVNUVURPUyBERQogUFJPVEVTVE9TIERFIFTDjVRVTE9TIERPIEJSQVNJTCDigJMgT0JKRVRJVkFORE8gQSBFRkVUSVZBw4fDg08gREUKIFBST1RFU1RPIERFIENSw4lESVRPIApDT01QT05FTlRFIERBIETDjVZJREEgQVRJVkEgRE8gTVVOSUNJUElPIOKAkyBQUk9DRVNTTyBBRE1JTklTVFJBVElWTyAxMTk0MS8yMDI0IgkJaHR0cHM6Ly9kcml2ZS5nb29nbGUuY29tL2RyaXZlL2ZvbGRlcnMvMXJ0eDQ3OWtzbWd3MmxMdlg5TVItZHZwbU1IVTBFRzZpP3VzcD1zaGFyaW5n"
).decode("utf-8-sig")


def get_connection():
    return psycopg2.connect(DATABASE_URL)


def initialize_database() -> None:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                    id BIGSERIAL PRIMARY KEY,
                    pasta TEXT NOT NULL DEFAULT '',
                    nome TEXT NOT NULL DEFAULT '',
                    conteudo TEXT NOT NULL DEFAULT '',
                    link TEXT NOT NULL DEFAULT ''
                )
                """
            )
            cursor.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}")
            if cursor.fetchone()[0] == 0:
                import_embedded_data(connection)
        connection.commit()


def import_embedded_data(connection) -> int:
    inserted = 0
    reader = csv.reader(io.StringIO(EMBEDDED_TSV), delimiter="\t", quotechar='"')
    next(reader, None)
    with connection.cursor() as cursor:
        for row in reader:
            if not row or not any(cell.strip() for cell in row):
                continue
            values = (row + [""] * 5)[:5]
            # A quarta coluna da fonte é vazia; o link está na quinta coluna.
            cursor.execute(
                f"INSERT INTO {TABLE_NAME} (pasta, nome, conteudo, link) VALUES (%s, %s, %s, %s)",
                (values[0].strip(), values[1].strip(), values[2].strip(), values[4].strip()),
            )
            inserted += 1
    connection.commit()
    return inserted


def list_items(search: str = "") -> list[dict[str, Any]]:
    with get_connection() as connection:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            if search.strip():
                pattern = f"%{search.strip()}%"
                cursor.execute(
                    f"""
                    SELECT id, pasta, nome, conteudo, link
                    FROM {TABLE_NAME}
                    WHERE pasta ILIKE %s OR nome ILIKE %s OR conteudo ILIKE %s OR link ILIKE %s
                    ORDER BY id
                    """,
                    (pattern, pattern, pattern, pattern),
                )
            else:
                cursor.execute(f"SELECT id, pasta, nome, conteudo, link FROM {TABLE_NAME} ORDER BY id")
            return [dict(row) for row in cursor.fetchall()]


def save_item(data: dict[str, str], item_id: int | None = None) -> None:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            if item_id is None:
                cursor.execute(
                    f"INSERT INTO {TABLE_NAME} (pasta, nome, conteudo, link) VALUES (%s, %s, %s, %s)",
                    (data["pasta"], data["nome"], data["conteudo"], data["link"]),
                )
            else:
                cursor.execute(
                    f"""
                    UPDATE {TABLE_NAME}
                    SET pasta = %s, nome = %s, conteudo = %s, link = %s
                    WHERE id = %s
                    """,
                    (data["pasta"], data["nome"], data["conteudo"], data["link"], item_id),
                )
        connection.commit()


def delete_item(item_id: int) -> None:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(f"DELETE FROM {TABLE_NAME} WHERE id = %s", (item_id,))
        connection.commit()


initialize_database()

COLUMNS = [
    {"name": "pasta", "label": "Pasta", "field": "pasta", "align": "left", "sortable": True},
    {"name": "nome", "label": "Nome", "field": "nome", "align": "left", "sortable": True},
    {"name": "conteudo", "label": "Conteúdo", "field": "conteudo", "align": "left"},
    {"name": "link", "label": "Pasta Digitalizada", "field": "link", "align": "left"},
]


@ui.page("/")
def main_page() -> None:
    search_input: ui.input
    item_table: ui.table
    dialog: ui.dialog
    total_label: ui.label
    fields: dict[str, Any] = {}
    current_id: int | None = None

    def refresh_table() -> None:
        item_table.rows = list_items(search_input.value or "")
        item_table.update()
        total_label.set_text(f"{len(item_table.rows)} registro(s) exibido(s)")

    def close_dialog() -> None:
        dialog.close()

    def save_form() -> None:
        data = {key: str(field.value or "").strip() for key, field in fields.items()}
        if not data["nome"] and not data["conteudo"]:
            ui.notify("Informe o nome ou o conteúdo do convênio.", type="warning")
            return
        save_item(data, current_id)
        close_dialog()
        refresh_table()
        ui.notify("Registro salvo com sucesso.", type="positive")

    def confirm_delete() -> None:
        if current_id is None:
            return
        with ui.dialog() as confirmation:
            with ui.card().classes("w-96"):
                ui.label("Excluir registro?").classes("text-h6")
                ui.label("Esta ação não poderá ser desfeita.").classes("text-gray-600")
                with ui.row().classes("w-full justify-end gap-2 mt-4"):
                    ui.button("Cancelar", on_click=confirmation.close).props("flat")
                    def do_delete() -> None:
                        delete_item(current_id)
                        confirmation.close()
                        close_dialog()
                        refresh_table()
                        ui.notify("Registro excluído.", type="positive")
                    ui.button("Excluir", color="negative", on_click=do_delete)
        confirmation.open()

    def open_form(item: dict[str, Any] | None = None) -> None:
        nonlocal current_id
        current_id = item["id"] if item else None
        dialog.clear()
        with dialog, ui.card().classes("w-full max-w-4xl"):
            ui.label("Editar convênio" if item else "Adicionar convênio").classes("text-h5")
            ui.label("Informe os dados do convênio, parceria ou instrumento administrativo.").classes("text-gray-600 mb-3")
            with ui.column().classes("w-full gap-2"):
                fields["pasta"] = ui.input("Pasta", value=str(item.get("pasta", "") if item else "")).props("outlined dense")
                fields["nome"] = ui.textarea("Nome", value=str(item.get("nome", "") if item else "")).props("outlined autogrow")
                fields["conteudo"] = ui.textarea("Conteúdo", value=str(item.get("conteudo", "") if item else "")).props("outlined autogrow")
                fields["link"] = ui.input("Pasta Digitalizada", value=str(item.get("link", "") if item else "")).props("outlined dense")
            with ui.row().classes("w-full justify-between mt-4"):
                if item:
                    ui.button("Excluir", icon="delete", color="negative", on_click=confirm_delete).props("outline")
                else:
                    ui.element("div")
                with ui.row().classes("gap-2"):
                    ui.button("Cancelar", on_click=close_dialog).props("flat")
                    ui.button("Salvar", icon="save", color="primary", on_click=save_form)
        dialog.open()

    def handle_double_click(event: Any) -> None:
        args = event.args
        row = None
        if isinstance(args, dict):
            row = args.get("row") or args
        elif isinstance(args, list):
            for value in args:
                if isinstance(value, dict) and ("id" in value or "row" in value):
                    row = value.get("row", value)
                    break
        if row and row.get("id") is not None:
            item = next((value for value in item_table.rows if value["id"] == row["id"]), None)
            if item:
                open_form(item)

    ui.add_head_html("""
        <style>
            body { background: #f5f7fb; }
            .q-table th { font-weight: 700; background: #f0e9df; }
            .q-table tbody tr { cursor: pointer; }
            .q-table tbody tr:hover { background: #fff7ed !important; }
        </style>
    """)

    with ui.header().classes("items-center justify-between bg-amber-950 px-6"):
        with ui.row().classes("items-center gap-3"):
            ui.icon("handshake", size="32px").classes("text-amber-200")
            ui.label("Convênios e Parcerias").classes("text-h5 text-white font-bold")
        ui.label("Cadastro de instrumentos administrativos").classes("text-amber-100")

    with ui.column().classes("w-full max-w-screen-2xl mx-auto p-6 gap-4"):
        with ui.card().classes("w-full"):
            with ui.row().classes("w-full items-end gap-3"):
                search_input = ui.input("Buscar por pasta, nome, conteúdo ou link").props("outlined clearable").classes("flex-1")
                ui.button("Buscar", icon="search", on_click=refresh_table).classes("h-14")
                ui.button("Adicionar registro", icon="add", color="primary", on_click=lambda: open_form()).classes("h-14")
            search_input.on("keydown.enter", refresh_table)

        with ui.row().classes("w-full items-center justify-between"):
            total_label = ui.label()
            ui.label("Dica: dê duplo clique em uma linha para editar ou excluir.").classes("text-gray-600")

        item_table = ui.table(columns=COLUMNS, rows=list_items(), row_key="id", pagination={"rowsPerPage": 25}).classes("w-full")
        item_table.add_slot(
            "body-cell-link",
            """
            <q-td :props="props">
                <a v-if="props.value" :href="props.value" target="_blank" rel="noopener" class="text-amber-800 underline">Abrir pasta</a>
                <span v-else class="text-gray-400">Sem link</span>
            </q-td>
            """,
        )
        item_table.on("rowDblclick", handle_double_click)
        total_label.set_text(f"{len(item_table.rows)} registro(s) exibido(s)")

    dialog = ui.dialog()


ui.run(title="Convênios e Parcerias", host="0.0.0.0", port=PORT, reload=False)
