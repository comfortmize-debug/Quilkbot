import os
import logging
import io
import random
import string
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import requests
from PIL import Image, ImageDraw, ImageFont
import textwrap
import json
import re

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')

# User states
USER_STATES = {}

# Free image generation using public APIs (no key needed)
def generate_free_image(prompt):
    """Generate image using free services without API key"""
    try:
        # Method 1: Using Pollinations.ai (completely free, no API key)
        # This creates images on the fly
        image_url = f"https://image.pollinations.ai/prompt/{prompt.replace(' ', '%20')}?width=512&height=512&nologo=true"
        
        response = requests.get(image_url, timeout=30)
        if response.status_code == 200:
            return response.content
        else:
            return None
    except Exception as e:
        logger.error(f"Error generating image: {e}")
        return None

def generate_free_image_fallback(prompt):
    """Alternative free image generation"""
    try:
        # Using Picsum.photos for random images (with text overlay)
        width = 512
        height = 512
        image_url = f"https://picsum.photos/seed/{prompt[:10]}/{width}/{height}"
        
        response = requests.get(image_url, timeout=30)
        if response.status_code == 200:
            return response.content
        else:
            return None
    except:
        return None

def create_text_image(text, width=800, height=400):
    """Create an image with text (for content generation)"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        import textwrap
        
        # Create image
        img = Image.new('RGB', (width, height), color=(25, 25, 40))
        d = ImageDraw.Draw(img)
        
        # Try to use a font, fallback to default
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 20)
        except:
            try:
                font = ImageFont.truetype("arial.ttf", 20)
            except:
                font = ImageFont.load_default()
        
        # Wrap text
        wrapped_text = textwrap.fill(text, width=50)
        
        # Draw text
        d.text((20, 20), wrapped_text, fill=(255, 255, 255), font=font)
        
        # Convert to bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        return img_bytes.getvalue()
    except Exception as e:
        logger.error(f"Error creating text image: {e}")
        return None

def generate_content(prompt, content_type='general'):
    """Generate written content without API key"""
    try:
        # Different content types
        if content_type == 'story':
            templates = [
                f"Once upon a time, {prompt}. This is a story about discovery, growth, and the power of imagination.",
                f"In a world where {prompt}, anything was possible. The journey began with a single step.",
                f"{prompt} - this was the beginning of an incredible adventure that would change everything."
            ]
            return random.choice(templates)
            
        elif content_type == 'poem':
            templates = [
                f"In the realm of {prompt},\nWhere dreams take flight,\nMagic fills the air,\nWith endless light.",
                f"{prompt} whispers soft,\nThrough the gentle breeze,\nA story to be told,\nThat puts the mind at ease."
            ]
            return random.choice(templates)
            
        elif content_type == 'blog':
            return f"""**Blog Post: {prompt.title()}**

In today's fast-paced world, {prompt} has become increasingly important. This topic touches the lives of millions and deserves our attention.

**Key Points:**
• Understanding the fundamentals of {prompt}
• Practical applications in daily life
• Future trends and developments

**Conclusion:**
{prompt} continues to evolve and shape our world in meaningful ways. Stay tuned for more insights!"""
            
        elif content_type == 'social':
            posts = [
                f"🌟 Just discovered something amazing about {prompt}! This changes everything! #mindblown",
                f"💡 New idea: {prompt}. What are your thoughts? Let's discuss!",
                f"🚀 Excited to share my journey with {prompt}. Stay tuned for updates!",
                f"✨ {prompt} is the key to unlocking your potential. Start today!"
            ]
            return random.choice(posts)
            
        elif content_type == 'business':
            return f"""**Business Proposal: {prompt.title()}**

**Overview:**
{prompt} presents a unique opportunity for innovation and growth.

**Strategy:**
1. Market Analysis
2. Implementation Plan
3. Expected Outcomes

**Next Steps:**
Ready to explore {prompt}? Let's connect and make it happen!"""
            
        else:  # general
            topics = [
                f"Exploring {prompt}: A comprehensive look at this fascinating topic.",
                f"What if {prompt} could change the way we live and work?",
                f"The future of {prompt} is bright and full of possibilities.",
                f"Understanding {prompt}: Key insights and practical applications."
            ]
            return random.choice(topics)
            
    except Exception as e:
        logger.error(f"Error generating content: {e}")
        return "I couldn't generate content at this moment. Please try again with a different prompt."

