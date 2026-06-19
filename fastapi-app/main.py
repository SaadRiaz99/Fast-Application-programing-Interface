# from fastapi import FastApi 


# app = fastApi()


# @app.get("/")
# def main():
#     return {"message": "Hello I am saad Bin Riaz"}


# def main(firstname : str , lastname : str ):
#     firstname.capitalize()
#     return firstname + lastname


# first = "Saad"

# last = "Riaz"
# a = main(first , last)
# print(a)

from fastapi import FastAPI
from pydantic import BaseModel
# from pydantic import BaseModel
# from fastapi import jinja2

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
# from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()
templates = Jinja2Templates(directory = "template")
app.mount("/static", StaticFiles(directory="static"), name="static")
class user(BaseModel):
    name : str
    Age : int
@app.get("/")

def main():
    return "I am Saad Bin Riaz and learn a fastapi "


@app.get("/user/{user_id}")
def readid(user_id : int , q : str |None = None):
    print(f"user Id {user_id and q is {q}}")

@app.get("/home")
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": "FastAPI Template",
            "message": "Welcome to FastAPI!"
        }
    )