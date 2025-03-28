import datetime
import hashlib
import json
import mimetypes
import os
import shutil
import stat
import tkinter as tk
import unicodedata
import zipfile
from fractions import Fraction
from pathlib import Path

import exiftool
import magic
from PIL import Image
from PIL.ExifTags import GPSTAGS, TAGS
from PIL.TiffTags import TAGS_V2
from tzlocal import get_localzone

from utils.api_perdigueiro import registrar_acao
from utils.metadata import calculate_hash, get_file_metadata
from utils.renomear_zip import renomear_zip


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(
            obj, (Fraction, int, float)
        ):  # Converte IFDRational e números para float
            return float(obj)
        elif isinstance(obj, bytes):  # Converte bytes para string legível
            return obj.decode(errors="ignore")
        elif isinstance(
            obj, datetime.datetime
        ):  # Converte datetime para string formatada
            return obj.isoformat()
        elif isinstance(obj, tuple):  # Converte tuplas para listas
            return list(obj)
        elif isinstance(obj, set):  # Converte conjuntos para listas
            return list(obj)
        elif isinstance(
            obj, dict
        ):  # Converte dicionários com chaves não string para strings
            return {str(k): v for k, v in obj.items()}
        elif hasattr(
            obj, "__dict__"
        ):  # Converte objetos personalizados para dicionários
            return obj.__dict__
        return str(obj)  # Converte qualquer outro tipo para string


# Remove acentos do path do arquivo
def remover_acentos(texto):
    """Remove acentos e caracteres especiais do nome do arquivo."""
    return "".join(
        c for c in unicodedata.normalize("NFKD", texto) if not unicodedata.combining(c)
    )


# Cria uma cópia do arquivo original sem acentos no nome e retorna o novo caminho
def arquivo_temporario_sem_acentos(file_path):

    file_path = Path(file_path)  # Garante que é um objeto Path

    if not file_path.exists():
        return None

    user_dir = str(Path.home())
    temp_dir = user_dir + "\\AppData\\Local\\Temp"

    # Gera novo nome sem acentos
    novo_nome = remover_acentos(file_path.name).split("\\")[-1]
    novo_caminho = temp_dir + f"\\COPIA_{novo_nome}"

    try:
        shutil.copy2(file_path, novo_caminho)  # Copia preservando metadados
        print(f"Cópia criada: {novo_caminho}")
        return novo_caminho
    except Exception as e:
        print(f"ERRO ao copiar o arquivo: {e}")
        return None


# Converte valores EXIF não serializáveis para tipos JSON compatíveis
def normalize_exif_data(exif_data):

    if isinstance(exif_data, dict):
        normalized_data = {}
        for key, value in exif_data.items():
            if isinstance(value, (Fraction, int, float, str, list, dict, type(None))):
                normalized_data[key] = (
                    float(value) if isinstance(value, Fraction) else value
                )  # Converte Fraction
            elif isinstance(value, tuple):
                normalized_data[key] = list(value)  # Converte tuple para list
            elif isinstance(value, bytes):
                normalized_data[key] = value.decode(
                    errors="ignore"
                )  # Converte bytes para string
            else:
                normalized_data[key] = str(
                    value
                )  # Converte qualquer outro tipo para string
        return normalized_data
    return exif_data


# Calcula os hashes MD5, SHA-1, SHA-256 e SHA-512 do arquivo
def calculate_hashes(file_path):

    hashes = {
        "MD5": hashlib.md5(),
        "SHA-1": hashlib.sha1(),
        "SHA-256": hashlib.sha256(),
    }

    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            for hash_func in hashes.values():
                hash_func.update(chunk)

    return {name: hash_func.hexdigest() for name, hash_func in hashes.items()}


# Extrai metadados EXIF de imagens
def get_exif_data(file_path):

    try:
        image = Image.open(file_path)
        exif_data = image._getexif()
        metadata = {}

        if exif_data:
            for tag_id, value in exif_data.items():
                tag = TAGS.get(tag_id, tag_id)
                metadata[tag] = value

            # Extraindo coordenadas GPS se disponíveis
            if "GPSInfo" in metadata:
                gps_data = {}
                for gps_tag_id, gps_value in metadata["GPSInfo"].items():
                    gps_tag = GPSTAGS.get(gps_tag_id, gps_tag_id)
                    gps_data[gps_tag] = gps_value
                metadata["GPSInfo"] = gps_data
        return normalize_exif_data(metadata)
    except Exception:
        return {}


