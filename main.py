from flask import Flask, send_file
from PIL import Image, ImageDraw
from io import BytesIO

app = Flask(__name__)

@app.route('/')
def draw_circle():
    # Create a new image with white background
    img = Image.new('RGB', (400, 400), 'white')
    draw = ImageDraw.Draw(img)
    
    # Draw a black circle
    # Parameters: [left, top, right, bottom]
    draw.ellipse([100, 100, 300, 300], outline='black', width=2)
    
    # Save image to memory buffer
    img_io = BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    
    # Return the image as a response
    return send_file(img_io, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)
