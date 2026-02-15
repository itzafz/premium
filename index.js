import { Telegraf } from "telegraf";
import express from "express";

const BOT_TOKEN = process.env.BOT_TOKEN;
const PORT = process.env.PORT || 3000;

const bot = new Telegraf(BOT_TOKEN);
const app = express();

// Health check route (Heroku ke liye)
app.get("/", (req, res) => {
  res.send("RK Bot is running 🚀");
});

// /start command
bot.start((ctx) => {
  ctx.replyWithHTML(`
<b>Welcome to RK Bot</b> 🚀

Premium emoji test:
<tg-emoji emoji-id="5368324170671202286">🔥</tg-emoji>

Enjoy! 😄
  `);
});

// Bot start
bot.launch();

// Express server (Heroku needs this)
app.listen(PORT, () => {
  console.log(`Server running on ${PORT}`);
});

// Graceful shutdown
process.once("SIGINT", () => bot.stop("SIGINT"));
process.once("SIGTERM", () => bot.stop("SIGTERM"));
