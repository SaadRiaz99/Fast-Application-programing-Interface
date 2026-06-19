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
from fastapi import jinja2

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


app = FastAPI()
templates = Jinja2Templates(directory = "template")
class user(BaseModel):
    name : str
    Age : int
@app.get("/")

def main():
    return "I am Saad Bin Riaz and learn a fastapi "


@app.get("/user/{user_id}")
def readid(user_id : int , q : str |None = None):
    print(f"user Id {user_id and q is {q}}")