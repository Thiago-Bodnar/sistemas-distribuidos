#trabalho04\local\polly_local.py
import argparse
import sys
from pathlib import Path

import boto3
from botocore.exceptions import BotoCoreError, ClientError


def define_parser():
    """
    define parser de argumentos para linha de comando (helper pros tansos como eu)    
    """
    parser = argparse.ArgumentParser(
        description="converte texto em MP3 usando Amazon Polly."
    )
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--text", help="Texto a ser sintetizado.")
    g.add_argument("--file", help="Caminho para arquivo .txt com o conteúdo.")
    parser.add_argument("--out", default="polly_output.mp3", help="Arquivo de saída .mp3.")
    parser.add_argument("--voice-id", default="Camila", help="Ex.: Camila, Ricardo.")
    parser.add_argument("--engine", default="neural", choices=["neural", "standard"])
    parser.add_argument("--ssml", action="store_true", help="Interpreta entrada como SSML.")
    return parser

def sintetiza_para_mp3(
    text: str,
    out_path: Path,
    voice_id: str = "Camila",
    engine: str = "neural",
    is_ssml: bool = False,
):
    """
    sintetiza texto em arquivo MP3 usando Amazon Polly
    """
    polly = boto3.client("polly")

    kwargs = {
        "Text": text,
        "OutputFormat": "mp3",
        "VoiceId": voice_id,
        "Engine": engine,
        "LanguageCode": "pt-BR",
    }

    if is_ssml:
        kwargs["TextType"] = "ssml"

    resp = polly.synthesize_speech(**kwargs)
    stream = resp.get("AudioStream")
    if not stream:
        raise RuntimeError("Resposta do Polly sem 'AudioStream'.")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "wb") as f:
        f.write(stream.read())
    return str(out_path)


def main():
    parser = define_parser()
    args = parser.parse_args()

    try:
        text = args.text
        if args.file:
            text = Path(args.file).read_text(encoding="utf-8")

        if not text or not text.strip():
            print("Erro: texto vazio.", file=sys.stderr)
            sys.exit(2)

        path = sintetiza_para_mp3(
            text=text,
            out_path=Path(args.out),
            voice_id=args.voice_id,
            engine=args.engine,
            is_ssml=args.ssml,
        )
        print(f"OK: MP3 gerado em {path}")

    except (BotoCoreError, ClientError) as e:
        print(f"Falha na chamada ao Polly: {e}", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        print(f"Erro: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
