# Arquivos públicos e privados

O Git existe apenas nesta pasta de código público. O jogo original, a cópia adaptada, bibliotecas comerciais, saves, logs e artes ficam fora do repositório.

`PUBLIC_FILES.txt` é a lista explícita dos arquivos autorizados para a publicação. `tools/publicar_pacote.py` verifica os arquivos rastreados, texto UTF-8, ausência de binários e sinais de credenciais antes de produzir o pacote de código.

As transformações são aplicadas localmente à cópia fornecida pelo usuário. Não há distribuição de executáveis ou shaders modificados. Os scripts de transformação e a camada de controles/pausa são código próprio.
