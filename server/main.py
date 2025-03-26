from fastapi import FastAPI

from fastapi.exceptions import RequestValidationError
from server.error.email_exception_handler import validation_exception_handler

from server.routes import email_receiver, email_result

from server.configs.lifespan import lifespan


app = FastAPI(openapi_url="/openapi.json", lifespan=lifespan)

app.add_exception_handler(RequestValidationError, validation_exception_handler)

# router
app.include_router(email_receiver.router)
app.include_router(email_result.router)

# main module
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)