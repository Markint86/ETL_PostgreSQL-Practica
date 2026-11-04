-- =====================================================================
--  Consultas de ejemplo sobre los datos cargados
-- =====================================================================

-- 1. Clientes que compraron un producto concreto (productid = 1)
SELECT *
FROM customers c
WHERE EXISTS (
    SELECT 1 FROM purchases p
    WHERE c.customerid = p.customerid
      AND p.productid = 1
);

-- 2. Número de productos distintos que compró cada cliente
SELECT customerid,
       COUNT(DISTINCT productid) AS "Number of Products"
FROM purchases
GROUP BY customerid;

-- 3. Qué productos ha comprado cada cliente
SELECT DISTINCT c.customerid, c.firstname, c.lastname, p.productname
FROM purchases pr
JOIN customers c ON c.customerid = pr.customerid
JOIN products  p ON p.productid  = pr.productid
ORDER BY c.customerid;

-- 4. Ranking de productos más vendidos
WITH product_sales AS (
    SELECT p.productid,
           p.productname,
           COUNT(pr.purchaseid) AS total_sales
    FROM products p
    JOIN purchases pr ON p.productid = pr.productid
    GROUP BY p.productid, p.productname
)
SELECT productid,
       productname,
       total_sales,
       RANK() OVER (ORDER BY total_sales DESC) AS ranking
FROM product_sales;
