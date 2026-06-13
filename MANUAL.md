# Manual — WhisperFlow Local

Ditado por voz **100% local** (offline), estilo Wispr Flow: aperte um atalho, fale,
aperte de novo e o texto é digitado onde o cursor estiver. Transcrição na GPU com
`faster-whisper`, overlay com ondas sonoras, histórico e configurações em janela.

- **Privacidade:** o áudio nunca sai da máquina.
- **Custo:** zero (sem API).
- **Hardware de referência:** i5-12400 · 32 GB RAM · RTX 4060 (8 GB).

---

## 1. Instalação

### Pré-requisitos
- Windows 10/11.
- Python instalado (testado e funcionando no **Python 3.14**).
- GPU NVIDIA para usar `cuda` (opcional — há modo CPU).

### Passo a passo

Para **poupar o disco C**, instale tudo no disco **D**. Abra o terminal e:

```bash
# 1) Ambiente virtual no disco D
py -3.14 -m venv D:\WhisperFlowLocal\.venv

# 2) Ativar o ambiente
D:\WhisperFlowLocal\.venv\Scripts\activate

# 3) Instalar dependências (inclui PySide6, faster-whisper e libs CUDA)
cd D:\CloudCode-Projects\whisperflow-local
pip install -r requirements.txt
```

As bibliotecas CUDA (cuBLAS/cuDNN) vêm como pacotes pip (`nvidia-cublas-cu12`,
`nvidia-cudnn-cu12`) — **não é preciso instalar o CUDA Toolkit**. O app localiza
essas DLLs automaticamente (`src/cuda_setup.py`).

### Primeira execução

```bash
python src/main.py
```

Na **primeira vez**, o modelo `large-v3` (~3 GB) é baixado para
`D:\WhisperFlowLocal\models`. Depois disso, funciona totalmente offline.

> Para fechar: ícone na bandeja (perto do relógio) → botão direito → **Sair**.

### Atalho clicável (recomendado para uso diário)

Em vez de abrir o terminal, dê **dois cliques** em
`scripts\Iniciar WhisperFlow.vbs` — ele abre o app **sem janela de console**,
direto na bandeja. (Edite os caminhos dentro do `.vbs` se instalou em outro local.)
Para iniciar como administrador (necessário para o Win+H), clique com o botão direito
no `.vbs` → "Executar como administrador", ou use a tarefa agendada (seção 6).

---

## 2. Como usar

1. Com o app aberto, procure o **ícone na bandeja** (círculo azul com microfone).
   Pode estar em "mostrar ícones ocultos" (seta `⌃`).
2. Clique num campo de texto qualquer (deixe o cursor onde quer o texto).
3. Aperte o **atalho** (padrão de fábrica: `Win+H`; configurável) → aparece a
   **pílula com ondas sonoras** na parte inferior da tela. **Fale.**
4. Aperte o **atalho de novo** → mostra "transcrevendo…" e em ~1–2 s o texto é
   **digitado** no campo ativo.
5. Cada transcrição é salva no **Histórico** (veja na janela).

**Modo toggle:** o atalho é um interruptor — aperta para iniciar, aperta para parar.
Não precisa segurar.

---

## 3. A janela (Histórico e Configurações)

Abra clicando no ícone da bandeja.

### Aba Histórico
- Lista das transcrições (mais recentes no topo).
- Clique numa para ver/editar o texto.
- **Salvar alteração** · **Copiar** · **Excluir**.

### Aba Configurações
| Campo | O que faz |
|---|---|
| **Modelo** | `tiny`→`large-v3`. Maior = mais preciso e mais pesado. |
| **Dispositivo** | `cuda` (GPU) ou `cpu`. |
| **Idioma** | `pt` (fixo, mais rápido) ou vazio (detecção automática). |
| **Atalho** | Combinação de teclas (sintaxe da lib `keyboard`, ex.: `alt gr+z`). |
| **Modo** | `toggle` (aperta/aperta). |
| **Pasta de dados/modelos** | Onde ficam settings, histórico e modelos — use o disco D. |
| **Digitar no app ativo** | Liga/desliga a digitação automática. |
| **Substituir atalho do Windows** | Suprime o atalho nativo (requer admin). |

