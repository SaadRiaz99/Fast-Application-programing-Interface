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


app = FastAPI()

@app.get("/")

def main():
    return "I am Saad Bin Riaz and learn a fastapi "