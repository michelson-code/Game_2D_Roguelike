# 🛸 Space Roguelike 2D

Este projeto é um jogo de exploração espacial com elementos de Roguelike, desenvolvido em Python utilizando a biblioteca **Pygame Zero**.  
O jogador assume o papel de um herói que deve navegar por um mapa gerado aleatoriamente, enfrentando diferentes tipos de alienígenas e coletando moedas para aumentar sua pontuação.

---

## 📖 Sobre o Jogo

Em **Space Roguelike**, cada partida oferece um novo desafio devido à geração procedural de obstáculos.  
O objetivo principal é a sobrevivência e a limpeza completa do setor espacial (o mapa), eliminando todos os inimigos presentes.

### Principais Características

- **Geração Procedural**: O mapa cria paredes e caminhos aleatórios a cada início de jogo, garantindo que nenhuma partida seja igual à outra.  
- **Variedade de Inimigos**: Existem três tipos distintos de alienígenas (Alien comum, Alien feio e Polvo espacial) que possuem comportamentos de perseguição ao jogador.  
- **Sistema de Combate**: O herói é equipado com uma arma de laser azul capaz de disparar em quatro direções.  
- **Economia de Jogo**: Moedas espalhadas pelo mapa incentivam a exploração e aumentam o score final.  
- **Gestão de Vida**: O jogador possui uma barra de HP; o contato com aliens causa dano, e chegar a zero resulta em *Game Over*.

---

## 🎮 Como Jogar

O objetivo é coletar o máximo de moedas possível e matar todos os aliens para vencer.

### Comandos do Teclado

| Ação             | Teclas                             |
| ---------------- | ---------------------------------- |
| Movimentação     | Setas Direcionais (↑, ↓, ←, →)     |
| Atirar (Laser)   | Teclas **W, A, S, D**              |

---

## 🛠️ Tecnologias Utilizadas

- **Python 3.x**: Linguagem base do projeto.  
- **Pygame Zero**: Framework para facilitar a criação de jogos.  
- **Módulos Nativos**: `random` para geração do mapa e `math` para cálculos de distância.

---

## 📂 Estrutura do Repositório

- `game_pg_zero.py`: Núcleo do código, contendo a lógica de estados (Menu, Jogando, Vitória, Game Over) e classes do herói e inimigos.  
- `images/`: Contém todos os sprites do jogo (Hero, Alien, Alien3, Alien_ugly, Laser, Coin).  
- `sounds/`: Arquivos de áudio para música de fundo e efeitos sonoros de tiro e impacto.

---

## 🔧 Instalação e Execução

### Pré-requisitos

Certifique-se de ter o Python instalado.  
Recomenda-se a instalação da biblioteca **pgzero**:

```
pip install pgzero
```

### Executando o Jogo

Navegue até a pasta do projeto e execute o seguinte comando no terminal:

```
pgzrun game_pg_zero.py
```

---

## 📝 Créditos e Licença

- **Desenvolvedor**: Bruno Dantas  
- **Repositório**: [michelson-code/Game_2D_Roguelike](https://github.com/michelson-code/Game_2D_Roguelike)
