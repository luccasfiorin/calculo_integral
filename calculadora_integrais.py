import numpy as num
import matplotlib.pyplot as grafico
from matplotlib.widgets import Slider as BarraDeslizante
from sympy import Symbol as Simbolo, integrate as integrar, lambdify as para_numerico
from sympy.parsing.sympy_parser import (parse_expr as texto_para_expressao,
                                        standard_transformations as regras_padrao,
                                        implicit_multiplication_application as multiplicacao_implicita,
                                        convert_xor as circunflexo_vira_potencia)

# Regras de leitura: as padrão + entender "5x" como 5*x e "x^2" como potência
REGRAS = regras_padrao + (multiplicacao_implicita, circunflexo_vira_potencia)
x = Simbolo("x")  


def ler(pergunta, aceita_x):
    while True:  
        try:
            # Converte o texto digitado em expressão matemática ("pi" vira π, "oo" vira ∞)
            expressao = texto_para_expressao(input(pergunta), transformations=REGRAS)
            # Aceita só se usar letras permitidas: x na função, nenhuma nos limites
            if expressao.free_symbols <= ({x} if aceita_x else set()):
                return expressao
        except Exception: 
            pass
        print("  [!] Entrada inválida. Exemplos: x^4 - 5x^3 + 8, sin(x), 2, pi, oo")


def avaliar(f_numerica, pontos):
    with num.errstate(all="ignore"):  # Silencia avisos do numpy (ex: divisão por zero)
        # Calcula f em todos os pontos; "* ones_like" vira lista mesmo se f for constante
        y = num.asarray(f_numerica(pontos), dtype=float) * num.ones_like(pontos)
    return num.where(num.isfinite(y), y, num.nan)  # Infinito/erro vira nan (não desenha)


def riemann(f_numerica, a, b, n):
    dx = (b - a) / n  # Largura de cada retângulo
    centros = a + dx * (num.arange(n) + 0.5)  # Ponto médio de cada pedaço
    alturas = num.nan_to_num(avaliar(f_numerica, centros))  # Altura = f(centro); nan vira 0
    return centros, alturas, dx, float(alturas.sum() * dx)  # Soma das áreas = soma das alturas × dx


def desenhar(f, f_numerica, a, b, valor):
    # Se algum limite for infinito, desenha só um trecho de tamanho 10
    ini = float(a) if a.is_finite else (float(b) - 10 if b.is_finite else -10.0)
    fim = float(b) if b.is_finite else max(ini, 0.0) + 10
    margem = 0.2 * (fim - ini) or 1.0  # 20% de espaço extra dos lados (1.0 se der zero)
    x_curva = num.linspace(ini - margem, fim + margem, 600)  # 600 pontos para a curva
    x_area = num.linspace(ini, fim, 400)  # 400 pontos dentro dos limites
    y_area = num.nan_to_num(avaliar(f_numerica, x_area))

    janela, eixos = grafico.subplots(figsize=(9, 5.5))  # Cria a janela e a área de desenho
    eixos.plot(x_curva, avaliar(f_numerica, x_curva), color="navy", lw=2, zorder=3, label=f"f(x) = {f}")
    # Pinta a área: verde acima do eixo x (soma), vermelho abaixo (subtrai)
    for parte, cor, nome in ((y_area >= 0, "seagreen", "positiva"), (y_area < 0, "crimson", "negativa")):
        eixos.fill_between(x_area, y_area, where=parte, color=cor, alpha=0.45, interpolate=True, label=f"Área {nome}")

    baixo, cima = min(y_area.min(), 0), max(y_area.max(), 0)  # Faixa vertical, sempre incluindo o 0
    folga = 0.15 * (cima - baixo) or 1.0
    resultado = round(valor, 4) if valor is not None else "diverge"
    # Trava os limites dos eixos (evita escala gigante em casos como 1/x) e define os textos
    eixos.set(xlim=(x_curva[0], x_curva[-1]), ylim=(baixo - folga, cima + folga),
              xlabel="x", ylabel="f(x)", title=f"∫ f(x) dx de {a} a {b} = {resultado}")
    eixos.axhline(0, color="gray", lw=1)  # Eixo x
    eixos.axvline(0, color="gray", lw=1)  # Eixo y
    eixos.grid(alpha=0.3)
    eixos.legend(loc="best", framealpha=0.85)
    grafico.tight_layout(rect=(0, 0.08, 1, 1))  # Ajusta margens e reserva espaço embaixo para a barra

    if a.is_finite and b.is_finite:  # Retângulos só em intervalo finito
        # Barra de 1 a 100 retângulos, começando em 12; os números em add_axes são posição e tamanho
        barra = BarraDeslizante(janela.add_axes((0.18, 0.03, 0.64, 0.035)), "Retângulos (n)",
                                1, 100, valinit=12, valstep=1, color="darkorange")

        def atualizar(n):  # Roda toda vez que a barra é mexida
            for antigos in list(eixos.containers):  # Apaga os retângulos anteriores
                antigos.remove()
            centros, alturas, dx, soma = riemann(f_numerica, float(a), float(b), int(n))
            texto = f"Riemann (n = {int(n)}): {round(soma, 4) + 0:.4f}"  # "+ 0" evita mostrar -0.0000
            if valor is not None:
                texto += f"   erro: {abs(soma - valor):.4f}"  # Diferença para o valor exato
            eixos.bar(centros, alturas, width=dx, color="gold", alpha=0.35, edgecolor="darkorange", label=texto)
            eixos.legend(loc="best", framealpha=0.85)
            janela.canvas.draw_idle()  # Redesenha a janela

        atualizar(12)  # Desenha os retângulos iniciais
        barra.on_changed(atualizar)  # Liga a barra à função atualizar
    grafico.show()  # Abre o gráfico


def calcular():
    f = ler("\nDigite a função f(x) (ex: x^2, 5x^3 + 2, sin(x)): ", aceita_x=True)
    a = ler("Limite inferior (número, pi, oo ou -oo): ", aceita_x=False)
    b = ler("Limite superior (número, pi, oo ou -oo): ", aceita_x=False)

    exata = integrar(f, (x, a, b))  # Integral definida exata: F(b) - F(a)
    valor = float(exata) if exata.is_finite else None  # Valor decimal, ou None se divergir

    print("-" * 50)
    print(f"f(x) = {f}")
    print(f"Integral indefinida: F(x) = {integrar(f, x)} + C")  # Sem limites = primitiva
    print(f"Integral definida de {a} a {b}: {exata}",
          f"(aprox. {valor:.4f})" if valor is not None else "(diverge, não tem valor finito)")

    print("-" * 50 + "\nFeche a janela do gráfico para continuar.")
    desenhar(f, para_numerico(x, f, "numpy"), a, b, valor)  # Versão rápida (numpy) de f para o gráfico


def principal():
    print("=" * 50 + "\n   CALCULADORA DE INTEGRAIS  |  Cálculo I\n" + "=" * 50)
    while True:
        calcular()
        if not input("\nCalcular outra integral? (s/n): ").strip().lower().startswith("s"):
            break
    print("Até a próxima!")


if __name__ == "__main__":  
    principal()
