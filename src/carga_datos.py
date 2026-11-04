import os
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, URL
from sqlalchemy.exc import SQLAlchemyError

load_dotenv()

engine = create_engine(URL.create(
    drivername="postgresql+psycopg",
    username=os.getenv("DB_USER", "postgres"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", 5432)),
    database=os.getenv("DB_NAME", "Actividad BBDNG"),
))

ruta_archivo = Path(__file__).resolve().parent.parent / "data" / "clientes-productos-plain.txt"

# --- EXTRACT ---
df = pd.read_csv(ruta_archivo, sep=",", skipinitialspace=True)
df.columns = df.columns.str.strip()

# --- TRANSFORM ---
# Validaciones y limpieza
df = df.drop_duplicates()
df = df[df["Precio"] >= 0]
df["Email"] = df["Email"].str.strip().str.lower()
df["Producto"] = df["Producto"].str.strip()

# Un registro por cliente y por producto
clientes = df[["Nombre", "Apellido", "Email"]].drop_duplicates(subset="Email")
productos = df[["Producto", "Precio"]].drop_duplicates(subset="Producto")

# --- LOAD ---
try:
    with engine.begin() as conn:   # todo en una transacción: o entra todo o nada

        # 1. Clientes (si el email ya existe, se ignora)
        conn.execute(text("""
            INSERT INTO customers (firstname, lastname, email)
            VALUES (:Nombre, :Apellido, :Email)
            ON CONFLICT (email) DO NOTHING
        """), clientes.to_dict("records"))

        # 2. Productos (si el nombre ya existe, se ignora)
        conn.execute(text("""
            INSERT INTO products (productname, price)
            VALUES (:Producto, :Precio)
            ON CONFLICT (productname) DO NOTHING
        """), productos.to_dict("records"))

        # 3. Recuperar los IDs que ha generado la BD
        ids_clientes = pd.read_sql(
            text("SELECT customerid, email FROM customers WHERE email = ANY(:emails)"),
            conn, params={"emails": clientes["Email"].tolist()},
        )
        ids_productos = pd.read_sql(
            text("SELECT productid, productname FROM products WHERE productname = ANY(:nombres)"),
            conn, params={"nombres": productos["Producto"].tolist()},
        )

        # 4. Cada línea del txt -> una compra, con sus IDs
        compras = (
            df.merge(ids_clientes, left_on="Email", right_on="email")
              .merge(ids_productos, left_on="Producto", right_on="productname")
              [["customerid", "productid"]]
        )

        compras.to_sql("purchases", conn, if_exists="append", index=False)

    print(f"Carga completada: {len(clientes)} clientes, {len(productos)} productos, {len(compras)} compras.")

except SQLAlchemyError as e:
    print(f"Error en la carga, no se ha insertado nada: {e}")
finally:
    engine.dispose()