Clique em **Salvar configurações** para aplicar (recarrega o modelo se necessário e
re-registra o atalho).

---

## 4. Configurar o atalho

A sintaxe é a da lib `keyboard`. Exemplos válidos:

- `alt gr+z` (AltGr + Z) — **recomendado**: AltGr é pouco usado e o Z não tem
  caractere especial no teclado ABNT2, então não digita nada por engano.
- `alt gr+v`, `alt gr+space`
- `ctrl+alt+space`
- `windows+h` (substitui o Ditado por Voz do Windows — ver seção 6)

Altere em **Configurações → Atalho** e salve, ou edite direto o
`settings.json` (ver seção 7).

---

## 5. GPU vs CPU

- **GPU (RTX 4060):** `Dispositivo = cuda`, modelo `large-v3`. Rápido e preciso.
- **CPU (sem GPU ou erro de cuDNN):** `Dispositivo = cpu`. O app usa `int8`
  automaticamente; prefira modelo `small` ou `medium` para não ficar lento.

---

## 6. Substituir o Win+H do Windows (administrador)

`Win+H` é o atalho do **Ditado por Voz nativo** do Windows. Para que o WhisperFlow
o substitua, é preciso **suprimir** o atalho, e isso só funciona com o app **elevado
(administrador)**.

- **Marque** "Substituir atalho do Windows" nas configurações e defina o atalho como
  `windows+h`.
- **Rode o app como administrador.** Sem admin, o app avisa no console que a supressão
  falhou e o ditado nativo pode abrir junto.

### Iniciar junto com o Windows

```bash
# Opção A — sem admin (não substitui o Win+H), sobe sem console:
python scripts/startup.py install
python scripts/startup.py uninstall
python scripts/startup.py status

# Opção B — ELEVADO (substitui o Win+H no boot). Rode num terminal ADMIN:
python scripts/startup.py install-admin
python scripts/startup.py uninstall-admin
```

Use **ou** a opção A **ou** a B, não as duas.

---

## 7. Onde ficam os arquivos

| Item | Local (padrão) |
|---|---|
| Código | `D:\CloudCode-Projects\whisperflow-local` |
| Ambiente virtual | `D:\WhisperFlowLocal\.venv` |
| Configurações | `D:\WhisperFlowLocal\settings.json` |
| Histórico | `D:\WhisperFlowLocal\history.json` |
| Modelos (cache) | `D:\WhisperFlowLocal\models` (~3 GB) |
| Ponteiro (único no C:) | `%APPDATA%\WhisperFlowLocal\location.json` (poucos bytes) |

Para mudar a pasta de dados: **Configurações → Pasta de dados/modelos → Procurar…**.
Ao salvar, os arquivos existentes são movidos para o novo local.

### Exemplo de `settings.json`
```json
{
  "model_size": "large-v3",
  "device": "cuda",
  "compute_type": "float16",
  "language": "pt",
  "hotkey": "alt gr+z",
  "mode": "toggle",
  "suppress_hotkey": false,
  "type_output": true,
  "print_output": true
}
```

---

## 8. Solução de problemas

| Sintoma | Causa / solução |
|---|---|
| `cublas64_12.dll is not found` | DLL CUDA não encontrada. Já tratado por `cuda_setup.py`; garanta que `nvidia-cublas-cu12` e `nvidia-cudnn-cu12` estão instalados. |
| App "trava" em "transcrevendo…" | Erro durante a transcrição. A versão atual libera o estado mesmo em erro; veja o log do console. |
| Win+H abre o ditado do Windows junto | App não está como administrador. Use a tarefa elevada (seção 6) ou troque o atalho. |
| Atalho não dispara | Verifique a sintaxe do atalho (seção 4); rode como admin se for combinação de sistema. |
| Lento na transcrição | Use GPU (`cuda`) ou um modelo menor (`small`/`medium`). |
| Disco C enchendo | Confirme a pasta de dados em D (seção 7) e crie o venv em D. |
| Texto não é digitado | "Digitar no app ativo" desmarcado, ou app de destino com privilégio elevado (rode o WhisperFlow como admin). |

