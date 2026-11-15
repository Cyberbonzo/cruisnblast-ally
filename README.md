# Cruis'n Blast Ally — 0.1.0

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
| A na pausa | Retomar |

Configuração padrão: tela cheia 1920×1080, jogo livre e unidades métricas. O perfil usa SDL no lugar da placa de entradas do gabinete. A pausa mantém o loop de jogo parado, suspende a simulação PhysX e o grupo principal de áudio, e ajusta os relógios internos ao retomar.

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
