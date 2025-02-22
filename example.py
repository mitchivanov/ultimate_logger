products = {'apple': 10, 'banana': 20, 'orange': 30}

#1. Добавление нового продукта
products['mango'] = 40

#2. Удаление продукта 
del products['banana']

#3. Изменение цены продукта
products['apple'] = 15

#4. Вывод всех продуктов и их цен
print(products)

#5. Вывод цены конкретного продукта
print(products['apple'])

#6. Вывод всех продуктов
for product in products:
    print(product)
    
#7. Вывод всех продуктов и их цен
for product, price in products.items():
    print(f'{product}: {price}')

