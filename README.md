# Birthday Video Maker

Crie vídeos personalizados de aniversário automaticamente usando After Effects, Python e FFmpeg.

## Funcionalidades
- Geração automática de vídeo de aniversário a partir de um template do After Effects (.aep)
- Substituição automática de avatar e informações do aniversariante
- Conversão automática do vídeo final para MP4 usando FFmpeg
- Barra de progresso animada para renderização e conversão
- Interface simples via terminal

## Pré-requisitos
- **Python 3.8+**
- **After Effects** instalado (com o utilitário `aerender.exe`)
- **FFmpeg** instalado e disponível no PATH
- **Pillow** e **tqdm** instalados (`pip install pillow tqdm`)

## Como usar
1. Clone este repositório e coloque seu template `.aep` na raiz do projeto.
2. Execute o script:
   ```bash
   python app.py
   ```
3. Siga as instruções no terminal:
   - Informe o nome e função do aniversariante
   - Selecione a imagem do avatar
4. O vídeo será gerado automaticamente na pasta `final/`.

## Estrutura do Projeto
```
Birthday Video Maker/
├── app.py
├── BirthdayVideoTemplate.aep
├── dados/
│   ├── info.json
│   └── avatar.jpg
├── final/
│   ├── BirthdayVideoFinal.mov
│   └── BirthdayVideoFinal.mp4
├── imagens/
│   └── ...
├── Assets/
│   └── ...
```

## Observações
- O caminho do `aerender.exe` deve estar correto no `app.py`.
- O template `.aep` deve conter uma composição chamada `PRINCIPAL`.
- O script remove arquivos antigos antes de gerar novos vídeos.

## Licença
Este projeto é livre para uso pessoal e educacional.
