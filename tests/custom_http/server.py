import httpx

from xeely.custom_http.server import run_http_server


def test_running_server():
    lhost = "127.0.0.1"
    lport = 8000

    with run_http_server(lhost=lhost, lport=lport):
        response = httpx.get(f"http://{lhost}:{lport}")
        assert response.status_code == 200
