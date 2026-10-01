# Limitações

- As duas portas usam os mesmos parâmetros, em objetos de configuração separados
  para permitir evolução futura. Mudanças feitas pelo software em COM20 não são
  detectadas nem propagadas automaticamente à COM física.
- Transparência é dos bytes lidos, não dos tempos do sinal elétrico. Drivers,
  buffers, disco e terminal acrescentam latência. `--quiet` reduz custo do terminal.
  Carga superior à capacidade de encaminhamento pode causar perda nos buffers.
- RTS, DTR, CTS, DSR, BREAK e outros eventos de controle não são espelhados.
  A abertura da porta pode alterar RTS/DTR conforme o driver. XON/XOFF pode consumir
  bytes de controle no driver; mantenha desativado para transportar todos os valores
  binários sem esse tratamento. O par virtual deve ter configuração compatível.
- RS485 depende do controle de direção do adaptador/driver; esta versão não faz
  comutação manual de RTS nem configura modo RS485 especial.
- Ctrl+C interrompe novas leituras e permite concluir a escrita do bloco atual
  dentro dos timeouts configurados. Dados ainda nos buffers podem não ser capturados
  ou entregues. Não há garantia de drenagem física dos buffers de saída.
- Desconexão, porta ocupada/inexistente, timeout de escrita e falha de disco são
  reportados e encerram a sessão. Não há reconexão automática.
- Encerramento forçado, queda de energia ou desconexão podem perder dados. Flush
  não equivale a gravação durável com `fsync`; os dois arquivos não são uma transação.
- Logs podem conter números de série, configurações, credenciais, comandos e
  informações proprietárias. São locais e nunca publicados automaticamente.
  `logs/` está no `.gitignore`; proteja também diretórios alternativos.
- Não há filtros, injeção, replay, GUI, reconhecimento de baud, instalação de
  drivers ou interpretação Modbus/CAN/JBD nesta versão.


- Somente dispositivos que aparecem como COM são suportados. Não captura USB bruto
  nem dispositivos HID diretamente e não interpreta protocolos.
- Parâmetros seriais permanecem fixos durante a execução nesta versão.
- Não usar inicialmente para firmware/bootloader crítico sem validação prévia.
