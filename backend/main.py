from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from database import engine, Base, get_db
import models
import schemas
from auth import get_current_user, create_access_token, require_feature
import ai_service
import pdf_service
import whatsapp_service

Base.metadata.create_all(bind=engine)

app = FastAPI(title="FSM Enterprise API", version="4.0")

# --- 1. Авторизация ---
@app.post("/api/auth/login", response_model=schemas.Token)
def login(login_data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == login_data.email).first()
    if not user or user.hashed_password != login_data.password:
        raise HTTPException(status_code=400, detail="Неверный email или пароль")
    
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

# --- 2. Заказы (Starter Tier) ---
@app.post("/api/orders", response_model=schemas.OrderResponse)
def create_order(
    order_in: schemas.OrderCreate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    new_order = models.Order(
        title=order_in.title,
        description=order_in.description,
        address=order_in.address,
        assigned_to=order_in.assigned_to,
        company_id=current_user.company_id
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order

@app.get("/api/orders", response_model=List[schemas.OrderResponse])
def get_my_orders(
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    orders = db.query(models.Order).filter(models.Order.assigned_to == current_user.id).all()
    return orders

@app.patch("/api/orders/{order_id}/status", response_model=schemas.OrderResponse)
def update_order_status(
    order_id: UUID, 
    status_update: schemas.OrderStatusUpdate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
        
    order.status = status_update.status
    db.commit()
    db.refresh(order)
    return order

# --- 3. Трекинг геолокации ---
@app.post("/api/geo/track")
def receive_geo_track(
    location: schemas.GeoLocation, 
    current_user: models.User = Depends(get_current_user)
):
    print(f"📍 GPS Мастера {current_user.email}: {location.latitude}, {location.longitude}")
    return {"status": "ok"}

# --- 4. Склад в машине / Van Stock (Pro Tier Feature Flag) ---
@app.get(
    "/api/van-inventory", 
    response_model=List[schemas.VanInventoryResponse],
    dependencies=[Depends(require_feature("van_stock"))]
)
def get_my_van_stock(
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    stock = db.query(models.VanInventory).filter(models.VanInventory.user_id == current_user.id).all()
    return stock

@app.post(
    "/api/van-inventory/consume", 
    dependencies=[Depends(require_feature("van_stock"))]
)
def consume_part(
    consume_data: schemas.VanStockConsume, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    item_in_van = db.query(models.VanInventory).filter(
        models.VanInventory.user_id == current_user.id,
        models.VanInventory.item_id == consume_data.item_id
    ).first()

    if not item_in_van or item_in_van.quantity < consume_data.quantity:
        raise HTTPException(status_code=400, detail="Недостаточно запчастей в авто складе")

    item_in_van.quantity -= consume_data.quantity
    db.commit()

    return {
        "status": "success", 
        "consumed": consume_data.quantity, 
        "remaining": item_in_van.quantity
    }

# --- 5. AI Copilot: Перевод заметок (Pro Tier) ---
@app.post(
    "/api/ai/translate", 
    response_model=schemas.TranslateResponse,
    dependencies=[Depends(require_feature("ocr"))]
)
def translate_note(
    payload: schemas.TranslateRequest,
    current_user: models.User = Depends(get_current_user)
):
    translated = ai_service.translate_text(payload.text, payload.target_lang)
    return {
        "original_text": payload.text,
        "translated_text": translated,
        "target_lang": payload.target_lang
    }

# --- 6. AI Copilot: Gemini Vision OCR Сканер (Pro Tier) ---
@app.post(
    "/api/ai/ocr",
    dependencies=[Depends(require_feature("ocr"))]
)
async def scan_label_ocr(
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user)
):
    image_bytes = await file.read()
    result = ai_service.scan_equipment_label(image_bytes)
    return result

# --- 7. AI Quality Gate: Проверка фотоотчётов (Enterprise Tier) ---
@app.post(
    "/api/ai/quality-check",
    dependencies=[Depends(require_feature("ai_copilot"))]
)
async def check_photo_quality(
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user)
):
    image_bytes = await file.read()
    result = ai_service.validate_repair_photo(image_bytes)
    return result

# --- 8. AI Voice-to-Task: Голосовые отчёты (Enterprise Tier) ---
@app.post(
    "/api/ai/voice-report",
    dependencies=[Depends(require_feature("ai_copilot"))]
)
async def process_voice_report(
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user)
):
    audio_bytes = await file.read()
    result = ai_service.process_voice_note(audio_bytes, mime_type=file.content_type or "audio/wav")
    return result

# --- 9. Генерация PDF-инвойсов (Rechnung) ---
@app.get("/api/invoices/generate/{order_id}")
def download_invoice(
    order_id: UUID, 
    db: Session = Depends(get_db)
):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    title = order.title if order else "Сервисный ремонт оборудования"
    address = order.address if order else "г. Берлин, ул. Александрплац, 12"

    sample_items = [
        {"name": "Выезд мастера и диагностика", "quantity": 1, "unit_price": 85.00},
        {"name": "Заправка хладагента R410A", "quantity": 2, "unit_price": 45.00}
    ]
    
    pdf_bytes = pdf_service.generate_invoice_pdf(
        order_title=title,
        address=address,
        items=sample_items,
        total_amount=175.00,
        currency="EUR"
    )

    return Response(
        content=pdf_bytes, 
        media_type="application/pdf", 
        headers={"Content-Disposition": f"attachment; filename=Rechnung_{order_id}.pdf"}
    )

# --- 10. WhatsApp Уведомление клиенту ---
@app.post("/api/whatsapp/send-invoice/{order_id}")
def send_whatsapp_invoice(
    order_id: UUID,
    phone: str = "+4915112345678",
    client_name: str = "Клиент",
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    order_title = order.title if order else "Сервисные работы"

    res = whatsapp_service.send_invoice_and_tracking_link(
        phone_number=phone,
        client_name=client_name,
        order_title=order_title,
        order_id=str(order_id)
    )
    return res