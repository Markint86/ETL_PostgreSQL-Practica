-- =====================================================================
--  Esquema de la base de datos "Actividad BBDNG"
--  Tienda de ropa: clientes, productos y compras (modelo en 3NF)
-- =====================================================================

CREATE TABLE Customers
(
    CustomerID  INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    FirstName   VARCHAR(30) NOT NULL,
    LastName    VARCHAR(30) NOT NULL,
    Email       VARCHAR(50) UNIQUE
);

CREATE TABLE Products
(
    ProductID   INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    ProductName VARCHAR(30) NOT NULL UNIQUE,   -- se asume que el nombre identifica al producto
    Price       DECIMAL(10,2) NOT NULL CHECK (Price >= 0)
);

CREATE TABLE Purchases
(
    PurchaseID   INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    CustomerID   INTEGER NOT NULL,
    ProductID    INTEGER NOT NULL,
    PurchaseDate DATE,
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID),
    FOREIGN KEY (ProductID)  REFERENCES Products(ProductID)
);
