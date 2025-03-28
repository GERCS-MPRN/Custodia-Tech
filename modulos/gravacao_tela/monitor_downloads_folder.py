import os
import shutil
import time
import zipfile
from pathlib import Path

from utils.metadata import calculate_hash, get_file_metadata
from utils.renomear_zip import renomear_zip


def monitor_downloads_folder(case_directory, videos_data):

    downloads_folder = str(Path.home() / "Downloads")
    print(f"Monitorando a pasta de Downloads: {downloads_folder}")

    while True:
        # Lista todos os arquivos na pasta de Downloads
        for file_name in os.listdir(downloads_folder):
            # Verifica se o arquivo começa com 'Gravação_'
            if file_name.startswith("CustodiaTech_Gravação_"):
                source_path = os.path.join(downloads_folder, file_name)
                dest_path = os.path.join(case_directory, file_name)

                # Verifica se o arquivo não é temporário (.tmp) e se não existe no destino
                if file_name.endswith(".webm") and os.path.isfile(source_path):
                    if not os.path.exists(dest_path):  # Verifica se o arquivo já existe
                        try:
                            # Tenta mover o arquivo
                            shutil.move(source_path, dest_path)
                            print(f"Arquivo movido: {file_name}")

                            # Create a zip file
                            zip_file_path = os.path.join(
                                case_directory, f"{file_name}.zip"
                            )
                            with zipfile.ZipFile(zip_file_path, "w") as zip_file:
                                zip_file.write(dest_path, file_name)
                            print(f"Arquivo compactado em {zip_file_path}")
                            # Obter metadados
                            hashes = calculate_hash(
                                zip_file_path, ["md5", "sha1", "sha256"]
                            )
                            metadata = get_file_metadata(zip_file_path)

                            metadata, nome_final_zip = renomear_zip(
                                zip_file_path, metadata, "CustodiaTech_Gravação_"
                            )

                            videos_data.append(
                                {
                                    "Caminho do Arquivo": nome_final_zip,
                                    "Metadados": metadata,
                                    "Hashes": hashes,
                                }
                            )

                            os.remove(dest_path)
                            print(f"Arquivo original removido: {file_name}")
                        except Exception as e:
                            print(f"Erro ao mover o arquivo: {e}")

        time.sleep(2)
