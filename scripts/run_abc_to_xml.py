from datetime import datetime
import json
from pathlib import Path

from transfolk_core.config import *
from transfolk_core.db.config_registry import ConfigRegistry
from transfolk_core.preprocessing.abc_to_musicxml import convert_abc_folder_to_musicxml


def save_conversion_report(
    *,
    corpus,
    summary: dict,
    report_dir: str | Path,
    input_dir: str | Path,
    output_dir: str | Path,
) -> tuple[Path, Path]:
    """
    Guarda un reporte de conversión ABC -> MusicXML en formato JSON y TXT.

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
        "process": "ABC_TO_MUSICXML",
        "datetime": timestamp_human,
        "corpus": corpus_name,
        "input_dir": str(Path(input_dir).resolve()),
        "output_dir": str(Path(output_dir).resolve()),
        "summary": summary,
    }

    json_report_path = report_dir / f"{timestamp_file}_{corpus_name}_abc_to_musicxml_report.json"
    txt_report_path = report_dir / f"{timestamp_file}_{corpus_name}_abc_to_musicxml_report.txt"

    with json_report_path.open("w", encoding="utf-8") as f:
        json.dump(report_data, f, ensure_ascii=False, indent=4)

    with txt_report_path.open("w", encoding="utf-8") as f:
        f.write("=" * 70 + "\n")
        f.write("REPORTE DE CONVERSIÓN ABC -> MUSICXML\n")
        f.write("=" * 70 + "\n\n")

        f.write(f"Fecha y hora           : {timestamp_human}\n")
        f.write(f"Corpus                 : {corpus_name}\n")
        f.write(f"Proceso                : ABC_TO_MUSICXML\n")
        f.write(f"Carpeta de entrada     : {Path(input_dir).resolve()}\n")
        f.write(f"Carpeta de salida      : {Path(output_dir).resolve()}\n")
        f.write(f"Carpeta de reportes    : {report_dir}\n\n")

        f.write("-" * 70 + "\n")
        f.write("RESUMEN\n")
        f.write("-" * 70 + "\n")
        f.write(f"Archivos ABC procesados: {summary.get('abc_files_processed', 0)}\n")
        f.write(f"Tunes detectadas       : {summary.get('tunes_detected', 0)}\n")
        f.write(f"Convertidas OK         : {summary.get('converted_ok', 0)}\n")
        f.write(f"Fallidas               : {summary.get('failed', 0)}\n\n")

        errors = summary.get("errors", [])

        if errors:
            f.write("-" * 70 + "\n")
            f.write("DETALLE DE ERRORES\n")
            f.write("-" * 70 + "\n")

            for idx, err in enumerate(errors, start=1):
                f.write(f"\nError {idx}\n")
                f.write(f"  Archivo : {err.get('file')}\n")
                f.write(f"  Tune    : {err.get('tune_index')}\n")
                f.write(f"  Título  : {err.get('title')}\n")
                f.write(f"  Error   : {err.get('error')}\n")
        else:
            f.write("-" * 70 + "\n")
            f.write("ERRORES\n")
            f.write("-" * 70 + "\n")
            f.write("No se han producido errores.\n")

        f.write("\n" + "=" * 70 + "\n")
        f.write("FIN DEL REPORTE\n")
        f.write("=" * 70 + "\n")

    return json_report_path, txt_report_path


if __name__ == "__main__":
    settings = Settings()
    paths = ProjectPaths(settings.root)
    resolver = PathResolver(paths)
    registry = ConfigRegistry(paths.db_sqlite)
    registry.load_all()

    corpus = registry.find_by_name("essen")

    data_dir_raw = resolver.data_raw(corpus)
    data_dir_normalized = resolver.data_normalized(corpus)
    data_report = resolver.data_report(corpus)

    summary = convert_abc_folder_to_musicxml(
        input_dir=data_dir_raw,
        output_dir=data_dir_normalized,
        respect_subfolder=False,
        show_progress=True
    )

    json_report_path, txt_report_path = save_conversion_report(
        corpus=corpus,
        summary=summary,
        report_dir=data_report,
        input_dir=data_dir_raw,
        output_dir=data_dir_normalized,
    )

    print("Archivos ABC procesados:", summary["abc_files_processed"])
    print("Tunes detectadas:", summary["tunes_detected"])
    print("Convertidas OK:", summary["converted_ok"])
    print("Fallidas:", summary["failed"])

    for err in summary["errors"][:10]:
        print(err)

    print(f"\n[OK] Reporte JSON guardado en: {json_report_path}")
    print(f"[OK] Reporte TXT guardado en : {txt_report_path}")