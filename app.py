import io
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
from flask import Flask, render_template, request, Response
from markupsafe import Markup

app = Flask(__name__)

x = sp.Symbol('x')

funcion_str_global = None
a_global = None
b_global = None

def esImpar(funcion):
    return sp.simplify(funcion.subs(x, -x)) == -funcion

def integrar_definida(funcion, a, b):
    if esImpar(funcion):
        integral_definida = sp.integrate(sp.Abs(funcion), (x, a, b)).evalf()
    else:
        integral_definida = sp.integrate(funcion, (x, a, b)).evalf()

    funcion_numerica = sp.lambdify(x, funcion, "numpy")

    #Rango de valores
    x_vals = np.linspace(float(a), float(b), 400)
    y_vals = funcion_numerica(x_vals)

    #Graficar
    fig, ax = plt.subplots()
    ax.plot(x_vals, y_vals, label=f'y = {funcion}')
    ax.fill_between(x_vals, y_vals, where=[(x >= a and x <= b) for x in x_vals], alpha=0.3, color='green', label=f'Área = {integral_definida}')
    ax.set_title(f'Integral y gráfica de la función {funcion}')
    ax.set_xlabel('x')
    ax.set_ylabel('f(x)')
    ax.axhline(0, color='black', linewidth=0.5)
    ax.axvline(0, color='black', linewidth=0.5)
    ax.legend()

    img = io.BytesIO()
    fig.savefig(img, format='png')
    img.seek(0)

    #Retornar imagen
    return img

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/plot', methods=['POST'])
def plot_post():
    global funcion_str_global, a_global, b_global
    funcion_str_global = request.form['funcion']
    tipo_integral = request.form['tipo_integral']

    try:
        funcion = sp.sympify(funcion_str_global)
    except sp.SympifyError:
        return "Error: Función no válida."

    if tipo_integral == 'definida':
        try:
            a_global = float(request.form['a'])
            b_global = float(request.form['b'])
        except ValueError:
            return "Error: Límite inferior o superior no válido."

        return "success"
    
    elif tipo_integral == 'indefinida':
        integral_indefinida = sp.integrate(funcion, x)
        
        #Representar la función y la integral con su formato
        funcion_latex = sp.latex(funcion)
        integral_latex = sp.latex(integral_indefinida)
        
        #integral indefinida
        result_html = f"<h3>Integral indefinida: \\(\\int {funcion_latex} \\, dx = {integral_latex} + C\\)</h3>"
        
        #Permitir LaTeX en el HTML
        return Markup(result_html)

# Ruta para devolver la imagen de la gráfica
@app.route('/plot.png')
def plot_png():
    if funcion_str_global and a_global is not None and b_global is not None:
        # Simbolizar la función
        funcion = sp.sympify(funcion_str_global)

        # Generar la gráfica
        img = integrar_definida(funcion, a_global, b_global)
        
        # Devolver la imagen como respuesta
        return Response(img.getvalue(), mimetype='image/png')
    else:
        return "Error: No se ha proporcionado una función o límites válidos.", 400


if __name__ == '__main__':
    app.run(debug=True)
