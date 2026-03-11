"""
Jarvis AI — Tam Sistem Doğrulama Testi

Tüm bileşenleri sırayla test eder:
  1. Python modül importları
  2. Settings konfigürasyonu
  3. Ollama LLM erişimi + model listesi
  4. Qdrant vektör veritabanı (Tailscale)
  5. Nextcloud WebDAV (Tailscale)
  6. n8n otomasyon (Tailscale)
  7. FastAPI sunucu başlatma + health endpoint
  8. Chat endpoint (gerçek LLM çağrısı)
"""

import asyncio
import sys
import time


PASS = "  [OK]"
FAIL = "  [XX]"
WARN = "  [!!]"


def section(title: str) -> None:
    print(f"\n{'='*50}")
    print(f"  {title}")
    print(f"{'='*50}")


# ── 1. Import Kontrolleri ──────────────────────────────────

def test_imports() -> bool:
    section("1. MODUL IMPORT KONTROLLERI")
    tests = [
        ("settings",              "from Config.settings import get_settings"),
        ("logging_config",        "from Config.logging_config import get_logger, setup_logging"),
        ("Server.app",            "from Server.app import app"),
        ("Server.schemas",        "from Server.schemas import ChatRequest, ChatResponse, HealthResponse"),
        ("Server.dependencies",   "from Server.dependencies import SessionManager, SharedState"),
        ("Core.async_handler",    "from Core.async_handler import process_input_async"),
        ("Integrations.qdrant",   "from Integrations.qdrant_memory import QdrantMemory"),
        ("Integrations.nextcloud","from Integrations.nextcloud_client import NextcloudClient"),
        ("Integrations.n8n",      "from Integrations.n8n_client import N8NClient"),
        ("MCP.tool_registry",     "from MCP.tool_registry import mcp"),
        ("MCP.tools.memory",      "from MCP.tools.memory_tools import remember, recall"),
        ("MCP.tools.cloud",       "from MCP.tools.cloud_tools import cloud_list, cloud_read, cloud_write"),
        ("MCP.tools.notification","from MCP.tools.notification_tools import send_telegram, send_notification"),
    ]
    ok = 0
    for name, imp in tests:
        try:
            exec(imp)
            ok += 1
            print(f"{PASS} {name}")
        except Exception as e:
            print(f"{FAIL} {name}: {e}")
    total = len(tests)
    print(f"\n  Sonuc: {ok}/{total}")
    return ok == total


# ── 2. Settings ────────────────────────────────────────────

def test_settings() -> bool:
    section("2. SETTINGS KONFIGURASYONU")
    try:
        from Config.settings import get_settings
        s = get_settings()
        print(f"{PASS} API:       {s.api_host}:{s.api_port}")
        print(f"{PASS} Ollama:    {s.ollama_base_url}")
        print(f"{PASS} Qdrant:    {s.qdrant_url}")
        print(f"{PASS} Nextcloud: {s.nextcloud_url}")
        print(f"{PASS} n8n:       {s.n8n_webhook_url}")
        print(f"{PASS} Embedding: {s.embedding_model} ({s.embedding_dim}d)")
        return True
    except Exception as e:
        print(f"{FAIL} Settings yuklenemedi: {e}")
        return False


# ── 3. Ollama ──────────────────────────────────────────────

def test_ollama() -> bool:
    section("3. OLLAMA LLM")
    try:
        import httpx
        from Config.settings import get_settings
        url = get_settings().ollama_base_url
        r = httpx.get(f"{url}/api/tags", timeout=5)
        if r.status_code == 200:
            models = [m["name"] for m in r.json().get("models", [])]
            print(f"{PASS} Baglanti: OK")
            print(f"{PASS} Modeller: {', '.join(models)}")

            has_embed = any("nomic-embed" in m for m in models)
            if has_embed:
                print(f"{PASS} nomic-embed-text: Yuklu")
            else:
                print(f"{WARN} nomic-embed-text: YOK — 'ollama pull nomic-embed-text' calistir")
            return True
        else:
            print(f"{FAIL} HTTP {r.status_code}")
            return False
    except Exception as e:
        print(f"{FAIL} Ollama erisilemedi: {e}")
        return False


# ── 4. Qdrant ──────────────────────────────────────────────

def test_qdrant() -> bool:
    section("4. QDRANT VEKTOR VERITABANI (Tailscale)")
    try:
        import httpx
        from Config.settings import get_settings
        url = get_settings().qdrant_url
        r = httpx.get(f"{url}/collections", timeout=10)
        if r.status_code == 200:
            collections = r.json().get("result", {}).get("collections", [])
            names = [c["name"] for c in collections]
            print(f"{PASS} Baglanti: {url}")
            print(f"{PASS} Collections: {names if names else '(bos — ilk calisma)'}")
            return True
        else:
            print(f"{FAIL} HTTP {r.status_code}")
            return False
    except Exception as e:
        print(f"{FAIL} Qdrant erisilemedi: {e}")
        return False


# ── 5. Nextcloud ───────────────────────────────────────────

