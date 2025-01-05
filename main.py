from flask import Flask, render_template, send_from_directory
from flask.templating import render_template_string
import logging

app = Flask(__name__)

# CSS styles
STYLES = '''
    #canvas {
        border: 1px solid black;
    }
    #colorPicker {
        margin: 10px;
        padding: 10px;
        background: #f0f0f0;
        border-radius: 5px;
    }
    .color-btn {
        margin: 5px;
        padding: 10px 20px;
        border: none;
        border-radius: 5px;
        cursor: pointer;
    }
'''

# JavaScript animation code
ANIMATION_SCRIPT = '''
    const canvas = document.getElementById('canvas');
    const ctx = canvas.getContext('2d');
    const duckSound = new Audio('static/duck.mp3');
    
    let x = 150;
    let y = 150;
    let dx = 4;
    let dy = 4;
    const radius = 50;
    let circleColor = 'red';  // default color
    
    const rainbowColors = {
        'Red': '#FF0000',
        'Orange': '#FF7F00',
        'Yellow': '#FFFF00',
        'Green': '#00FF00',
        'Blue': '#0000FF',
        'Indigo': '#4B0082',
        'Violet': '#8F00FF'
    };

    function setColor(color) {
        circleColor = color;
        document.getElementById('colorPicker').style.display = 'none';
        drawCircle();
    }
    
    function playDuckSound() {
        duckSound.currentTime = 0;
        duckSound.play();
    }
    
    function drawCircle() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        ctx.beginPath();
        ctx.arc(x, y, radius, 0, Math.PI * 2);
        ctx.fillStyle = circleColor;
        ctx.fill();
        ctx.strokeStyle = '#00FF00';
        ctx.lineWidth = 2;
        ctx.stroke();
        
        if (x + radius > canvas.width || x - radius < 0) {
            dx = -dx;
            playDuckSound();
        }
        if (y + radius > canvas.height || y - radius < 0) {
            dy = -dy;
            playDuckSound();
        }
        
        x += dx;
        y += dy;
        
        requestAnimationFrame(drawCircle);
    }
'''

@app.route('/')
def draw_circle():
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            {STYLES}
        </style>
    </head>
    <body>
        <div id="colorPicker">
            <h3>Choose a color for the circle:</h3>
            <button class="color-btn" style="background: #FF0000" onclick="setColor('#FF0000')">Red</button>
            <button class="color-btn" style="background: #FF7F00" onclick="setColor('#FF7F00')">Orange</button>
            <button class="color-btn" style="background: #FFFF00" onclick="setColor('#FFFF00')">Yellow</button>
            <button class="color-btn" style="background: #00FF00" onclick="setColor('#00FF00')">Green</button>
            <button class="color-btn" style="background: #0000FF" onclick="setColor('#0000FF')">Blue</button>
            <button class="color-btn" style="background: #4B0082" onclick="setColor('#4B0082')">Indigo</button>
            <button class="color-btn" style="background: #8F00FF" onclick="setColor('#8F00FF')">Violet</button>
        </div>
        <canvas id="canvas" width="800" height="600"></canvas>
        <script>
            {ANIMATION_SCRIPT}
        </script>
    </body>
    </html>
    '''
    return render_template_string(html)

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    app.logger.setLevel(logging.DEBUG)
    app.run(debug=True, port=8000)
