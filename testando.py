import cv2
import pytesseract
import re
import numpy
from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def home():
    return '''
        <html>
<head>
	<title>Extrair informações de imagem</title>
	<style type="text/css">
    
        h1{
        text-align: center;
        }

		body {
  background-color: #eee;
}

form {
  margin: 50px auto;
  width: 50%;
  background-color: #fff;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0px 5px 10px rgba(0, 0, 0, 0.3);
  animation: form-anim 1s ease-in-out forwards;
}

@keyframes form-anim {
  0% {
    opacity: 0;
    transform: translateY(-50px);
  }
  100% {
    opacity: 1;
    transform: translateY(0px);
  }
}

input[type="file"] {
  padding: 10px;
  border-radius: 5px;
  border: 2px dashed #aaa;
  font-size: 1.2em;
  margin-bottom: 20px;
  width: 100%;
}

input[type="submit"] {
  background-color: #4CAF50;
  border: none;
  color: white;
  padding: 10px 20px;
  text-align: center;
  text-decoration: none;
  display: inline-block;
  font-size: 1.2em;
  margin-top: 20px;
  border-radius: 5px;
  cursor: pointer;
  transition: all 0.3s ease-in-out;
}

input[type="submit"]:hover {
  background-color: #3e8e41;
}


	</style>
</head>
<body>
	<h1>Extrair informações de imagem</h1>
	<form method="POST" enctype="multipart/form-data">
		<input type="file" name="imagem">
		<input type="submit" value="Enviar">
	</form>
</body>
</html>
    '''

@app.route('/', methods=['POST'])
def upload_imagem():
    imagem = request.files['imagem']
    img = cv2.imdecode(numpy.fromstring(imagem.read(), numpy.uint8), cv2.IMREAD_UNCHANGED)

    config = r'--oem 3 --psm 6'

    resultado = pytesseract.image_to_string(img, config=config)

    # Divida o texto extraído em uma lista de linhas
    linhas = resultado.split("\n")

    nome = ""
    rg = ""
    cpf = ""
    dn = ""

    texto_desejado = "NOME: "
    for i in range(len(linhas)):
        if "NOME" in linhas[i]:
            if i + 1 < len(linhas):
                nome += linhas[i + 1]

        elif "DOC. IDENTIDADE" in linhas[i]:
            if i + 1 < len(linhas):
                rg += linhas[i + 1]

        elif "CPF" in linhas[i]:
            if i + 1 < len(linhas):
                cpf += linhas[i + 1]

                cpf_regex = r'\d{3}\.\d{3}\.\d{3}-\d{2}'
                cpf_match = re.search(cpf_regex, cpf)

                dn_regex = r'\d{2}/\d{2}/\d{4}'
                dn_match = re.search(dn_regex, cpf)

                if dn_match:
                    dn = dn_match.group()

            if cpf_match:
                cpf += cpf_match.group()

    with open('resultado.txt', 'w') as f:
        f.write(f"NOME: {nome}\n")
        f.write(f"RG: {rg}\n")
        f.write(f"CPF: {cpf_match.group()}\n")
        f.write(f"DATA DE NASCIMENTO: {dn}\n")

    return f'<h1>Upload bem sucedido!</h1><p>Resultados salvos em resultado.txt</p>'

if __name__ == '__main__':
    app.run()