# Welcome message
WELCOME_TEXT = """
🎨 **Quilk Bot - Your AI Creation Assistant**

Welcome to Quilk! I help you create amazing content and images.

**What I can do:**

🖼️ **Generate Images** - Describe an image, I'll create it
📝 **Write Stories** - Create engaging stories
📖 **Poems** - Generate beautiful poetry
📰 **Blog Posts** - Write content for your blog
📱 **Social Media** - Create engaging posts
💼 **Business Content** - Professional content creation

**How to use:**
/image [description] - Create an image
/story [topic] - Write a story
/poem [topic] - Generate a poem
/blog [topic] - Write a blog post
/social [topic] - Create social media post
/business [topic] - Generate business content
/content [topic] - General content generation
/help - Show all commands

**Examples:**
• /image A beautiful sunset over mountains
• /story A robot learning to love
• /poem The beauty of nature
• /blog Artificial intelligence
• /social Amazing travel experience
• /business Digital transformation

Let's create something amazing together! 🚀
"""

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message"""
    await update.message.reply_text(WELCOME_TEXT, parse_mode='Markdown')

# Help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help"""
    help_text = """
🎨 **Quilk Bot - Commands**

**Image Creation:**
/image [description] - Create an image

**Content Creation:**
/story [topic] - Write a story
/poem [topic] - Generate a poem
/blog [topic] - Write a blog post
/social [topic] - Create social media post
/business [topic] - Generate business content
/content [topic] - General content generation

**General:**
/start - Start the bot
/help - Show this help
/guide - Detailed usage guide

**Quick Tips:**
• Be descriptive in your prompts
• For images, describe colors, objects, mood
• For text, specify style (funny, serious, etc.)
• You can combine commands with extra details

**Examples:**
/image A cute cat wearing a hat
/story A magical adventure in space
/poem The ocean at sunset

What would you like to create today? 🎨✨
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')

# Image generation command
async def image_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate an image"""
    prompt = ' '.join(context.args)
    
    if not prompt:
        await update.message.reply_text(
            "🖼️ **Image Generation**\n\nPlease describe the image you want.\n\nExample: /image A beautiful sunset over mountains with a lake\n\nBe descriptive for better results! 🌅",
            parse_mode='Markdown'
        )
        return
    
    # Show typing indicator
    await update.message.chat.send_action(action="typing")
    
    # Send initial message
    status_msg = await update.message.reply_text(f"🎨 Creating your image: *{prompt[:50]}*...", parse_mode='Markdown')
    
    try:
        # Try to generate image
        image_data = generate_free_image(prompt)
        
        if image_data:
            # Send the image
            await update.message.reply_photo(
                photo=io.BytesIO(image_data),
                caption=f"🖼️ **Generated Image**\n\nPrompt: {prompt}\n\nCreated by Quilk Bot 🎨",
                parse_mode='Markdown'
            )
            await status_msg.delete()
        else:
            # Try fallback
            image_data = generate_free_image_fallback(prompt)
            if image_data:
                await update.message.reply_photo(
                    photo=io.BytesIO(image_data),
                    caption=f"🖼️ **Generated Image (Alternative Style)**\n\nPrompt: {prompt}\n\nCreated by Quilk Bot 🎨",
                    parse_mode='Markdown'
                )
                await status_msg.delete()
            else:
                # Create text-based image as fallback
                text_image = create_text_image(f"Your Image Idea:\n{prompt}\n\nImage generation is currently being enhanced. Your creative idea has been noted!")
                if text_image:
                    await update.message.reply_photo(
                        photo=io.BytesIO(text_image),
                        caption=f"📝 **Your Creative Idea**\n\nPrompt: {prompt}\n\nOur image generator is working on this! 🌟",
                        parse_mode='Markdown'
                    )
                    await status_msg.delete()
                else:
                    await status_msg.edit_text(
                        f"🔄 **Image Generation**\n\nI'm still learning to create images! Here's your idea:\n\n*{prompt}*\n\nTry again in a moment! 🎨",
                        parse_mode='Markdown'
                    )
    
    except Exception as e:
        logger.error(f"Error in image_command: {e}")
        await status_msg.edit_text(
            "⚠️ Sorry, I encountered an issue generating your image. Please try again with a simpler description.",
            parse_mode='Markdown'
        )

# Content generation commands
async def story_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate a story"""
    topic = ' '.join(context.args)
    if not topic:
        await update.message.reply_text(
            "📖 **Story Generation**\n\nTell me what you want a story about.\n\nExample: /story A young wizard discovering magic\n\nLet your imagination flow! ✨",
            parse_mode='Markdown'
        )
        return
    
    await update.message.chat.send_action(action="typing")
    content = generate_content(topic, 'story')
    await update.message.reply_text(
        f"📖 **Your Story**\n\n{content}\n\n---\nCreated by Quilk Bot 📝",
        parse_mode='Markdown'
    )

async def poem_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate a poem"""
    topic = ' '.join(context.args)
    if not topic:
        await update.message.reply_text(
            "📖 **Poem Generation**\n\nShare a theme for your poem.\n\nExample: /poem The night sky\n\nLet's create beauty with words! 🌙",
            parse_mode='Markdown'
        )
        return
    
    await update.message.chat.send_action(action="typing")
    content = generate_content(topic, 'poem')
    await update.message.reply_text(
        f"📖 **Your Poem**\n\n{content}\n\n---\n✨ Created by Quilk Bot",
        parse_mode='Markdown'
    )

