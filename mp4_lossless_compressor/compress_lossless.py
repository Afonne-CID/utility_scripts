import ffmpeg
import sys
import os
import argparse

def get_video_info(input_path):
    """Get comprehensive video information"""
    try:
        probe = ffmpeg.probe(input_path)
        video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
        audio_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'audio'), None)
        format_info = probe['format']
        
        duration = float(format_info['duration'])
        file_size = int(format_info['size'])
        current_bitrate = (file_size * 8) / duration  # bits per second
        
        # Collect detailed info
        video_info = {
            'duration': duration,
            'current_bitrate': current_bitrate,
            'file_size': file_size,
            'format_name': format_info.get('format_name', 'Unknown'),
            'video_codec': video_stream.get('codec_name', 'Unknown') if video_stream else 'No video',
            'video_bitrate': video_stream.get('bit_rate', 'Unknown') if video_stream else 'No video',
            'width': video_stream.get('width', 'Unknown') if video_stream else 'No video',
            'height': video_stream.get('height', 'Unknown') if video_stream else 'No video',
            'fps': eval(video_stream.get('r_frame_rate', '0/1')) if video_stream else 'No video',
            'pixel_format': video_stream.get('pix_fmt', 'Unknown') if video_stream else 'No video',
            'audio_codec': audio_stream.get('codec_name', 'Unknown') if audio_stream else 'No audio',
            'audio_bitrate': audio_stream.get('bit_rate', 'Unknown') if audio_stream else 'No audio',
            'audio_sample_rate': audio_stream.get('sample_rate', 'Unknown') if audio_stream else 'No audio',
            'audio_channels': audio_stream.get('channels', 'Unknown') if audio_stream else 'No audio',
        }
        
        return video_info
    except Exception as e:
        print(f"❌ Error getting video info: {e}")
        return None

def print_video_details(video_info):
    """Print comprehensive video details in a formatted way"""
    if not video_info:
        print("❌ No video information available")
        return
    
    print("\n" + "="*60)
    print("📹 VIDEO FILE ANALYSIS")
    print("="*60)
    
    # File info
    file_size_gb = video_info['file_size'] / (1024 * 1024 * 1024)
    file_size_mb = video_info['file_size'] / (1024 * 1024)
    duration_mins = video_info['duration'] / 60
    
    print(f"📁 File Size: {file_size_gb:.3f} GB ({file_size_mb:.1f} MB)")
    print(f"⏱️  Duration: {duration_mins:.1f} minutes ({video_info['duration']:.1f} seconds)")
    print(f"📦 Container: {video_info['format_name'].upper()}")
    print(f"📊 Overall Bitrate: {int(video_info['current_bitrate'] // 1000)} kbps")
    
    print("\n" + "-"*30 + " VIDEO STREAM " + "-"*30)
    if video_info['video_codec'] != 'No video':
        print(f"🎥 Codec: {video_info['video_codec'].upper()}")
        print(f"📐 Resolution: {video_info['width']}x{video_info['height']}")
        print(f"🎞️  Frame Rate: {video_info['fps']:.2f} fps")
        print(f"🎨 Pixel Format: {video_info['pixel_format']}")
        if video_info['video_bitrate'] != 'Unknown':
            video_bitrate_kbps = int(video_info['video_bitrate']) // 1000
            print(f"📈 Video Bitrate: {video_bitrate_kbps} kbps")
        else:
            print("📈 Video Bitrate: Not specified in metadata")
    else:
        print("❌ No video stream found")
    
    print("\n" + "-"*30 + " AUDIO STREAM " + "-"*30)
    if video_info['audio_codec'] != 'No audio':
        print(f"🔊 Codec: {video_info['audio_codec'].upper()}")
        if video_info['audio_bitrate'] != 'Unknown':
            audio_bitrate_kbps = int(video_info['audio_bitrate']) // 1000
            print(f"📊 Audio Bitrate: {audio_bitrate_kbps} kbps")
        else:
            print("📊 Audio Bitrate: Not specified in metadata")
        print(f"🎵 Sample Rate: {video_info['audio_sample_rate']} Hz")
        print(f"🔈 Channels: {video_info['audio_channels']}")
    else:
        print("❌ No audio stream found")
    
    print("="*60)

