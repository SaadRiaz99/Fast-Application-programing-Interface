from fastapi import FastAPI


app = FastAPI()


@app.get("/")
def main():
    print("Hello I am Saad Bin Riaz I engineer")


if __name__ == "__main__":
    main()
