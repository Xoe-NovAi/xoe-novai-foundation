---
title: Fastapi Cli
service: FastAPI
source_urls: ["/tmp/tmp2aqkafzm/repo/docs/pt/docs/fastapi-cli.md"]
scraped_at: 2026-02-17T00:28:19.489079
content_hash: 64253a80939dcc26f5d75acc033152ed604c4b30ec77b38c1d1cac1bde0d3ddc
size_kb: 5.04
---

# FastAPI CLI { #fastapi-cli }

**FastAPI CLI** é um programa de linha de comando que você pode usar para servir sua aplicação FastAPI, gerenciar seu projeto FastAPI e muito mais.

Quando você instala o FastAPI (por exemplo, com `pip install "fastapi[standard]"`), isso inclui um pacote chamado `fastapi-cli`; esse pacote disponibiliza o comando `fastapi` no terminal.

Para executar sua aplicação FastAPI durante o desenvolvimento, você pode usar o comando `fastapi dev`:

<div class="termy">

```console
$ <font color="#4E9A06">fastapi</font> dev <u style="text-decoration-style:solid">main.py</u>

  <span style="background-color:#009485"><font color="#D3D7CF"> FastAPI </font></span>  Starting development server 🚀

             Searching for package file structure from directories with
             <font color="#3465A4">__init__.py</font> files
             Importing from <font color="#75507B">/home/user/code/</font><font color="#AD7FA8">awesomeapp</font>

   <span style="background-color:#007166"><font color="#D3D7CF"> module </font></span>  🐍 main.py

     <span style="background-color:#007166"><font color="#D3D7CF"> code </font></span>  Importing the FastAPI app object from the module with the
             following code:

             <u style="text-decoration-style:solid">from </u><u style="text-decoration-style:solid"><b>main</b></u><u style="text-decoration-style:solid"> import </u><u style="text-decoration-style:solid"><b>app</b></u>

      <span style="background-color:#007166"><font color="#D3D7CF"> app </font></span>  Using import string: <font color="#3465A4">main:app</font>

   <span style="background-color:#007166"><font color="#D3D7CF"> server </font></span>  Server started at <font color="#729FCF"><u style="text-decoration-style:solid">http://127.0.0.1:8000</u></font>
   <span style="background-color:#007166"><font color="#D3D7CF"> server </font></span>  Documentation at <font color="#729FCF"><u style="text-decoration-style:solid">http://127.0.0.1:8000/docs</u></font>

      <span style="background-color:#007166"><font color="#D3D7CF"> tip </font></span>  Running in development mode, for production use:
             <b>fastapi run</b>

             Logs:

     <span style="background-color:#007166"><font color="#D3D7CF"> INFO </font></span>  Will watch for changes in these directories:
             <b>[</b><font color="#4E9A06">&apos;/home/user/code/awesomeapp&apos;</font><b>]</b>
     <span style="background-color:#007166"><font color="#D3D7CF"> INFO </font></span>  Uvicorn running on <font color="#729FCF"><u style="text-decoration-style:solid">http://127.0.0.1:8000</u></font> <b>(</b>Press CTRL+C to
             quit<b>)</b>
     <span style="background-color:#007166"><font color="#D3D7CF"> INFO </font></span>  Started reloader process <b>[</b><font color="#34E2E2"><b>383138</b></font><b>]</b> using WatchFiles
     <span style="background-color:#007166"><font color="#D3D7CF"> INFO </font></span>  Started server process <b>[</b><font color="#34E2E2"><b>383153</b></font><b>]</b>
     <span style="background-color:#007166"><font color="#D3D7CF"> INFO </font></span>  Waiting for application startup.
     <span style="background-color:#007166"><font color="#D3D7CF"> INFO </font></span>  Application startup complete.
```

</div>

O programa de linha de comando chamado `fastapi` é o **FastAPI CLI**.

O FastAPI CLI recebe o caminho para o seu programa Python (por exemplo, `main.py`), detecta automaticamente a instância de `FastAPI` (comumente nomeada `app`), determina a forma correta de importação e então a serve.

Para produção, você usaria `fastapi run`. 🚀

Internamente, o **FastAPI CLI** usa o <a href="https://www.uvicorn.dev" class="external-link" target="_blank">Uvicorn</a>, um servidor ASGI de alta performance e pronto para produção. 😎

## `fastapi dev` { #fastapi-dev }

Executar `fastapi dev` inicia o modo de desenvolvimento.

Por padrão, o recarregamento automático está ativado, recarregando o servidor automaticamente quando você faz mudanças no seu código. Isso consome muitos recursos e pode ser menos estável do que quando está desativado. Você deveria usá-lo apenas no desenvolvimento. Ele também escuta no endereço IP `127.0.0.1`, que é o IP para a sua máquina se comunicar apenas consigo mesma (`localhost`).

## `fastapi run` { #fastapi-run }

Executar `fastapi run` inicia o FastAPI em modo de produção por padrão.

Por padrão, o recarregamento automático está desativado. Ele também escuta no endereço IP `0.0.0.0`, o que significa todos os endereços IP disponíveis; dessa forma, ficará acessível publicamente para qualquer pessoa que consiga se comunicar com a máquina. É assim que você normalmente o executaria em produção, por exemplo, em um contêiner.

Na maioria dos casos, você teria (e deveria ter) um "proxy de terminação" tratando o HTTPS por cima; isso dependerá de como você faz o deploy da sua aplicação, seu provedor pode fazer isso por você ou talvez seja necessário que você configure isso por conta própria.

/// tip | Dica

Você pode aprender mais sobre isso na [documentação de deployment](deployment/index.md){.internal-link target=_blank}.

///