# Usa ExifTool para extrair metadados adicionais, incluindo GPS e Autor
def get_exiftool_metadata(file_path):

    user_dir = str(Path.home())
    user_dir_custodiatech = user_dir + "\\AppData\\Local\\CustodiaTech"
    exiftool_dir = user_dir_custodiatech + "\\_internal\\ExifToolPackage"

    EXIFTOOL_PATH = f"{exiftool_dir}\\exiftool(-k).exe"  # Caminho do ExifTool

    with exiftool.ExifTool(EXIFTOOL_PATH) as et:
        metadata = et.execute_json("-j", file_path)
        if metadata:
            meta = metadata[0]

            # Extraindo informações de GPS
            gps_data = {
                "Latitude": meta.get("GPSLatitude"),
                "Longitude": meta.get("GPSLongitude"),
                "Altitude": meta.get("GPSAltitude"),
                "GPS Date/Time": meta.get("GPSDateTime"),
            }
            gps_data = {k: v for k, v in gps_data.items() if v is not None}
            meta["GPS Information"] = gps_data if gps_data else "Não disponível"

            # Extraindo informações do autor/criador do arquivo
            author_fields = [
                "Author",
                "XPAuthor",
                "OwnerName",
                "Creator",
                "FileOwner",
                "Copyright",
                "Artist",
            ]
            for field in author_fields:
                if field in meta:
                    meta["File Author"] = meta[field]
                    break

            if "File Author" not in meta:
                meta["File Author"] = "Não disponível"

            return meta
    return {}


# Coleta todos os metadados forenses do arquivo
def captar_metadados(file_path):

    temp_file = str(arquivo_temporario_sem_acentos(file_path)).replace("\\", "/")

    stat_info = os.stat(file_path)

    fuso_local = get_localzone()

    metadata = {
        "File Path": file_path,
        "Size (bytes)": stat_info.st_size,
        "Created": datetime.datetime.fromtimestamp(
            stat_info.st_birthtime, tz=fuso_local
        ).strftime("%d/%m/%Y %H:%M:%S UTC %Z"),
        "Modified": datetime.datetime.fromtimestamp(
            stat_info.st_mtime, tz=fuso_local
        ).strftime("%d/%m/%Y %H:%M:%S UTC %Z"),
        "Accessed": datetime.datetime.fromtimestamp(
            stat_info.st_atime, tz=fuso_local
        ).strftime("%d/%m/%Y %H:%M:%S UTC %Z"),
        "File Type": magic.from_file(temp_file, mime=True),
        "MIME Type": mimetypes.guess_type(file_path)[0],
        "Hashes": calculate_hashes(file_path),
        "Permissions": {
            "Read": bool(stat_info.st_mode & stat.S_IREAD),
            "Write": bool(stat_info.st_mode & stat.S_IWRITE),
            "Execute": bool(stat_info.st_mode & stat.S_IEXEC),
        },
    }

    os.remove(temp_file)

    # Adiciona EXIF se for imagem
    if metadata["MIME Type"] and metadata["MIME Type"].startswith("image"):
        metadata["EXIF"] = get_exif_data(file_path)

    # Metadados via ExifTool (incluindo GPS e Autor)
    metadata["Advanced Metadata"] = get_exiftool_metadata(file_path)

    return metadata


def extracao_metadados(arquivo, case_directory, usuario, metadados_total):

    if not arquivo:
        print("Nenhum arquivo selecionado.")
        return

    print(f"\nArquivo Selecionado: {arquivo}\n")
    metadata = captar_metadados(arquivo)

    try:
        json_metadata = json.dumps(
            metadata, indent=4, ensure_ascii=False, cls=CustomJSONEncoder
        )
        print(json_metadata)

        output_file = os.path.join(
            case_directory, f"{os.path.basename(arquivo)}.metadata.json"
        )
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(json_metadata)

        print(f"\nMetadados salvos em: {output_file}")
    except Exception as e:
        print(f"\nErro ao serializar JSON: {e}")

    nome_base = os.path.splitext(os.path.basename(arquivo))[0]
    novo_zip_path = os.path.join(case_directory, f"{nome_base}.zip")

    # Cria o arquivo ZIP e copia o arquivo para dentro dele
    with zipfile.ZipFile(novo_zip_path, "w") as zip_file:
        zip_file.write(arquivo, os.path.basename(arquivo))
        zip_file.write(output_file, os.path.basename(output_file))

    # Remove o arquivo JSON após adicioná-lo ao ZIP
    os.remove(output_file)

    # Calcula os hashes e obtém os metadados do arquivo ZIP
    hashes = calculate_hash(novo_zip_path, algorithms=["md5", "sha1", "sha256"])
    metadata = get_file_metadata(novo_zip_path)

    metadata, nome_final_zip = renomear_zip(novo_zip_path, metadata, f"{nome_base}_")

    # Adiciona os metadados à lista total
    metadados_total.append(
        {"nome_do_arquivo": nome_final_zip, "hashes": hashes, "metadata": metadata}
    )

    registrar_acao(
        "Metadados extraídos",
        f"Metadados extraídos do arquivo {arquivo} pelo usuário {usuario} e copiado para {case_directory}",
    )
