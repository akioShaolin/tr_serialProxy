# tr_serialProxy

**Transparent Serial Proxy Logger for Windows**

Ponte transparente entre uma COM virtual e uma COM física, com registro de todo
o tráfego bidirecional recebido, sem interpretar ou modificar os bytes.
Versão inicial de desenvolvimento: **0.1.0**.

## Motivação

O projeto surgiu da necessidade de observar bytes trafegando por dispositivos
seriais que aparecem como COM, sem precisar de uma ferramenta completa de análise
de rede ou USB. Não é um sniffer USB: funciona como proxy serial.

```text
byte recebido → registrar → encaminhar exatamente o mesmo byte
```

## Arquitetura

```text
Software proprietário
        ↕
   COM virtual A (COM20)
        ↕
   COM virtual B (COM21)
        ↕
  tr_serialProxy
        ↕
    COM física (COM6)
        ↕
    dispositivo
```

**TX = software → dispositivo. RX = dispositivo → software.**
Duas threads encaminham bytes simultaneamente. Cada bloco é registrado antes
da escrita no destino. Leia a [arquitetura detalhada](docs/architecture.md).

## Requisitos

- Windows e Python 3.10 ou superior.
- pySerial, única dependência de execução.
- Dispositivo que apareça como COM e par de COMs virtuais criado externamente.
- pytest para desenvolvimento/testes; setuptools para empacotamento.

## Instalação

Na raiz do projeto, usando PowerShell:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install .
.\.venv\Scripts\python.exe -m tr_serial_proxy --help
```

Para desenvolver, use `pip install -e ".[test]"` no ambiente escolhido.
`requirements.txt` contém a dependência de execução; instalar apenas esse arquivo
não instala o pacote localizado em `src/` nem o comando `tr-serial-proxy`.

Os exemplos seguintes pressupõem que o Python do ambiente instalado está ativo.
Sem ativá-lo, use `.\.venv\Scripts\python.exe` ou
`.\.venv\Scripts\tr-serial-proxy.exe` explicitamente.

## Configuração da COM virtual

Um driver externo aprovado deve criar um par como `COM20 ↔ COM21`.
O software abre **COM20**; o proxy abre **COM21** e a porta física **COM6**.
A instalação/configuração do driver pode exigir administrador; o uso normal do
proxy não deve exigir elevação se as portas estiverem disponíveis e acessíveis.
O projeto não instala drivers. Veja [configuração da COM virtual](docs/virtual-com-setup.md).

## Exemplos de uso

```powershell
python -m tr_serial_proxy --list-ports
tr-serial-proxy --physical-port COM6 --virtual-port COM21 --baud 9600 --bytesize 8 --parity N --stopbits 1
python -m tr_serial_proxy --physical-port COM6 --virtual-port COM21 --baud 115200 --raw-log --quiet
```

Execute o proxy antes do tráfego do software. Ctrl+C encerra a sessão e mostra
duração, blocos e bytes por direção. O arquivo `serial_proxy.py` permanece como
launcher de compatibilidade, após a instalação do pacote.

Consulte [todos os argumentos](docs/usage.md) e os
[exemplos USB-TTL e RS485](docs/examples.md).

## Formato dos logs

Cada execução cria `logs/serial-AAAA-MM-DD_HH-MM-SS-microssegundos.log`.
`--raw-log` cria também JSONL reversível. **Os dados abaixo são fictícios.**

```text
[2026-09-30T14:35:22.123456-03:00] [+0.381224] TX  4 bytes
00 41 7F FF
```

```json
{"time":"2026-09-30T14:35:22.123456-03:00","elapsed":0.381224,"direction":"TX","length":4,"data":"00417fff"}
```

O horário inclui fuso e microssegundos; a precisão real depende do sistema.
O tempo decorrido usa `time.perf_counter()`. Os bytes são representados em HEX,
sem decodificação Unicode. `--ascii` adiciona apenas visualização.
Contadores medem blocos registrados, não entrega confirmada.

## Limitações

Somente dispositivos COM são suportados; não há captura USB bruta, HID direto
ou interpretação de protocolo. Blocos de `read()` não equivalem necessariamente
a frames. Parâmetros ficam fixos durante a execução e mudanças feitas pelo
software na COM virtual não são propagadas automaticamente.

Há latência adicional e possível perda em sobrecarga, desconexão ou interrupção.
Sinais de controle não são espelhados. Não use inicialmente para firmware ou
bootloader crítico sem validação. Consulte [todas as limitações](docs/limitations.md).

## Segurança e privacidade

**Captured data may be sensitive.**

Logs podem conter números de série, comandos proprietários, parâmetros,
credenciais, tokens e informações internas. Nunca adicione logs reais ao
repositório sem revisão. Os logs são locais e nunca publicados automaticamente.
O `.gitignore` exclui capturas `.log`, `.jsonl` e `.bin`, além do conteúdo de
`logs/`, preservando apenas `.gitkeep`. Revise também capturas com outras extensões.

## Testes

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[test]"
.\.venv\Scripts\python.exe -m pytest -v
```

Os testes usam portas simuladas e não exigem hardware nem drivers virtuais.
O workflow [tests.yml](.github/workflows/tests.yml) está configurado para Windows
com Python 3.10 e 3.13; sua execução no GitHub depende da publicação do repositório.
Há também um [teste manual com dois pares virtuais](examples/README.md) usando
`scripts/serial_test_peer.py` e dados sintéticos.

## Roadmap

- V0.1: bridge bidirecional + log (implementado; validar no ambiente de destino).
- V0.2: filtros de visualização.
- V0.3: estatísticas e análise de timing.
- Futuro: replay opcional.
- Futuro: decodificadores de protocolo como plugins.

Os itens futuros não fazem parte desta implementação.

## Licença

Licença ainda não definida. Nenhum arquivo `LICENSE` foi adicionado; a escolha
deve ocorrer antes da distribuição pública sob uma licença específica.
