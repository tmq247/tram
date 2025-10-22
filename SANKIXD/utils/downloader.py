from os import path
import yt_dlp
from yt_dlp.utils import DownloadError

ytdl = yt_dlp.YoutubeDL(
    {
        "outtmpl": "downloads/%(id)s.%(ext)s",
        "format": "bestaudio[ext=m4a]",
        "geo_bypass": True,
        "nocheckcertificate": True,
    }
 )


def download(url: str, my_hook) -> str:       
    ydl_optssx = {
        'format' : 'bestaudio[ext=m4a]',
        "outtmpl": "downloads/%(id)s.%(ext)s",
        "geo_bypass": True,
        "nocheckcertificate": True,
        'quiet': True,
        'no_warnings': True,
    }
    info = ytdl.extract_info(url, False)
    try:
        x = yt_dlp.YoutubeDL(ydl_optssx)
        x.add_progress_hook(my_hook)
        dloader = x.download([url])
    except Exception as y_e:
        return print(y_e)
    else:
        dloader
    xyz = path.join("downloads", f"{info['id']}.{info['ext']}")
    return xyz
    # --- alias giữ API cũ ---
    try:
        # nếu download_audio là async
        async def download_audio_concurrent(urls, out_dir, **kwargs):
            if isinstance(urls, (str, bytes)):
                urls = [urls]
            from asyncio import gather
            return await gather(*[download_audio(u, out_dir, **kwargs) for u in urls])
    except NameError:
        # nếu download_audio là sync
        def download_audio_concurrent(urls, out_dir, **kwargs):
            if isinstance(urls, (str, bytes)):
                urls = [urls]
            results = []
            for u in urls:
                results.append(download_audio(u, out_dir, **kwargs))
            return results

    __all__ = [*globals().get("__all__", []), "download_audio_concurrent"]