def test_nextcloud() -> bool:
    section("5. NEXTCLOUD WEBDAV (Tailscale)")
    try:
        import httpx
        from Config.settings import get_settings
        s = get_settings()
        r = httpx.get(f"{s.nextcloud_url}:8080/status.php", timeout=10)
        if r.status_code == 200:
            data = r.json()
            print(f"{PASS} Baglanti: {s.nextcloud_url}:8080")
            print(f"{PASS} Versiyon: {data.get('versionstring', '?')}")
            print(f"{PASS} Kurulum:  {'Tamamlandi' if data.get('installed') else 'Bekleniyor'}")
            return True
        else:
            print(f"{WARN} HTTP {r.status_code} (Nextcloud kurulumu tamamlanmamis olabilir)")
            return False
    except Exception as e:
        print(f"{FAIL} Nextcloud erisilemedi: {e}")
        return False


# ── 6. n8n ─────────────────────────────────────────────────

def test_n8n() -> bool:
    section("6. N8N OTOMASYON (Tailscale)")
    try:
        import httpx
        from Config.settings import get_settings
        s = get_settings()
        base = f"http://{s.remote_server_ip}:5678"
        r = httpx.get(f"{base}/healthz", timeout=10, follow_redirects=True)
        if r.status_code == 200:
            print(f"{PASS} Baglanti: {base}")
            print(f"{PASS} Durum: Calisiyor")
            return True
        else:
            # n8n bazen /healthz 404 verir ama ana sayfa 200 olabilir
            r2 = httpx.get(base, timeout=10, follow_redirects=True)
            if r2.status_code == 200:
                print(f"{PASS} Baglanti: {base}")
                print(f"{PASS} Durum: Calisiyor (web UI erisiliyor)")
                return True
            print(f"{FAIL} HTTP {r.status_code}")
            return False
    except Exception as e:
        print(f"{FAIL} n8n erisilemedi: {e}")
        return False


# ── 7. FastAPI ─────────────────────────────────────────────

def test_fastapi() -> bool:
    section("7. FASTAPI SUNUCU")
    from Server.app import app
    routes = [r.path for r in app.routes if hasattr(r, "methods")]
    print(f"{PASS} App:    {app.title} v{app.version}")
    print(f"{PASS} Routes: {routes}")
    return True


# ── 8. Chat Endpoint (Canli LLM Testi) ────────────────────

def test_chat_endpoint() -> bool:
    section("8. CHAT ENDPOINT (Canli LLM Testi)")
    import httpx
    import threading

    # Sunucuyu ayri thread'de baslat
    port = 18765
    server_ready = threading.Event()

    def run_server():
        import uvicorn
        from Config.settings import get_settings
        config = uvicorn.Config("Server.app:app", host="127.0.0.1", port=port, log_level="error")
        server = uvicorn.Server(config)
        server_ready.set()
        server.run()

    t = threading.Thread(target=run_server, daemon=True)
    t.start()
    server_ready.wait()
    time.sleep(1.5)  # uvicorn'un tam baslamasi icin

    try:
        from Config.settings import get_settings
        r = httpx.get(f"http://127.0.0.1:{port}/api/health", timeout=10)
        if r.status_code != 200:
            print(f"{FAIL} Health endpoint: HTTP {r.status_code}")
            return False

        health = r.json()
        print(f"{PASS} Health: status={health['status']}, ollama={health['ollama_reachable']}, qdrant={health['qdrant_reachable']}")

        # Gercek chat testi
        print(f"  ... LLM'e mesaj gonderiliyor (bu 5-15 saniye surebilir)...")
        start = time.time()
        r = httpx.post(
            f"http://127.0.0.1:{port}/api/chat",
            json={"user_id": "test_user", "message": "Merhaba Jarvis", "platform": "api"},
            timeout=60,
        )
        elapsed = time.time() - start

        if r.status_code == 200:
            data = r.json()
            response_text = data.get("response", "")
            action = data.get("action_taken", "?")
            ms = data.get("processing_time_ms", 0)
            # Yanitı kısalt
            short = response_text[:80] + "..." if len(response_text) > 80 else response_text
            print(f"{PASS} Yanit:   \"{short}\"")
            print(f"{PASS} Aksiyon: {action}")
            print(f"{PASS} Sure:    {ms:.0f}ms (toplam: {elapsed:.1f}s)")
            return True
        else:
            print(f"{FAIL} Chat: HTTP {r.status_code}")
            try:
                print(f"  Detay: {r.json()}")
            except Exception:
                pass
            return False

    except httpx.ReadTimeout:
        print(f"{FAIL} Zaman asimi — Ollama yavas olabilir, tekrar dene")
        return False
    except Exception as e:
        print(f"{FAIL} Chat testi hatasi: {e}")
        return False


# ── Ana ────────────────────────────────────────────────────

def main():
    print()
    print("  JARVIS AI — TAM SISTEM DOGRULAMA")
    print(f"  Tarih: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    results = {}
    results["Imports"]   = test_imports()
    results["Settings"]  = test_settings()
    results["Ollama"]    = test_ollama()
    results["Qdrant"]    = test_qdrant()
    results["Nextcloud"] = test_nextcloud()
    results["n8n"]       = test_n8n()
    results["FastAPI"]   = test_fastapi()
    results["Chat"]      = test_chat_endpoint()

    section("SONUC TABLOSU")
    all_ok = True
    for name, ok in results.items():
        icon = PASS if ok else FAIL
        print(f"{icon} {name}")
        if not ok:
            all_ok = False

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    print(f"\n  {'='*40}")
    if all_ok:
        print(f"  TUMU GECTI ({passed}/{total}) — Sistem tamamen hazir!")
    else:
        print(f"  {passed}/{total} gecti — Yukaridaki hatalara bak")
    print()


if __name__ == "__main__":
    main()
