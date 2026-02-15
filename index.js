import { Telegraf } from "telegraf";
import express from "express";

const BOT_TOKEN = process.env.BOT_TOKEN;
const PORT = process.env.PORT || 3000;

if (!BOT_TOKEN) {
  console.error("❌ BOT_TOKEN missing!");
  process.exit(1);
}

const bot = new Telegraf(BOT_TOKEN);
const app = express();

// Health check
app.get("/", (req, res) => {
  res.send("RK Telegram Bot running 🚀");
});

// 🔎 LOG ALL UPDATES (to capture custom_emoji_id)
bot.on("message", (ctx) => {
  console.log("=== NEW UPDATE ===");
  console.log(JSON.stringify(ctx.update, null, 2));
});

// /hi command with premium emoji (fallback safe)
bot.command("hi", async (ctx) => {
  const REAL_CUSTOM_ID = "PASTE_REAL_CUSTOM_EMOJI_ID_HERE"; // <-- yahan apna ID daalna

  await ctx.replyWithHTML(`
<b>How are you</b> 
<tg-emoji emoji-id="${REAL_CUSTOM_ID}">💕</tg-emoji>
<tg-emoji emoji-id="${REAL_CUSTOM_ID}">💕</tg-emoji>
<tg-emoji emoji-id="${REAL_CUSTOM_ID}">☺️</tg-emoji>
  `);
});

// Start bot
bot.launch();
console.log("🤖 Bot launched");

// Express server for Heroku
app.listen(PORT, () => {
  console.log(`🌐 Server running on ${PORT}`);
});

// Graceful shutdown
process.once("SIGINT", () => bot.stop("SIGINT"));
process.once("SIGTERM", () => bot.stop("SIGTERM"));
