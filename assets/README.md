# Assets - Ícones e Recursos

## Ícones Disponíveis

Esta pasta contém os ícones do aplicativo WhatsApp Rebooter:

- **icon.ico** - Ícone principal usado no executável e na janela do aplicativo
- **icon_256.png** - Versão PNG 256x256 pixels
- **icon_512.png** - Versão PNG 512x512 pixels  
- **whatsapprebooter.png** - Versão PNG alternativa

## Uso

### No Aplicativo
O ícone é carregado automaticamente quando o aplicativo inicia. O código procura o arquivo `icon.ico` nesta pasta.

### No Executável
Os scripts de build (`build.bat` e `build.sh`) automaticamente incluem o ícone no executável quando você compila o aplicativo.

## Verificação

Para verificar se o ícone está sendo usado:

1. **Durante desenvolvimento**: O ícone aparece na barra de título da janela
2. **No executável**: O ícone aparece:
   - No arquivo `.exe` gerado
   - Na barra de tarefas quando o app está rodando
   - No gerenciador de tarefas

## Atualização

Se você quiser atualizar o ícone:

1. Substitua o arquivo `icon.ico` nesta pasta
2. O aplicativo carregará automaticamente na próxima execução
3. Para o executável, recompile usando `build.bat` ou `build.sh`