---

## 9. Arquitetura (resumo)

| Arquivo (`src/`) | Papel |
|---|---|
| `config.py` | Configurações (JSON) |
| `paths.py` | Resolve a pasta de dados no disco D |
| `cuda_setup.py` | Registra as DLLs CUDA antes de carregar o ctranslate2 |
| `audio.py` | Captura do microfone + nível (ondas) |
| `transcriber.py` | Transcrição `faster-whisper` (recarregável) |
| `output.py` | Digita o texto no app ativo |
| `hotkey.py` | Atalho global + supressão (lib `keyboard`) |
| `overlay.py` | Pílula com ondas sonoras (PySide6) |
| `window.py` | Janela (histórico + config) + bandeja |
| `main.py` | Orquestra tudo (toggle + Qt + threads) |

---

## 10. Versões portáteis e GitHub

O programa pode ser usado de quatro formas. Escolha a que combina com você:

### A) A partir do GitHub (recomendado para reinstalar / Linux)
No GitHub fica só o **código** (leve). O modelo (~3 GB) baixa sozinho na 1ª execução.

```bash
git clone <seu-repositorio> whisperflow-local
cd whisperflow-local
setup.bat        # Windows  (ou:  bash setup.sh  no Linux/macOS)
run.bat          # inicia   (ou:  ./run.sh)
```

`setup` cria um `.venv` **dentro da pasta** e instala tudo. Sem GPU NVIDIA, edite o
`setup` para usar `requirements-cpu.txt` (mais leve) e deixe `device="cpu"`.

### B) Pasta portátil com Python embutido (para PC sem Python / pendrive / amigo)
Gere uma vez na sua máquina:

```bash
build\build_portable.bat
```

Isso cria a pasta **`WhisperFlow-Portable\`** com Python embutido + dependências.
Copie essa pasta para qualquer PC Windows (mesmo sem Python) e dê 2 cliques em
**`Iniciar WhisperFlow.bat`**. Tudo (settings, histórico, modelos) fica **dentro
da pasta** (`data\`) — é só copiar a pasta inteira para mover.

### C) Executável .exe (PyInstaller)
```bash
build\build_exe.bat
```
Gera `build\dist\WhisperFlow\WhisperFlow.exe`. Copie a pasta `WhisperFlow\` inteira.
Com CUDA o resultado é grande (~2 GB); para um .exe enxuto, instale o ambiente com
`requirements-cpu.txt` antes de gerar.

### D) Modo portátil manual
Crie um arquivo vazio chamado **`portable.txt`** na raiz do programa (ou defina a
variável de ambiente `WHISPERFLOW_PORTABLE=1`). A partir daí, os dados deixam de ir
para `D:\WhisperFlowLocal` e passam a ficar em **`data\`** ao lado do programa.

### O que vai (e o que não vai) para o GitHub
O `.gitignore` já cuida disso. **Vai:** código, scripts, manual. **Não vai:** `.venv`,
`models/`, `data/`, `settings.json`, `history.json`, builds (`dist/`, `.exe`, portátil).
Assim o repositório fica leve e você reinstala em minutos.

### Linux
Funciona com `setup.sh`/`run.sh`. Diferenças: atalhos globais (lib `keyboard`) exigem
**rodar como root** (`sudo ./run.sh`); a supressão do Win+H e a tarefa agendada são
exclusivas do Windows; o overlay e a digitação funcionam sob X11.
