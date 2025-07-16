from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from services import GenericCRUDService

def get_crud_router(model, schema_in, schema_update, schema_out):
    router = APIRouter()
    service = GenericCRUDService(model)

    @router.get("/", response_model=list[schema_out])
    def read_all(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
        return service.get_all(db, skip, limit)

    @router.get("/{id}", response_model=schema_out)
    def read_one(id: int, db: Session = Depends(get_db)):
        obj = service.get(db, id)
        if not obj:
            raise HTTPException(status_code=404, detail="Item not found")
        return obj

    @router.post("/", response_model=schema_out)
    def create(obj_in: schema_in, db: Session = Depends(get_db)):
        return service.create(db, obj_in.dict())

    @router.put("/{id}", response_model=schema_out)
    def update(id: int, obj_in: schema_update, db: Session = Depends(get_db)):
        db_obj = service.get(db, id)
        if not db_obj:
            raise HTTPException(status_code=404, detail="Item not found")
        return service.update(db, db_obj, obj_in.dict(exclude_unset=True))

    @router.delete("/{id}")
    def delete(id: int, db: Session = Depends(get_db)):
        service.delete(db, id)
        return {"detail": "Deleted successfully"}

    return router