def calculate_target_bitrate(duration, target_size_gb=1.0):
    """Calculate target bitrate to achieve desired file size"""
    target_size_bytes = target_size_gb * 1024 * 1024 * 1024  # Convert GB to bytes
    # Leave some headroom (90% of target) to account for audio and container overhead
    target_bitrate = (target_size_bytes * 0.9 * 8) / duration  # bits per second
    return int(target_bitrate)

def compress_video_to_size(input_path, output_path=None, target_size_gb=1.0, downscale_to_1080p=False, use_hevc=False, reduce_fps=False):
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file does not exist: {input_path}")
    
    if output_path is None:
        base, _ = os.path.splitext(input_path)
        suffix = "_compressed"
        if downscale_to_1080p:
            suffix += "_1080p"
        if use_hevc:
            suffix += "_h265"
        if reduce_fps:
            suffix += "_30fps"
        output_path = f"{base}{suffix}.mp4"

    # Get comprehensive video information
    video_info = get_video_info(input_path)
    if video_info is None:
        raise ValueError("Could not get video information")
    
    # Print detailed video analysis
    print_video_details(video_info)
    
    current_size_gb = video_info['file_size'] / (1024 * 1024 * 1024)
    print(f"\n🎯 Target file size: {target_size_gb} GB")
    
    if current_size_gb <= target_size_gb:
        print(f"✅ File is already under {target_size_gb} GB. No compression needed.")
        return input_path
    
    # Calculate target bitrate
    target_bitrate = calculate_target_bitrate(video_info['duration'], target_size_gb)
    target_bitrate_kbps = target_bitrate // 1000
    
    # Adjust bitrate based on options
    if downscale_to_1080p:
        # 1080p needs much less bitrate than 4K
        target_bitrate_kbps = min(target_bitrate_kbps, 12000)  # Cap at 12Mbps for 1080p
        print(f"📐 Downscaling to 1080p - using capped bitrate: {target_bitrate_kbps} kbps")
    
    if use_hevc:
        # H.265 is more efficient, can use lower bitrate
        target_bitrate_kbps = int(target_bitrate_kbps * 0.7)  # 30% reduction
        print(f"🎥 Using H.265 codec - reduced bitrate: {target_bitrate_kbps} kbps")
    
    print(f"\n📉 Final target bitrate: {target_bitrate_kbps} kbps")
    print(f"🔄 Starting compression...")

    # Build ffmpeg command
    input_stream = ffmpeg.input(input_path)
    
    # Video codec selection
    vcodec = 'libx265' if use_hevc else 'libx264'
    
    # Build output parameters
    output_params = {
        'vcodec': vcodec,
        'video_bitrate': f'{target_bitrate_kbps}k',
        'preset': 'medium',
        'acodec': 'aac',
        'audio_bitrate': '128k'
    }
    
    # Add scaling if requested
    if downscale_to_1080p:
        output_params['vf'] = 'scale=1920:1080'
    
    # Add frame rate reduction if requested
    if reduce_fps:
        output_params['r'] = '30'

    try:
        (
            input_stream
            .output(output_path, **output_params)
            .overwrite_output()
            .run(quiet=False)
        )
        
        # Check final file size
        final_size = os.path.getsize(output_path)
        final_size_gb = final_size / (1024 * 1024 * 1024)
        
        print(f"\n✅ Video compressed and saved to: {output_path}")
        print(f"📊 Final file size: {final_size_gb:.2f} GB")
        
        if final_size_gb <= target_size_gb:
            print(f"🎉 Successfully achieved target size!")
        else:
            print(f"⚠️  File is slightly larger than target, but close enough.")
            
        return output_path
        
    except ffmpeg.Error as e:
        print("❌ FFmpeg error:\n", e.stderr.decode(), file=sys.stderr)
        raise