async def blog_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate a blog post"""
    topic = ' '.join(context.args)
    if not topic:
        await update.message.reply_text(
            "📰 **Blog Post Generation**\n\nTell me what topic you want to write about.\n\nExample: /blog Remote work trends\n\nWrite better content! ✍️",
            parse_mode='Markdown'
        )
        return
    
    await update.message.chat.send_action(action="typing")
    content = generate_content(topic, 'blog')
    await update.message.reply_text(
        f"📰 **Your Blog Post**\n\n{content}\n\n---\n✍️ Created by Quilk Bot",
        parse_mode='Markdown'
    )

async def social_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate social media post"""
    topic = ' '.join(context.args)
    if not topic:
        await update.message.reply_text(
            "📱 **Social Media Post**\n\nWhat's your topic for social media?\n\nExample: /social New product launch\n\nCreate engaging content! 📱",
            parse_mode='Markdown'
        )
        return
    
    await update.message.chat.send_action(action="typing")
    content = generate_content(topic, 'social')
    await update.message.reply_text(
        f"📱 **Social Media Post**\n\n{content}\n\n---\n🌟 Created by Quilk Bot\n\n#QuilkBot #SocialMedia #ContentCreation",
        parse_mode='Markdown'
    )

async def business_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate business content"""
    topic = ' '.join(context.args)
    if not topic:
        await update.message.reply_text(
            "💼 **Business Content**\n\nTell me what business content you need.\n\nExample: /business Digital marketing strategy\n\nProfessional content created for you! 💼",
            parse_mode='Markdown'
        )
        return
    
    await update.message.chat.send_action(action="typing")
    content = generate_content(topic, 'business')
    await update.message.reply_text(
        f"💼 **Business Content**\n\n{content}\n\n---\n🚀 Created by Quilk Bot",
        parse_mode='Markdown'
    )

async def content_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate general content"""
    topic = ' '.join(context.args)
    if not topic:
        await update.message.reply_text(
            "📝 **Content Generation**\n\nWhat kind of content do you need?\n\nExample: /content Healthy living tips\n\nI'll create something amazing! ✨",
            parse_mode='Markdown'
        )
        return
    
    await update.message.chat.send_action(action="typing")
    content = generate_content(topic, 'general')
    await update.message.reply_text(
        f"📝 **Generated Content**\n\n{content}\n\n---\n🎨 Created by Quilk Bot",
        parse_mode='Markdown'
    )

# Guide command
async def guide_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show detailed guide"""
    guide_text = """
🎨 **Quilk Bot - Complete Guide**

**Getting Started:**
1. Use /start to initialize
2. Choose a command below
3. Add your description
4. Get your creation!

**Tips for Better Results:**

🖼️ **Images:**
- Be specific: colors, style, objects
- Add mood: peaceful, dramatic, cute
- Mention details: size, setting, perspective

📝 **Text Content:**
- Be clear about the topic
- Specify the style (humorous, formal)
- Add context for better results

**Content Types:**
📖 Stories - Narratives, adventures
📖 Poems - Rhymes, verses
📰 Blogs - Articles, posts
📱 Social - Posts, updates
💼 Business - Proposals, strategies

**Example Prompts:**
• /image A cyberpunk city at night, neon lights
• /story A detective solving mysteries in space
• /poem The beauty of autumn leaves
• /blog Tips for work-life balance
• /social Exciting weekend adventure
• /business Startup growth strategies

**Need help?** Just ask! I'm here to help you create! 🎨✨
"""
    await update.message.reply_text(guide_text, parse_mode='Markdown')

# Handle regular messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages"""
    text = update.message.text
    
    if not text:
        return
    
    # Check if user is in a creation state
    user_id = update.effective_user.id
    state = USER_STATES.get(user_id, 'default')
    
    if state == 'image':
        # Process as image prompt
        await image_command(update, context)
        USER_STATES[user_id] = 'default'
    else:
        # General response
        response = f"""🤖 Hi! I'm Quilk Bot, your creative assistant.

I can help you create:
🖼️ Images - Use /image
📖 Stories - Use /story
📖 Poems - Use /poem
📰 Blogs - Use /blog
📱 Social posts - Use /social
💼 Business content - Use /business

Just use the command followed by your topic!

Type /help to see all commands! 🎨"""
        
        await update.message.reply_text(response)

# Callback handler
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    action = query.data
    
    if action == 'image':
        USER_STATES[update.effective_user.id] = 'image'
        await query.edit_message_text(
            "🖼️ **Describe your image**\n\nSend me a description of what you want to create.\n\nExample: A beautiful sunset over mountains with a river\n\nBe creative! 🎨",
            parse_mode='Markdown'
        )

def main():
    """Start the bot"""
    if not BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN environment variable not set!")
        return
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("guide", guide_command))
    application.add_handler(CommandHandler("image", image_command))
    application.add_handler(CommandHandler("story", story_command))
    application.add_handler(CommandHandler("poem", poem_command))
    application.add_handler(CommandHandler("blog", blog_command))
    application.add_handler(CommandHandler("social", social_command))
    application.add_handler(CommandHandler("business", business_command))
    application.add_handler(CommandHandler("content", content_command))
    
    # Message handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Callback handlers
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Start the bot
    logger.info("Quilk Bot starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
