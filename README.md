# Cruis'n Blast Ally — 0.1.3

Adaptação comunitária para executar uma cópia própria do arcade Linux 1.25 no ROG Ally com Bazzite. Inclui recuperação da inicialização ELF, compatibilidade gráfica com Mesa/AMD, controles do portátil e uma tela de pausa. Executa nativamente em Linux, sem Proton.

**Traga sua própria cópia do jogo.** Este repositório contém somente código próprio e documentação. Não inclui jogo, ROM, executáveis originais, bibliotecas comerciais, chaves, saves, imagens ou artes oficiais. Não é um produto oficial nem possui vínculo com os titulares do jogo. A licença MIT abrange apenas o código próprio aqui publicado.

## Controles

| Controle | Função |
|---|---|
| Analógico esquerdo | Direção, com zona morta de 12% |
| RT | Acelerador analógico |
| LT | Freio |
| A | Iniciar / confirmar; também aciona Blast durante a corrida |
| X | Blast |
| B | Câmera |
| Y | Música |
| Direcional | Navegação |
| Start | Pausar / retomar |
| Direcional na pausa | Selecionar opção |
| A na pausa | Confirmar / alternar cheat |
| B na pausa | Retomar |

Configuração padrão: tela cheia 1920×1080, jogo livre e unidades métricas. O perfil usa SDL no lugar da placa de entradas do gabinete. A pausa mantém o loop de jogo parado, suspende a simulação PhysX e o grupo principal de áudio, e ajusta os relógios internos ao retomar.

## Boost infinito

Pressione **Start/Menu**, selecione **CHEATS INFINITE BLAST** com o direcional e pressione **A** para alternar **ON/OFF**. **B** ou **Start** retoma. O menu de pausa é inglês.

O padrão desta revisão é ON quando não existe preferência anterior. A escolha fica no arquivo privado `game/g5/race/pmuser/ally-infinite-blast.cfg` e é relida ao iniciar. Durante a corrida, pressione **X** para usar Blast. Com ON, o helper repõe o estoque do carro local para três cargas quando fica abaixo disso. A duração do efeito, a física e a ativação continuam nativas. OFF interrompe a reposição; cargas já fornecidas permanecem disponíveis para consumo normal. Não é boost permanentemente ativo e não elimina os intervalos nativos entre ativações.

A revisão suportada é conferida pela assinatura da instrução que consome Blast antes de qualquer reposição. A preferência é gravada por arquivo temporário e renomeação; falhas de gravação aparecem na pausa. Não são alterados executáveis em disco nem arquivos de progresso pelo cheat.

## Instalação

São usados Python 3, GCC com geração i386, Bubblewrap e as bibliotecas de 32 bits já presentes no Bazzite/Steam. O instalador não instala pacotes no sistema. Mantém o jogo e suas dependências em uma pasta privada fora deste checkout.

O runtime PhysX 2.8.1 precisa ser fornecido separadamente pelo usuário, obtido da [distribuição oficial da NVIDIA](https://developer.download.nvidia.com/PhysX/2.8.1/PhysX_2.8.1_SDK_CoreLinux_deb.tar.gz). As bibliotecas FMOD são importadas da própria cópia do jogo; SDL/GLU/GLUT são reutilizadas do Steam Linux Runtime instalado.

```bash
python3 tools/instalar.py --zip /caminho/jogo.zip --sdk /caminho/PhysX_2.8.1_SDK_CoreLinux_deb.tar.gz --dest "$HOME/Games/CruisnBlast"
```

Adicione `jogar.sh` da pasta de destino à biblioteca Steam como jogo não Steam. Deixe o modo de compatibilidade Proton desativado e use o layout padrão de gamepad. Encerre outros jogos antes de testar.

O executável original deve ter SHA-256 `cdb5f6b6797ea4ca0c3f76714cf65fa2c8b6602164c5babae0a729843ef8c3c9`. Outras revisões não são suportadas. O arquivo original é preservado e a adaptação gera `cruisn-ally.elf` somente no computador do usuário.

## Estado da versão

Validado no ROG Ally X com Bazzite: inicialização nativa, menus, corrida, aceleração, modo métrico, tela cheia e pausa/retomada. O usuário confirmou funcionamento e controles. A verificação do relógio confirmou que o tempo de pausa não avança o cronômetro da corrida. Nem todas as pistas e combinações de configuração foram testadas.

Veja [VALIDACAO.md](docs/VALIDACAO.md) para os resultados e [PUBLICACAO.md](docs/PUBLICACAO.md) para a separação entre arquivos privados e públicos.

## Dificuldade — 0.1.2

O perfil aplica dificuldade **0** ao iniciar e salva pela rotina nativa do jogo. A escala suportada é de 0 a 10. Para mudar o padrão deste perfil, ajuste a chamada `setting("game","difficulty",0)` no código de compatibilidade e recompile.

## Progresso automático — 0.1.3

O perfil local é carregado automaticamente antes da seleção de carros, sem digitar PIN. Carro/cor selecionados, melhorias, estatísticas e melhores tempos registrados pelo perfil nativo são preservados. A tabela de recordes do gabinete continua sendo gravada pelo próprio jogo.

O helper salva mudanças a cada cinco segundos, ao pausar, nos pontos de gravação nativos e antes de encerrar o perfil. O desligamento normal também solicita uma gravação. Uma cópia completa do perfil usa checksum, arquivo temporário, fsync e renomeação atômica. O launcher mantém as oito últimas cópias diferentes dos saves e restaura automaticamente um perfil/tabela ausente ou estruturalmente danificado. Os backups têm SHA-256 por arquivo; arquivos atuais válidos não são substituídos por versões antigas. Uma segunda instância é bloqueada para evitar gravações concorrentes.

Arquivos privados: `game/g5/race/pmuser/ally-profile.bin`, `player_tbl`, `aud/save/highscores.*.xml` e `saves/backups/`. Preserve-os ao trocar de instalação. O perfil usa uma identidade local fixa; não é login online nem credencial. O modo de demonstração não recebe essa identidade e não substitui seu progresso. Falha na gravação do perfil aparece como **PROFILE SAVE FAILED** na pausa.

São mantidos os dados que esta versão arcade realmente registra; não é um save state e uma corrida interrompida não recomeça do mesmo ponto. Desbloqueios e recordes só existem depois de concedidos pelo jogo. Uma interrupção forçada pode perder mudanças posteriores à última gravação. Não é possível recuperar sessões antigas que nunca foram salvas. Este recurso não adiciona a campanha da edição para consoles.
