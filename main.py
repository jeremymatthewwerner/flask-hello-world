from flask import Flask, render_template, send_from_directory
from flask.templating import render_template_string
import logging

app = Flask(__name__)

# CSS styles
STYLES = '''
    #canvas {
        border: 1px solid black;
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
    
    function playDuckSound() {
        duckSound.currentTime = 0;
        duckSound.play();
    }
    
    function drawCircle() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        ctx.beginPath();
        ctx.arc(x, y, radius, 0, Math.PI * 2);
        ctx.fillStyle = 'red';
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
    
    drawCircle();
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
