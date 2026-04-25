# Manual de Deploy e Manutenção em Produção (Linux)
Este documento contém o passo a passo necessário para atualizar o código, parar e reiniciar a aplicação do Sistema de Inspeção Técnica na máquina virtual Linux (onde roda em background usando `nohup` na porta 5002).

## 1. Derrubando (Parando) o Sistema Atual
Como o sistema roda em segundo plano na porta **5002**, precisamos encontrar o número do processo (PID) dele para interrompê-lo.

Execute o comando abaixo para listar quem está usando a porta 5002:
```bash
lsof -i :5002
```
*(Se o comando `lsof` não funcionar no seu sistema, você pode procurar pelo nome do processo executando: `ps aux | grep python`)*

A saída será algo parecido com isso:
```text
COMMAND   PID USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
python3 12345 root    3u  IPv4  12345      0t0  TCP *:5002 (LISTEN)
```
Pegue o número listado na coluna **PID** (no exemplo acima, `12345`) e encerre o processo com o comando:
```bash
kill -9 12345
```
Pronto, o sistema anterior foi parado e a porta está livre.

---

## 2. Atualizando o Código na VM
Agora você precisa levar as alterações do código atual para dentro da VM.
Se você estiver utilizando **Git**:
```bash
cd /caminho/do/seu/sistema
git pull origin main
```
*Se você atualiza os arquivos via cópia por rede ou FTP, certifique-se de substituir as pastas `/app/templates`, `/app/static` e os arquivos principais como dependências e o `app.py`.*

---

## 3. Subindo o Sistema Novamente (Produção)
Acesse a raiz do projeto (onde está o arquivo principal da aplicação) e ative o seu ambiente virtual (se você utilizar um):
```bash
cd /caminho/do/seu/sistema
source venv/bin/activate   # Adapte para o nome correto da pasta do ambiente virtual
```

Em seguida, inicie o sistema de forma desanexada (para que continue rodando após você fechar o terminal) usando o comando `nohup`:
```bash
nohup python run.py > nohup.out 2>&1 &
```
*(Observação: Se o servidor rodar com uma versão específica, troque por `python3 run.py` ou comando correspondente do seu webserver, como gunicorn).*

---

## 4. Manutenção e Leitura de Logs
Depois que você subir o sistema, toda a saída do console da aplicação (informações de acesso, envios de alerta de e-mail e erros gerais) será gravada no arquivo `nohup.out`.

Para acompanhar o sistema "ao vivo" funcionando (lendo os logs em tempo real):
```bash
tail -f nohup.out
```
*Dica:* Para sair da visualização ao vivo, pressione **`CTRL + C`**. Fazer isso não parará o sistema.

---

## Bônus: Script Rápido de Reinicialização (`restart.sh`)
Para facilitar as atualizações e não precisar digitar todos os comandos informados acima frequentemente, você pode criar um arquivo chamado `restart.sh` na pasta raiz do seu projeto na VM.

Crie o arquivo:
```bash
nano restart.sh
```

Cole o seguinte conteúdo dentro:
```bash
#!/bin/bash
echo "Derrubando sistema atual na porta 5002..."
# Tenta matar o processo que está usando a porta 5002
kill -9 $(lsof -t -i:5002) 2>/dev/null

echo "Subindo novo sistema..."
# Execute de acordo com sua versão do Python:
nohup python3 run.py > nohup.out 2>&1 &

echo "Sistema reiniciado! Verificando os logs mais recentes:"
sleep 2
tail -n 10 nohup.out
```

Salve o arquivo (`CTRL + O` e `Enter`) e saia (`CTRL + X`).
Não esqueça de dar permissão de execução ao script:
```bash
chmod +x restart.sh
```

De agora em diante, sempre que fizer o upload do código novo, basta executar:
```bash
./restart.sh
```
E ele matará a versão antiga e colocará a versão mais nova no ar listando os últimos logs!
