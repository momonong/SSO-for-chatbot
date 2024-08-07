from fastapi import FastAPI, Request, Depends, HTTPException, status, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from requests_oauthlib import OAuth2Session
from dotenv import load_dotenv
from datetime import timedelta
import requests
import logging
import base64
import json
import os
import httpx
import asyncio

# 設置日誌記錄
logging.basicConfig(level=logging.DEBUG)

load_dotenv()  # 加載 .env 文件中的變量

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY"))

# Use relative path for templates directory
current_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(current_dir, "templates")
templates = Jinja2Templates(directory=template_dir)
print(f"\n\nTemplate directory: {template_dir}\n\n")

# OAuth 配置
CLIENT_ID = os.getenv("OAUTH2_CLIENT_ID")
CLIENT_SECRET = os.getenv("OAUTH2_CLIENT_SECRET")
AUTHORIZATION_BASE_URL = os.getenv("OAUTH2_AUTHORIZATION_URL")
TOKEN_URL = os.getenv("OAUTH2_TOKEN_URL")
REDIRECT_URI = os.getenv("OAUTH2_REDIRECT_URI")
RESOURCE = os.getenv("OAUTH2_RESOURCE")
USER_INFO_URL = os.getenv("OAUTH2_USER_INFO_URL")
LOGOUT_URL = os.getenv("OAUTH2_LOGOUT_URL")


def clear_token(session):
    if "oauth_token" in session:
        del session["oauth_token"]


def decode_token(access_token):
    try:
        jwt_parts = access_token.split(".")
        if len(jwt_parts) != 3:
            raise ValueError("Invalid token format")
        payload_encoded = jwt_parts[1]
        payload_encoded += "=" * (4 - len(payload_encoded) % 4)
        payload_decoded = base64.urlsafe_b64decode(payload_encoded)
        payload = json.loads(payload_decoded)
        return payload
    except Exception as e:
        print(f"\n\nError decoding token: {str(e)}\n\n")
        return {}


def normalize_name(display_name, student_en_name):
    """
    Normalize the display name and student English name to ensure consistent formatting.
    """
    if student_en_name.lower() not in display_name.lower():
        full_name = f"{display_name} {student_en_name}"
    else:
        full_name = display_name
    return full_name


@app.get("/register", response_class=RedirectResponse)
def index(request: Request):
    session = request.session
    session.clear()
    clear_token(session)

    chat_id = request.query_params.get("chat_id")
    if chat_id:
        print(f"\n\nReceived chat_id: {chat_id}\n\n")
        session["chat_id"] = chat_id
    else:
        print(f"\n\nDid not receive chat_id\n\n")

    logout_redirect = f"https://fs.ncku.edu.tw/adfs/ls/?wa=wsignout1.0&wreply=https://chatbot.oia.ncku.edu.tw/register/start-auth"
    return RedirectResponse(url=logout_redirect)


@app.get("/register/start-auth", response_class=RedirectResponse)
def start_auth(request: Request):
    session = request.session
    chat_id = session.get("chat_id")
    if chat_id:
        print(f"\n\nUsing chat_id from session: {chat_id}\n\n")
    else:
        raise HTTPException(status_code=400, detail="No chat_id found in session")

    ncku = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI)
    authorization_url, state = ncku.authorization_url(
        AUTHORIZATION_BASE_URL, resource=RESOURCE
    )
    session["oauth_state"] = state
    session["chat_id"] = chat_id  # 再次保存 chat_id
    print(f"\n\noauth state: {state}\nChat ID: {chat_id}\n\n")
    return RedirectResponse(url=authorization_url)


@app.get("/register/callback", response_class=RedirectResponse)
def register_callback(request: Request):
    authorization_code = request.query_params.get("code")
    try:
        data = {
            "grant_type": "authorization_code",
            "code": authorization_code,
            "redirect_uri": REDIRECT_URI,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        }
        response = requests.post(TOKEN_URL, data=data)
        if response.status_code == 200:
            token = response.json()
            request.session["access_token"] = token
            print(f"\n\nAccess token: {token}\n\n")
            print(f"\n\nSession: {request.session}\n\n")
            return RedirectResponse(url="/register/fill-form")
        else:
            raise HTTPException(
                status_code=400, detail=f"Failed to fetch token: {response.json()}"
            )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch token: {str(e)}")


@app.get("/register/fill-form", response_class=HTMLResponse)
def fill_form(request: Request):
    if "access_token" not in request.session:
        raise HTTPException(
            status_code=400, detail="User info not found in the session"
        )
    token = request.session.get("access_token")
    user_info = decode_token(token["access_token"])
    user_info["normalized_name"] = normalize_name(
        user_info["DisplayName"], user_info["studentStuEnName"]
    )
    print(f"\n\nUser info: {user_info}\n\n")
    return templates.TemplateResponse(
        "fill_form.html", {"request": request, "user_info": user_info}
    )


@app.post("/register/submit-info", response_class=HTMLResponse)
async def submit_info(
    request: Request,
    name: str = Form(...),
    department: str = Form(...),
    student_id: str = Form(...),
    line_name: str = Form(...),
    nationality: str = Form(...),
    language: str = Form(...),
    status: str = Form(...),
):
    session = request.session
    chat_id = session.get("chat_id")

    # 檢查所有表單數據是否存在
    if not all(
        [
            name,
            department,
            student_id,
            line_name,
            nationality,
            language,
            status,
            chat_id,
        ]
    ):
        print("\n\nMissing form data or chat_id.\n\n")
        return templates.TemplateResponse("submission_error.html", {"request": request})

    # 打印所有提交的表單數據
    print("\n所有提交的表單數據:")
    print(
        f"name: {name}, department: {department}, student_id: {student_id}, line_name: {line_name}, nationality: {nationality}, language: {language}, status: {status}, chat_id: {chat_id}"
    )
    print("\n\n")
    redirect_url = f"https://chatbot.oia.ncku.edu.tw/sign_up/student/{nationality}&{student_id}&{name}&{department}&{line_name}&{language}&{status}&{chat_id}"

    # Asynchronous request
    try:
        response_text = await send_async_request(redirect_url)
        if response_text:
            print(f"\n\nredirect_url: {redirect_url}\n\n")
            return templates.TemplateResponse(
                "submission_success.html", {"request": request}
            )
        else:
            print("\n\nFailed to send data to the API. Rendering error page.\n\n")
            return templates.TemplateResponse(
                "submission_error.html", {"request": request}
            )
    except Exception as e:
        print(f"\n\nError during async request: {str(e)}\n\n")
        return templates.TemplateResponse("submission_error.html", {"request": request})


async def send_async_request(url):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            if response.status_code == 200:
                print("\n\nData successfully sent to the API.\n\n")
                return response.text
            else:
                print(f"\n\nFailed to send data to the API: {response.status_code}\n\n")
                return None
        except Exception as e:
            print(f"\n\nError sending data to the API: {str(e)}\n\n")
            return None


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
