import discord
from discord.ext import commands
import requests
import os
import urllib.parse

# Cấu hình Bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Tỷ giá USD -> VND (Bạn có thể cập nhật số này tùy thời điểm)
EXCHANGE_RATE = 25400 

def format_vnd(amount):
    """Hàm định dạng số thành tiền Việt (e.g., 100.000đ)"""
    return "{:,.0f}đ".format(amount)

def get_cs2_price_range(item_name):
    # Encode tên skin (ví dụ: dấu '|' sẽ thành %7C)
    encoded_name = urllib.parse.quote(item_name)
    url = f"https://steamcommunity.com/market/priceoverview/?appid=730&currency=1&market_hash_name={encoded_name}"
    
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if data.get("success"):
            # Lấy giá thấp nhất (Steam trả về dạng string như "$1.50" hoặc "$1,200.00")
            low_str = data.get("lowest_price", "$0")
            # Xử lý chuỗi để lấy số: bỏ dấu $, bỏ dấu phẩy
            low_val = float(low_str.replace("$", "").replace(",", ""))
            
            # Tính toán khoảng giá (Ví dụ: từ giá thấp nhất đến giá đó + 7%)
            min_usd = low_val
            max_usd = low_val * 1.07
            
            # Chuyển sang VNĐ
            min_vnd = min_usd * EXCHANGE_RATE
            max_vnd = max_usd * EXCHANGE_RATE
            
            return format_vnd(min_vnd), format_vnd(max_vnd)
        return None, None
    except Exception as e:
        print(f"Lỗi API: {e}")
        return None, None

@bot.event
async def on_ready():
    print(f'Đã đăng nhập thành công bot: {bot.user.name}')

@bot.command(name="skin")
async def skin(ctx, *, name: str):
    await ctx.send(f"🔍 Đang định giá: **{name}**...")
    
    p_min, p_max = get_cs2_price_range(name)
    
    if p_min:
        embed = discord.Embed(
            title="🎯 ĐỊNH GIÁ SKIN CS2", 
            description=f"**Tên vật phẩm:** {name}",
            color=0x1dff00 # Màu xanh lá
        )
        embed.add_field(name="Khoảng giá xấp xỉ (VNĐ)", value=f"```Từ {p_min} đến {p_max}```", inline=False)
        embed.set_footer(text=f"Tỷ giá áp dụng: 1 USD = {EXCHANGE_RATE:,} VNĐ")
        await ctx.send(embed=embed)
    else:
        await ctx.send("❌ Không tìm thấy skin này! Lưu ý:\n1. Phải ghi đúng tên tiếng Anh.\n2. Ví dụ: `!skin AK-47 | Slate (Factory New)`\n3. Hoặc: `!skin Recoil Case`")

# Lấy Token từ Variables của Railway
token = os.getenv("DISCORD_TOKEN")
if token:
    bot.run(token)
else:
    print("Lỗi: Không tìm thấy DISCORD_TOKEN trong biến môi trường!")
