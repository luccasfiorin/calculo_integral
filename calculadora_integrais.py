import numpy as num
import matplotlib.pyplot as grafico
from matplotlib.widgets import Slider as BarraDeslizante
from sympy import Symbol as Simbolo, integrate as integrar, lambdify as para_numerico
from sympy.parsing.sympy_parser import (parse_expr as texto_para_expressao,
                                        standard_transformations as regras_padrao,
                                        implicit_multiplication_application as multiplicacao_implicita,
                                        convert_xor as circunflexo_vira_potencia)

REGRAS = regras_padrao + (multiplicacao_implicita, circunflexo_vira_potencia)
x = Simbolo("x")


def ler(pergunta, aceita_x):
    while True:
        try:
            expressao = texto_para_expressao(input(pergunta), transformations=REGRAS)
            if expressao.free_symbols <= ({x} if aceita_x else set()):
                return expressao
        except Exception:
            pass
        print("  [!] Entrada inválida. Exemplos: x^4 - 5x^3 + 8, sin(x), 2, pi, oo")


def avaliar(f_numerica, pontos):
    with num.errstate(all="ignore"):
        y = num.asarray(f_numerica(pontos), dtype=float) * num.ones_like(pontos)
    return num.where(num.isfinite(y), y, num.nan)


def riemann(f_numerica, a, b, n):
    dx = (b - a) / n
    centros = a + dx * (num.arange(n) + 0.5)
    alturas = num.nan_to_num(avaliar(f_numerica, centros))
    return centros, alturas, dx, float(alturas.sum() * dx)


def desenhar(f, f_numerica, a, b, valor):
    ini = float(a) if a.is_finite else (float(b) - 10 if b.is_finite else -10.0)
    fim = float(b) if b.is_finite else max(ini, 0.0) + 10
    margem = 0.2 * (fim - ini) or 1.0
    x_curva = num.linspace(ini - margem, fim + margem, 600)
    x_area = num.linspace(ini, fim, 400)
    y_area = num.nan_to_num(avaliar(f_numerica, x_area))

    janela, eixos = grafico.subplots(figsize=(9, 5.5))
    eixos.plot(x_curva, avaliar(f_numerica, x_curva), color="navy", lw=2, zorder=3, label=f"f(x) = {f}")
    for parte, cor, nome in ((y_area >= 0, "seagreen", "positiva"), (y_area < 0, "crimson", "negativa")):
        eixos.fill_between(x_area, y_area, where=parte, color=cor, alpha=0.45, interpolate=True, label=f"Área {nome}")

    baixo, cima = min(y_area.min(), 0), max(y_area.max(), 0)
    folga = 0.15 * (cima - baixo) or 1.0
    resultado = round(valor, 4) if valor is not None else "diverge"
    eixos.set(xlim=(x_curva[0], x_curva[-1]), ylim=(baixo - folga, cima + folga),
              xlabel="x", ylabel="f(x)", title=f"∫ f(x) dx de {a} a {b} = {resultado}")
    eixos.axhline(0, color="gray", lw=1)
    eixos.axvline(0, color="gray", lw=1)
    eixos.grid(alpha=0.3)
    eixos.legend(loc="best", framealpha=0.85)
    grafico.tight_layout(rect=(0, 0.08, 1, 1))

    if a.is_finite and b.is_finite:
        barra = BarraDeslizante(janela.add_axes((0.18, 0.03, 0.64, 0.035)), "Retângulos (n)",
                                1, 100, valinit=12, valstep=1, color="darkorange")

        def atualizar(n):
            for antigos in list(eixos.containers):
                antigos.remove()
            centros, alturas, dx, soma = riemann(f_numerica, float(a), float(b), int(n))
            texto = f"Riemann (n = {int(n)}): {round(soma, 4) + 0:.4f}"
            if valor is not None:
                texto += f"   erro: {abs(soma - valor):.4f}"
            eixos.bar(centros, alturas, width=dx, color="gold", alpha=0.35, edgecolor="darkorange", label=texto)
            eixos.legend(loc="best", framealpha=0.85)
            janela.canvas.draw_idle()

        atualizar(12)
        barra.on_changed(atualizar)
    grafico.show()


def calcular():
    f = ler("\nDigite a função f(x) (ex: x^2, 5x^3 + 2, sin(x)): ", aceita_x=True)
    a = ler("Limite inferior (número, pi, oo ou -oo): ", aceita_x=False)
    b = ler("Limite superior (número, pi, oo ou -oo): ", aceita_x=False)

    exata = integrar(f, (x, a, b))
    valor = float(exata) if exata.is_finite else None

    print("-" * 50)
    print(f"f(x) = {f}")
    print(f"Integral indefinida: F(x) = {integrar(f, x)} + C")
    print(f"Integral definida de {a} a {b}: {exata}",
          f"(aprox. {valor:.4f})" if valor is not None else "(diverge, não tem valor finito)")

    print("-" * 50 + "\nFeche a janela do gráfico para continuar.")
    desenhar(f, para_numerico(x, f, "numpy"), a, b, valor)


def principal():
    print("=" * 50 + "\n   CALCULADORA DE INTEGRAIS  |  Cálculo I\n" + "=" * 50)
    while True:
        calcular()
        if not input("\nCalcular outra integral? (s/n): ").strip().lower().startswith("s"):
            break
    print("Até a próxima!")


if __name__ == "__main__":
    principal()
