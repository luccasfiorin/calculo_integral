# Calculadora de Integrais

Programa em Python para a disciplina de Cálculo I. Calcula integrais indefinidas e definidas (inclusive com limites infinitos) e mostra o gráfico da função com a área da integral e os retângulos da Soma de Riemann, controlados por uma barra deslizante.

## Requisitos

- Python 3
- Bibliotecas: `sympy`, `numpy` e `matplotlib`

```
pip install sympy numpy matplotlib
```

## Como usar

```
python calculadora_integrais.py
```

O programa pede a função e os limites de integração. Exemplos de entrada:

| Função | Limite inferior | Limite superior | Resultado |
|---|---|---|---|
| `x^2` | `0` | `3` | 9 |
| `x^3 - x` | `-2` | `2` | 0 |
| `exp(-x)` | `0` | `oo` | 1 |

Use `oo` para infinito e `pi` para π. Multiplicação implícita (`5x`) e potência com `^` são aceitas.
