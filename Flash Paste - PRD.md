# Product Requirements Document (PRD): FlashPaste

## 1. Visão Geral e Propósito

**FlashPaste** é um aplicativo nativo para Linux (Ubuntu/GNOME) destinado ao gerenciamento de textos temporários (snippets).

* **Conceito:** "Cache mental rápido". O usuário cola textos que precisa usar em breve.
* **Regra de Ouro:** Textos na pilha principal expiram e são deletados automaticamente após 24 horas.
* **Publicação:** Textos podem ser "salvos" enviando-os para o Pastebin, movendo-os para uma aba de histórico permanente.

## 2. Especificações Técnicas (Tech Stack)

* **Linguagem:** Python 3.11+.
* **GUI Toolkit:** GTK 4 + LibAdwaita (via `PyGObject`).
* **Gerenciamento de Janelas:** `Adw.Application`, `Adw.ApplicationWindow`.
* **Armazenamento de Dados:** SQLite3 (localizado em `XDG_DATA_HOME`).
* **Configurações:** GSettings / Gio.Settings (com Schema XML).
* **Rede:** Biblioteca `requests` (para comunicação com API Pastebin).
* **Distribuição:** Flatpak (Runtime: `org.gnome.Platform`, SDK: `org.gnome.Sdk`, versão 45 ou 46).

## 3. Arquitetura de Interface (UI/UX)

### 3.1. Estrutura Principal

* **Janela:** `Adw.ApplicationWindow` com suporte a temas claro/escuro do sistema.
* **Navegação:** `Adw.ViewSwitcher` (Abas) localizado na `Adw.HeaderBar` (ou bottom bar em mobile).
* **Aba 1: Rascunhos (Inbox):** Ícone `edit-paste-symbolic`.
* **Aba 2: Publicados (Cloud):** Ícone `cloud-upload-symbolic`.



### 3.2. Menu Principal (Hambúrguer)

* Ações:
* `Preferências` (abre a janela de configurações).
* `Sobre` (créditos).



### 3.3. Janela de Preferências (`Adw.PreferencesWindow`)

Deve conter uma página "Geral" com um grupo "Integração Pastebin":

1. **API Developer Key:**
* Widget: `Adw.PasswordEntryRow`.
* Ação: Vinculado via GSettings (chave `api-dev-key`).
* Descrição: "Chave obrigatória para publicar textos".


2. **Privacidade Padrão:**
* Widget: `Adw.ComboRow`.
* Opções: Público, Não Listado (Unlisted), Privado.
* Ação: Vinculado via GSettings (chave `default-privacy`).



### 3.4. Lista de Itens (Cards)

Os textos devem ser exibidos em um `Gtk.ListBox` com estilo `boxed-list`. Cada linha (`Adw.ActionRow` ou custom widget) deve conter:

* **Preview:** As primeiras 2 linhas do texto.
* **Metadados:**
* Aba 1: "Expira em X horas".
* Aba 2: Link do Pastebin (clicável/copiável).


* **Botões de Ação (Sufixo):**
* *Copiar:* Copia conteúdo para o clipboard.
* *Publicar (Só Aba 1):* Envia para API e move para Aba 2.
* *Deletar:* Remove do banco local.



## 4. Regras de Negócio e Dados

### 4.1. Schema do Banco de Dados (SQLite)

Tabela: `snippets`

```sql
CREATE TABLE snippets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_published BOOLEAN DEFAULT 0,
    pastebin_url TEXT,
    pastebin_key TEXT -- (Opcional, para deletar remotamente no futuro)
);

```

### 4.2. Lógica de Expiração (Garbage Collection)

* Ao iniciar o aplicativo E a cada 60 segundos (via `GLib.timeout_add`):
* Verificar registros onde `is_published == 0`.
* Se `(CurrentTime - created_at) >= 24 hours`: **DELETE** do banco.
* Atualizar a UI imediatamente se algo for removido.



### 4.3. Lógica de Publicação

1. Usuário clica em "Publicar".
2. App verifica se `api-dev-key` está preenchida no GSettings.
* *Se vazio:* Exibir `Adw.Toast`: "Configure a chave API nas preferências".


3. App envia POST request para `https://pastebin.com/api/api_post.php`.
4. *Sucesso:*
* Recebe URL.
* Update DB: `pastebin_url = [URL]`, `is_published = 1`.
* Item move visualmente da Aba 1 para Aba 2.


5. *Erro:* Exibir Toast com a mensagem de erro.

## 5. Integração com Sistema (Flatpak & GSettings)

### 5.1. GSettings Schema (`io.github.user.flashpaste.gschema.xml`)

```xml
<schema id="io.github.user.flashpaste" path="/io/github/user/flashpaste/">
  <key name="api-dev-key" type="s">
    <default>""</default>
    <summary>Pastebin API Developer Key</summary>
  </key>
  <key name="default-privacy" type="i">
    <default>1</default> <summary>Default privacy level for pastes</summary>
  </key>
  <key name="window-width" type="i"><default>800</default></key>
  <key name="window-height" type="i"><default>600</default></key>
</schema>

```

### 5.2. Permissões Flatpak (`finish-args`)

O manifesto deve incluir:

* `--share=network` (Para acessar Pastebin).
* `--share=ipc` (Padrão GTK).
* `--socket=fallback-x11` (Compatibilidade).
* `--socket=wayland` (Nativo).
* `--filesystem=xdg-run/dconf` (Para salvar configurações).
* `--own-name=org.gnome.*` (Para GSettings).

---

## Instruções para o Assistente de IA (Copie isto para o chat)

> **Contexto:** Você é um Engenheiro de Software Sênior especialista em desenvolvimento Linux Desktop (GNOME).
> **Tarefa:** Criar a estrutura inicial e o código funcional do aplicativo "FlashPaste" baseado rigorosamente no PRD acima.
> **Etapas de Execução:**
> 1. **Estrutura de Arquivos:** Defina a árvore de diretórios padrão Meson/Flatpak.
> 2. **Manifesto Flatpak:** Gere o arquivo `.json` com as dependências do SDK GNOME 45+.
> 3. **Schema GSettings:** Crie o XML para as configurações (API Key).
> 4. **Backend (Database):** Crie uma classe `DatabaseManager` que lida com o SQLite e a lógica de expiração de 24h.
> 5. **Frontend (GTK4/Adwaita):**
> * `main.py`: Ponto de entrada.
> * `window.py`: A `AdwApplicationWindow` contendo o `AdwViewSwitcher`.
> * `preferences.py`: A `AdwPreferencesWindow` com o binding das chaves API.
> 
> 
> 6. **Lógica de API:** Um módulo simples `pastebin_client.py` usando `requests`.
> 
> 
> **Prioridade:** O código deve ser moderno, tipado (type hints), usar `PyGObject` corretamente e estar pronto para rodar via `flatpak-builder`. Comece gerando a estrutura de arquivos e o Manifesto Flatpak.


