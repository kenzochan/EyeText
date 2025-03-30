import sys
import os
import pytesseract
from PIL import Image, ImageGrab
import keyboard
import pyperclip
from pynput import mouse
import tempfile
import time

class EyeText:
    def __init__(self):
        self.running = True
        self.start_pos = None
        self.current_pos = None
        self.listener = None
        self.screenshot = None
        self.last_captured_text = ""
        
        # Se necessário, configurar o caminho do Tesseract:
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        
    def start(self):
        print("Aplicativo iniciado. Pressione Ctrl+Alt+q para capturar uma área da tela.")
        keyboard.add_hotkey('ctrl+alt+shift+q', self.start_selection)
        
        try:
            while self.running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        self.running = False
        if self.listener: 
            self.listener.stop()
        print("Aplicativo encerrado.")
        sys.exit(0)
    
    def start_selection(self):
        print("Selecione uma área da tela (clique e arraste)")
        self.start_pos = None
        self.current_pos = None
        
        # Inicia o listener do mouse
        self.listener = mouse.Listener(
            on_move=self.on_move,
            on_click=self.on_click,
            on_scroll=self.on_scroll)
        self.listener.start()
    
    def on_move(self, x, y):
        if self.start_pos and not self.current_pos:
            self.current_pos = (x, y)
    
    def on_click(self, x, y, button, pressed):
        if button == mouse.Button.left:
            if pressed:
                self.start_pos = (x, y)
            else:
                self.current_pos = (x, y)
                self.capture_area()
                return False  # Para o listener
    
    def on_scroll(self, x, y, dx, dy):
        pass
    
    def capture_area(self):
        if not self.start_pos or not self.current_pos:
            return
        
        x1, y1 = self.start_pos
        x2, y2 = self.current_pos
        
        # Garante que x1,y1 é o canto superior esquerdo e x2,y2 o inferior direito
        x1, x2 = sorted([x1, x2])
        y1, y2 = sorted([y1, y2])
        
        # Captura a área da tela
        try:
            self.screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
            
            # Salva temporariamente para debug (opcional)
            temp_path = os.path.join(tempfile.gettempdir(), 'eyetext.png')
            self.screenshot.save(temp_path)
            print(f"Captura salva temporariamente em: {temp_path}")
            
            # Processa a imagem com OCR
            self.process_image()
            
        except Exception as e:
            print(f"Erro ao capturar a tela: {e}")
    
    def process_image(self):
        if not self.screenshot:
            return
        
        try:
            # Converte a imagem para texto usando OCR
            text = pytesseract.image_to_string(self.screenshot)
            
            if text.strip():
                self.last_captured_text = text
                pyperclip.copy(text)  # Copia para área de transferência
                print("Texto extraído e copiado para a área de transferência:")
                print("-----")
                print(text)
                print("-----")
                print("Você pode agora colar o texto (Ctrl+V)")
            else:
                print("Nenhum texto foi detectado na área selecionada.")
                
        except Exception as e:
            print(f"Erro ao processar a imagem: {e}")

if __name__ == "__main__":
    app = EyeText()
    try:
        app.start()
    except Exception as e:
        print(f"Erro: {e}")
        app.stop()