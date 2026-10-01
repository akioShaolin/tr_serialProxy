# Exemplos genéricos

Após instalar o pacote, substitua as portas pelos nomes disponíveis no ambiente.
Os exemplos não usam capturas reais.

## USB-TTL — 115200 8N1

```powershell
tr-serial-proxy --physical-port COM6 --virtual-port COM21 --baud 115200 --bytesize 8 --parity N --stopbits 1
```

## RS485 — 9600 8N1

```powershell
tr-serial-proxy --physical-port COM8 --virtual-port COM21 --baud 9600 --bytesize 8 --parity N --stopbits 1
```

## RS485 — 19200 8E1

```powershell
tr-serial-proxy --physical-port COM8 --virtual-port COM21 --baud 19200 --bytesize 8 --parity E --stopbits 1
```

RS485 depende do controle de direção do adaptador/driver; o programa não configura
comutação manual de RTS.

## Log estruturado reversível

```powershell
tr-serial-proxy --physical-port COM6 --virtual-port COM21 --baud 115200 --raw-log --log-dir logs --log-prefix serial
```

## Modo quiet

```powershell
tr-serial-proxy --physical-port COM6 --virtual-port COM21 --baud 9600 --quiet
```

## Listar portas

```powershell
tr-serial-proxy --list-ports
```

Em todos os exemplos, `tr-serial-proxy` pode ser substituído por
`python -m tr_serial_proxy`. Veja [todos os argumentos](usage.md).
