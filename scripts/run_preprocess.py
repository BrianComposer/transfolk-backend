from transfolk_core.config import *
from transfolk_core.db.config_registry import ConfigRegistry
from transfolk_core.preprocessing.dataCleaning import normalize_musicxml_corpus_new
from transfolk_core.preprocessing.count_TS_tonality import count_ts_mode_distribution

from pathlib import Path
from datetime import datetime
import json


def save_normalization_report(
    *,
    corpus,
    summary: dict,
    report_dir: str | Path,
    input_dir: str | Path,
    output_dir: str | Path,
) -> tuple[Path, Path]:
    """
    Guarda un reporte de normalización MusicXML en formato JSON y TXT.

    El reporte incluye fecha, hora, corpus, rutas usadas, contadores del proceso
    y detalle por archivo con mensajes, errores, omisiones y modificaciones.
    """
    report_dir = Path(report_dir).resolve()
    report_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now()
    timestamp_file = now.strftime("%Y%m%d_%H%M%S")
    timestamp_human = now.strftime("%Y-%m-%d %H:%M:%S")

    corpus_name = getattr(corpus, "name", str(corpus))

    report_data = {
        "process": "MUSICXML_NORMALIZATION",
        "datetime": timestamp_human,
        "corpus": corpus_name,
        "input_dir": str(Path(input_dir).resolve()),
        "output_dir": str(Path(output_dir).resolve()),
        "summary": summary,
    }

    json_report_path = report_dir / f"{timestamp_file}_{corpus_name}_musicxml_normalization_report.json"
    txt_report_path = report_dir / f"{timestamp_file}_{corpus_name}_musicxml_normalization_report.txt"

    with json_report_path.open("w", encoding="utf-8") as f:
        json.dump(report_data, f, ensure_ascii=False, indent=4)

    totals = summary.get("totals", {})
    files = summary.get("files", [])

    saved_files = [f for f in files if f.get("status") == "saved"]
    ignored_files = [f for f in files if f.get("status") == "ignored"]
    error_files = [f for f in files if f.get("status") == "error"]
    modified_files = [f for f in files if f.get("modified") is True]

    with txt_report_path.open("w", encoding="utf-8") as f:
        f.write("=" * 70 + "\n")
        f.write("REPORTE DE NORMALIZACIÓN MUSICXML\n")
        f.write("=" * 70 + "\n\n")

        f.write(f"Fecha y hora           : {timestamp_human}\n")
        f.write(f"Corpus                 : {corpus_name}\n")
        f.write(f"Proceso                : MUSICXML_NORMALIZATION\n")
        f.write(f"Carpeta de entrada     : {Path(input_dir).resolve()}\n")
        f.write(f"Carpeta de salida      : {Path(output_dir).resolve()}\n")
        f.write(f"Carpeta de reportes    : {report_dir}\n\n")

        f.write("-" * 70 + "\n")
        f.write("RESUMEN\n")
        f.write("-" * 70 + "\n")
        f.write(f"Archivos encontrados   : {summary.get('files_found', 0)}\n")
        f.write(f"Leídos correctamente   : {totals.get('read', 0)}\n")
        f.write(f"Procesados y guardados : {totals.get('processed', 0)}\n")
        f.write(f"Ignorados              : {totals.get('ignored', 0)}\n")
        f.write(f"Errores                : {totals.get('errors', 0)}\n")
        f.write(f"Archivos escritos      : {totals.get('saved', 0)}\n")
        f.write(f"Archivos modificados   : {len(modified_files)}\n\n")

        if saved_files:
            f.write("-" * 70 + "\n")
            f.write("ARCHIVOS GUARDADOS\n")
            f.write("-" * 70 + "\n")

            for idx, item in enumerate(saved_files, start=1):
                f.write(f"\nArchivo {idx}\n")
                f.write(f"  Entrada     : {item.get('file')}\n")
                f.write(f"  Salida      : {item.get('output')}\n")
                f.write(f"  Modificado  : {item.get('modified')}\n")

                messages = item.get("messages", [])
                if messages:
                    f.write("  Mensajes    :\n")
                    for msg in messages:
                        f.write(f"    - {msg}\n")

            f.write("\n")

        if ignored_files:
            f.write("-" * 70 + "\n")
            f.write("ARCHIVOS IGNORADOS\n")
            f.write("-" * 70 + "\n")

            for idx, item in enumerate(ignored_files, start=1):
                f.write(f"\nIgnorado {idx}\n")
                f.write(f"  Archivo : {item.get('file')}\n")

                messages = item.get("messages", [])
                if messages:
                    f.write("  Motivo  :\n")
                    for msg in messages:
                        f.write(f"    - {msg}\n")

            f.write("\n")

        if error_files:
            f.write("-" * 70 + "\n")
            f.write("DETALLE DE ERRORES\n")
            f.write("-" * 70 + "\n")

            for idx, item in enumerate(error_files, start=1):
                f.write(f"\nError {idx}\n")
                f.write(f"  Archivo : {item.get('file')}\n")

                messages = item.get("messages", [])
                if messages:
                    f.write("  Detalle :\n")
                    for msg in messages:
                        f.write(f"    - {msg}\n")

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


    corpus = registry.find_by_name("valencia")
    adc=registry.find_by_name("corpus_cleaning")

    data_dir_normalized = resolver.data_normalized(corpus)
    data_dir_clean = resolver.data_clean(corpus)
    data_report = resolver.data_report(corpus)



    summary = normalize_musicxml_corpus_new(data_dir_normalized,
                                            data_dir_clean,
                                            adc.durations,
                                            midi_min=30,
                                            midi_max=110,
                                            overwrite=True,
                                            delete_grace_notes=False,
                                            create_title=True,
                                            respect_time_signature_changes=True,
                                            respect_ties=True)


    json_report_path, txt_report_path = save_normalization_report(
        corpus=corpus,
        summary=summary,
        report_dir=data_report,
        input_dir=data_dir_normalized,
        output_dir=data_dir_clean,
    )

    print(f"Reporte JSON guardado en: {json_report_path}")
    print(f"Reporte TXT guardado en: {txt_report_path}")