from flask import Flask, render_template, request

# Vòng lặp Feistel
def feistel_round(left, right, key): # lặp từng cặp của khối với từng khóa
    new_right = left ^ (right ^ key)
    return right, new_right
# Mã hóa Feistel
def feistel_encrypt(plaintext, keys): # Mã hóa khối với từng khóa
    left, right = plaintext
    for key in keys:
        left, right = feistel_round(left, right, key)
    return left, right
# Giải mã Feistel
def feistel_decrypt(ciphertext, keys): # Giải mã khối với từng khóa
    left, right = ciphertext
    for key in reversed(keys): # Đảo ngược keys 
        right, left = feistel_round(right, left, key)  # Đảo ngược left và right
    return left, right
# Chuyển đổi văn bản thành khối
def text_to_blocks(text):
    text = text.ljust(len(text) + len(text) % 2, '\0') # Nếu độ dài văn bản là số lẻ thì thêm ký tự NULL vào cuối
    return [(ord(text[i]), ord(text[i+1])) for i in range(0, len(text), 2)] # Dùng hàm ord() để chuyển ký tự thành mã ASCII
# Chuyển đổi khối thành văn bản
def blocks_to_text(blocks):
    return ''.join(chr(left) + chr(right) for left, right in blocks).rstrip('\0') # Dùng hàm chr() để chuyển mã ASCII thành ký tự và dùng dàm rstrip() để loại bỏ ký tự NULL

app = Flask(__name__) # Khởi tạo ứng dụng Flask
keys = [42, 23, 56, 78]  # sử dụng khóa mặc định cho Feistel

@app.route('/', methods=['GET', 'POST'])
def index():
    encrypted_text = decrypted_text = ""
    if request.method == 'POST':
        text = request.form['text'] # Lấy văn bản từ form
        action = request.form['action'] # Lấy hành động từ form(encrypt hoặc decrypt)
        blocks = text_to_blocks(text) # Chuyển văn bản thành khối
        
        if action == 'encrypt':
            encrypted_blocks = [feistel_encrypt(block, keys) for block in blocks] # Mã hóa từng khối
            encrypted_text = ' '.join(f"({left},{right})" for left, right in encrypted_blocks) # Chuyển khối đã mã hóa thành văn bản
        elif action == 'decrypt':
            try:
                encrypted_pairs = [tuple(map(int, pair.strip('()').split(','))) for pair in text.split()] # Chuyển văn bản đã mã hóa thành khối
                decrypted_blocks = [feistel_decrypt(block, keys) for block in encrypted_pairs] # Giải mã từng khối
                decrypted_text = blocks_to_text(decrypted_blocks) # Chuyển khối đã giải mã thành văn bản
            except Exception as e:
                decrypted_text = "Error in decryption: " + str(e) # Xuất lỗi nếu gặp lỗi
        
    return render_template('index.html', encrypted_text=encrypted_text, decrypted_text=decrypted_text) # Trả về trang web

if __name__ == '__main__':
    app.run(debug=True)
