"""Internationalisation for Alf Torrent.

The source language is European Portuguese. A catalog maps each Portuguese source string
(or format template) to its translation. To add a language, add a new dict to CATALOGS and an
entry to LANGUAGES. Anything missing from a catalog falls back to the Portuguese source text.
"""
import os

LANG = "pt"
LANGUAGES = {"pt": "Português (Portugal)", "en": "English"}
MISSING = set()          # strings without a translation seen at runtime (useful when testing)

EN = {
    "Ficheiro Torrent":
        "Torrent file",
    "Cliente BitTorrent":
        "BitTorrent client",
    "Fila":
        "Queue",
    "BIBLIOTECA":
        "LIBRARY",
    "PREFERÊNCIAS":
        "PREFERENCES",
    "Velocidade de download":
        "Download speed",
    "Velocidade de upload":
        "Upload speed",
    "Transferências ativas":
        "Active transfers",
    "Total transferido":
        "Total downloaded",
    "Geral":
        "General",
    "Pasta de destino, automatização e integração com o Windows.":
        "Destination folder, automation and Windows integration.",
    "Destino":
        "Destination",
    "Pasta de destino":
        "Destination folder",
    "Onde as novas transferências são guardadas.":
        "Where new downloads are saved.",
    "Pasta vigiada":
        "Watched folder",
    "Adicionar automaticamente":
        "Add automatically",
    "Os ficheiros .torrent largados na pasta são adicionados e verificados sozinhos.":
        "Any .torrent files dropped in the folder are added and verified automatically.",
    "Pasta a vigiar":
        "Folder to watch",
    "Iniciar com o Windows":
        "Start with Windows",
    "Arranca já escondido na bandeja.":
        "Starts hidden in the system tray.",
    "Fechar para a bandeja":
        "Close to tray",
    "Continua a transferir e a partilhar em segundo plano.":
        "Keeps downloading and seeding in the background.",
    "Ficheiros .torrent e links magnet":
        ".torrent files and magnet links",
    "Regista o programa; o Windows pede-te para o escolheres como predefinido.":
        "Registers the app; Windows will ask you to confirm it as the default.",
    "Desempenho":
        "Performance",
    "Modo discreto":
        "Discreet mode",
    "Prioridade baixa, menos ligações em simultâneo e sem atualizar o ecrã quando a janela está escondida.":
        "Low priority, fewer simultaneous connections and no screen updates while the window is hidden.",
    "Rede e limites":
        "Network & limits",
    "Velocidade, fila, privacidade e firewall.":
        "Speed, queue, privacy and firewall.",
    "Velocidade e fila":
        "Speed & queue",
    "Aplicar alterações":
        "Apply changes",
    "Os limites aplicam-se de imediato.":
        "Limits take effect immediately.",
    "Privacidade":
        "Privacy",
    "Encriptação do tráfego":
        "Traffic encryption",
    "Ajuda contra a limitação de velocidade do operador. «Obrigatória» só liga a peers compatíveis. Não esconde o teu IP.":
        "Helps against ISP throttling. “Required” only connects to compatible peers. It does not hide your IP.",
    "Ligação à VPN":
        "VPN connection",
    "Escolhe o adaptador da tua VPN. Se cair, todas as transferências e partilhas são bloqueadas até voltar.":
        "Choose your VPN adapter. If it drops, all downloads and uploads are blocked until it comes back.",
    "Estado da proteção":
        "Protection status",
    "Diagnóstico de partilha":
        "Seeding diagnostics",
    "Testar ligação":
        "Test connection",
    "Mostra quantos peers estão ligados, se há ligações de entrada (porta acessível) e se alguém está a pedir dados teus.":
        "Shows how many peers are connected, whether there are incoming connections (reachable port) and whether anyone is requesting data from you.",
    "Testar upload (local)":
        "Test upload (local)",
    "Um peer de teste local descarrega uns MB de um torrent completo da lista. Prova que o programa envia dados e que o ecrã os mostra.":
        "A local test peer downloads a few MB from a complete torrent in your list. It proves the app sends data and the screen shows it.",
    "Resultado":
        "Result",
    "Firewall do Windows":
        "Windows Firewall",
    "Regra de entrada e saída":
        "Inbound and outbound rule",
    "Permite as ligações deste programa na Firewall.":
        "Allows this program's connections through the firewall.",
    "Agendamento":
        "Schedule",
    "Descarrega apenas nas horas que escolheres.":
        "Download only during the hours you choose.",
    "Horário de transferência":
        "Download window",
    "Transferir só neste horário":
        "Download only during this window",
    "Fora do horário os downloads esperam; a partilha (upload) continua.":
        "Outside the window downloads wait; seeding (upload) continues.",
    "Estado":
        "Status",
    "Mais recentes":
        "Newest",
    " Com a VPN escolhida o UPnP está desligado.":
        " With the chosen VPN, UPnP is turned off.",
    "(Medição do momento: repete se ninguém estava a descarregar.)":
        "(Snapshot of the moment: repeat if nobody was downloading.)",
    "Tudo bloqueado: a VPN escolhida está em baixo.":
        "Everything blocked: the chosen VPN is down.",
    "Este torrent ainda não está completo; está a transferir.":
        "This torrent isn't complete yet; it is downloading.",
    "Sem peers ligados: ninguém está a pedir dados teus neste momento.":
        "No connected peers: nobody is requesting data from you right now.",
    "Os peers ligados são seeds e, segundo o tracker, não há leechers: sem leechers não há upload.":
        "The connected peers are seeds and, according to the tracker, there are no leechers: without leechers there is no upload.",
    "RESUMO":
        "SUMMARY",
    "ESTADO":
        "STATUS",
    "ENXAME":
        "SWARM",
    "TRACKERS":
        "TRACKERS",
    "PEERS LIGADOS":
        "CONNECTED PEERS",
    "Detalhes do torrent":
        "Torrent details",
    "Todas (sem proteção)":
        "All (no protection)",
    "✓ Horário guardado":
        "✓ Schedule saved",
    "Pesquisar torrents":
        "Search torrents",
    "✓ Aplicado":
        "✓ Applied",
    "Limites do torrent":
        "Torrent limits",
    "Programa registado.\n\nO Windows exige que confirmes tu o programa por defeito. Vou abrir as Definições: procura «Alf Torrent» e escolhe-o para .torrent e MAGNET.":
        "App registered.\n\nWindows requires you to confirm the default program yourself. I'll open Settings: look for “Alf Torrent” and choose it for .torrent and MAGNET.",
    "Transferências":
        "Transfers",
    "A transferir":
        "Downloading",
    "A partilhar":
        "Seeding",
    "Em pausa":
        "Paused",
    "Biblioteca":
        "Library",
    "Sem agendamento":
        "No schedule",
    "Pesquisar transferências…":
        "Search transfers…",
    "0 transferências":
        "0 transfers",
    "Pausar todas":
        "Pause all",
    "Limite de download (KB/s)":
        "Download limit (KB/s)",
    "0 = sem limite.":
        "0 = unlimited.",
    "Limite de upload (KB/s)":
        "Upload limit (KB/s)",
    "As restantes ficam em fila.":
        "The rest wait in the queue.",
    "Porta de ligação":
        "Connection port",
    "Entre 1025 e 65535.":
        "Between 1025 and 65535.",
    "Preferida":
        "Preferred",
    "Ainda não testado.":
        "Not tested yet.",
    "Preferências":
        "Preferences",
    "Nome":
        "Name",
    "Sem transferências.\nAdiciona um ficheiro .torrent, um link magnet ou usa a pesquisa.":
        "No transfers.\nAdd a .torrent file, a magnet link or use search.",
    "Nenhuma transferência neste filtro.":
        "No transfers in this filter.",
    "Detalhes e peers…":
        "Details & peers…",
    "Abrir pasta":
        "Open folder",
    "Limites do torrent…":
        "Torrent limits…",
    "Subir na fila":
        "Move up in queue",
    "Descer na fila":
        "Move down in queue",
    "Verificar ficheiros":
        "Verify files",
    "Copiar link magnet":
        "Copy magnet link",
    "Remover da lista":
        "Remove from list",
    "Remover e apagar ficheiros…":
        "Remove and delete files…",
    "A medir…":
        "Measuring…",
    "Mapeamento automático (UPnP/NAT-PMP): desligado com a VPN; a porta tem de ser aberta no fornecedor da VPN.":
        "Automatic port mapping (UPnP/NAT-PMP): turned off with the VPN; the port must be opened at your VPN provider.",
    "DHT: inativo.":
        "DHT: inactive.",
    "Bloqueado: a VPN escolhida está em baixo.":
        "Blocked: the chosen VPN is down.",
    "A testar o upload (7 s)…":
        "Testing upload (7 s)…",
    "  Segundo o tracker: desconhecido (ainda sem resposta)":
        "  According to the tracker: unknown (no response yet)",
    "  Sem trackers (só DHT e peers conhecidos).":
        "  No trackers (DHT and known peers only).",
    "  Nenhum.":
        "  None.",
    "saída":
        "outgoing",
    "entrada":
        "incoming",
    "pede dados":
        "requesting data",
    "✓ Link magnet copiado":
        "✓ Magnet link copied",
    "●  Sem proteção: usa todas as ligações":
        "●  No protection: uses all connections",
    "Ligação direta (sem VPN)":
        "Direct connection (no VPN)",
    "●  Sem agendamento":
        "●  No schedule",
    "O que procuras?":
        "What are you looking for?",
    "Pesquisar":
        "Search",
    "Escolher ficheiros .torrent":
        "Choose .torrent files",
    "Link magnet inválido.":
        "Invalid magnet link.",
    "A carregar…":
        "Loading…",
    "Apagar também os ficheiros transferidos?":
        "Also delete the downloaded files?",
    "Pasta vigiada (.torrent)":
        "Watched folder (.torrent)",
    "Escolhe primeiro a pasta a vigiar":
        "Choose the folder to watch first",
    "Queres criar uma regra na Firewall do Windows para permitir ligações a este programa? (Pede permissões de administrador)":
        "Do you want to create a Windows Firewall rule to allow this program's connections? (Requires administrator permissions)",
    "A regra já existe":
        "The rule already exists",
    "Não há regra para remover":
        "There is no rule to remove",
    "Link magnet":
        "Magnet link",
    "Adicionar torrent":
        "Add torrent",
    "Todas":
        "All",
    "Progresso":
        "Progress",
    "Tamanho":
        "Size",
    "Alterar…":
        "Change…",
    "Nenhuma pasta escolhida":
        "No folder chosen",
    "Escolhe uma pasta":
        "Choose a folder",
    "Escolher…":
        "Choose…",
    "Associar…":
        "Associate…",
    "Aplicar":
        "Apply",
    "Atualizar":
        "Refresh",
    "Testar agora":
        "Test now",
    "Testar upload":
        "Test upload",
    "Criar regra":
        "Create rule",
    "Remover":
        "Remove",
    "Guardar horário":
        "Save schedule",
    "DHT: ativo mas com 0 nós (a ligar-se; se ficar a 0, a tua rede pode estar a bloqueá-lo).":
        "DHT: active but with 0 nodes (connecting; if it stays at 0, your network may be blocking it).",
    "Não há torrents na lista.":
        "There are no torrents in the list.",
    "A VPN escolhida está em baixo: tudo bloqueado.":
        "The chosen VPN is down: everything is blocked.",
    "Precisas de pelo menos um torrent completo na lista para este teste.":
        "You need at least one complete torrent in the list for this test.",
    "O programa não está a escutar em nenhuma porta.":
        "The program is not listening on any port.",
    "a contactar…":
        "contacting…",
    "sem mensagem":
        "no message",
    "A verificar ficheiros…":
        "Verifying files…",
    "Não foi possível copiar o link":
        "Couldn't copy the link",
    "VPN em baixo: tudo bloqueado":
        "VPN down: everything blocked",
    "●  Dentro do horário: a transferir":
        "●  Inside the window: downloading",
    "●  Fora do horário: downloads em espera":
        "●  Outside the window: downloads on hold",
    "Horário inválido (usa HH:MM, ex. 01:30)":
        "Invalid time (use HH:MM, e.g. 01:30)",
    "A pesquisar…":
        "Searching…",
    "A obter…":
        "Fetching…",
    "Valores inválidos (porta 1025–65535, ativas 1–50)":
        "Invalid values (port 1025–65535, active 1–50)",
    "✓ Ficheiros encontrados, a verificar…":
        "✓ Files found, verifying…",
    "Download (KB/s)":
        "Download (KB/s)",
    "Upload (KB/s)":
        "Upload (KB/s)",
    "Abrir":
        "Open",
    "Sair":
        "Quit",
    "●  Regra ativa":
        "●  Rule active",
    "●  Sem regra":
        "●  No rule",
    "Confirma o pedido do Windows (UAC)":
        "Confirm the Windows prompt (UAC)",
    "Sem permissões de administrador":
        "No administrator permissions",
    "A obter metadados…":
        "Fetching metadata…",
    "Retomar todas":
        "Resume all",
    "Continua a transferir e a partilhar em segundo plano. Usa o ícone junto ao relógio para abrir ou sair.":
        "Keeps downloading and seeding in the background. Use the icon next to the clock to open or quit.",
    "Armazenamento":
        "Storage",
    "Tudo o que está a chegar. Tudo o que está a partilhar.":
        "Everything that's arriving. Everything that's being shared.",
    "Início":
        "Start",
    "Formato HH:MM, por exemplo 01:00.":
        "HH:MM format, for example 01:00.",
    "Fim":
        "End",
    "Aceita horários que passam da meia-noite (23:00 às 07:00).":
        "Accepts windows that cross midnight (23:00 to 07:00).",
    "Mapeamento automático (UPnP/NAT-PMP): o router não respondeu. Se ninguém se ligar a ti, abre a porta manualmente no router.":
        "Automatic port mapping (UPnP/NAT-PMP): the router didn't respond. If nobody connects to you, open the port manually on the router.",
    "O peer de teste não conseguiu ligar-se ao programa. A escuta local está com problemas (outro programa na porta, firewall ou VPN a bloquear).":
        "The test peer couldn't connect to the program. The local listener has a problem (another program on the port, firewall or VPN blocking).",
    "O peer de teste ligou-se mas não recebeu dados. Verifica se o torrent está mesmo completo («Verificar ficheiros» no menu do cartão).":
        "The test peer connected but received no data. Check that the torrent is really complete (“Verify files” in the card menu).",
    "Atualiza a cada segundo. Mostra só dados de ficheiros (sem tráfego de protocolo).":
        "Updates every second. Shows file data only (no protocol traffic).",
    "Ligação VPN perdida: transferências bloqueadas.":
        "VPN connection lost: transfers blocked.",
    "Pesquisar no Internet Archive":
        "Search the Internet Archive",
    "Filmes, música, software e livros de domínio público ou de licença livre. Sem anúncios nem pop-ups.":
        "Public-domain and freely licensed movies, music, software and books. No ads or pop-ups.",
    "Sem resultados.":
        "No results.",
    "Adicionar":
        "Add",
    "Cola o link magnet:":
        "Paste the magnet link:",
    "0 = sem limite (usa o limite geral)":
        "0 = unlimited (uses the global limit)",
    "Guardar":
        "Save",
    "Mapeamento automático no router: ":
        "Automatic port mapping on the router: ",
    "Mapeamento automático no router FALHOU: ":
        "Automatic port mapping on the router FAILED: ",
    "Já existe na lista":
        "Already in the list",
    "Usa números inteiros.":
        "Use whole numbers.",
    "VPN reposta: transferências retomadas.":
        "VPN restored: transfers resumed.",
    "Erro":
        "Error",
    "Sem torrent":
        "No torrent",
    "✓ Adicionado":
        "✓ Added",
    "Já existe":
        "Already exists",
    "A pedir dados: {wants}. Upload ativo: {up_speed}.":
        "Requesting data: {wants}. Upload active: {up_speed}.",
    "{app} v{version}\n\nCliente BitTorrent baseado no libtorrent {lt_version}.\n\nDados e definições:\n{data_dir}":
        "{app} v{version}\n\nBitTorrent client built on libtorrent {lt_version}.\n\nData and settings:\n{data_dir}",
    "Peers ligados: {peers}, mas nenhum está a pedir dados teus.":
        "Connected peers: {peers}, but none is requesting data from you.",
    "A pedir dados: {wants}, mas todas as ligações foram iniciadas por ti; nenhuma de entrada. A porta {port} pode estar fechada.":
        "Requesting data: {wants}, but every connection was started by you; none incoming. Port {port} may be closed.",
    "  Progresso: {progress:.1f}%   ·   Tamanho: {size}":
        "  Progress: {progress:.1f}%   ·   Size: {size}",
    "  Partilhado no total: {uploaded}   ·   Descarregado no total: {downloaded}":
        "  Uploaded in total: {uploaded}   ·   Downloaded in total: {downloaded}",
    "  Velocidade (dados): ↓ {down_speed}   ↑ {up_speed}":
        "  Speed (data): ↓ {down_speed}   ↑ {up_speed}",
    "  Pasta: {path}":
        "  Folder: {path}",
    "  Peers ligados: {peers} (conhecidos: {known})   ·   seeds ligados: {seeds}":
        "  Connected peers: {peers} (known: {known})   ·   connected seeds: {seeds}",
    "  Ligações recebidas (porta acessível): {incoming}   ·   iniciadas por ti: {outgoing}":
        "  Incoming connections (reachable port): {incoming}   ·   started by you: {outgoing}",
    "  A pedir dados teus: {wants}":
        "  Requesting data from you: {wants}",
    "✓ Encriptação: {mode}":
        "✓ Encryption: {mode}",
    "Não encontrei «{name}» em:\n{dest}\n\nJá tens estes ficheiros noutra pasta?\n\nSim – escolher a pasta onde estão (só valida e partilha)\nNão – transferir para a pasta de destino\nCancelar – não adicionar":
        "I couldn't find “{name}” in:\n{dest}\n\nDo you already have these files in another folder?\n\nYes – choose the folder where they are (just verifies and seeds)\nNo – download to the destination folder\nCancel – don't add",
    "Não encontrei «{name}» nessa pasta (o nome tem de ser igual ao do torrent).\n\nAdicionar mesmo assim? Os ficheiros serão transferidos de novo.":
        "I couldn't find “{name}” in that folder (the name must match the torrent's).\n\nAdd anyway? The files will be downloaded again.",
    "   ·   enxame: {seeds} seeds, {leechers} leechers":
        "   ·   swarm: {seeds} seeds, {leechers} leechers",
    "{n} transferência{s}":
        "{n} transfer{s}",
    "Escuta: FALHOU ({error}). Outro programa (por exemplo outro cliente de torrents) pode estar a usar a porta {port}.":
        "Listening: FAILED ({error}). Another program (for example another torrent client) may be using port {port}.",
    "Para abrir a porta: no router, redireciona TCP e UDP {port} para {ip} (o IP deste PC) e reserva esse IP para o PC.":
        "To open the port: on your router, forward TCP and UDP {port} to {ip} (this PC's IP) and reserve that IP for the PC.",
    "✓ O programa enviou {size} para um peer de teste e o cartão mostrou ↑ {speed}. O envio e o ecrã funcionam; se não há upload real, a causa está na rede (porta, router, trackers ou falta de leechers). Usa «Testar agora» para ver qual.":
        "✓ The program sent {size} to a test peer and the card showed ↑ {speed}. Sending and the screen work; if there is no real upload, the cause is the network (port, router, trackers or no leechers). Use “Test now” to see which.",
    "Não foi possível ler o estado: {error}":
        "Couldn't read the status: {error}",
    "  Segundo o tracker: {seeds} seeds, {leechers} leechers":
        "  According to the tracker: {seeds} seeds, {leechers} leechers",
    "   ·   {seeds} seeds, {leechers} leechers":
        "   ·   {seeds} seeds, {leechers} leechers",
    "  {url}\n     {msg}{sw}   ·   falhas: {fails}":
        "  {url}\n     {msg}{sw}   ·   failures: {fails}",
    "{name} — (desligada)":
        "{name} — (disconnected)",
    "Pasta onde estão os ficheiros de {name}":
        "Folder containing the files of {name}",
    " {n} peer{s}{swarm}":
        " {n} peer{s}{swarm}",
    "{n} transferência{s} em curso":
        "{n} transfer{s} in progress",
    "{n} torrent{s} a partilhar":
        "{n} torrent{s} seeding",
    "{n} a transferir":
        "{n} downloading",
    "·  {n} a partilhar":
        "·  {n} seeding",
    "Escuta: a porta {port} estava ocupada e o programa usa a {real}. Abre a {real} no router.":
        "Listening: port {port} was busy and the program uses {real}. Open {real} on your router.",
    "Escuta: porta {port} ativa.":
        "Listening: port {port} active.",
    "DHT: ativo, {nodes} nós.":
        "DHT: active, {nodes} nodes.",
    "O teu IP público ({ext}) está na gama de CGNAT: o operador partilha o IP e não é possível abrir portas (só com IP público dedicado ou VPN com redirecionamento).":
        "Your public IP ({ext}) is in the CGNAT range: your ISP shares the IP and ports can't be opened (only with a dedicated public IP or a VPN with port forwarding).",
    "Endereço público visto pelos peers: {ext}. Se for diferente do IP WAN que o teu router mostra, o operador usa CGNAT e não dá para abrir portas.":
        "Public address seen by peers: {ext}. If it differs from the WAN IP your router shows, your ISP uses CGNAT and ports can't be opened.",
    "O programa enviou {size}, mas o cartão não mostrou velocidade de upload: defeito de visualização.":
        "The program sent {size}, but the card showed no upload speed: display bug.",
    "  {url}\n     sem resposta ainda":
        "  {url}\n     no response yet",
    "●  «{name}» em baixo: tudo bloqueado":
        "●  “{name}” is down: everything blocked",
    "●  Protegido: só via «{name}»":
        "●  Protected: only via “{name}”",
    "Protegido via «{name}»":
        "Protected via “{name}”",
    "O adaptador «{name}» está desligado.\n\nAs transferências ficam bloqueadas até ele voltar. Continuar?":
        "The adapter “{name}” is disconnected.\n\nTransfers will be blocked until it comes back. Continue?",
    "Horário {start}–{end}":
        "Window {start}–{end}",
    "Fora do horário ({start}–{end})":
        "Outside the window ({start}–{end})",
    "{count} resultados (os mais descarregados primeiro)":
        "{count} results (most downloaded first)",
    "Já existe: {name}":
        "Already exists: {name}",
    "Não foi possível abrir a pasta:\n{error}":
        "Couldn't open the folder:\n{error}",
    "Erro: {error}":
        "Error: {error}",
    "↑ {size} partilhados":
        "↑ {size} uploaded",
    "Sem peers ligados em {count} torrent(s): ninguém está ligado a ti neste momento. Vê os trackers em «Detalhes e peers…».{vpn_note}":
        "No connected peers in {count} torrent(s): nobody is connected to you right now. Check the trackers in “Details & peers…”.{vpn_note}",
    "Não foi possível preparar o teste: {error}":
        "Couldn't prepare the test: {error}",
    "Ficheiro .torrent inválido:\n{file}\n{error}":
        "Invalid .torrent file:\n{file}\n{error}",
    "Não foi possível adicionar:\n{error}":
        "Couldn't add:\n{error}",
    "Apagar «{name}» e os ficheiros transferidos?":
        "Delete “{name}” and the downloaded files?",
    "Concluído: {name}":
        "Finished: {name}",
    "Peers ligados: {tot}, mas nenhum se ligou a ti: só tu te ligas a eles. A porta {port} parece fechada (router, firewall ou VPN) e isso reduz muito o upload.{vpn_note}":
        "Connected peers: {tot}, but none connected to you: only you connect to them. Port {port} looks closed (router, firewall or VPN) and that greatly reduces upload.{vpn_note}",
    "Peers ligados: {tot}, dos quais {incoming} se ligaram a ti (porta acessível). A pedir dados teus: {wants}. Leechers no enxame segundo os trackers: {leech}.":
        "Connected peers: {tot}, of which {incoming} connected to you (reachable port). Requesting data from you: {wants}. Leechers in the swarm according to the trackers: {leech}.",
    "{size}   ·   {downloads} descargas   ·   {id}":
        "{size}   ·   {downloads} downloads   ·   {id}",
    "Erro na pesquisa: {error}":
        "Search error: {error}",
    "porta externa {port} ({kind})":
        "external port {port} ({kind})",
    "Em fila":
        "Queued",
    "A verificar ficheiros":
        "Verifying files",
    "A obter metadados":
        "Fetching metadata",
    "Concluído":
        "Finished",
    "Desativada":
        "Disabled",
    "Obrigatória":
        "Required",
    "Vídeo":
        "Video",
    "Áudio":
        "Audio",
    "Livros e textos":
        "Books and texts",
    "Tudo":
        "Everything",
    "Agendado":
        "Scheduled",
    "Bloqueado (sem VPN)":
        "Blocked (no VPN)",
    "{used} de {total}":
        "{used} of {total}",
    "este torrent":
        "this torrent",
    "Software":
        "Software",
    "Idioma":
        "Language",
    "Idioma da interface":
        "Interface language",
    "Muda de imediato.":
        "Changes immediately.",
}

CATALOGS = {"en": EN}


def set_language(code):
    global LANG
    LANG = code if code in LANGUAGES else "pt"


def detect_language():
    """Portuguese if the system UI language is Portuguese, English otherwise."""
    try:
        import ctypes
        lid = ctypes.windll.kernel32.GetUserDefaultUILanguage()
        return "pt" if (lid & 0x3FF) == 0x16 else "en"
    except Exception:
        pass
    import locale
    loc = (locale.getlocale()[0] or os.environ.get("LANG", "")).lower()
    return "pt" if loc.startswith("pt") else "en"


def resolve_language(setting):
    """'auto' -> system language; otherwise the explicit code."""
    return detect_language() if setting in (None, "", "auto") else setting


def tr(text, **kw):
    cat = CATALOGS.get(LANG)
    if cat is None:
        out = text
    else:
        out = cat.get(text)
        if out is None:
            MISSING.add(text)
            out = text
    return out.format(**kw) if kw else out


def pl(n):
    """Plural suffix 's' for n != 1 (works for both Portuguese and English templates)."""
    return "" if n == 1 else "s"
