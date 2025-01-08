import asyncio
import os
from pathlib import Path
import logging
import subprocess
from typing import Tuple

logger = logging.getLogger(__name__)

class FFmpegWrapper:
    @staticmethod
    async def validate_file(file_path: str) -> Tuple[bool, str]:
        """
        Validate if file exists and is a valid media file
        Returns: (is_valid, error_message)
        """
        try:
            if not os.path.exists(file_path):
                return False, f"File not found: {file_path}"

            result = subprocess.run(
                ["ffmpeg", "-i", file_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            if "Invalid data found" in result.stderr:
                return False, "Invalid media file format"

            return True, ""

        except Exception as e:
            logger.error(f"Error validating file: {str(e)}")
            return False, str(e)

    @staticmethod
    async def convert_to_mp3(input_path: str, job_id: str) -> Tuple[bool, str, str]:
        """
        Convert video to MP3
        Returns: (success, output_path, error_message)
        """
        try:
            # Validate input path
            if not os.path.exists(input_path):
                return False, "", f"Input file not found: {input_path}"

            # Create output directory
            output_dir = Path("/tmp/converted")
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = str(output_dir / f"{job_id}.mp3")

            # Log the conversion attempt
            logger.info(f"Converting {input_path} to {output_path}")

            # Run FFmpeg command
            command = [
                "ffmpeg",
                "-y",  # Overwrite output file
                "-i", input_path,  # Input file
                "-vn",  # Disable video
                "-acodec", "libmp3lame",  # Audio codec
                "-ab", "192k",  # Bitrate
                "-ar", "44100",  # Sample rate
                output_path  # Output file
            ]

            # Run the command and capture output
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Log the complete command output
            if result.stdout:
                logger.info(f"FFmpeg stdout: {result.stdout}")
            if result.stderr:
                logger.info(f"FFmpeg stderr: {result.stderr}")

            if result.returncode != 0:
                logger.error(f"FFmpeg error: {result.stderr}")
                return False, "", f"Conversion failed: {result.stderr}"

            if not os.path.exists(output_path):
                return False, "", "Output file was not created"

            logger.info(f"Successfully converted {input_path} to {output_path}")
            return True, output_path, ""

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Conversion error: {error_msg}")
            return False, "", f"Error during conversion: {error_msg}"

        finally:
            # Cleanup input file
            try:
                if os.path.exists(input_path):
                    os.remove(input_path)
                    logger.info(f"Cleaned up input file: {input_path}")
            except Exception as e:
                logger.error(f"Error cleaning up input file: {str(e)}")

    @staticmethod
    async def get_file_info(file_path: str) -> Tuple[bool, dict, str]:
        """
        Get information about a media file using ffprobe
        Returns: (success, info_dict, error_message)
        """
        try:
            if not os.path.exists(file_path):
                return False, {}, f"File not found: {file_path}"

            command = [
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                file_path
            ]

            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            if result.returncode != 0:
                return False, {}, f"FFprobe error: {result.stderr}"

            import json
            info = json.loads(result.stdout)
            return True, info, ""

        except Exception as e:
            logger.error(f"Error getting file info: {str(e)}")
            return False, {}, str(e)

ffmpeg = FFmpegWrapper()