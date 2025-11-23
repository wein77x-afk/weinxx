import os
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8255307706:AAFKmRts1Ua31zYFxBoTw_SU9tUSa94Iwcc"   # <-- sadece burayı sen dolduracaksın

playlist = []

def download_song(query):
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": "song.%(ext)s",
        "quiet": True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=True)
        file_path = ydl.prepare_filename(info["entries"][0])
        title = info["entries"][0]["title"]
    return file_path, title

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎵 Playlist", callback_data="playlist")],
        [InlineKeyboardButton("▶ Tümünü Çal", callback_data="play_all")]
    ]
    await update.message.reply_text(
        "🎶 Hoş geldin! Şarkı ismi yaz, mp3 göndereyim. Dinlediğin şarkılar playlist'e eklenir.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    msg = await update.message.reply_text("🔍 Arıyorum...")

    try:
        file_path, title = download_song(query)
        playlist.append(title)
        await msg.edit_text(f"🎧 *{title}* bulundu, gönderiyorum...", parse_mode="Markdown")
        await update.message.reply_audio(audio=open(file_path, "rb"))
        os.remove(file_path)
    except:
        await msg.edit_text("❌ Şarkı indirilemedi!")

async def playlist_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not playlist:
        await update.message.reply_text("📭 Playlist boş.")
        return
    text = "📀 *Playlist:*\n\n" + "\n".join([f"{i+1}. {t}" for i, t in enumerate(playlist)])
    await update.message.reply_text(text, parse_mode="Markdown")

async def play_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not playlist:
        await update.message.reply_text("📭 Playlist boş.")
        return
    await update.message.reply_text("▶ Playlist çalınıyor...")
    for title in playlist.copy():
        try:
            file_path, real_title = download_song(title)
            await update.message.reply_audio(audio=open(file_path, "rb"))
            os.remove(file_path)
        except:
            pass

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "playlist":
        if not playlist:
            await query.edit_message_text("📭 Playlist boş.")
            return
        text = "📀 *Playlist:*\n\n" + "\n".join([f"{i+1}. {t}" for i, t in enumerate(playlist)])
        await query.edit_message_text(text, parse_mode="Markdown")

    elif query.data == "play_all":
        if not playlist:
            await query.edit_message_text("📭 Playlist boş.")
            return
        await query.edit_message_text("▶ Playlist çalınıyor...")
        for title in playlist.copy():
            try:
                file_path, real_title = download_song(title)
                await query.message.reply_audio(audio=open(file_path, "rb"))
                os.remove(file_path)
            except:
                pass

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("playlist", playlist_cmd))
app.add_handler(CommandHandler("play", play_cmd))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

from telegram.ext import CallbackQueryHandler
app.add_handler(CallbackQueryHandler(button_handler))

app.run_polling()
