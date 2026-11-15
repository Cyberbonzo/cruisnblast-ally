# Validação — 0.1.0

Data: 15/11/2026. Ambiente: ROG Ally X, Bazzite x86_64, Mesa 26.2.6, runtime do jogo i386.

- O executável original foi preservado e verificado por SHA-256.
- Foram reconstruídas 636 entradas de importação, a entrada do processo e os dados de ligação dinâmica. A memória BSS capturada no arquivo foi limpa para a inicialização nativa.
- Threads de leitura passaram a herdar a prioridade do usuário, resolvendo `EPERM` sem elevar privilégios.
- Fontes, shaders básicos e apresentação passaram a carregar. A normalização das saídas GLSL removeu a incompatibilidade observada entre saídas nomeadas e `gl_FragData` no Mesa.
- Corridas de Londres e Madagascar chegaram à jogabilidade. Uma captura de teste registrou 233 km/h após entrada de acelerador.
- A pausa exibiu sua interface em tela cheia. O relógio da simulação permaneceu em 37767 durante dois segundos de pausa e chegou a 38518 após a retomada e o intervalo de coleta, sem incorporar o tempo da pausa.
- O usuário confirmou funcionamento, incluindo a configuração de controles e pausa.

Limite da validação: a versão não representa uma campanha completa de testes de todas as pistas. O teste de entrada automatizado usa o mesmo callback dos controles, mas não substitui a confirmação dos botões físicos feita pelo usuário.

Não foram instalados pacotes de sistema. O runtime privado contém apenas as bibliotecas necessárias para este jogo. As regras de dispositivos escritas pelo software do gabinete ficam em um caminho privado dentro do sandbox; o `/etc/udev` do sistema permanece intacto.
