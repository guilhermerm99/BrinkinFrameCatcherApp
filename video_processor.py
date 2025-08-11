# video_processor.py
import cv2
import os
from utils import format_time

def extract_frames(video_path, output_dir, mode, options, progress_callback, stop_event):
    """
    Extrai frames de um vídeo de forma desacoplada da UI.
    """
    cap = None
    frames_saved = 0
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError("Não foi possível abrir o arquivo de vídeo.")

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps == 0:
            raise ValueError("FPS do vídeo é zero, impossível calcular os tempos.")

        if mode == "Intervalo":
            interval = options.get('interval', 1)
            # Pega os tempos. Se a chave não existir, o padrão é None.
            start_time_s = options.get('start_time_s')
            end_time_s = options.get('end_time_s')

            if interval <= 0:
                raise ValueError("O intervalo deve ser um número positivo.")

            # Lógica corrigida para início e fim opcionais
            start_frame = int(start_time_s * fps) if start_time_s is not None else 0
            end_frame = int(end_time_s * fps) if end_time_s is not None else total_frames
            
            if start_frame >= total_frames:
                raise ValueError("O tempo de início é maior que a duração do vídeo.")
            if end_frame > total_frames:
                end_frame = total_frames
            
            cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
            
            frame_interval = int(interval * fps)
            if frame_interval == 0: frame_interval = 1
            
            total_extraction_frames = end_frame - start_frame
            if total_extraction_frames <= 0:
                 raise ValueError("O tempo de fim deve ser maior que o tempo de início.")

            for frame_num in range(start_frame, end_frame, frame_interval):
                if stop_event.is_set():
                    return {"status": "stopped", "frames_saved": frames_saved}

                # Usar cap.read() é mais confiável em um loop do que múltiplos cap.set()
                ret, frame = cap.read()
                if not ret: break
                
                # A posição real do frame pode ser obtida com CAP_PROP_POS_FRAMES
                current_frame_pos = int(cap.get(cv2.CAP_PROP_POS_FRAMES)) - 1
                timestamp_s = current_frame_pos / fps

                filename = f"frame_{format_time(timestamp_s)}.jpg"
                cv2.imwrite(os.path.join(output_dir, filename), frame)
                frames_saved += 1
                
                progress = (current_frame_pos - start_frame) / total_extraction_frames
                status_text = f"Processando: {format_time(timestamp_s).replace('-',':')}"
                progress_callback(progress, status_text)
                
                # Pular para o próximo frame de interesse
                if frame_interval > 1:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame_pos + frame_interval)

        elif mode == "Especifico":
            # (A lógica para este modo permanece a mesma)
            targets = sorted(options.get('times', []))
            if not targets:
                raise ValueError("Nenhum tempo específico foi adicionado.")

            for i, target_s in enumerate(targets):
                if stop_event.is_set():
                    return {"status": "stopped", "frames_saved": frames_saved}
                # ... (resto do código igual)
                frame_num = int(target_s * fps)
                if frame_num >= total_frames: continue
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
                ret, frame = cap.read()
                if not ret: continue
                filename = f"extraido_{format_time(target_s)}.jpg"
                cv2.imwrite(os.path.join(output_dir, filename), frame)
                frames_saved += 1
                progress = (i + 1) / len(targets)
                status_text = f"Capturado frame em {format_time(target_s).replace('-',':')}"
                progress_callback(progress, status_text)
        
        return {"status": "success", "frames_saved": frames_saved}

    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        if cap:
            cap.release()