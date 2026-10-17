# Alf Torrent

**Um cliente BitTorrent moderno, com tema escuro, para Windows, construído sobre o [libtorrent](https://www.libtorrent.org/).**
Partilha a biblioteca que já tens sem a descarregar outra vez, liga-te à tua VPN com bloqueio automático, agenda downloads e vê exatamente *porque* há (ou não há) upload.

![Python 3.12](https://img.shields.io/badge/python-3.12-blue) ![Licença: MIT](https://img.shields.io/badge/licen%C3%A7a-MIT-green) ![Plataforma: Windows](https://img.shields.io/badge/plataforma-Windows-lightgrey) ![Idiomas: EN | PT](https://img.shields.io/badge/idiomas-EN%20%7C%20PT-informational)

[English](README.md)

![Transferências](docs/transfers.png)
![Rede e limites](docs/network.png)

*As capturas usam dados de exemplo (software e filmes de licença livre) e estão em inglês. O programa abre em português se o Windows estiver em português.*

## Funcionalidades

**Transferências**
- Adiciona ficheiros `.torrent` ou links magnet; filtra (todas / a transferir / a partilhar / em pausa), pesquisa e ordena a lista.
- Fila com número configurável de downloads ativos (3 por defeito). Os torrents concluídos continuam a partilhar, independentemente desse limite.
- Pausa e retoma um ou todos, sobe e desce torrents na fila, define limites de velocidade por torrent, verifica ficheiros, copia o link magnet.
- Limites globais de download e upload e porta de escuta configurável.
- As velocidades mostradas são só **dados de ficheiros**: o tráfego de protocolo (pedidos, mensagens `have`…) não conta, por isso um torrent concluído mostra `0 B/s` de download.

**Partilha o que já tens**
- Ao adicionar um `.torrent`, a app procura os ficheiros pelo nome na pasta de destino e em pastas de biblioteca que já indicaste. Se estiverem completos, são verificados e partilhados **sem descarregar nada**.
- Se os ficheiros estiverem noutro sítio, pergunta uma vez e lembra-se da pasta (também funciona para um lote inteiro).
- Guarda dados de retoma rápida, por isso uma biblioteca grande não é reverificada a cada arranque.

**Rede e privacidade**
- **Encriptação do tráfego** (desativada / preferida / obrigatória). Ajuda contra a limitação de velocidade do operador; **não** esconde o teu IP.
- **Ligação à VPN com bloqueio**: escolhes o adaptador da VPN e a app liga-se a ele. Se o adaptador cair, tudo é bloqueado (downloads *e* uploads) e retoma sozinho quando volta, mesmo que o IP mude.
- O UPnP/NAT-PMP fica desligado enquanto estiver ligada a um adaptador de VPN.

**Agendamento e automatização**
- **Janela de download** (por exemplo 01:00–08:00, pode passar da meia-noite). Fora dela os downloads esperam; a partilha continua.
- **Pasta vigiada**: largas ficheiros `.torrent` numa pasta e são adicionados e verificados sozinhos (movidos para as subpastas `adicionados` / `erros`).
- Iniciar com o Windows, fechar para a bandeja, notificações ao concluir, associação de `.torrent` e `magnet:` e uma única instância a correr.

**Diagnóstico**
- **Testar ligação**: porta de escuta, mapeamento automático no router, estado do DHT, peers ligados, ligações de entrada e de saída e uma pista de CGNAT.
- **Detalhes do torrent**: enxame, trackers e lista de peers em direto, com velocidades e quem está a pedir dados teus.
- **Teste de upload local**: um peer de teste local descarrega uns MB de um dos teus torrents completos para provar, de ponta a ponta, que a app envia dados e que o ecrã os mostra.

**Pesquisa integrada**
- Pesquisa no [Internet Archive](https://archive.org/) (filmes, música, software e livros de domínio público ou de licença livre) e adiciona o torrent com um clique. Sem anúncios nem pop-ups.

**Interface**
- Interface escura com barra lateral, gráficos de velocidade em direto, cartões por transferência e páginas de preferências.
- Português (Portugal) e inglês: segue o idioma do sistema na primeira vez e pode mudar-se a qualquer momento na barra lateral.
- *Modo discreto*: prioridade baixa do processo, menos ligações simultâneas e sem atualizar o ecrã quando a janela está escondida. Num teste em Linux, sem ecrã físico, com 10 torrents, a app usou cerca de 65 MB de RAM e 1–2 % de CPU; os teus valores vão variar.

## Como começar

### Requisitos
- Windows 10/11 (alvo principal)
- **Python 3.12, 64 bits** — os pacotes do `libtorrent` não existem para todas as versões do Python (a 3.14, por exemplo, ainda não tem)

### Executar a partir do código
```bat
py -3.12 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

### Compilar o `.exe`
```bat
build.bat
```
O resultado fica em `dist\AlfTorrent.exe`. O workflow do GitHub Actions em `.github/workflows/build.yml` também o compila num runner Windows e publica-o como artefacto.

> O executável **não está assinado digitalmente**. O Windows SmartScreen ou o antivírus podem avisar sobre compilações PyInstaller sem assinatura (falso positivo). Podes ler o código e compilá-lo tu.

## Notas de utilização

**Fazer o upload funcionar.** Só há upload quando outros peers conseguem ligar-se a ti. Se o diagnóstico disser que não há ligações de entrada:
1. Cria a regra na Firewall do Windows (*Rede e limites → Firewall do Windows*).
2. Redireciona no router a porta **6881 TCP e UDP** (ou a que configuraste) para o IP local do PC e reserva esse IP para o PC. Usa o IP **local** (por exemplo `192.168.x.x`), não o público.
3. Se o teu operador usa CGNAT (IP público partilhado), não é possível abrir portas; o diagnóstico dá uma pista.
4. Com a ligação a um adaptador de VPN, a porta tem de ser aberta no fornecedor da VPN.

**Ligação à VPN.** Liga os sockets da própria app ao adaptador, o que funciona como um bloqueio ao nível da aplicação. Não controla os pedidos de DNS feitos pelo Windows, por isso os nomes dos trackers podem continuar a ser resolvidos pelo teu DNS normal. Podes verificar com um teste de deteção de torrents como o [ipleak.net](https://ipleak.net).

**Idioma.** Escolhe *Português* ou *English* no fundo da barra lateral (ou em *Geral → Idioma da interface*). Muda de imediato.

## Dados e definições

Guardados em `%APPDATA%\AlfTorrent\`:

| Caminho | Conteúdo |
|---|---|
| `config.json` | Definições e lista de torrents |
| `resume\` | Dados de retoma rápida |
| `torrents\` | Cópias dos ficheiros `.torrent` adicionados |

## Limitações

- Pensado primeiro para Windows. A bandeja, o arranque com o Windows, a associação de ficheiros e a regra de firewall são funcionalidades do Windows. A partir do código a interface também corre em Linux (foi assim que se fizeram os testes automáticos da interface), mas essas funcionalidades não se aplicam lá.
- A encriptação não te torna anónimo, e a ligação à VPN vale o que a tua VPN valer.
- A pesquisa está limitada ao Internet Archive, por opção.

## Estrutura do projeto

```
app.py              aplicação (interface + ligação ao motor)
i18n.py             traduções (textos-fonte em português -> catálogo em inglês)
AlfTorrent.ico      ícone (gerado por make_icon.py)
make_icon.py        desenha o ícone com o Pillow
build.bat           compila dist\AlfTorrent.exe com o PyInstaller
requirements.txt    dependências de execução
tests/              testes do catálogo de traduções
docs/               capturas de ecrã
.github/workflows/  CI: testes + compilação para Windows
```

## Contribuir

- **Testes:** `python -m unittest discover -s tests -v` (não precisam de ecrã nem de libtorrent). Verificam que todos os textos traduzidos existem no catálogo e que os parâmetros coincidem.
- **Adicionar um idioma:** o idioma de origem é o português. Em `i18n.py`, adiciona a `CATALOGS` um dicionário que associa cada texto em português à tradução (copia o dicionário `EN` como ponto de partida) e adiciona o idioma a `LANGUAGES`. O que faltar volta ao português.
- Mantém o texto visível ao utilizador dentro de `tr("...")`; usa parâmetros com nome (`tr("{n} peers", n=3)`) e o auxiliar `pl(n)` para o plural.

## Software de terceiros

[libtorrent](https://www.libtorrent.org/) (BSD-3-Clause), [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) (MIT), [Pillow](https://python-pillow.org/) (HPND), [psutil](https://github.com/giampaolo/psutil) (BSD-3-Clause) e [pystray](https://github.com/moses-palmer/pystray) (LGPL-3.0). Se distribuíres uma compilação, confirma as obrigações da LGPL para o `pystray`; o código e o `requirements.txt` permitem a qualquer pessoa recompilar com outra versão.

## Aviso

O Alf Torrent é um cliente BitTorrent de uso geral. A responsabilidade pelo que descarregas e partilhas é tua: usa-o apenas com conteúdo que tenhas o direito de distribuir.

## Licença

[MIT](LICENSE)
