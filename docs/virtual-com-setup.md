# Configuração conceitual da COM virtual

Solicite ao administrador/TI um driver externo de portas COM virtuais aprovado
para o ambiente. Instalação e configuração podem exigir administrador. O projeto
não instala drivers nem cria portas automaticamente.

## Caso validado com com0com

O com0com foi utilizado no teste como um null modem virtual: cria duas portas
COM conectadas entre si, e o que é escrito em uma ponta fica disponível na outra.
O par abaixo foi validado com comunicação bidirecional, software operacional e
registro TX/RX. COM13/COM14 são exemplos usados no teste, não números obrigatórios.
Depois da configuração do driver, o proxy apenas abre portas já existentes.

Configure um par, por exemplo:

```text
COM13 ↔ COM14
```

1. Configure o software existente para abrir **COM13**.
2. Configure o tr_serialProxy com `--virtual-port COM14`.
3. Identifique a COM física com `python -m tr_serial_proxy --list-ports`.
4. Configure `--physical-port COM6` (substitua pela porta real) e os parâmetros
   esperados pelo dispositivo e pelo software.
5. Inicie o proxy e depois a comunicação do software.

```powershell
python -m tr_serial_proxy --physical-port COM6 --virtual-port COM14 --baud 9600
```

O software não deve abrir COM6 diretamente durante a captura. Feche terminais ou
outros programas que ocupem COM14/COM6. As portas física e virtual do proxy devem
ser diferentes. O próprio pySerial suporta números acima de COM9.

O uso normal do proxy não deve exigir elevação quando as portas já estiverem
disponíveis e o usuário tiver acesso. Use o procedimento aprovado de instalação
do driver mantendo as proteções do Windows habilitadas.

Alterações dinâmicas de baud, paridade ou sinais de controle na COM13 não são
propagadas automaticamente pelo proxy. Consulte as [limitações](limitations.md)
e o [teste manual com dois pares](../examples/README.md).

## Comando com porta física a substituir

```powershell
python -m tr_serial_proxy --physical-port COMX --virtual-port COM14 --baud 9600 --raw-log
```

Substitua **COMX** pelo nome real da porta conectada ao dispositivo antes de
executar. Ajuste baud e demais parâmetros ao equipamento. Mantenha o software na
COM13: ele não precisa conhecer COMX. Veja o [procedimento validado](validation.md).