def analyze_video_only(input_path):
    """Just analyze and print video details without compression"""
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file does not exist: {input_path}")
    
    video_info = get_video_info(input_path)
    if video_info is None:
        raise ValueError("Could not get video information")
    
    print_video_details(video_info)
    
    # Print compression recommendations
    current_size_gb = video_info['file_size'] / (1024 * 1024 * 1024)
    print(f"\n💡 COMPRESSION RECOMMENDATIONS:")
    print(f"   Current size: {current_size_gb:.3f} GB")
    
    # Detect if this is 4K content
    is_4k = video_info['width'] >= 3840 or video_info['height'] >= 2160
    is_high_fps = video_info['fps'] > 30
    
    if is_4k:
        print(f"\n🎬 4K VIDEO DETECTED - Special recommendations:")
        print(f"   📐 Resolution: {video_info['width']}x{video_info['height']}")
        print(f"   🎞️  Frame Rate: {video_info['fps']:.1f} fps")
        print(f"   ⚠️  High quality 4K content requires high bitrates for good results")
        
        if current_size_gb > 1.0:
            target_bitrate_1gb = calculate_target_bitrate(video_info['duration'], 1.0) // 1000
            print(f"\n   🎯 For 1.0 GB (maintaining 4K): ~{target_bitrate_1gb} kbps")
            
            # Suggest alternative approaches
            print(f"\n   🔄 ALTERNATIVE APPROACHES for better compression:")
            print(f"      • Downscale to 1080p: ~8,000-12,000 kbps (much smaller file)")
            print(f"      • Use H.265/HEVC codec: ~50% smaller than H.264")
            if is_high_fps:
                print(f"      • Reduce frame rate to 30fps: ~{video_info['fps']/30:.1f}x smaller")
        
        print(f"\n   💭 QUALITY vs SIZE trade-offs:")
        print(f"      • 4K @ current quality → Very large files")
        print(f"      • 4K @ lower bitrate → Possible quality loss")
        print(f"      • 1080p @ good bitrate → Much smaller, still great quality")
        
    else:
        if current_size_gb > 1.0:
            target_bitrate_1gb = calculate_target_bitrate(video_info['duration'], 1.0) // 1000
            print(f"   For 1.0 GB: Use bitrate ~{target_bitrate_1gb} kbps")
        
        if current_size_gb > 0.5:
            target_bitrate_half = calculate_target_bitrate(video_info['duration'], 0.5) // 1000
            print(f"   For 0.5 GB: Use bitrate ~{target_bitrate_half} kbps")

def main():
    parser = argparse.ArgumentParser(description="Video Compressor - Compress videos to target size")
    parser.add_argument("input", help="Path to the input video file")
    parser.add_argument("-o", "--output", help="Optional: Path for the output compressed file")
    parser.add_argument("-s", "--size", type=float, default=1.0, 
                       help="Target file size in GB (default: 1.0)")
    parser.add_argument("-a", "--analyze", action="store_true",
                       help="Only analyze the video without compressing (ignores other options)")
    parser.add_argument("--1080p", action="store_true",
                       help="Downscale 4K video to 1080p for much smaller file sizes")
    parser.add_argument("--hevc", action="store_true",
                       help="Use H.265/HEVC codec for better compression (slower encoding)")
    parser.add_argument("--30fps", action="store_true",
                       help="Reduce frame rate to 30fps for smaller file size")

    args = parser.parse_args()
    
    if args.analyze:
        analyze_video_only(args.input)
    else:
        compress_video_to_size(
            args.input, 
            args.output, 
            args.size,
            downscale_to_1080p=getattr(args, '1080p'),
            use_hevc=args.hevc,
            reduce_fps=getattr(args, '30fps')
        )

if __name__ == "__main__":
    main()
