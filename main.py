from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates



app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="template") 
@app.get("/home")
# def main():
#     print("Hello I am Saad Bin Riaz I engineer")


# if __name__ == "__main__":
#     main()
@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        "landing.html",
        {"request": request}
    )


@app.get("/dashboard")
async def dashboard(request: Request):
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request}
    )


@app.get("/login")
async def login(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {"request": request}
    )
