import re
import itertools
import unicodedata

class LogicInterpreter:
    def __init__(self):
        self.simbolos = {
            '∧': ' and ',
            '∨': ' or ',
            '~': ' not ',
            '¬': ' not ',
            '→': ' implies ',  # Lo manejaremos con una función especial
            '↔': ' == ',
            '=': ' == ',   # Para comparación
            'x': '*',      # Para multiplicación
        }
        self.expresion_original = None

    def normalizar_texto(self, texto):
        """Convierte caracteres Unicode raros a ASCII estándar y conectivos correctos."""
        self.expresion_original = texto  # Guardar la versión original

        texto = unicodedata.normalize('NFKD', texto)

        reemplazos = {
            '˄': '∧',
            '𝐯': '∨',
            '𝑣': '∨',
            'v': '∨',   # si aparece como operador
            '–': '-',   # guion largo
            '—': '-',   # guion em dash
        }
        for raro, normal in reemplazos.items():
            texto = texto.replace(raro, normal)

        # Convertir letras matemáticas a ASCII simple
        texto = ''.join(
            c if ord(c) < 128 else unicodedata.normalize('NFKD', c)[0]
            for c in texto
        )

        # Sustituir corchetes por paréntesis
        texto = texto.replace('[', '(').replace(']', ')')

        return texto

    def limpiar_expresion(self, texto):
        """Reemplaza símbolos del PDF por operadores de Python."""
        for simb, python_op in self.simbolos.items():
            texto = texto.replace(simb, python_op)
        return texto

    def resolver_implicacion(self, expresion):
        """Transforma (A implies B) en (not A or B) recursivamente."""
        while ' implies ' in expresion:
            expresion = re.sub(
                r'(\w+|\(.+?\))\s+implies\s+(\w+|\(.+?\))',
                r'(not \1 or \2)',
                expresion
            )
        return expresion

    def es_proposicion(self, texto):
        """Verifica si la expresión contiene operadores lógicos o comparaciones."""
        operadores = ['∧', '∨', '~', '¬', '→', '↔', '=', '>', '<']
        if not any(op in texto for op in operadores):
            return False
        return True

    def tabla_verdad(self, entrada, vars_detectadas):
        """Genera la tabla de verdad completa para la expresión."""
        paso1 = self.limpiar_expresion(entrada)
        paso2 = self.resolver_implicacion(paso1)

        print("\n=== TABLA DE VERDAD ===")
        header = " | ".join(vars_detectadas) + " | Resultado"
        print(header)
        print("-" * len(header))

        for combo in itertools.product([True, False], repeat=len(vars_detectadas)):
            valores = dict(zip(vars_detectadas, combo))
            try:
                resultado = eval(paso2, {"__builtins__": None}, valores)
                fila = " | ".join("V" if valores[v] else "F" for v in vars_detectadas)
                fila += " | " + ("V" if resultado else "F")
                print(fila)
            except Exception as e:
                print(f"Error en combinación {valores}: {e}")

    def ejecutar(self):
        print("--- MOTOR DE INFERENCIA LÓGICA (Unidad 1) ---")
        print("Pegue la expresión (use ∧, ∨, ~, →, ↔ o letras comunes)")
        
        entrada = input("\nPregunta/Expresión: ")

        # Normalizar automáticamente
        entrada_normalizada = self.normalizar_texto(entrada)

        # Mostrar al usuario la versión limpia
        print(f"\nExpresión original: {self.expresion_original}")
        print(f"Expresión normalizada: {entrada_normalizada}")
        confirmar = input("¿Está bien continuar con esta versión? (s/n): ").lower()
        if confirmar != 's':
            print("Expresión descartada. Intente nuevamente.")
            return

        entrada = entrada_normalizada

        if not self.es_proposicion(entrada):
            print("\nLa expresión ingresada no es una proposición evaluable.")
            return
        
        vars_detectadas = sorted(list(set(re.findall(r'\b[a-z]\b', entrada))))
        print(f"\nSe detectaron las proposiciones: {vars_detectadas}")

        modo = input("¿Generar tabla de verdad completa? (s/n): ").lower()
        if modo == 's':
            self.tabla_verdad(entrada, vars_detectadas)
            return

        valores = {}
        for v in vars_detectadas:
            val = input(f"¿Cuál es el valor de v({v})? (v/f): ").lower()
            valores[v] = True if val == 'v' else False

        paso1 = self.limpiar_expresion(entrada)
        paso2 = self.resolver_implicacion(paso1)
        
        try:
            resultado = eval(paso2, {"__builtins__": None}, valores)
            print(f"\n{'='*30}")
            print(f"ANÁLISIS DE (original): {self.expresion_original}")
            print(f"VERSIÓN PYTHON: {paso2}")
            print(f"RESULTADO FINAL: {'VERDADERO (V)' if resultado else 'FALSO (F)'}")
            print(f"{'='*30}")
        except Exception as e:
            print(f"Error al procesar: {e}")

# Iniciar el laboratorio
if __name__ == "__main__":
    lab = LogicInterpreter()
    while True:
        lab.ejecutar()
        if input("\n¿Resolver otro? (s/n): ").lower() != 's':
            break
