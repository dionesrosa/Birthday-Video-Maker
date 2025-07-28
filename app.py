import json
import shutil
import subprocess
import sys
import os
import re
from tqdm import tqdm
from tkinter import Tk, filedialog
from PIL import Image

# --- Configurações e caminhos globais ---
base_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(base_dir, "dados", "info.json")
avatar_path = os.path.join(base_dir, "dados", "avatar.jpg")
aerender_path = r"C:\Program Files\Adobe\Adobe After Effects 2020\Support Files\aerender.exe"
aep_template_path = os.path.join(base_dir, "BirthdayVideoTemplate.aep")
output_video_path = os.path.join(base_dir, "final", "BirthdayVideoFinal.mp4")
output_video_path_temp = output_video_path.replace(".mp4", ".mov")
output_log = os.path.join(base_dir, "final", "log.txt")

# --- Utilitários ---
def is_ffmpeg_installed():
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except FileNotFoundError:
        print("Erro: FFmpeg não está instalado ou não está no PATH.")
        return False

def decode_text(encoded_text):
    try:
        return encoded_text.encode('latin1').decode('utf-8')
    except UnicodeDecodeError:
        return "Erro ao decodificar o texto. Verifique a codificação."

def remove_old_files():
    for arquivo in [output_video_path, output_video_path_temp]:
        if os.path.exists(arquivo):
            try:
                os.remove(arquivo)
                print(f"Arquivo antigo removido: {arquivo}")
            except Exception as e:
                print(f"Não foi possível remover {arquivo}: {e}")

# --- Manipulação de dados ---
def update_info_json(info):
    try:
        new_data = {
            "nome": info.get("nome", "") if isinstance(info, dict) else getattr(info, "nome", ""),
            "funcao": info.get("funcao", "") if isinstance(info, dict) else getattr(info, "funcao", "")
        }
        with open(json_path, 'w') as f:
            json.dump(new_data, f, indent=4)
        print(f"Arquivo info.json atualizado com o nome: {new_data['nome']}")
    except Exception as e:
        print(f"Erro ao atualizar info.json: {e}")

def update_avatar_image(nova_imagem):
    shutil.copy(nova_imagem, avatar_path)
    print(f"Imagem do avatar atualizada com: {nova_imagem}")

# --- Processamento de vídeo ---
def render_video_with_progress():
    process = None
    try:
        command = [
            aerender_path,
            "-comp", "PRINCIPAL",
            "-project", aep_template_path,
            "-output", output_video_path_temp
        ]
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="cp850"
        )
        total_frames = None
        pbar = None
        frame_rate = None
        duration_str = None

        for line in process.stdout:
            if duration_str is None:
                match = re.search(r'Duração:\s*(\d+):(\d+):(\d+):(\d+)', line)
                if match:
                    h, m, s, f = map(int, match.groups())
                    duration_str = (h, m, s, f)
            if frame_rate is None:
                match = re.search(r'Taxa de quadros:\s*([\d,\.]+)', line)
                if match:
                    frame_rate = float(match.group(1).replace(',', '.'))
            if total_frames is None and duration_str and frame_rate:
                h, m, s, f = duration_str
                total_frames = int(round(((h * 3600 + m * 60 + s) * frame_rate) + f))
                pbar = tqdm(
                    total=total_frames,
                    desc="Renderizando",
                    unit="frame",
                    ncols=80,
                    dynamic_ncols=True,
                    bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]"
                )
            match = re.search(r'\((\d+)\):', line)
            if match and pbar:
                current_frame = int(match.group(1))
                pbar.n = current_frame
                pbar.last_print_n = current_frame
                pbar.update(0)
        process.wait()
        if pbar:
            pbar.n = pbar.total
            pbar.update(0)
            pbar.close()
        if process.returncode == 0:
            print(f"\nVídeo renderizado e salvo em: {output_video_path_temp}")
        else:
            print(f"\nErro ao renderizar o vídeo. Código de saída: {process.returncode}")
    except KeyboardInterrupt:
        print("\nRenderização interrompida pelo usuário.")
        if process:
            process.terminate()
            process.wait()
        if pbar:
            pbar.close()
        raise
    except Exception as e:
        print(f"Erro na execução do aerender.exe: {e}")

