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

## Revisão 0.1.1 — 16/11/2026

- Boost infinito ON/OFF na pausa inglesa, com escolha persistente em arquivo privado.
- Teste pelo callback dos controles: OFF consumiu três cargas e terminou com zero, sem novas ativações; ON executou cinco ativações e manteve três cargas disponíveis.
- O relógio permaneceu parado por dois segundos na pausa. O submenu aceitou direcional, A para alternar e B para retomar.
- Assinatura do consumo de Blast validada na revisão 1.25. Nenhuma biblioteca adicional instalada.
- Reinicialização completa leu corretamente a preferência OFF salva; a opção foi então recolocada em ON pelo menu e conferida no arquivo. O jogo foi deixado com boost infinito ativado.

## Revisão 0.1.2 — 16/11/2026

Dificuldade configurada em 0 pela API nativa de ajustes durante a inicialização. As três cópias persistidas de difficulty foram lidas e apresentaram val = 0 após iniciar no Ally.

## Revisão 0.1.3 — 16/11/2026

- Perfil automático carregado antes da seleção de carros, sem entrada de PIN. Os seis pontos de integração são validados antes da instalação em memória.
- Sessão anterior de convidado preservada localmente e migrada sem apagar dados preexistentes. A melhoria que estava em memória foi mantida.
- Corrida real em Londres registrada com tempo de 1:39,58. O perfil, a tabela nativa e a cópia atômica concordaram sobre carro, melhorias e tempo.
- Após fechar completamente e reabrir pelo Steam, o teste comparou carro, todas as 23 entradas de melhorias, os cinco melhores tempos e todos os bytes de estatísticas: iguais ao save anterior, sem digitar PIN.
- Pausa permaneceu funcional, com relógio congelado por dois segundos; boost infinito ON e dificuldade 0 preservados.
- Testes em pasta temporária verificaram restauração de perfil corrompido/tabela truncada, rejeição de checksum inválido, preservação de arquivo atual válido e rotação de oito backups. Dois testes públicos usam somente dados sintéticos; nenhum save é distribuído.
- GCC i386 compilou a integração sem avisos. Nenhum pacote adicional instalado.

Limites: a validação não percorreu todos os desbloqueios e pistas. O mecanismo preserva o perfil completo nativo, mas não cria conteúdo de outras edições nem salva a posição de uma corrida em andamento. Records de gabinete existentes foram mantidos; o novo tempo também apareceu na tabela de Londres.
