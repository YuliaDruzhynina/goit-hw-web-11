import pathlib
import time
from typing import List

from fastapi import FastAPI, Depends, HTTPException, status, Path, Request, Query

#from sqlalchemy import text
from sqlalchemy.orm import Session
from datetime import date, timedelta, datetime
from db import get_db
from models import Contact
from schema import ContactSchema, ContactResponse

app = FastAPI()



@app.get("/")
def main_root():
    return {"message": "Application V0.0.1"}


@app.get("/contacts", response_model=list[ContactResponse])
async def get_contacts(db: Session = Depends(get_db)):
    contacts = db.query(Contact).all()
    return contacts


@app.get("/contacts/id/{contact_id}", response_model=ContactResponse)
async def get_contact_by_id(contact_id: int = Path(ge=1), db: Session = Depends(get_db)):
    contact = db.query(Contact).filter_by(id=contact_id).first()
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact

@app.get("/contacts/by_name/{contact_fullname}", response_model=ContactResponse)
async def get_contact_by_fullname(contact_fullname: str = Path(...), db: Session = Depends(get_db)):
    contact = db.query(Contact).filter(Contact.fullname.ilike(f"%{contact_fullname}%")).first()
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact

@app.get("/contacts/by_email/{contact_email}", response_model=ContactResponse)
async def get_contact_by_email(contact_email: str = Path(...), db: Session = Depends(get_db)):
    print("Searching for contact with name:", contact_email)
    contact = db.query(Contact).filter(Contact.email.ilike(f"%{contact_email}%")).first()
    print("Found contact:", contact)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact

@app.get("/contacts/by_birthday/{get_birthday}", response_model=list[ContactResponse])
async def get_upcoming_birthdays(db: Session = Depends(get_db)):
    current_date = date.today()
    future_date = current_date + timedelta(days=7)
    contacts = db.query(Contact).filter(current_date >= Contact.birthday, Contact.birthday <= future_date).all()
    print(contacts)
    return contacts

@app.get("/contacts/get_new_day/{new_date}", response_model=list[ContactResponse])
async def get_upcoming_birthdays_from_new_date(new_date: str = Path(..., description="Current date in format YYYY-MM-DD"),db: Session = Depends(get_db)):
    new_date_obj = datetime.strptime(new_date,"%Y-%m-%d").date()
    future_date = new_date_obj + timedelta(days=7)
    contacts = db.query(Contact).filter(Contact.birthday >= new_date_obj, Contact.birthday <= future_date).all()
    
    print(contacts)
    return contacts

@app.post("/contacts/", response_model=ContactSchema)
async def create_contact(body: ContactSchema, db: Session = Depends(get_db)):
    contact = db.query(Contact).filter_by(email=body.email).first()
    if contact:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Contact already exists!")

    contact=Contact(fullname=body.fullname, phone_number=body.phone_number, email=body.email, birthday =body.birthday)
    # Создаем новый контакт
    # new_contact = Contact(**body.dict())
    db.add(contact)
    db.commit()
    return contact

@app.put("/contacts/update/{contact_id}", response_model=ContactResponse)
async def update_contact(body: ContactSchema, contact_id: int = Path(ge=1),db: Session = Depends(get_db)):
    contact = db.query(Contact).filter_by(id = contact_id).first()
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    
    contact.fullname = body.fullname
    contact.email = body.email
    contact.phone_number = body.phone_number
    contact.birthday = body.birthday

    db.commit()
    return contact


@app.delete("/contacts/{contact_id}", response_model=ContactResponse)
async def delete_contact(contact_id: int = Path(ge=1), db: Session = Depends(get_db)):
    contact = db.query(Contact).filter_by(id=contact_id).first()
    if contact is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Contact does not exist!")
    db.delete(contact)
    db.commit()
    return contact

# @app.exception_handler(HTTPException)
# def handle_http_exception(request: Request, exc: HTTPException):
#     return {"message": str(exc.detail)}

# @app.exception_handler(ValidationError)
# def validation_error_handler(request: Request, exc: ValidationError):
#     return JSONResponse(
#         status_code=status.HTTP_400_BAD_REQUEST,
#         content={"message": "Invalid input data"}
#     )

# @app.exception_handler(HTTPException)
# def http_exception_handler(request: Request, exc: HTTPException):
#     return JSONResponse(
#         status_code=exc.status_code,
#         content={"message": exc.detail},
#     )

# @app.exception_handler(Exception)
# def unexpected_exception_handler(request: Request, exc: Exception):
#     return JSONResponse(
#         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         content={"message": "An unexpected error occurred"},
#     )
