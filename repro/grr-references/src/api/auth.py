from fastapi import Request


def identity(request: Request) -> str:
    return request.headers.get("x-auth-request-email", "local-developer")
