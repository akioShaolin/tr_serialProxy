# Uso e referência da CLI

Instale o pacote conforme o [README](../README.md).

## Opções

| Opção | Padrão / valores |
| --- | --- |
| `--physical-port` | Obrigatória, por exemplo COM6 |
| `--virtual-port` | Obrigatória, ponta aberta pelo Python, por exemplo COM21 |
| `--baud` | Obrigatório, inteiro positivo |
| `--bytesize` | 8; aceita 5, 6, 7, 8 |
| `--parity` | N; aceita N, E, O, M, S (também minúsculas) |
| `--stopbits` | 1; aceita 1, 1.5, 2 |
| `--timeout` | 0.01 s; finito e positivo |
| `--write-timeout` | 1 s; finito e positivo |
| `--xonxoff` | Habilita controle de fluxo por software XON/XOFF; desabilitado por padrão |
| `--rtscts` | Habilita controle de fluxo RTS/CTS; desabilitado por padrão |
| `--dsrdtr` | Habilita controle de fluxo DSR/DTR; desabilitado por padrão |
| `--chunk-size` | 4096 bytes; inteiro positivo |
| `--log-dir` | `./logs` |
| `--log-prefix` | `serial`; letras ASCII, números, hífen e sublinhado |
| `--quiet` | Suprime tráfego no terminal; mantém configuração, erros e resumo |
| `--ascii` | Acrescenta visualização ASCII imprimível (32–126); demais bytes viram `.` |
| `--raw-log` | Acrescenta arquivo JSONL com os bytes em hexadecimal |
| `--list-ports` | Lista portas, descrição e identificador; dispensa argumentos obrigatórios |

Timeouts ilimitados e leitura sem bloqueio não são aceitos, para permitir
encerramento e evitar consumo desnecessário de CPU. COM acima de COM9 é tratada
pelo próprio pySerial. Configurações inválidas para um driver podem ser rejeitadas
na abertura mesmo que sejam valores serial válidos.

## Logs e contadores

Cada execução cria um `.log` exclusivo com data, hora e microssegundos no nome.
`--raw-log` cria também um `.jsonl` de mesmo nome-base.

- **TX:** software → dispositivo físico.
- **RX:** dispositivo físico → software.

```text
[2026-09-30T14:35:22.123456-03:00] [+0.381224] TX  8 bytes
01 03 00 10 00 02 C5 CE
```

```json
{"time":"2026-09-30T14:35:22.123456-03:00","elapsed":0.381224,"direction":"TX","length":8,"data":"010300100002c5ce"}
```

`time` é o horário local com fuso, formatado com microssegundos (a precisão real
depende do sistema). `elapsed` usa `time.perf_counter()` desde a criação da captura.
O timestamp é coletado após a leitura, não no instante de chegada ao fio.
Os bytes não passam por decodificação Unicode: hexadecimal é uma representação
reversível (`bytes.fromhex(registro["data"])`). ASCII é apenas visualização.

Duas threads leem simultaneamente. Cada leitura é registrada sob um lock,
com flush dos arquivos, antes da escrita no destino. Escritas parciais são
completadas; uma exceção interrompe a sessão, sem tentar reenviar bytes cuja
entrega ficou incerta. Os contadores representam blocos registrados e seus bytes,
**não comprovam entrega ao dispositivo**. Uma falha de log interrompe a ponte.

Um bloco da API serial **não representa necessariamente um frame do protocolo**.
Leituras podem dividir um frame ou incluir vários frames. Não há agrupamento
posterior, interpretação ou reconstrução. As linhas dos dois sentidos podem ser
intercaladas, mas cada registro é escrito inteiro.


## Exemplos completos

As flags de fluxo são independentes; configure apenas o que o dispositivo e o
driver suportam. Paridade: N = nenhuma, E = par, O = ímpar, M = mark, S = space.

```powershell
python -m tr_serial_proxy --physical-port COM6 --virtual-port COM21 --baud 115200 --bytesize 8 --parity N --stopbits 1 --timeout 0.01 --write-timeout 1 --chunk-size 4096 --log-dir logs --log-prefix serial --raw-log --quiet
tr-serial-proxy --physical-port COM8 --virtual-port COM21 --baud 19200 --parity E --ascii
tr-serial-proxy --list-ports
```

Execute o proxy antes de iniciar o tráfego do software. Ctrl+C encerra a sessão.
Códigos de saída: 0 para saída normal/Ctrl+C, 1 para falhas e 2 para argumentos inválidos.
Todos os dados de log nesta documentação são fictícios.
