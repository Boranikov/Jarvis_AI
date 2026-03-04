"""
Jarvis AI — Nextcloud WebDAV Client

Jarvis'in kişisel bulut depolama alanına async erişim sağlar.
Nextcloud WebDAV protokolü (PROPFIND, GET, PUT, DELETE) üzerinden çalışır.

Sunucu: Ubuntu (Tailscale mesh — 100.x.x.x)
"""

from dataclasses import dataclass
from typing import Any
from xml.etree import ElementTree as ET

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from logging_config import get_logger
from settings import JarvisSettings, get_settings

logger = get_logger("integrations.nextcloud")

# WebDAV XML namespace
_DAV_NS = "{DAV:}"


@dataclass
class FileInfo:
    """Nextcloud dosya/klasör bilgisi."""

    name: str
    path: str
    is_directory: bool
    size: int = 0
    content_type: str = ""
    last_modified: str = ""


class NextcloudClient:
    """
    Nextcloud WebDAV async client.

    Kullanım:
        client = NextcloudClient(settings)
        files = await client.list_files("/Documents")
        content = await client.read_file("/Documents/notes.txt")
        await client.write_file("/Documents/new.txt", b"Merhaba")
    """

    def __init__(self, settings: JarvisSettings | None = None) -> None:
        self._settings = settings or get_settings()
        self._base_url = self._settings.nextcloud_webdav_url
        self._auth = httpx.BasicAuth(
            username=self._settings.nextcloud_user,
            password=self._settings.nextcloud_pass.get_secret_value(),
        )
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Lazy-initialized async HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                auth=self._auth,
                timeout=httpx.Timeout(30.0, connect=10.0),
                follow_redirects=True,
            )
        return self._client

    def _build_url(self, path: str) -> str:
        """WebDAV URL'sini oluştur."""
        clean_path = path.strip("/")
        return f"{self._base_url}/{clean_path}" if clean_path else self._base_url

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=5))
    async def list_files(self, path: str = "/") -> list[FileInfo]:
        """
        Klasör içeriğini listele (PROPFIND).

        Args:
            path: Klasör yolu (örn: "/Documents")

        Returns:
            FileInfo listesi
        """
        client = await self._get_client()
        url = self._build_url(path)

        # PROPFIND ile dosya/klasör listesi al
        propfind_body = """<?xml version="1.0" encoding="UTF-8"?>
        <d:propfind xmlns:d="DAV:">
            <d:prop>
                <d:displayname/>
                <d:getcontentlength/>
                <d:getcontenttype/>
                <d:getlastmodified/>
                <d:resourcetype/>
            </d:prop>
        </d:propfind>"""

        response = await client.request(
            method="PROPFIND",
            url=url,
            content=propfind_body.encode(),
            headers={
                "Content-Type": "application/xml",
                "Depth": "1",
            },
        )
        response.raise_for_status()

        return self._parse_propfind(response.text, path)

    def _parse_propfind(self, xml_text: str, base_path: str) -> list[FileInfo]:
        """PROPFIND XML yanıtını FileInfo listesine dönüştür."""
        root = ET.fromstring(xml_text)
        files: list[FileInfo] = []

        for response_elem in root.findall(f"{_DAV_NS}response"):
            href_elem = response_elem.find(f"{_DAV_NS}href")
            if href_elem is None:
                continue

            href = href_elem.text or ""
            propstat = response_elem.find(f"{_DAV_NS}propstat")
            if propstat is None:
                continue

            prop = propstat.find(f"{_DAV_NS}prop")
            if prop is None:
                continue

            # Kendi kendini skip et (base path)
            display_name_elem = prop.find(f"{_DAV_NS}displayname")
            display_name = display_name_elem.text if display_name_elem is not None else ""

            resource_type = prop.find(f"{_DAV_NS}resourcetype")
            is_dir = (
                resource_type is not None
                and resource_type.find(f"{_DAV_NS}collection") is not None
            )

            size_elem = prop.find(f"{_DAV_NS}getcontentlength")
            size = int(size_elem.text) if size_elem is not None and size_elem.text else 0

            content_type_elem = prop.find(f"{_DAV_NS}getcontenttype")
            content_type = content_type_elem.text if content_type_elem is not None else ""

            last_modified_elem = prop.find(f"{_DAV_NS}getlastmodified")
            last_modified = last_modified_elem.text if last_modified_elem is not None else ""

            if display_name:
                files.append(
                    FileInfo(
                        name=display_name,
                        path=href,
                        is_directory=is_dir,
                        size=size,
                        content_type=content_type or "",
                        last_modified=last_modified or "",
                    )
                )

        logger.info("files_listed", path=base_path, count=len(files))
        return files

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=5))
    async def read_file(self, path: str) -> bytes:
        """
        Dosya içeriğini oku (GET).

        Args:
            path: Dosya yolu

        Returns:
            Dosya içeriği (bytes)
        """
        client = await self._get_client()
        url = self._build_url(path)

        response = await client.get(url)
        response.raise_for_status()

        logger.info("file_read", path=path, size=len(response.content))
        return response.content

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=5))
    async def write_file(self, path: str, content: bytes | str) -> bool:
        """
        Dosya yaz veya güncelle (PUT).

        Args:
            path: Dosya yolu
            content: Dosya içeriği

        Returns:
            Başarı durumu
        """
        client = await self._get_client()
        url = self._build_url(path)

        if isinstance(content, str):
            content = content.encode("utf-8")

        response = await client.put(url, content=content)
        success = response.status_code in (200, 201, 204)

        logger.info("file_written", path=path, size=len(content), success=success)
        return success

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=5))
    async def delete_file(self, path: str) -> bool:
        """
        Dosya veya klasör sil (DELETE).

        Args:
            path: Dosya/klasör yolu

        Returns:
            Başarı durumu
        """
        client = await self._get_client()
        url = self._build_url(path)

        response = await client.delete(url)
        success = response.status_code in (200, 204)

        logger.info("file_deleted", path=path, success=success)
        return success

    @retry(stop=stop_after_attempt(2), wait=wait_exponential(min=1, max=3))
    async def file_exists(self, path: str) -> bool:
        """
        Dosya/klasör var mı kontrol et (HEAD).

        Args:
            path: Kontrol edilecek yol

        Returns:
            Varsa True
        """
        client = await self._get_client()
        url = self._build_url(path)

        try:
            response = await client.head(url)
            return response.status_code == 200
        except httpx.HTTPStatusError:
            return False

    async def create_directory(self, path: str) -> bool:
        """
        Klasör oluştur (MKCOL).

        Args:
            path: Klasör yolu

        Returns:
            Başarı durumu
        """
        client = await self._get_client()
        url = self._build_url(path)

        response = await client.request(method="MKCOL", url=url)
        success = response.status_code in (200, 201)

        logger.info("directory_created", path=path, success=success)
        return success

    async def close(self) -> None:
        """HTTP client'ı kapat."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None
            logger.info("nextcloud_disconnected")
