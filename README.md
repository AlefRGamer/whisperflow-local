# WhisperFlow Local

Ditado por voz (speech-to-text) rodando **100% local** na própria máquina — alternativa offline a apps como o Wispr Flow. Captura áudio do microfone, transcreve com um modelo Whisper local e insere o texto onde o cursor estiver.

> Documentação no vault: `D:\Obsidian-Vault\Projetos\WhisperFlow Local.md`

## Objetivo

- Transcrição local, sem enviar áudio para a nuvem (privacidade + sem custo de API).
- Atalho global para iniciar/parar o ditado em qualquer aplicativo.
- Inserção automática do texto transcrito via teclado.

## Stack candidata

- **Python 3.10+**
- **Transcrição:** [`faster-whisper`](https://github.com/SYSTRAN/faster-whisper) (CTranslate2, rápido em CPU/GPU) ou `whisper.cpp`.
- **Áudio:** `sounddevice` ou `pyaudio` para capturar o microfone.
- **Atalho global + digitação:** `pynput` / `keyboard`.
- **GPU:** RTX 4060 (8 GB) → CUDA + `float16`, roda `large-v3` em tempo real.

## Hardware alvo

i5-12400 · 32 GB RAM · RTX 4060 (8 GB). Config padrão já vem para GPU:
`device="cuda"`, `compute_type="float16"`, `model_size="large-v3"`.

### Pré-requisito da GPU (faster-whisper)

O `faster-whisper` no device `cuda` precisa das bibliotecas **cuBLAS** e **cuDNN 9**.
No Windows, instale via pip (não exige CUDA Toolkit completo):

```bash
pip install nvidia-cublas-cu12 nvidia-cudnn-cu12
```

Se a GPU falhar ao carregar, troque para CPU no `config.py`:
`device="cpu"`, `compute_type="int8"` (use `model_size="small"` ou `medium`).

## Como usar

App residente (fica em segundo plano, ícone na bandeja):

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python src/main.py
```

- Aperte **`Win+H`** (modo **toggle**) para **iniciar** a gravação → aparece um
  **overlay com ondas sonoras** reagindo à sua voz.
- Aperte **`Win+H`** de novo para **parar** → o overlay mostra "transcrevendo…",
  o texto é gerado na GPU e **digitado no campo ativo** (onde estiver o cursor).
- A transcrição vai para o **histórico** (janela acessível pela bandeja).
- Para **sair**: menu da bandeja → **Sair**.

### Substituir o Win+H do Windows (administrador)

`Win+H` é o atalho do **Ditado por Voz nativo** do Windows. Para que o WhisperFlow
o substitua, o atalho precisa ser **suprimido**, o que exige **rodar como administrador**
(a opção "Substituir atalho do Windows" já vem marcada nas configurações).

- **Com admin:** o ditado nativo não abre; só o WhisperFlow responde ao Win+H.
- **Sem admin:** o app avisa no console que a supressão falhou e segue funcionando,
  mas o ditado nativo pode abrir junto. Para voltar 100% ao nativo, desmarque
  "Substituir atalho do Windows" ou troque o atalho nas **Configurações**.

### Janela (histórico + configurações)

Abra pela bandeja (clique no ícone). Duas abas:

- **Histórico:** lista das transcrições; selecione para **editar**, **Copiar** ou
  **Excluir**. Persistido em `%APPDATA%\WhisperFlowLocal\history.json`.
- **Configurações:** modelo, dispositivo (cuda/cpu), idioma, atalho, modo, digitar no
  app ativo, substituir atalho do Windows. **Salvar** aplica na hora (recarrega o
  modelo se mudar) e grava em `%APPDATA%\WhisperFlowLocal\settings.json`.

### Onde os dados ficam (disco D)

Para **não encher o disco C**, settings, histórico e o **cache dos modelos** (~3 GB
para o `large-v3`) ficam numa **pasta de dados** configurável — por padrão
`D:\WhisperFlowLocal`. O único resíduo no C é um ponteiro de poucos bytes em
`%APPDATA%\WhisperFlowLocal\location.json` que diz onde está a pasta real.

Troque a pasta em **Configurações → Pasta de dados/modelos** (botão *Procurar…*):
ao salvar, os arquivos existentes são **movidos** para o novo local.

> Dica: crie também o ambiente virtual no D (`D:\WhisperFlowLocal\.venv`) para que as
> dependências grandes (PySide6, libs CUDA/cuDNN) não pesem no C.

### Iniciar junto com o Windows

```bash
python scripts/startup.py install     # HKCU Run: sobe sem console (SEM admin)
python scripts/startup.py uninstall
python scripts/startup.py status
```

Para **suprimir o Win+H desde o boot**, o app precisa subir **como administrador**.
O HKCU Run não eleva privilégio — use a **tarefa agendada elevada** (rode num
terminal **aberto como administrador**):

```bash
python scripts/startup.py install-admin    # tarefa ONLOGON com privilégio mais alto
python scripts/startup.py uninstall-admin
```

A tarefa executa o mesmo `pythonw src/main.py` a cada logon, já elevado, então o
Win+H é suprimido automaticamente. Use **ou** o HKCU Run **ou** a tarefa elevada
(não os dois ao mesmo tempo).

## Arquitetura (`src/`)

| Arquivo | Papel |
|---|---|
| `config.py` | Configurações persistidas em JSON (modelo, GPU, tecla, idioma) |
| `paths.py` | Resolve a pasta de dados (disco D) p/ settings, histórico e modelos |
| `store.py` | Histórico de transcrições (JSON) |
| `audio.py` | Captura do microfone + nível em tempo real (RMS) |
| `transcriber.py` | Transcrição com `faster-whisper` (recarregável) |
| `output.py` | Digita o texto no app ativo (`pynput`) |
| `hotkey.py` | Atalho global via `keyboard` + supressão do Win+H |
| `overlay.py` | Overlay flutuante com ondas sonoras (PySide6/Qt) |
| `window.py` | Janela (histórico + configurações) + ícone na bandeja |
| `main.py` | Orquestra: hotkey toggle + event loop Qt + threads |

Fluxo: Win+H → `AudioRecorder.start` + overlay; níveis de áudio viajam por sinais Qt
até o overlay; Win+H de novo → uma thread transcreve, digita e grava no histórico,
enquanto a GUI segue fluida.

## Próximos passos

- [ ] Filtro de comandos de voz ("nova linha", "ponto final").
- [ ] Tarefa agendada elevada para subir com admin no boot.
- [ ] Atalho configurável por captura de tecla (em vez de digitar o nome).
