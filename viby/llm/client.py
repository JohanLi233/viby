from typing import Optional
from viby.utils.lazy_import import lazy_import

# 懒加载 OpenAI 库以减少启动时间
openai = lazy_import("openai")


def create_openai_client(
    api_key: Optional[str],
    base_url: str,
    http_referer: Optional[str] = None,
    app_title: Optional[str] = None,
):
    default_headers = {}
    default_headers["HTTP-Referer"] = http_referer
    default_headers["X-Title"] = app_title

    return openai.OpenAI(
        api_key=api_key or "EMPTY",
        base_url=base_url.rstrip("/"),
        default_headers=default_headers if default_headers else None,
    )
