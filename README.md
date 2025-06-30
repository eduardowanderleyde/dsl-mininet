# Web Cenários Mininet-WiFi

## Como rodar com Docker

1. Build da imagem:
   ```bash
   docker build -t web-cenarios .
   ```
2. Execute o container:
   ```bash
   docker run -it --rm -p 5000:5000 -v $(pwd)/cenarios:/app/cenarios web-cenarios
   ```

Acesse em http://localhost:5000

## Funcionalidades
- Criar, visualizar e salvar cenários (JSON)
- Executar cenários (chama script Python)
- Download dos logs gerados

---

**Obs:** Os arquivos de cenário ficam na pasta `cenarios/`. 