# Frame Catcher 🎬

Um aplicativo de desktop simples e eficiente para extrair frames de vídeos com precisão.

![Screenshot da Aplicação](https://drive.google.com/file/d/1yfbejOZK1rVkQIwvJpr06fgWY0FUaEEn/view?usp=sharing) 
## ✨ Funcionalidades

* **Extração por Intervalo Fixo:** Capture um frame a cada `X` segundos.
* **Extração por Tempos Específicos:** Adicione uma lista de timestamps exatos (HH:MM:SS) para extrair frames específicos.
* **Controle de Trecho:** Defina um tempo de início e fim para a extração por intervalo, processando apenas a parte desejada do vídeo.
* **Interrupção de Processo:** Cancele uma extração em andamento a qualquer momento com o botão "Parar".
* **Pré-visualização:** Veja uma miniatura (thumbnail) do vídeo selecionado.
* **Interface Intuitiva:** Interface moderna e fácil de usar, construída com CustomTkinter.

## 🚀 Como Usar

### Para Usuários
1.  Vá para a [página de Releases](https://github.com/guilhermerm99/FrameCatcherApp).
2.  Baixe o arquivo `.zip` da versão mais recente (ex: `FrameCatcher_v1.0.0.zip`).
3.  Extraia o arquivo e execute o `FrameCatcher.exe`.

### Para Desenvolvedores
1.  Clone este repositório: `git clone https://github.com/guilhermerm99/FrameCatcherApp`
2.  Crie e ative um ambiente virtual: `python -m venv venv` e `.\venv\Scripts\activate`
3.  Instale as dependências: `pip install -r requirements.txt`
4.  Execute a aplicação: `python main.py`

## 🛠️ Tecnologias Utilizadas

* **Python 3**
* **CustomTkinter:** Para a criação da interface gráfica.
* **OpenCV-Python:** Para o processamento e extração de frames de vídeo.
* **Pillow (PIL):** Para manipulação de imagens (thumbnails).
* **PyInstaller:** Para a criação do executável.

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.