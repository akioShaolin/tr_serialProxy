# Arquitetura

```text
Software ↔ COM20 ↔ COM21 ↔ tr_serialProxy ↔ COM6 ↔ dispositivo
           par virtual                    física
```

A COM física representa o adaptador/dispositivo real. O driver externo conecta
as duas COM virtuais: bytes escritos em uma ponta são recebidos na outra.
O software abre COM20; o proxy abre COM21 e COM6.

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
