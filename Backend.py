from flask import Flask, request, jsonify
from flask_cors import CORS
import secrets
import string
import os
import csv

app = Flask(__name__)
CORS(app)

CSV_FILE = "senhas_seguras.csv"

# Função para gerar senha segura
def generate_secure_password(length=16):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password

# Função para salvar senha no CSV sem `pandas`
def save_password(title, password):
    file_exists = os.path.isfile(CSV_FILE)

    with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Título", "Senha"])  # Escreve o cabeçalho se o arquivo não existir
        writer.writerow([title, password])

# Rota para gerar senha e salvar no CSV
@app.route('/generate-password', methods=['POST'])
def generate_password():
    data = request.json
    title = data.get("title")

    if not title:
        return jsonify({"error": "Título é obrigatório"}), 400

    password = generate_secure_password()
    save_password(title, password)

    return jsonify({"title": title, "password": password})

# Rota para obter senhas sem `pandas`
@app.route('/get-passwords', methods=['GET'])
def get_passwords():
    if not os.path.exists(CSV_FILE):
        return jsonify([])

    passwords = []
    with open(CSV_FILE, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            passwords.append({"Título": row["Título"], "Senha": row["Senha"]})

    return jsonify(passwords)

# Rota para deletar senha sem `pandas`
@app.route('/delete-password', methods=['POST'])
def delete_password():
    data = request.json
    title_to_delete = data.get("title")

    if not os.path.exists(CSV_FILE):
        return jsonify({"error": "Arquivo não encontrado"}), 404

    new_rows = []
    deleted = False

    with open(CSV_FILE, mode="r", encoding="utf-8") as file:
        reader = csv.reader(file)
        headers = next(reader)  # Mantém o cabeçalho
        for row in reader:
            if row[0] == title_to_delete:
                deleted = True
                continue  # Pula a linha a ser deletada
            new_rows.append(row)

    if not deleted:
        return jsonify({"error": "Título não encontrado"}), 404

    # Reescreve o CSV com os dados atualizados
    with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(new_rows)

    return jsonify({"message": "Senha deletada com sucesso"}), 200

if __name__ == '__main__':
    app.run(debug=True)
