# FIND UVICORN SERVER PROCESS
# taskkill /F /IM uvicorn.exe

# KILL UVICORN SERVER PROCESS
# taskkill /F /IM uvicorn.exe

# # LOADS A SINGLE PRODUCT ON A PAGE
# @router.get("/{product_id}")
# def product_detail(product_id: str, request: Request):
#     product = next((p for p in PRODUCTS if p["id"] == product_id), None)

#     if not product:
#         return templates.TemplateResponse(
#             "404.html",
#             {"request": request},
#             status_code=404
#         )

#     return templates.TemplateResponse(
#         "product_detail.html",
#         {"request": request, "product": product}
#     )


# Dependecies
# pip install fastapi[all] python-jose sqlalchemy passlib[argon2]