def convert_to_mp4_with_progress(input_video, output_video):
    try:
        command = [
            "ffmpeg",
            "-i", input_video,
            "-vcodec", "libx264",
            "-crf", "23",
            "-preset", "slow",
            "-acodec", "aac",
            "-b:a", "128k",
            output_video
        ]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        duration = None
        pbar = None
        for line in process.stdout:
            if duration is None:
                match = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", line)
                if match:
                    duration = (
                        int(match.group(1)) * 3600 +
                        int(match.group(2)) * 60 +
                        float(match.group(3))
                    )
                    pbar = tqdm(
                        total=int(duration),
                        desc="Convertendo para MP4",
                        unit="segundos",
                        ncols=80,
                        dynamic_ncols=True,
                        bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]"
                    )
            if duration:
                match = re.search(r"time=(\d+):(\d+):(\d+\.\d+)", line)
                if match and pbar:
                    elapsed = (
                        int(match.group(1)) * 3600 +
                        int(match.group(2)) * 60 +
                        float(match.group(3))
                    )
                    pbar.n = int(elapsed)
                    pbar.last_print_n = int(elapsed)
                    pbar.update(0)
        process.wait()
        if pbar:
            pbar.n = pbar.total
            pbar.update(0)
            pbar.close()
        if process.returncode == 0:
            print(f"\nVídeo convertido para MP4: {output_video}")
        else:
            print(f"\nErro na conversão. Código de saída: {process.returncode}")
    except Exception as e:
        print(f"Erro ao converter para MP4: {e}")

# --- Interface e entrada de dados ---
def coletar_dados_usuario():
    nome = input("Digite o nome: ")
    funcao = input("Digite a função: ")
    root = Tk()
    root.withdraw()
    root.lift()
    root.attributes('-topmost', True)
    root.after_idle(root.attributes, '-topmost', False)
    imagem = filedialog.askopenfilename(
        title="Selecione a imagem do avatar",
        filetypes=[("Imagens", "*.jpg *.jpeg *.png *.bmp *.gif")]
    )
    root.destroy()
    if not imagem:
        print("Nenhuma imagem selecionada. Encerrando o programa.")
        sys.exit(1)
    imagens_dir = os.path.join(base_dir, "imagens")
    os.makedirs(imagens_dir, exist_ok=True)
    nome_arquivo = f"{nome.lower()}_avatar.jpg"
    destino = os.path.join(imagens_dir, nome_arquivo)
    try:
        with Image.open(imagem) as img:
            min_side = min(img.width, img.height)
            left = (img.width - min_side) // 2
            top = (img.height - min_side) // 2
            right = left + min_side
            bottom = top + min_side
            img_cropped = img.crop((left, top, right, bottom))
            img_resized = img_cropped.resize((800, 800), Image.LANCZOS)
            rgb_img = img_resized.convert("RGB")
            rgb_img.save(destino, "JPEG")
        print(f"Imagem convertida, recortada e salva em: {destino}")
        imagem = destino
    except Exception as e:
        print(f"Erro ao converter/salvar a imagem: {e}")
        sys.exit(1)
    return {"nome": nome, "funcao": funcao, "imagem": imagem}

# --- Função principal ---
def gerar_video_aniversario(dados):
    remove_old_files()
    if not os.path.exists(aep_template_path):
        print("Erro: O arquivo do projeto After Effects (.aep) não foi encontrado.")
        return
    if not os.path.exists(dados["imagem"]):
        print("Erro: A imagem do avatar não foi encontrada.")
        return
    try:
        update_info_json(dados)
        update_avatar_image(dados["imagem"])
        render_video_with_progress()
        if os.path.exists(output_video_path_temp):
            convert_to_mp4_with_progress(output_video_path_temp, output_video_path)
        else:
            print("A renderização falhou ou o arquivo de saída não foi encontrado. Conversão não será executada.")
    except KeyboardInterrupt:
        print("\nProcesso interrompido pelo usuário. Nada será convertido.")
    except Exception as e:
        print(f"Erro no processo de geração de vídeo: {e}")

def main():
    dados = coletar_dados_usuario()
    gerar_video_aniversario(dados)

if __name__ == '__main__':
    main()