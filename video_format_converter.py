import os
from pathlib import Path
import subprocess


def check_ffmpeg_installed():
    """Check if FFmpeg is installed and accessible."""
    try:
        subprocess.run(["ffmpeg", "-version"], 
                       stdout=subprocess.PIPE, 
                       stderr=subprocess.PIPE, 
                       check=True,
                       shell=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        raise EnvironmentError(
            "FFmpeg is not installed or not found in the system PATH. "
            "Please install FFmpeg and ensure it's accessible. "
            "Download from: https://ffmpeg.org/download.html"
        )


def convert_video(input_file, output_format="mp4", output_file=None):
    """Convert a video file to a specified format (default: mp4).

    :param: input_file (str): Path to the input video file.
    :param: output_format (str): Desired output format (default: "mp4").
    :param: output_file (str): Path to the output file (optional).
                               default: input file name.

    returns -> str: Path to the converted video file.
    """
    check_ffmpeg_installed()

    input_file = Path(os.path.expanduser(input_file)).resolve()
    if not input_file.is_file():
        raise FileNotFoundError(
            f"Input file '{input_file}' not found. "
            f"Please check the path and ensure the file exists. "
            f"Current working directory: {os.getcwd()}"
        )

    input_ext = input_file.suffix[1:].lower()

    # cannot convert to the same format
    if input_ext == output_format.lower():
        print(f"Warning: File already in '{output_format}' format.")
        return str(input_file)

    if not output_file:
        output_file = input_file.with_suffix(f".{output_format}")
    else:
        output_file = Path(os.path.expanduser(output_file)).resolve()
    output_file.parent.mkdir(parents=True, exist_ok=True)

    command = [
        "ffmpeg",
        "-i", str(input_file),     # input file
        "-c:v", "libx264",         # video codec (H.264)
        "-preset", "medium",       # encoding speed/quality balance
        "-crf", "23",              # "Constant Rate Factor" for quality
        "-c:a", "aac",             # audio codec (AAC)
        "-b:a", "192k",            # audio bitrate
        "-y",                      # output overwrite
        str(output_file)           # output file
    ]

    try:
        subprocess.run(
            command, 
            check=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True
        )
        return str(output_file)
    
    except subprocess.CalledProcessError as e:
        error_message = f"""
Error during video conversion:
- Command: {' '.join(command)}
- Error Output: {e.stderr}
- Possible causes:
  1. Incompatible input file
  2. Insufficient permissions
  3. Corrupted video file
"""
        raise RuntimeError(error_message) from e

    except Exception as e:
        raise RuntimeError(f"Unexpected error during conversion: {e}") from e

def main():
    try:
        input_path = input("Input video: ").strip()
        output_format = input("Desired output format (default: mp4): ").strip() or "mp4"
        output_path = input("Desired output path (or press Enter to use default): ").strip()

        result_file = convert_video(
            input_path, 
            output_format, 
            output_path or None
        )
        print(f"Converted video saved at: {result_file}")

    except Exception as e:
        print(f"Conversion failed: {e}")
        return 1
    return 0


if __name__ == "__main__":
    main()
