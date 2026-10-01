# Arquitetura

```text
Software ↔ COM13 ↔ COM14 ↔ tr_serialProxy ↔ COM6 ↔ dispositivo
           par virtual                    física
```

A COM física representa o adaptador/dispositivo real. O driver externo conecta
as duas COM virtuais: bytes escritos em uma ponta são recebidos na outra.
O software abre COM13; o proxy abre COM14 e COM6.

O proxy participa do caminho dos dados e precisa estar em execução para que a
ponte funcione. Um sniffer observa tráfego de outro caminho; este programa não
captura USB bruto nem pacotes de rede.

- **TX:** software → COM virtual → proxy → COM física → dispositivo.
- **RX:** dispositivo → COM física → proxy → COM virtual → software.

Duas threads permitem leituras simultâneas, uma por direção. Cada thread lê um
bloco binário, registra esse bloco e escreve os mesmos bytes no destino. Escritas
curtas são completadas. Não há reconstrução de mensagens nem interpretação de
protocolo; os limites de `read()` não representam necessariamente frames.

O logger usa um lock para preservar registros inteiros nos arquivos e nos
contadores. O flush ocorre antes do encaminhamento. Disco lento, saída de terminal,
buffers e agendamento das threads acrescentam latência; não existe garantia de
tempo real. `--quiet` reduz o custo do terminal, mas não elimina o custo de logging.

Ctrl+C ou uma falha sinaliza parada compartilhada. Leituras são canceladas quando
o driver permite; escritas correntes usam o timeout configurado. Depois de aguardar
as threads, o programa fecha os logs, fecha as portas e imprime os contadores.
Não há reconexão nem reenvio após erro de entrega incerta. Bytes ainda nos buffers
podem ser perdidos. Veja [limitações](limitations.md).

## Organização do código

| Módulo | Responsabilidade |
| --- | --- |
| `cli.py` | Argumentos, validação e listagem de portas |
| `bridge.py` | Encaminhamento, threads e ciclo de vida da captura |
| `serial_config.py` | Configuração imutável de cada porta e conversões |
| `logger.py` | Logs textuais/JSONL, timestamps e contadores |
| `utils.py` | Validadores simples e formatação hexadecimal |
| `__main__.py` | Execução via `python -m tr_serial_proxy` |

Os dois objetos de configuração inicialmente têm os mesmos valores; ficam
separados para permitir configurações independentes no futuro. Não há detecção
das configurações impostas pelo software na outra ponta virtual.

## Protótipo inicial: ligação física intermediária

```text
Software → COM6 ↔ USB-RS485 A ↔ cabo RS485 ↔ USB-RS485 B/COM8
                                                        ↕
                                                  tr_serialProxy
                                                        ↕
                                              COM7/conversor → dispositivo
```

Todas as conexões transportam dados nos dois sentidos. O software abriu COM6;
o proxy abriu COM8 no lado do software e COM7 no lado do dispositivo. Foram
usados **três conversores no total**: dois substituíam o par virtual e o terceiro
atendia o dispositivo. O argumento `--virtual-port COM8` aceitou uma porta física:
seu nome indica o papel no fluxo, não uma exigência de driver virtual.
Esse arranjo provou o recebimento, registro e retransmissão bidirecional.

## Arquitetura atual: com0com

O teste posterior usou COM13 ↔ COM14 via com0com, com o software na COM13 e o
proxy na COM14 e na COM física do dispositivo. A comunicação continuou operacional
com TX e RX registrados. O par virtual elimina os dois conversores usados apenas
como ponte no protótipo; permanece o adaptador do dispositivo.
Veja a [validação em etapas](validation.md).

## Fragmentação normal de leitura

**Uma porta serial representa um fluxo de bytes. Os limites retornados por
`read()` não correspondem necessariamente aos limites das mensagens do protocolo.**

No teste virtual, a captura mostrou leituras RX sucessivas de 1, 1, 1 e 14 bytes.
Isso, por si só, não indica frames separados, inserção de dados pelo com0com,
quebras de linha no protocolo ou escritas separadas feitas pelo software.
É comportamento normal de buffering e leitura. O proxy lê o que está disponível,
limitado por `--chunk-size`, e espera por um byte quando o buffer está vazio.

O logger continua registrando cada bloco recebido, sem juntar blocos,
reconstruir frames, interpretar protocolo ou modificar bytes. Os contadores
são de blocos, não de mensagens. Nenhum payload real é reproduzido aqui.
