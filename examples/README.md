# Teste manual com dados sintéticos

Instale o pacote conforme o [README](../README.md) e execute a partir da raiz.

Para teste manual com dois pares virtuais, peça ao TI para criar
`COM20 ↔ COM21` e `COM30 ↔ COM31`. Abra três terminais, nesta ordem:

```powershell
python scripts/serial_test_peer.py --port COM31 --baud 9600
python -m tr_serial_proxy --physical-port COM30 --virtual-port COM21 --baud 9600 --raw-log
python scripts/serial_test_peer.py --port COM20 --baud 9600 --send-test
```

O último comando envia todos os 256 valores de byte e verifica o eco exato.
Neste teste COM30 faz o papel da porta física. Use 8N1 sem controle de fluxo;
não execute o peer de teste em equipamentos reais, pois ele envia dados de teste.
O teste virtual não substitui validação no adaptador e software de destino.

Veja também os [exemplos de configuração](../docs/examples.md). Não inclua capturas reais neste diretório.
