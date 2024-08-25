import fastapi

app = fastapi.FastAPI()


@app.post('/notification')
async def notification(data=fastapi.Body()):
    print(data)


@app.post('/successful_payment')
async def successful_payment(data=fastapi.Body()):
    print(data)


@app.post('/back')
async def back(data=fastapi.Body()):
    print(data)
