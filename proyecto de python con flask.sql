CREATE DATABASE api_flask;
use api_flask;

CREATE TABLE cliente (
    idcliente INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100),
    appaterno VARCHAR(100),
    apmaterno VARCHAR(100),
    cedula varchar(12)
);

CREATE TABLE producto (
    idproducto INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100),
    precioProducto DECIMAL(5,2),
    stock INT
);

CREATE TABLE factura (
    idfactura INT AUTO_INCREMENT PRIMARY KEY,
    fechaFactura DATE,
    fkcliente INT,
    FOREIGN KEY (fkcliente) REFERENCES cliente(idcliente)
);

CREATE TABLE detalle (
    iddetalle INT AUTO_INCREMENT PRIMARY KEY,
    fkfactura INT,
    fkproducto INT,
    cantidad INT,
    precioventa DECIMAL(5,2),
    FOREIGN KEY (fkfactura) REFERENCES factura(idfactura),
    FOREIGN KEY (fkproducto) REFERENCES producto(idproducto)
);
CREATE TABLE usuario (
    idUsuario INT AUTO_INCREMENT PRIMARY KEY,
    Nombre VARCHAR(100),
    contraseña VARCHAR(100)
);



insert into usuario (Nombre,contraseña) values ('Vichin','12345');

select idcliente,nombre,appaterno,apmaterno from cliente;
insert into cliente (nombre,appaterno,apmaterno,cedula) values ("Victor","Avendaño","Parreño","00000000000");
update cliente set cliente.nombre= "Juan" , cliente.appaterno = "Perez",cliente.apmaterno= "Cano" ,cliente.cedula = "096844095" where cliente.idcliente= 1;
delete from cliente where cliente.idcliente= 1;

Select idproducto,nombre,precioProducto,stock from producto;

insert into producto (nombre,precioProducto,stock) values ("lapiz",2.5,5);
delete from producto where producto.idproducto= 8;
update producto set producto.nombre = "Arroz" , producto.precioProducto = 2.8,producto.stock = 99 where producto.idproducto= 2;
delete from producto where producto.idproducto= 5;

/*  Consulta Dinamica*/
select* from producto where producto.nombre like concat('%','A','%');
select* from cliente where cliente.nombre like concat('%','v','%');

/* Creando factura*/
insert into factura (fechafactura,fkcliente) values (curdate(),1);
select*from factura;

/*INSERTA DETALLE no hay prueba */
insert into detalle(fkfactura,fkproducto,cantidaddetalledetalle,precioventa) values((select max(idfactura) from factura),?,?,?);

/*Reducir stock*/
update producto set stock =stock- ? where idproducto =?;
select*from detalle;

/*Monstrar Ultima Factura*/
select max(idfactura)as ultimaFactura from factura;
/*Mostrar datos de la Factura completa de los datos del cliente*/
select factura.idfactura,factura.fechaFactura,cliente.nombre,cliente.appaterno,cliente.apmaterno from factura inner join cliente on cliente.idcliente =factura.fkcliente where factura.idfactura = 2; 

/*Mostrar producto en base al numero de factura*/
SELECT producto.nombre, detalle.cantidad, detalle.precioventa FROM detalle
INNER JOIN factura ON factura.idfactura = detalle.fkfactura
INNER JOIN producto ON producto.idproducto = detalle.fkproducto
WHERE factura.idfactura = 7;

/*Mostrar ingreso totales total por fecha*/
SELECT factura.idfactura, factura.fechaFactura, producto.nombre, detalle.cantidad, detalle.precioventa FROM detalle
INNER JOIN factura ON factura.idfactura = detalle.fkfactura
INNER JOIN producto ON producto.idproducto = detalle.fkproducto
WHERE factura.idfactura between ? and ?;

/* ejemplo practico*/
CREATE INDEX idx_nombre_producto ON productos(nombre_producto);
/*Antes del tuning*/
SELECT * FROM productos;

/*Despues del tuning*/
SELECT nombre_producto, precio FROM productos 
WHERE categoria = 'electrónica' AND fecha_venta > '2023-01-01';