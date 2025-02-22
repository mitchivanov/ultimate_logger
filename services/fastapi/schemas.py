from pydantic import BaseModel

# Базовая схема продукта
class ProductBase(BaseModel):
    name: str
    description: str

# Схема для создания продукта (принимается от клиента)
class ProductCreate(ProductBase):
    pass

# Схема для ответа с данными продукта
class ProductResponse(ProductBase):
    id: int

    class Config:
        from_attributes = True  # Новое название для orm_mode в Pydantic V2 