# Webhook-Uploader

Aplicativo desktop em Python com interface em **PySide6** para monitorar uma pasta e enviar arquivos automaticamente para um **webhook do Discord**.

## Visão geral

O **Webhook-Uploader** foi criado para simplificar o envio de arquivos para o Discord de forma automática, com uma interface moderna, leve e prática para uso no dia a dia.

O aplicativo monitora uma pasta definida pelo usuário, aguarda o tempo configurado para cada arquivo ficar pronto e então realiza o envio para o webhook configurado. Também é possível pausar o monitoramento, enviar manualmente, testar o webhook e personalizar a mensagem da postagem.

---

## Funcionalidades

- Monitoramento automático de pasta
- Envio manual com botão **Enviar agora**
- Suporte a postagem com **embed** ou **mensagem normal**
- Escolha de **cor do embed**
- Editor de texto para personalizar o post
- Teste de webhook direto pela interface
- Variáveis automáticas no texto:
  - `{filename}`
  - `{creation_str}`
  - `{upload_str}`
- Ícone na bandeja do sistema com estados visuais:
  - rodando
  - pausado
  - enviando
- Opção para iniciar com o Windows
- Opção para excluir o arquivo após envio
- Limpeza do log de arquivos já enviados
- Proteção contra reenvio duplicado

---

## Requisitos

- **Windows**
- **Python 3.10+** recomendado

### Dependências

- `PySide6`
- `requests`
- `send2trash`

## Instalação

```bash
pip install PySide6 requests send2trash
```

---

## Como usar

### 1. Configure o webhook

Na primeira execução, informe a URL completa do webhook do Discord.

### 2. Escolha a pasta monitorada

Selecione a pasta que será observada pelo aplicativo. Os arquivos dentro dela poderão ser enviados manualmente ou automaticamente.

### 3. Personalize o post

Na área **Personalizar post**, você pode editar o texto que acompanhará o arquivo.

Exemplo:

```txt
🆕
📄 `{filename}`
📅 `{creation_str}`
🆙 Upload: {upload_str}
___
```

As variáveis são substituídas automaticamente no momento do envio.

### 4. Escolha o modo de envio

Você pode ativar ou desativar o uso de **embed**.

Quando o embed estiver ativado:
- o texto será enviado dentro da descrição do embed
- a cor do embed pode ser personalizada
- arquivos de imagem compatíveis podem ser exibidos junto ao envio

### 5. Inicie o monitoramento

Com webhook e pasta configurados, o aplicativo pode operar automaticamente em segundo plano.

---

## Fluxo de envio automático

O aplicativo verifica periodicamente os arquivos da pasta monitorada.

Antes de enviar, ele pode:
- aguardar um tempo mínimo para garantir que o arquivo terminou de ser gravado
- verificar se o arquivo não está em uso
- evitar reenvios duplicados
- registrar o histórico de arquivos enviados

---

## Estrutura de arquivos

Os arquivos de configuração e log são salvos localmente em:

```txt
%LOCALAPPDATA%\Webhook-Uploader\
```

Arquivos principais:
- `cfg.json` → configurações do aplicativo
- `log.json` → histórico de arquivos enviados

---

## Interface

O aplicativo utiliza **PySide6** com interface personalizada, incluindo:

- janela principal sem moldura padrão do sistema
- página inicial
- página de configurações
- página de personalização do post
- barra de rolagem estilizada
- funcionamento em bandeja do sistema

---

## Configurações disponíveis

- Iniciar com Windows
- Excluir após enviar
- Editar texto do post
- Escolher cor do embed
- Ativar ou desativar embed
- Limpar log
- Abrir pasta de configurações

---

## Observações

- O limite de upload considerado pelo app é de **25 MB**
- O aplicativo foi pensado para uso local no Windows
- O envio depende de um webhook válido do Discord
- O botão de esconder minimiza o app para a bandeja, sem encerrar o processo

---

## Execução

Execute normalmente com:

```bash
python nome_do_arquivo.py
```

Exemplo:

```bash
python v2.9.0.py
```

---

## Tecnologias usadas

- Python
- PySide6
- requests
- send2trash

---

## Licença

```md
MIT License
```