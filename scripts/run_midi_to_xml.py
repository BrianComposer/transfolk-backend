from transfolk_core.config import *
from transfolk_core.db.config_registry import ConfigRegistry
from transfolk_core.preprocessing.midi_to_musicxml import midi_folder_to_musicxml
from pathlib import Path
from datetime import datetime
import json

def save_midi_to_musicxml_report(
    *,
    corpus,
    report: dict,
    report_dir: str | Path,
    input_dir: str | Path,
    output_dir: str | Path,
) -> tuple[Path, Path]:
    """
    Guarda un reporte de conversión MIDI -> MusicXML en formato JSON y TXT.

    El reporte incluye fecha, hora, corpus, rutas usadas, contadores del proceso
    y detalle de errores si los hubiera.
    """
    report_dir = Path(report_dir).resolve()
    report_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now()
    timestamp_file = now.strftime("%Y%m%d_%H%M%S")
    timestamp_human = now.strftime("%Y-%m-%d %H:%M:%S")

    corpus_name = getattr(corpus, "name", str(corpus))

    report_data = {
        "process": "MIDI_TO_MUSICXML",
        "datetime": timestamp_human,
        "corpus": corpus_name,
        "input_dir": str(Path(input_dir).resolve()),
        "output_dir": str(Path(output_dir).resolve()),
        "report": report,
    }

    json_report_path = report_dir / f"{timestamp_file}_{corpus_name}_midi_to_musicxml_report.json"
    txt_report_path = report_dir / f"{timestamp_file}_{corpus_name}_midi_to_musicxml_report.txt"

    with json_report_path.open("w", encoding="utf-8") as f:
        json.dump(report_data, f, ensure_ascii=False, indent=4)

    files = report.get("files", [])
    converted_files = [f for f in files if f.get("status") == "converted"]
    failed_files = [f for f in files if f.get("status") == "failed"]

    with txt_report_path.open("w", encoding="utf-8") as f:
        f.write("=" * 70 + "\n")
        f.write("REPORTE DE CONVERSIÓN MIDI -> MUSICXML\n")
        f.write("=" * 70 + "\n\n")

        f.write(f"Fecha y hora           : {timestamp_human}\n")
        f.write(f"Corpus                 : {corpus_name}\n")
        f.write(f"Proceso                : MIDI_TO_MUSICXML\n")
        f.write(f"Carpeta de entrada     : {Path(input_dir).resolve()}\n")
        f.write(f"Carpeta de salida      : {Path(output_dir).resolve()}\n")
        f.write(f"Carpeta de reportes    : {report_dir}\n\n")

        f.write("-" * 70 + "\n")
        f.write("RESUMEN\n")
        f.write("-" * 70 + "\n")
        f.write(f"Archivos MIDI detectados : {report.get('midi_files_detected', 0)}\n")
        f.write(f"Convertidos OK           : {report.get('converted', 0)}\n")
        f.write(f"Fallidos                 : {report.get('failed_count', 0)}\n")
        f.write(f"Recursivo                : {report.get('recursive')}\n\n")

        if converted_files:
            f.write("-" * 70 + "\n")
            f.write("ARCHIVOS CONVERTIDOS\n")
            f.write("-" * 70 + "\n")

            for idx, item in enumerate(converted_files, start=1):
                f.write(f"\nArchivo {idx}\n")
                f.write(f"  Entrada : {item.get('input_path')}\n")
                f.write(f"  Salida  : {item.get('output_path')}\n")

            f.write("\n")

        if failed_files:
            f.write("-" * 70 + "\n")
            f.write("DETALLE DE ERRORES\n")
            f.write("-" * 70 + "\n")

            for idx, item in enumerate(failed_files, start=1):
                f.write(f"\nError {idx}\n")
                f.write(f"  Archivo : {item.get('input_path')}\n")
                f.write(f"  Salida  : {item.get('output_path')}\n")
                f.write(f"  Error   : {item.get('error')}\n")

            f.write("\n")
        else:
            f.write("-" * 70 + "\n")
            f.write("ERRORES\n")
            f.write("-" * 70 + "\n")
            f.write("No se han producido errores.\n\n")

        f.write("=" * 70 + "\n")
        f.write("FIN DEL REPORTE\n")
        f.write("=" * 70 + "\n")

    return json_report_path, txt_report_path




if __name__ == "__main__":
    settings = Settings()
    paths = ProjectPaths(settings.root)
    resolver = PathResolver(paths)
    registry = ConfigRegistry(paths.db_sqlite)
    registry.load_all()

    corpus = registry.find_by_name("altoaragon")
    adc=registry.find_by_name("basic_set")

    data_dir_raw = resolver.data_raw(corpus)
    data_dir_clean = resolver.data_normalized(corpus)
    data_report = resolver.data_report(corpus)

    summary = result = midi_folder_to_musicxml(
        input_folder=str(data_dir_raw),
        output_folder=str(data_dir_clean),
        allowed_durations=adc.durations,
        candidate_time_signatures=["2/4", "3/4", "4/4", "6/8"],
        recursive=True,
        verbose=True,
        corpus_name=corpus.name
    )

    json_report_path, txt_report_path = save_midi_to_musicxml_report(
        corpus=corpus,
        report=summary,
        report_dir=data_report,
        input_dir=data_dir_raw,
        output_dir=data_dir_clean,
    )

    print(f"Reporte JSON guardado en: {json_report_path}")
    print(f"Reporte TXT guardado en: {txt_report_path}")